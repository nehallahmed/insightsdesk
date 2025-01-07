import logging
from typing import Dict, TypedDict, Annotated, Sequence
from langgraph.graph import Graph, MessageGraph
import operator
from typing import Annotated, Sequence
import json
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage, AIMessage
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX, _mysql_prompt
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from sqlalchemy import create_engine, inspect
import pandas as pd
from tavily import TavilyClient
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


# Add these prompt definitions after your imports and before the workflow code
classifier_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a query classifier that determines if a question can be answered using SQL queries on the given database schema.
    Output only 'true' if the question requires querying the database, or 'false' if it's a general knowledge question.
    
    Database Schema:
    {schema}"""),
    MessagesPlaceholder(variable_name="messages"),
])

query_generator_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an SQL expert. Generate a SQL query using PostgreSQL syntax to answer the user's question based on the given schema.
    Output ONLY the raw SQL query without any markdown formatting, prefixes, or explanations.
    Example output format:
    SELECT column FROM table WHERE condition;
    SELECT column, count(*) as count FROM table WHERE condition group by column order by column;
    SELECT product_name, product_maximum_retail_price FROM products WHERE product_maximum_retail_price = (SELECT MAX(product_maximum_retail_price) FROM products);
    
    Database Schema:
    {schema}"""),
    MessagesPlaceholder(variable_name="messages"),
])

interpreter_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that interprets SQL query results in natural language.
    Explain the results in a clear and concise way that directly answers the user's question.
    
    Original question: {messages}
    SQL Query used: {query}
    Query results: {results}"""),
])
# Configure logging
def setup_logger():
    logger = logging.getLogger('database_query_system')
    logger.setLevel(logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler(f'query_log_{datetime.now().strftime("%Y%m%d")}.log')
    console_handler = logging.StreamHandler()
    
    # Create formatters and add it to handlers
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

# Database connection
db_params = {
    'host': 'localhost',
    'port': '5432',
    'user': 'admin',
    'password': 'admin',
    'database': 'mydb'
}

engine = create_engine(
    f'postgresql+psycopg2://{db_params["user"]}:{db_params["password"]}@'
    f'{db_params["host"]}:{db_params["port"]}/{db_params["database"]}'
)

# Initialize Tavily client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Function to get schema information
def get_schema_str():
    inspector = inspect(engine)
    schema_info = []
    
    for table_name in inspector.get_table_names():
        columns = []
        for column in inspector.get_columns(table_name):
            columns.append(f"{column['name']} ({column['type']})")
        schema_info.append(f"Table: {table_name}\nColumns: {', '.join(columns)}")
    
    return "\n\n".join(schema_info)

# State definition
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    is_db_related: bool
    sql_query: str
    results: str

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo-preview", api_key=OPENAI_API_KEY, temperature=0)

def classify(state: State) -> State:
    messages = state["messages"]
    classification_chain = classifier_prompt | llm | StrOutputParser()
    response = classification_chain.invoke({
        "messages": messages,
        "schema": get_schema_str()
    })
    state["is_db_related"] = response.lower() == "true"
    
    # Log classification result
    logger.info(f"Query Classification - Input: {messages[-1].content} - Is DB Related: {state['is_db_related']}")
    
    return state

def generate_query(state: State) -> State:
    if not state["is_db_related"]:
        return state
        
    messages = state["messages"]
    query_chain = query_generator_prompt | llm | StrOutputParser()
    query = query_chain.invoke({
        "messages": messages,
        "schema": get_schema_str()
    })
    state["sql_query"] = query
    
    # Log generated query
    logger.info(f"Generated SQL Query: {query}")
    
    return state

def execute_query(state: State) -> State:
    if not state["is_db_related"]:
        return state
        
    try:
        with engine.connect() as conn:
            # Log query execution attempt
            logger.info(f"Executing SQL Query: {state['sql_query']}")
            
            result = pd.read_sql_query(state["sql_query"], conn)
            state["results"] = result.to_string()
            
            # Log successful execution
            logger.info(f"Query Execution Successful - Result Shape: {result.shape}")
            
    except Exception as e:
        error_message = f"Error executing query: {str(e)}"
        state["results"] = error_message
        # Log error
        logger.error(f"Query Execution Failed: {error_message}")
        
    return state

def get_tavily_response(query: str) -> str:
    try:
        # Log Tavily API call
        logger.info(f"Calling Tavily API for query: {query}")
        
        response = tavily.search(
            query=query,
            search_depth="advanced",
            include_answer=True
        )
        
        # Log successful Tavily response
        logger.info("Tavily API call successful")
        
        return response.get('answer', 'No direct answer found.')
    except Exception as e:
        error_message = f"Tavily API Error: {str(e)}"
        logger.error(error_message)
        return f"Error getting information: {error_message}"

def interpret_results(state: State) -> State:
    messages = state["messages"]
    
    if not state["is_db_related"]:
        # Get response from Tavily for non-DB queries
        tavily_response = get_tavily_response(messages[-1].content)
        response = tavily_response
        
        # Log Tavily response
        logger.info(f"Non-DB Query - Tavily Response Used")
    else:
        # Interpret database results
        interpreter_chain = interpreter_prompt | llm | StrOutputParser()
        response = interpreter_chain.invoke({
            "messages": messages,
            "query": state["sql_query"],
            "results": state["results"]
        })
        
        # Log interpretation
        logger.info(f"DB Query - Interpretation Complete")
    
    state["messages"] = list(state["messages"]) + [AIMessage(content=response)]
    return state

# Rest of the code remains the same...
def build_graph():
    workflow = Graph()
    
    workflow.add_node("classifier", classify)
    workflow.add_node("query_generator", generate_query)
    workflow.add_node("executor", execute_query)
    workflow.add_node("interpreter", interpret_results)
    
    workflow.set_entry_point("classifier")
    
    workflow.add_edge("classifier", "query_generator")
    workflow.add_edge("query_generator", "executor")
    workflow.add_edge("executor", "interpreter")
    
    workflow.set_finish_point("interpreter")
    
    return workflow.compile()

# Create the agent
graph = build_graph()

def process_question(question: str) -> str:
    # Log incoming question
    logger.info(f"Processing New Question: {question}")
    
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "is_db_related": False,
        "sql_query": "",
        "results": ""
    }
    
    result = graph.invoke(initial_state)
    
    # Log completion
    logger.info("Question Processing Complete")
    
    return result["messages"][-1].content

if __name__ == "__main__":
    # Test with different types of questions
    questions = [
        "What is the name of the product having this barcode 5732~AAA0001~44?"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        print(f"Answer: {process_question(question)}")