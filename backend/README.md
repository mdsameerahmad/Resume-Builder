# ATS Resume Agent Backend

This is the backend foundation for the ATS Resume Agent, built with FastAPI, Python 3.12, and Clean Architecture. It provides a robust pipeline for uploading resumes, extracting high-fidelity layouts, parsing content with AI, analyzing job descriptions, running gap analyses, optimizing resumes, and generating one-page ATS-friendly PDFs that preserve the original design.

## Features

- **FastAPI**: Modern, fast (high-performance) web framework.
- **Pydantic v2**: Strict data validation and schema definitions.
- **SQLAlchemy 2.0 (Async)**: Non-blocking Database ORM.
- **Alembic**: Database migrations.
- **Clean Architecture**: Separation of concerns across routers, services, repositories, and models.
- **Layout Extraction Engine**: Uses `PyMuPDF` (`fitz`) to extract exact font styles, sizes, colors, and spatial bounding boxes from uploaded PDFs.
- **AI Integration (Gemini)**: Powers job description analysis, resume parsing, and content optimization.
- **Content Compression Pipeline**: Heuristic point-based (pt) height estimation to strictly compress content into a 1-page A4 format without losing critical information.
- **Template Preserving Rendering**: Converts extracted PDF styles into Jinja2/CSS templates.
- **Threaded PDF Generation**: Runs Playwright in a dedicated `ThreadPoolExecutor` with a `ProactorEventLoop` to bypass Windows `SelectorEventLoop` limitations for async subprocesses.

---

## Project Structure

```
backend/
├── app/
│   ├── api/            # API endpoints (v1 routers)
│   ├── core/           # Core config, logging, exceptions, windows compatibility
│   ├── config/         # App configuration settings
│   ├── database/       # Async SQLAlchemy setup and session management
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic schemas for requests/responses
│   ├── services/       # Core Business logic (Extraction, Parsing, Rendering, Compression)
│   ├── repositories/   # Data access layer (abstracts DB calls)
│   ├── utils/          # Utility functions
│   ├── middleware/     # Custom middleware (CORS, exceptions)
│   ├── templates/      # Jinja2 templates (fallback/base templates)
│   └── static/         # Static files (Generated HTML and PDFs are stored here)
├── alembic/            # Migration scripts
├── logs/               # Application logs
├── tests/              # Unit and integration tests
├── .env.example        # Example environment variables
├── requirements.txt    # Project dependencies
└── main.py             # FastAPI entry point
```

---

## API Endpoints Reference

All API routes are prefixed with `/api/v1` (configurable via `API_V1_STR` in settings). 

### 1. Resume Management
- **`POST /api/v1/resume/upload`**
  - **Description**: Uploads a PDF or DOCX file.
  - **Payload**: `multipart/form-data` with key `file`.
  - **Response**: `ResumeUploadResponse` containing `resume_id`.
- **`GET /api/v1/resume/list`**
  - **Description**: Lists all uploaded resumes.
- **`GET /api/v1/resume/{resume_id}`**
  - **Description**: Retrieves metadata for a specific resume.
- **`DELETE /api/v1/resume/{resume_id}`**
  - **Description**: Deletes a resume.

### 2. Resume Processing (Extraction & Parsing)
- **`POST /api/v1/resume/extract/{resume_id}`**
  - **Description**: Extracts raw text, layout data, fonts, and links from the PDF using PyMuPDF.
  - **Response**: `ExtractionResponse`.
- **`GET /api/v1/resume/extraction/{resume_id}`**
  - **Description**: Retrieves previously extracted data.
- **`POST /api/v1/resume/parse/{resume_id}`**
  - **Description**: Parses extracted text into a structured JSON Master Profile using AI.
  - **Response**: `MasterResumeResponse`.
- **`GET /api/v1/resume/master/{resume_id}`**
  - **Description**: Retrieves the parsed Master Resume Profile.

