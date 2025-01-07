Project Description:
    InsightsDesk is designed specifically for non-technical C-level executives to enable easy access to database insights without needing in-depth technical knowledge. Utilizing an open API, InsightsDesk communicates with users to deliver data-related insights directly or provides general answers using the Tavily API based on the nature of the queries.

Technology Stack:
    Python: For backend logic and data handling.
    Docker: Used to containerize the PostgreSQL database and pgAdmin tool.
    PostgreSQL: The database used to store and retrieve data.
    pgAdmin: Web-based administration tool for PostgreSQL.
    Streamlit: For creating the frontend user interface.
    Various Python libraries: Detailed in the requirements.txt.
    Setup Instructions Prerequisites:
        Docker installed on your machine.
        Python 3.x.
    Installation:
    Clone the repository:
        git clone <repository-url>
    Navigate to the project directory:
        cd InsightsDesk
    Start Docker containers:
        docker-compose up -d
    Install Python dependencies:
        pip install -r requirements.txt

Environment Variables
Set the following environment variables:
    TAVILY_API_KEY: Your Tavily API key.
    OPENAI_API_KEY: Your OpenAI API key.

Usage:
Once the setup is complete, you can start the Streamlit application to interact with the chatbot:
    streamlit run streamlit_app.py

Project Structure:
    docker-compose.yaml: Configures the Docker containers for PostgreSQL and pgAdmin.
    data2.ipynb: Jupyter notebook used to load CSV data into the PostgreSQL database.
    agent.py: Contains backend logic for query classification, SQL query generation, and results interpretation.
    streamlit_app.py: Streamlit application that serves as the frontend interface.

Features:
    Database Schema Introspection: Automatically fetches and displays database schema information.
    RAG-based Question Classification: Determines whether a question is related to the database or general knowledge.
    SQL Query Generation and Execution: Generates and executes SQL queries based on user input.
    Integration with Tavily API: Handles general knowledge questions by querying the Tavily API.

How to Contribute
If you wish to contribute to InsightsDesk, please follow these steps:
    Fork the repository.
    Create a new branch for your feature.
    Commit your changes.
    Push to the branch.
    Submit a pull request.