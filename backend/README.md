# ATS Resume Agent Backend

This is the backend foundation for the ATS Resume Agent, built with FastAPI, Python 3.12, and Clean Architecture.

## Features

- **FastAPI**: Modern, fast (high-performance) web framework.
- **Pydantic v2**: Data validation and settings management.
- **SQLAlchemy 2.0**: Database ORM.
- **Alembic**: Database migrations.
- **Loguru**: Enhanced logging.
- **Clean Architecture**: Structured for scalability and maintainability.

## Project Structure

```
backend/
├── app/
│   ├── api/            # API endpoints (v1)
│   ├── core/           # Core configuration, logging, exceptions
│   ├── config/         # App configuration settings
│   ├── database/       # Database connection and session management
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── repositories/   # Data access layer
│   ├── utils/          # Utility functions
│   ├── middleware/     # Custom middleware (exceptions, etc.)
│   ├── templates/      # Jinja2 templates (if needed)
│   └── static/         # Static files
├── uploads/            # Uploaded resumes
├── generated/          # Generated content
├── logs/               # Application logs
├── tests/              # Unit and integration tests
├── .env.example        # Example environment variables
├── requirements.txt    # Project dependencies
└── main.py             # Entry point
```

## Setup Instructions

1. **Python Version**: Ensure you are using Python 3.12.
2. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   - Copy `.env.example` to `.env`.
   - Update the variables in `.env` with your actual credentials.

## Running the Server

```bash
cd backend
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`.

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Health Check

- **Endpoint**: `GET /health`
- **Response**:
  ```json
  {
    "status": "ok",
    "service": "ats-resume-agent",
    "version": "1.0.0"
  }
  ```
