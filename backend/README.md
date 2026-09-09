# AI Cooking Platform - Backend

This is the FastAPI backend for the AI Cooking Platform 2.0.

## Setup Instructions

1. Ensure you have Python installed.
2. Create and activate a virtual environment (already done via `venv`).
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your secrets.
5. Run the server locally:
   ```bash
   uvicorn app.main:app --reload
   ```

## Structure
- `app/api`: FastAPI routers organized by feature.
- `app/core`: Configuration, settings, security.
- `app/db`: Database connection logic.
- `app/models`: MongoDB ORM/ODM models.
- `app/schemas`: Pydantic models for validation.
- `app/services`: Business logic (ML integrations, LLM calls, Recommendations).