### 3. Template Generation
- **`POST /api/v1/template/generate/{resume_id}`**
  - **Description**: Analyzes the original PDF's spatial layout and generates a reusable Jinja2 HTML/CSS template that mirrors the design.
  - **Response**: `TemplateCreateResponse`.
- **`GET /api/v1/template/{resume_id}`**
  - **Description**: Retrieves the generated template.
- **`GET /api/v1/template/{resume_id}/preview`**
  - **Description**: Renders and returns an HTML preview of the template injected with the master profile data.

### 4. Job Description (JD) Analysis
- **`POST /api/v1/jd/analyze`**
  - **Description**: Analyzes a raw job description text to extract keywords, skills, and requirements.
  - **Payload (JSON)**: `{"job_description": "Raw JD text..."}`
  - **Response**: `JDAnalysisResponse` with `job_id`.
- **`GET /api/v1/jd/{job_id}`**
  - **Description**: Retrieves parsed JD data.
- **`GET /api/v1/jd/user/all`**
  - **Description**: Lists all analyzed JDs.

### 5. Intelligence & Optimization Pipeline
- **`POST /api/v1/gap/analyze`**
  - **Description**: Compares the Master Resume against the parsed JD to calculate match scores and identify missing keywords.
  - **Payload (JSON)**: `{"resume_id": "uuid", "job_id": "uuid"}`
  - **Response**: `GapAnalysisResponse` with detailed score breakdowns.
- **`GET /api/v1/gap/{report_id}`**
  - **Description**: Retrieves a gap analysis report.
- **`POST /api/v1/optimizer/generate`**
  - **Description**: Generates an optimized, targeted JSON resume tailored to the JD.
  - **Payload (JSON)**: `{"resume_id": "uuid", "job_id": "uuid"}`
  - **Response**: `OptimizeResponse` with `optimized_resume_id`.
- **`GET /api/v1/optimizer/{optimized_id}`**
  - **Description**: Retrieves the optimized JSON payload.

### 6. PDF Rendering & Output
- **`POST /api/v1/pdf/generate`**
  - **Description**: Compresses the optimized JSON to fit 1 page, injects it into the custom HTML template, and renders a PDF via Playwright.
  - **Payload (JSON)**: `{"optimized_resume_id": "uuid"}`
  - **Response**: `PDFGenerateResponse` containing URLs to the generated PDF and HTML.
- **`GET /api/v1/pdf/{generated_id}`**
  - **Description**: Retrieves metadata for the generated files.
- **`GET /api/v1/pdf/{generated_id}/download`**
  - **Description**: Downloads the actual PDF file.

### 7. System Routes
- **`GET /api/v1/health/health`**: API health check.
- **`GET /api/v1/database/health`**: Database connection health check.
- **`POST /api/v1/database/init`**: Initializes database tables manually.

---

## Setup Instructions

1. **Python Version**: Ensure you are using Python 3.12+.
2. **Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   source venv/Scripts/activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install Playwright Browsers**:
   This is strictly required for the PDF rendering engine to function.
   ```bash
   playwright install chromium
   ```
5. **Environment Variables**:
   - Copy `.env.example` to `.env`.
   - Ensure you add your AI API Keys (e.g., `GEMINI_API_KEY`) and database connection strings.

## Running the Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`. 
Generated PDFs and HTML files will be served statically from `http://localhost:8000/static/resumes/`.

## API Documentation

FastAPI automatically generates interactive OpenAPI documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Important Architectural Notes

- **Windows AsyncIO Compatibility**: On Windows, FastAPI/Uvicorn defaults to `SelectorEventLoop`, which crashes when Playwright tries to open subprocesses. The backend mitigates this by dispatching Playwright rendering tasks to a dedicated thread with a new `ProactorEventLoop` initialized.
- **A4 Layout Compression**: The `PageOptimizer` calculates physical height in points (`pt`) using empirical metrics for Arial/Helvetica fonts to aggressively trim bullet points and summaries until the document is guaranteed to fit on a single A4 page (approx. 842 points height).
