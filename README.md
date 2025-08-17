# NyayEase - Legal AI Assistant

## Project Title
NyayEase - Legal AI Assistant

## Description
NyayEase is an AI-powered legal assistant designed to provide comprehensive support for Indian law. It leverages advanced AI models to answer legal queries, analyze legal documents, and offer guidance based on various legal scenarios. This application aims to make legal information more accessible and understandable.

## Features
*   **User Authentication:** Secure user registration and login functionalities.
*   **AI-powered Legal Query Answering:** Get instant answers to your legal questions.
*   **Document Upload and Analysis:** Upload PDF and DOCX documents for text extraction and analysis.
*   **Scenario-based Legal Guidance:** Explore legal implications through predefined scenarios.
*   **Static File Serving:** Serve static assets like CSS, JavaScript, and images.
*   **CORS Enabled:** Configured for cross-origin resource sharing.

## Technologies Used
The project is built using the following key technologies and libraries:

*   **Backend Framework:** FastAPI
*   **ASGI Server:** Uvicorn
*   **Database ORM:** SQLAlchemy
*   **Database:** SQLite (default, configurable)
*   **AI/ML:**
    *   Google Generative AI
    *   Langchain
    *   Langchain Community
    *   Sentence Transformers
    *   ChromaDB (Vector Store)
*   **Document Processing:**
    *   PyMuPDF (for PDF processing)
    *   PyTesseract (OCR)
    *   Pillow (PIL Fork)
    *   Python-Docx (for DOCX processing)
*   **Authentication:** Python-Jose, Passlib (Bcrypt)
*   **Templating:** Jinja2
*   **HTTP Client:** httpx, aiohttp
*   **Logging:** Structlog
*   **Development/Testing:** Pytest, Black, Flake8

## Setup and Installation

Follow these steps to set up and run the NyayEase application locally:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/NyayEase.git
cd NyayEase
```

### 2. Create a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
*   **Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
*   **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 4. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

### 5. Environment Variables
Create a `.env` file in the root directory of the project and add necessary environment variables. At a minimum, you'll need:

```
DATABASE_URL="sqlite:///./nyayease.db"
# Add your Google API Key for Generative AI
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```
Replace `YOUR_GOOGLE_API_KEY` with your actual Google API key.

### 6. Create Database Tables
Run the script to initialize the database schema:
```bash
python create_db.py
```

### 7. Run the Application
Start the FastAPI application using Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The `--reload` flag enables auto-reloading on code changes, which is useful for development. The `--host 0.0.0.0` makes the server accessible from your network, and `--port 8000` sets the port.

The application will be accessible at `http://127.0.0.1:8000` or `http://localhost:8000`.

## Usage

Once the application is running, you can access the web interface through your browser.

*   **Home Page:** `http://localhost:8000`
*   **Chat Interface:** `http://localhost:8000/chat`
*   **Documents Page:** `http://localhost:8000/documents`

You can interact with the API endpoints directly using tools like Postman, Insomnia, or `curl`.

## File Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py             # Application settings
│   ├── main.py               # Main FastAPI application, routes, middleware
│   ├── database/
│   │   ├── connection.py     # Database connection and session management
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── models/               # Pydantic models for request/response
│   │   ├── document.py
│   │   ├── query.py
│   │   └── user.py
│   ├── routes/               # API endpoint definitions
│   │   ├── auth.py           # Authentication routes
│   │   ├── document_upload.py# Document upload and processing routes
│   │   ├── legal_query.py    # Legal query handling routes
│   │   └── scenarios.py      # Legal scenarios routes
│   ├── scripts/
│   │   └── process_documents.py # Script for document processing
│   └── services/             # Business logic and external integrations
│       ├── ai_service.py     # AI model interactions
│       ├── auth_service.py   # Authentication logic
│       ├── ocr_service.py    # OCR functionalities
│       └── vector_service.py # Vector database interactions
│   └── utils/                # Utility functions
│       ├── embeddings.py     # Embedding generation
│       ├── text_processing.py# Text cleaning and manipulation
│       └── validators.py     # Data validation utilities
├── chroma_db/                # ChromaDB persistent storage
├── static/                   # Static files (CSS, JS, images)
├── templates/                # Jinja2 HTML templates
│   ├── base.html
│   ├── chat.html
│   ├── documents.html
│   └── index.html
├── uploads/                  # Directory for uploaded documents
├── .gitignore                # Git ignore file
├── create_db.py              # Script to create database tables
├── nyayease.db               # Default SQLite database file
├── requirements.txt          # Python dependencies
└── README.md                 # Project README file
```

## API Endpoints

The API endpoints are prefixed as follows:

*   **Authentication:** `/api/v1/auth`
*   **Legal Query:** `/api/v1/query`
*   **Documents:** `/api/v1/documents`
*   **Scenarios:** `/api/v1/scenarios`

Detailed API documentation (Swagger UI) will be available at `http://localhost:8000/docs` when the application is running.

## Database Schema

The application uses the following SQLAlchemy models for its database:

### `User` Table
*   `id` (Integer, Primary Key)
*   `username` (String, Unique, Indexed)
*   `email` (String, Unique, Indexed)
*   `hashed_password` (String)
*   `preferred_language` (String, default='en')
*   `created_at` (DateTime, default=utcnow)
*   `is_active` (Boolean, default=True)

### `Query` Table
*   `id` (Integer, Primary Key)
*   `user_id` (Integer, Foreign Key to `users.id`)
*   `query_text` (Text)
*   `response_text` (Text)
*   `query_type` (String) # e.g., "constitution", "scenario", "document"
*   `language` (String, default='en')
*   `created_at` (DateTime, default=utcnow)

### `Document` Table
*   `id` (Integer, Primary Key)
*   `user_id` (Integer, Foreign Key to `users.id`)
*   `filename` (String)
*   `file_path` (String)
*   `extracted_text` (Text)
*   `analysis_result` (Text)
*   `upload_date` (DateTime, default=utcnow)

### `LegalDocument` Table
*   `id` (Integer, Primary Key)
*   `title` (String)
*   `document_type` (String) # e.g., "constitution", "ipc", "act"
*   `section` (String)
*   `content` (Text)
*   `embedding_id` (String) # Reference to vector store

## License
This project is licensed under the MIT License.
