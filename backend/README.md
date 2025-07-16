# NBK Pay Backend

## Setup

1. Install Python 3.11+ and pip.
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and set all secrets/config.
5. Run DB migrations (if using Alembic), or let SQLAlchemy create tables.
6. Run the API:
   ```
   uvicorn app:app --reload
   ```

## Deployment

- Deploy on [Render.com](https://render.com/) as a Python web service.
- Set environment variables/secrets in Render dashboard.
- Use `uvicorn app:app` as start command.

## API Docs

- OpenAPI/Swagger docs at `/docs` after running.

---
