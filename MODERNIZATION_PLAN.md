# StockRocker Modernization Plan

## Current State Assessment

### What exists today
StockRocker (formerly Stocker) has two disconnected legacy generations and a new v3 foundation:

1. **v1 (legacy)**: A working stock ranking system with data import pipelines (Yahoo Finance, Quandl, NASDAQ CSV scraping), financial calculation engines (Magic Formula, GARP, PE ratios, ROA/ROE), and a Flask/Peewee server-rendered UI. Written in Python 2.x style, uses deprecated APIs (Yahoo Finance YQL), and is isolated in the `v1/` directory.

2. **v2 (legacy)**: A Flask REST API + React/Redux SPA skeleton that implements user authentication (registration, login, token-based auth) but none of the stock analysis features. Uses outdated tooling (React 15, Redux 3, Webpack 1, Babel 6).

3. **v3 (new foundation)**: FastAPI + SQLModel backend in `app/`, deployed on Fly.io with SQLite. Auth (register/login/JWT), company listing, and ranking endpoints are implemented. Secrets managed via EnvVault. Docker-ready. No frontend yet.

### Completed (Phase 1)
- Migrated backend from Flask to **FastAPI** with **SQLModel** (SQLAlchemy 2.0 + Pydantic)
- Replaced itsdangerous tokens with **python-jose JWT** (HS256, 2-week expiry)
- Replaced Flask-Bcrypt with **passlib bcrypt**
- Created SQLModel models for User, Company, FinancialData (ported from v1 Peewee schema)
- Set up **Fly.io** deployment (app: `fischer-stocker`, volume: `stocker_data`, region: `ewr`)
- Dockerized the application
- Stored secrets in **EnvVault** (`stocker` namespace)
- Pinned all dependency versions
- Added `.env.example`, `.dockerignore`, updated `.gitignore`
- SQLite with WAL mode on persistent volume

### Remaining problems
- v1 data sources (Yahoo Finance YQL API, Quandl) are defunct — need modern replacements
- No financial data import pipeline in v3 yet
- No frontend exists for v3
- No tests for the new FastAPI code
- No CI/CD pipeline
- Legacy code (v1/, application/, static/) still present

---

## Feature Inventory

### Existing features (working)
- [x] User registration with email/password
- [x] User login with token-based authentication
- [x] Token generation and validation (2-week expiry)
- [x] Protected routes (frontend HOC wrappers + backend decorator)
- [x] Email invitations via Mailgun
- [x] Database migrations via Alembic
- [x] Multi-database support (PostgreSQL, MySQL, SQLite)

### Existing features (broken/dormant)
- [ ] Stock data import from Yahoo Finance (API defunct)
- [ ] Stock data import from Quandl (API deprecated)
- [ ] Company list import from NASDAQ CSV endpoint
- [ ] Financial metric calculations (PE ratio FTM, GARP, Magic Formula)
- [ ] Stock ranking by multiple strategies
- [ ] Ranked results display with links to StockCharts
- [ ] Analytics page (placeholder, no implementation)

### Features to build during modernization
- [ ] Modern financial data API integration (replace Yahoo/Quandl)
- [ ] Stock dashboard with interactive charts
- [ ] Portfolio watchlist
- [ ] Real-time or scheduled data refresh
- [ ] User preferences and saved strategies

---

## Modernization Plan

### Phase 1: Foundation — Secure the base and modernize tooling

**Goal**: Make the project buildable, testable, and deployable with modern standards before changing any features.

#### 1.1 Secret management
- Remove all hardcoded secrets (`SECRET_KEY`, Mailgun API key, Quandl key, DB credentials)
- Create `.env.example` with placeholder values
- Add `.env` to `.gitignore`
- Load config from environment variables using `python-dotenv` or Flask's built-in env support
- Generate a proper random `SECRET_KEY`

