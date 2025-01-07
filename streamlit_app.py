import streamlit as st
from typing import List
from langchain_core.messages import ChatMessage
import time
from agent import process_question  # Import your existing process_question function

# Page configuration
st.set_page_config(
    page_title="InsightsDesk",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        ChatMessage(role="assistant", content="Hello! I can help you query the database. What would you like to know?")
    ]

def response_generator(response: str, delay: float = 0.03):
    """Generate response with a typing effect"""
    for token in response:
        yield token
        time.sleep(delay)

# Fixed StreamHandler class
class StreamHandler:
    def _init_(self):
        self.text = ""  # Initialize text attribute in _init_
        self.container = None
    
    def set_container(self, container):
        self.container = container
        return self
    
    def on_llm_new_token(self, token: str) -> None:
        if not hasattr(self, 'text'):  # Extra safety check
            self.text = ""
        self.text += token
        if self.container is not None:
            self.container.markdown(self.text)

# Sidebar
with st.sidebar:
    st.title("InsightsDesk")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = [
            ChatMessage(role="assistant", content="Hello! I can help you query the database. What would you like to know?")
        ]
        st.rerun()
    
    st.markdown("""
    ### Example Questions:
    - What products have the highest growth month over month?
    - What is the name of the product having this barcode 5732~AAA0001~44?
    - Which products have the most consistent sales?
    """)

# Main chat interface
st.title("InsightsDesk")

# Display chat history
for msg in st.session_state.messages:
    if msg.role == "user":
        st.chat_message("user").write(msg.content)
    else:
        st.chat_message("assistant").write(msg.content)

# User input
if user_input := st.chat_input("Ask a question about your data..."):
    # Add user message to chat history
    st.session_state.messages.append(ChatMessage(role="user", content=user_input))
    st.chat_message("user").write(user_input)
    
    # Process the query and stream the response
    with st.chat_message("assistant"):
        container = st.empty()
        stream_handler = StreamHandler().set_container(container)  # Chain the set_container call
        
        try:
            # Process the question using your existing backend
            response = process_question(user_input)
            
            # Stream the response with a typing effect
            for token in response_generator(response):
                stream_handler.on_llm_new_token(token)
            
            # Add assistant's response to chat history
            st.session_state.messages.append(
                ChatMessage(role="assistant", content=response)
            )
            
        except Exception as e:
            error_message = f"Error processing query: {str(e)}"
            stream_handler.on_llm_new_token(error_message)
            st.session_state.messages.append(
                ChatMessage(role="assistant", content=error_message)
            )

# Footer
st.markdown("---")
st.markdown("MSDS - FYP Project - Nehal Ahmed 25751")