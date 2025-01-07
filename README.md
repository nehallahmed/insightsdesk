# InsightsDesk

**InsightsDesk** is designed specifically for non-technical C-level executives to enable easy access to database insights without requiring in-depth technical knowledge. Utilizing an open API, InsightsDesk communicates with users to deliver data-related insights directly or provides general answers using the Tavily API based on the nature of the queries.

---

## Technology Stack
- **Python**: For backend logic and data handling.
- **Docker**: Used to containerize the PostgreSQL database and pgAdmin tool.
- **PostgreSQL**: The database used to store and retrieve data.
- **pgAdmin**: Web-based administration tool for PostgreSQL.
- **Streamlit**: For creating the frontend user interface.
- **Various Python libraries**: Detailed in `requirements.txt`.

---

## Setup Instructions

### Prerequisites
- Docker installed on your machine.
- Python 3.x installed.

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd InsightsDesk
   ```
3. Start Docker containers:
   ```bash
   docker-compose up -d
   ```
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Variables
Set the following environment variables:

- `TAVILY_API_KEY`: Your Tavily API key.
- `OPENAI_API_KEY`: Your OpenAI API key.

---

## Usage
Once the setup is complete, you can start the Streamlit application to interact with the chatbot:
```bash
streamlit run streamlit_app.py
```

---

## Project Structure
- **`docker-compose.yaml`**: Configures the Docker containers for PostgreSQL and pgAdmin.
- **`data2.ipynb`**: Jupyter notebook used to load CSV data into the PostgreSQL database.
- **`agent.py`**: Contains backend logic for query classification, SQL query generation, and results interpretation.
- **`streamlit_app.py`**: Streamlit application that serves as the frontend interface.

---

## Features
- **Database Schema Introspection**: Automatically fetches and displays database schema information.
- **RAG-based Question Classification**: Determines whether a question is related to the database or general knowledge.
- **SQL Query Generation and Execution**: Generates and executes SQL queries based on user input.
- **Integration with Tavily API**: Handles general knowledge questions by querying the Tavily API.

---

## How to Contribute
If you wish to contribute to **InsightsDesk**, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add description of changes"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Thank you for using **InsightsDesk**! 🎉 If you encounter any issues, feel free to create an issue in the repository.
```

### Notes:
1. Replace `<repository-url>` with your actual repository URL.
2. Add a `LICENSE` file to the repository if you plan to use an open-source license.
3. Feel free to add badges (e.g., build status, license type) to the top of the README for extra polish. Let me know if you'd like assistance with that!