#### 1.2 Python backend modernization
- Pin all dependency versions in `requirements.txt` (or migrate to `pyproject.toml` + `pip-tools`)
- Replace deprecated libraries:
  - `Flask-Script` → Flask's built-in CLI (`flask` command + `click`)
  - `itsdangerous.TimedJSONWebSignatureSerializer` (removed in itsdangerous 2.1) → `PyJWT` or `flask-jwt-extended`
  - `py-bcrypt` (duplicate) → rely solely on `Flask-Bcrypt`
- Upgrade Flask to 3.x and all dependencies to current versions
- Add `pyproject.toml` for project metadata
- Add type hints to all Python modules
- Structure the app as a proper Python package with `__init__.py` factory pattern
- Replace `index.py` global app creation with Flask application factory
- Add proper error handlers (400, 401, 404, 500) returning JSON
- Add request validation (marshmallow or pydantic)
- Add CORS configuration via `flask-cors`
- Add rate limiting on auth endpoints via `flask-limiter`

#### 1.3 Frontend modernization
- Upgrade React 15 → React 18+ (functional components, hooks)
- Upgrade Redux 3 → Redux Toolkit (RTK) or replace with lighter state (React Context / Zustand)
- Upgrade React Router 3 → React Router 6+
- Replace Webpack 1 + Babel 6 → Vite (or Webpack 5 if preferred)
- Replace Material-UI 0.16 → MUI 5+ (or a lighter alternative like shadcn/ui)
- Remove jQuery dependency entirely — no jQuery-based component mounting
- Remove Materialize CSS (conflicts with Material-UI / MUI)
- Remove Bootstrap or consolidate to a single design system
- Move all `devDependencies` to proper `dependencies` where they belong (React, Redux, etc.)
- Pin all dependency versions
- Replace `localStorage` token storage with `httpOnly` cookies or a more secure pattern
- Add TypeScript (optional but recommended)

#### 1.4 Project infrastructure
- Add `Dockerfile` and `docker-compose.yml` (Flask + PostgreSQL + optional Redis)
- Add `.github/workflows/ci.yml` for GitHub Actions (lint, test, build)
- Add `Makefile` or equivalent task runner for common commands
- Add pre-commit hooks (black, ruff/flake8, isort, eslint, prettier)
- Add `.editorconfig` for consistent formatting
- Replace `commander.sh` with documented `Makefile` targets

### Phase 2: Migrate stock analysis into v2 architecture

**Goal**: Bring the v1 stock analysis logic into the modern v2 API and frontend.

#### 2.1 Data models
- Create SQLAlchemy models for `Company` and `FinancialData` (porting from Peewee schema in `v1/database.py`)
- Generate Alembic migrations for the new tables
- Clean up column naming to follow Python/SQL conventions (no camelCase like `OneyrTargetPrice`)

#### 2.2 Financial data API integration
- Research and integrate a modern financial data provider:
  - **Alpha Vantage** (free tier available)
  - **Financial Modeling Prep** (good free tier)
  - **yfinance** (unofficial Yahoo Finance, works for basic data)
  - **Polygon.io** (robust, paid)
- Create a data ingestion service/module that replaces `v1/import_financials.py` and `v1/import_companies.py`
- Support scheduled data refresh (cron job, Celery task, or APScheduler)

#### 2.3 Calculation engine
- Port `v1/calc_financials.py` logic into a proper service module
- Implement ranking algorithms as composable functions:
  - Magic Formula (Trailing and Future)
  - GARP ratio
  - PE ratio rankings (TTM and FTM)
  - EBITDA ranking
  - ROA / ROE ranking
  - Dividend yield ranking
- Add unit tests for each calculation
- Fix the SQL injection vulnerability in `v1/data.py:get_ranks()` (string interpolation in SQL)

#### 2.4 REST API endpoints
- `GET /api/companies` — list/search companies with pagination
- `GET /api/companies/:symbol` — company detail with financials
- `GET /api/rankings/:strategy` — ranked results by strategy
- `GET /api/strategies` — list available ranking strategies
- `POST /api/watchlist` — add company to user watchlist
- `GET /api/watchlist` — get user's watchlist
- `GET /api/data/refresh` — trigger data refresh (admin only)
- Add OpenAPI/Swagger documentation

