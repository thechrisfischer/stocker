# StockRocker

## Project Overview

StockRocker is a full-stack web application for stock analysis and investment research. It ranks publicly traded companies using financial metrics (Magic Formula, EBITDA, P/E ratios, GARP, ROA, ROE, dividend yield) and presents ranked results through a REST API. The application is being modernized from a legacy Flask/React stack to FastAPI + SQLModel, deployed on Fly.io with SQLite.

## Architecture

### Backend (Python/FastAPI) — `app/`
- **Entry point**: `app/main.py` — FastAPI app with lifespan, CORS, and router registration
- **Config**: `app/config.py` — Pydantic Settings loading from environment / `.env`
- **Database**: `app/database.py` — SQLModel engine, session management, SQLite WAL mode
- **Models**: `app/models/` — SQLModel table models (User, Company, FinancialData) with built-in Pydantic schemas
- **Routers**: `app/routers/` — API route handlers (auth, companies, rankings)
- **Services**: `app/services/` — Business logic (auth token management, ranking calculations)

### Legacy code (not actively maintained)
- `application/` — Old Flask REST API (v2 skeleton)
- `v1/` — Original Flask + Peewee stock ranking system
- `static/` — Old React 15 / Redux 3 / Webpack 1 frontend

## Tech Stack

### Current (v3)
- **Python 3.12**, FastAPI 0.115, Uvicorn
- **SQLModel 0.0.22** (SQLAlchemy 2.0 + Pydantic under the hood)
- **SQLite** with WAL mode on Fly.io persistent volume
- **python-jose** (JWT auth), **passlib** (bcrypt password hashing)
- **Pydantic Settings** for config management
- **Docker** for containerization, **Fly.io** for deployment

### Legacy
- Flask, Flask-SQLAlchemy, Flask-Script, itsdangerous (v2 skeleton)
- Peewee ORM, Yahoo Finance API, Quandl API (v1)
- React 15, Redux 3, Webpack 1, Material-UI 0.16 (frontend)

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app factory with lifespan events |
| `app/config.py` | Pydantic Settings (env vars, `.env` file) |
| `app/database.py` | SQLModel engine, session generator, SQLite pragmas |
| `app/models/user.py` | User table + UserCreate/UserRead schemas |
| `app/models/company.py` | Company table + CompanyRead schema |
| `app/models/financial_data.py` | FinancialData table (40+ metric and rank columns) |
| `app/routers/auth.py` | Register, login, get current user |
| `app/routers/companies.py` | List/search/get companies |
| `app/routers/rankings.py` | List strategies, get rankings by strategy |
| `app/services/auth.py` | JWT token creation and verification |
| `app/services/rankings.py` | Ranking query engine, strategy definitions |
| `fly.toml` | Fly.io deployment config |
| `Dockerfile` | Container build definition |
| `requirements.txt` | Pinned Python dependencies |
| `.env.example` | Environment variable template |

## API Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/health` | No | Health check |
| POST | `/api/auth/register` | No | Register new user, returns JWT |
| POST | `/api/auth/login` | No | Login, returns JWT |
| GET | `/api/auth/me` | Yes | Get current user info |
| GET | `/api/companies/` | Yes | List/search companies (paginated) |
| GET | `/api/companies/{symbol}` | Yes | Get company detail |
| GET | `/api/rankings/strategies` | Yes | List available ranking strategies |
| GET | `/api/rankings/{strategy}` | Yes | Get ranked results for a strategy |
| GET | `/docs` | No | Auto-generated Swagger UI |
| GET | `/redoc` | No | Auto-generated ReDoc |

## Database

### Schema (SQLModel)
- **users**: `id` (PK), `email` (unique), `password_hash` (bcrypt), `is_active`
- **companies**: `id` (PK), `symbol` (unique), `name`, `sector`, `industry`
- **financial_data**: `id` (PK), `company_id` (FK), `symbol`, `date`, plus 25 metric columns and 13 rank columns

### Ranking strategies
- Magic Formula (Trailing and Future)
- EBITDA, PE Ratio (TTM/FTM), GARP Ratio
- Return on Assets, Return on Equity, Dividend Yield

## Authentication Flow

1. User registers via `POST /api/auth/register` with `{email, password}`
2. Password hashed with bcrypt via passlib, stored in `users` table
3. JWT generated via python-jose (HS256, 2-week expiry)
4. Token contains `{sub: user_id, email, exp}`
5. Subsequent requests send `Authorization: Bearer <token>`
6. `get_current_user` dependency validates token and returns User

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `DATABASE_URL` | No | `sqlite:///data/stocker.db` | Database connection string |
| `SECRET_KEY` | Yes | `change-me-in-production` | JWT signing key |
| `MAILGUN_API_KEY` | No | `""` | Mailgun API key |
| `MAILGUN_DOMAIN` | No | `""` | Mailgun sending domain |

Secrets are managed via [EnvVault](https://envvault.fly.dev) under the `stocker` namespace.

## Development

### Local setup
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit with your values
uvicorn app.main:app --reload  # API on :8000
```

### Testing
```bash
pytest
```

### Docker
```bash
docker build -t stockrocker .
docker run -p 8000:8000 -v $(pwd)/data:/data stockrocker
```

## Deployment

### Fly.io
- **App**: `fischer-stocker`
- **Region**: `ewr`
- **Volume**: `stocker_data` (1GB, mounted at `/data` for SQLite)
- **Config**: `fly.toml`
- **Deploy**: `flyctl deploy`

### Secrets (EnvVault)
Stored in the `stocker` namespace:
- `SECRET_KEY`
- `DATABASE_URL`
- `MAILGUN_API_KEY`
- `MAILGUN_DOMAIN`
