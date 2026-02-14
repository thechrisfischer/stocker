# CLAUDE.md - Stocker Project Guide

## Project Overview

Stocker is a stock market analysis and ranking application with a Flask REST API backend and a React 18 single-page application frontend. It provides user authentication (JWT-based), stock financial data storage, and investment strategy ranking (Magic Formula, GARP, PE ratios, ROA, ROE, dividend yield, etc.).

## Architecture

- **Backend**: Python 3 / Flask serving REST API + static SPA assets
- **Frontend**: React 18 SPA with Vite bundling (in `frontend/`)
- **Database**: SQLAlchemy ORM with SQLite (WAL mode enabled)
- **Auth**: JWT tokens via `PyJWT` with bcrypt password hashing
- **Legacy app**: `v1/` directory contains an older Peewee ORM + Flask-Bootstrap version (models and ranking logic have been ported to the main app)

### Key Entry Points

| File | Purpose |
|------|---------|
| `main.py` | WSGI entry point (used by gunicorn) |
| `index.py` | Flask app factory, db, bcrypt, limiter, migrate init |
| `cli.py` | Flask CLI commands (`flask create-db`, `flask drop-db`) |
| `application/app.py` | All Flask route definitions + SPA serving |
| `application/models.py` | SQLAlchemy models: User, Company, FinancialData |
| `application/rankings.py` | Stock ranking strategy engine |
| `application/utils/auth.py` | JWT token generation/verification, `@requires_auth` decorator |
| `config.py` | Flask configuration classes (BaseConfig, TestingConfig) |
| `frontend/src/main.jsx` | React app entry point |
| `frontend/src/App.jsx` | React Router route definitions |
| `frontend/vite.config.js` | Vite build config (proxy + output to static/dist/) |

### API Routes

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/health` | No | Health check |
| POST | `/api/create_user` | No | Register (rate limited: 5/min) |
| POST | `/api/get_token` | No | Login (rate limited: 10/min) |
| POST | `/api/is_token_valid` | No | Validate JWT token |
| GET | `/api/user` | Yes | Get current user info |
| GET | `/api/strategies` | No | List available ranking strategies |
| GET | `/api/rankings/<strategy>` | No | Get ranked companies for a strategy |
| GET | `/api/companies` | No | List all companies |
| GET | `/api/companies/<symbol>` | No | Get company + financial data |

## Build & Run Commands

### Backend (from project root)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize database tables
flask create-db

# Run database migrations
flask db migrate    # generate migration
flask db upgrade    # apply migration
flask db downgrade  # rollback migration

# Start dev server (port 5000)
flask run --port 5000

# Production server
gunicorn main:app
```

### Frontend (from `frontend/` directory)

```bash
npm install
npm run dev           # dev server with HMR on port 3000 (proxies /api to :5000)
npm run build         # production build (output to static/dist/)
npm run preview       # preview production build locally
```

### Scripted Setup (from project root)

```bash
source commander.sh setup     # full setup: venv, pip, npm, db
./commander startapp           # start both servers
./commander stopapp            # kill both servers
./commander backup             # backup SQLite database
./commander refresh_db         # delete and recreate database
```

## Test Commands

```bash
# Run all tests with coverage (from project root)
pytest tests/ --cov=application/ --cov-report=term

# Or with the legacy test runner
python test.py --cov-report=term --cov-report=html --cov=application/ tests/
```

- Tests use an in-memory SQLite database (`sqlite:///:memory:`) via `TestingConfig`
- Test base class is in `testing_config.py` - creates a default user before each test
- Rate limiting is disabled during tests
- Test files: `tests/test_api.py` (8 tests), `tests/test_models.py` (1 test)

## Code Style & Conventions

- **Python**: Standard Flask patterns. Imports use relative paths within `application/` package.
- **JavaScript**: React 18 functional components with hooks. No class components.
- **State management**: React Context (`AuthContext`) replaces Redux. No external state library.
- **API calls**: Native `fetch` API (no axios). All API functions in `frontend/src/utils/api.js`.
- **CSS**: Plain CSS with CSS custom properties (variables). No CSS framework.
- **API pattern**: JSON request/response. Auth via `Authorization` header with raw JWT token string.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | No | Random | Flask secret key (set in production!) |
| `DATABASE_URL` | No | `sqlite:///stocker.db` | Database connection string |
| `FLASK_DEBUG` | No | `false` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Python logging level |

Copy `.env.example` to `.env` for local development.

## Deployment

### Target: Single EC2 Instance

```
EC2 Instance (t3.small or t3.medium)
├── Caddy (reverse proxy + automatic HTTPS)
├── Gunicorn (Flask, 2-4 workers)
├── SQLite database (on EBS volume, WAL mode)
└── Static files (Vite build in static/dist/)
```

### Deployment Files (in `deploy/`)

| File | Purpose |
|------|---------|
| `Caddyfile` | Caddy reverse proxy config |
| `stocker.service` | systemd service for Gunicorn |
| `backup.sh` | Daily SQLite backup to S3 |
| `setup-ec2.sh` | Full EC2 provisioning script |

### CI/CD

GitHub Actions workflows in `.github/workflows/`:
- `ci.yml` - Run tests on push/PR
- `deploy.yml` - Test + SSH deploy to EC2 on push to main

Required GitHub Secrets: `EC2_HOST`, `EC2_SSH_KEY`

## Project Structure

```
stocker/
├── application/           # Flask backend
│   ├── app.py            # Routes + SPA serving
│   ├── models.py         # User, Company, FinancialData
│   ├── rankings.py       # Stock ranking strategies
│   └── utils/auth.py     # JWT auth
├── frontend/             # React 18 + Vite frontend
│   ├── src/
│   │   ├── components/   # Header, Footer
│   │   ├── context/      # AuthContext (replaces Redux)
│   │   ├── pages/        # Home, Login, Register, Dashboard, Analytics, Rankings
│   │   └── utils/        # api.js, validation.js
│   ├── package.json
│   └── vite.config.js
├── static/               # Legacy frontend (old Webpack + React 15)
│   └── dist/             # Build output (served by Flask)
├── deploy/               # EC2 deployment configs
├── tests/                # pytest test suite
├── .github/workflows/    # CI/CD
├── config.py             # Flask config
├── index.py              # App factory
├── cli.py                # Flask CLI commands
├── main.py               # WSGI entry point
└── v1/                   # Legacy Peewee app (models ported, can be removed)
```