#### 2.5 Frontend — stock analysis UI
- Company search and listing page
- Ranking results table (sortable, filterable) for each strategy
- Company detail page with financial metrics
- Charts for historical data (use recharts, chart.js, or similar)
- Strategy comparison view

### Phase 3: Polish and production readiness

**Goal**: Make the application production-grade.

#### 3.1 Testing
- Fix existing broken backend tests (update endpoint paths)
- Add comprehensive API tests for all new endpoints
- Add frontend unit tests (React Testing Library + Vitest/Jest)
- Add integration tests (Playwright or Cypress for E2E)
- Set up test coverage thresholds in CI

#### 3.2 Observability
- Add structured logging (replace `print()` calls)
- Add health check endpoint (`GET /health`)
- Add error tracking (Sentry or similar)
- Add basic metrics/monitoring

#### 3.3 Performance
- Add database indexing on frequently queried columns (symbol, date, ranks)
- Add caching layer for ranking queries (Redis or in-memory)
- Add pagination for all list endpoints
- Optimize frontend bundle size (code splitting, lazy loading)

#### 3.4 Deployment
- Production Docker image with multi-stage build
- Environment-specific configurations (dev, staging, production)
- Database backup strategy
- HTTPS enforcement
- Production CORS whitelist

#### 3.5 Cleanup
- Remove `v1/` directory entirely once all logic is migrated
- Remove dead/commented-out code in `application/app.py`
- Remove unused dependencies from both Python and Node
- Remove duplicate route definitions (`/user/create` defined twice)
- Update README.md with current setup instructions

---

## Suggested Execution Order

```
Phase 1.1 (secrets)          ← Do this first, it's a security fix
Phase 1.4 (infrastructure)   ← Docker + CI early enables faster iteration
Phase 1.2 (Python backend)   ← Modernize the foundation
Phase 1.3 (frontend)         ← Modernize the UI layer
Phase 2.1 (data models)      ← Schema for stock data
Phase 2.2 (data integration) ← Get real data flowing
Phase 2.3 (calc engine)      ← Port the ranking algorithms
Phase 2.4 (API endpoints)    ← Expose data via REST
Phase 2.5 (frontend UI)      ← Build the stock analysis UI
Phase 3.1 (testing)          ← Continuous throughout, formalize here
Phase 3.2 (observability)    ← Production monitoring
Phase 3.3 (performance)      ← Optimize after features work
Phase 3.4 (deployment)       ← Production infrastructure
Phase 3.5 (cleanup)          ← Final polish
```

---

## Technology Recommendations

| Current | Recommended Replacement | Reason |
|---------|------------------------|--------|
| Flask-Script | Flask CLI (click) | Flask-Script is unmaintained, Flask has built-in CLI |
| itsdangerous serializer | PyJWT / flask-jwt-extended | TimedJSONWebSignatureSerializer removed in itsdangerous 2.1 |
| React 15 | React 18+ | Class components → hooks, concurrent features, ecosystem support |
| Redux 3 + boilerplate | Redux Toolkit (RTK) | 80% less boilerplate, built-in best practices |
| React Router 3 | React Router 6 | Modern API, data loading, nested routes |
| Webpack 1 + Babel 6 | Vite | Faster builds, simpler config, native ESM |
| Material-UI 0.16 | MUI 5+ or shadcn/ui | Complete rewrite of Material-UI since v0.x |
| jQuery | Remove entirely | React manages the DOM |
| Bootstrap + Materialize | Single design system (MUI) | Conflicting CSS frameworks cause layout bugs |
| No version pinning | Pinned versions + lockfiles | Reproducible builds |
| Peewee (v1) | SQLAlchemy (already in v2) | Consolidate on one ORM |
| Yahoo Finance YQL | Alpha Vantage / yfinance | YQL API shut down in 2019 |
| Quandl | Financial Modeling Prep / yfinance | Quandl acquired by Nasdaq, API changed |
| localStorage tokens | httpOnly cookies | XSS protection |
| No linting (Python) | ruff | Fast, comprehensive Python linter/formatter |
| Heroku only | Docker + any cloud | Vendor flexibility |
