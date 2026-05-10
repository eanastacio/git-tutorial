# VisaSponsor

VisaSponsor is a production-oriented full-stack platform that helps international students identify U.S. companies with strong H1-B sponsorship history using U.S. Department of Labor LCA disclosure data.

## Tech Stack

### Frontend
- Next.js (App Router)
- TypeScript
- TailwindCSS
- shadcn-style reusable UI components
- Clerk authentication
- Recharts analytics visualizations

### Backend
- FastAPI (REST APIs)
- SQLAlchemy (async)
- pandas ETL pipeline
- Redis caching (optional but supported)
- SlowAPI rate limiting

### Database
- PostgreSQL with indexed normalized schema

### Infrastructure
- Docker + docker-compose
- Vercel config for frontend deployment
- Render/Railway templates for backend deployment

---

## Monorepo Structure

```text
apps/
  backend/
    app/
      api/              # REST routers
      core/             # config, auth, logging, caching
      db/               # DB engine/session
      models/           # SQLAlchemy models
      normalization/    # company + location normalization
      processors/       # row-level LCA parsing/cleaning
      scraper/          # DOL dataset downloader
      schemas/          # Pydantic request/response types
      services/         # domain/business services
    scripts/
      create_db.py
      seed_demo_data.py
      ingest_year.py
  frontend/
    app/                # landing/search/company/dashboard/saved pages
    components/
      ui/               # reusable shadcn-style primitives
      charts/
      layout/
      search/
    lib/
    types/
infra/
  render.yaml
  railway.toml
  vercel.json
docker-compose.yml
```

---

## Core Data Model

### `users`
- `id` (string PK; Clerk user id)
- `email`
- `created_at`

### `companies`
- `id`
- `normalized_name` (unique)
- `display_name`
- `total_filings`
- `total_certified`
- `sponsorship_score`
- `headquarters`
- `website`
- `latest_filing_year`

### `lcas`
- `id`
- `company_id`
- `case_number`
- `job_title`
- `soc_code`
- `city`
- `state`
- `wage`
- `wage_unit`
- `filing_year`
- `filing_date`
- `case_status`
- `visa_class`
- `worksite_location`
- `is_internship_role`
- `is_new_grad_role`
- `remote_type`
- `record_hash` (dedupe)

### `saved_companies`
- `id`
- `user_id`
- `company_id`
- `created_at`

### `ingestion_jobs` / `ingestion_failures`
- job monitoring, retry diagnosis, malformed row logging

---

## API Endpoints

Base URL: `/api/v1`

### Company Search
- `GET /companies`
  - filters: `query`, `title`, `state`, `city`, `year`, `visa_type`, `is_internship`, `is_new_grad`, `min_filings`, `max_filings`, `remote_type`
  - sorting: sponsorship score / filings / recent activity
  - paginated response
- `GET /companies/search?q=`
  - fuzzy autocomplete
- `GET /companies/:id`
  - trends, top titles, top locations, recent filings, certification rate

### Analytics
- `GET /analytics/top-companies`
- `GET /analytics/trends`
- `GET /analytics/dashboard`

### Saved Companies (auth required)
- `GET /saved-companies`
- `POST /saved-companies`
- `DELETE /saved-companies/:company_id`

### Admin / Data Pipeline
- `POST /admin/ingestion/run` (admin token required)
- `GET /admin/ingestion/jobs` (admin token required)

---

## Sponsorship Score

Composite score (0–100) using:
- historical filing volume
- recent filing intensity
- certification rate
- internship/new-grad role signal
- consistency across years

Implementation: `apps/backend/app/services/sponsorship_score.py`

---

## ETL Pipeline Overview

1. Download yearly DOL dataset (CSV/ZIP)
2. Normalize employer names
3. Standardize city/state and infer remote/hybrid signals
4. Parse salaries and filing dates
5. Detect internship/new-grad roles using keyword heuristics
6. Generate dedupe hash per filing
7. Upsert companies and insert unique LCA records
8. Log malformed rows into `ingestion_failures`
9. Recompute company aggregates + sponsorship scores

Supports incremental ingestion through `record_hash` conflict handling.

---

## Local Development

### 1) Environment files

```bash
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env
```

### 2) Run with Docker

```bash
docker compose up --build
```

### 3) Initialize DB + seed

In a backend shell:

```bash
cd apps/backend
pip install -e .
python scripts/create_db.py
python scripts/seed_demo_data.py
```

### 4) Run ingestion for a year

```bash
cd apps/backend
python scripts/ingest_year.py --year 2025
```

---

## Frontend Pages

- `/` Landing page
- `/search` Advanced company search + filters + pagination + save action
- `/companies/[id]` Company profile with trends, top roles, top locations, and recent filings table
- `/dashboard` National analytics dashboard
- `/saved` Authenticated saved companies list

Includes responsive layout + dark mode toggle.

---

## Security + Reliability

- JWT auth verification via Clerk JWKS on backend
- Rate limiting with SlowAPI
- Input validation with Pydantic
- Structured ingestion job/error tracking
- Optional Redis caching for expensive list/analytics queries

---

## Scalability Notes

- Indexed queries for high-cardinality filtering paths
- Paginated API responses
- Async API + DB access
- Cache layer for frequent searches and dashboard requests
- Batch ETL in chunked pandas processing
