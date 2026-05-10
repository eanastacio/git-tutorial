# VisaSponsor Backend

FastAPI service for VisaSponsor, including:

- Search/filter APIs for sponsorship data
- Analytics APIs for dashboards
- Authenticated saved-company endpoints
- Admin ingestion APIs and batch ETL pipeline

## Run locally

```bash
cp .env.example .env
pip install -e .
python scripts/create_db.py
python scripts/seed_demo_data.py
uvicorn app.main:app --reload --port 8000
```

## Ingest data

```bash
python scripts/ingest_year.py --year 2025
```
