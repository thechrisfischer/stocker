# Stocker

## Project Overview

Stocker is a full-stack web application for stock analysis and investment research. It ranks publicly traded companies using financial metrics (Magic Formula, EBITDA, P/E ratios, GARP, ROA, ROE, dividend yield) and presents ranked results through a web interface. The project has two generations: a legacy v1 system (Flask + Peewee + server-rendered templates) and a current v2 skeleton (Flask REST API + React/Redux SPA) that implements user authentication but has not yet migrated the stock analysis features.

## Architecture

### Backend (Python/Flask)
- **Entry point**: `index.py` - creates Flask app, SQLAlchemy db, and Bcrypt instances
- **Routes**: `application/app.py` - REST API endpoints and template-served pages
- **Models**: `application/models.py` - SQLAlchemy User model with bcrypt password hashing
- **Auth**: `application/utils/auth.py` - token generation/verification using `itsdangerous.TimedJSONWebSignatureSerializer`
- **Email**: `application/libs/mailgun/mailgun.py` - Mailgun API integration for invitations
- **Config**: `config.py` - BaseConfig and TestingConfig classes
- **CLI**: `manage.py` - Flask-Script manager with db migration commands
- **Migrations**: `migrations/` - Alembic database migration files

### Frontend (React/Redux)
- **Location**: `static/` directory
- **Entry point**: `static/src/index.js` - mounts React components via jQuery DOM scanning
- **Routing**: `static/src/routes.js` - React Router 3 routes
- **State**: Redux store with thunk middleware (`static/src/store/configureStore.js`)
- **Components**: `static/src/components/` - LoginView, RegisterView, ProtectedView, Header, Footer, Analytics, Home, NotFound
- **Containers**: `static/src/containers/` - App, HomeContainer (smart components)
- **Actions**: `static/src/actions/` - Redux action creators for auth flows
- **Reducers**: `static/src/reducers/` - auth and data reducers
- **Build**: Webpack 1 with Babel 6 (es2015, react, stage-0 presets)
- **Dev server**: Express with webpack-dev-middleware and hot module replacement (`static/bin/server.js`)

### Legacy v1 System (`v1/` directory)
- **Web app**: `v1/webapp.py` - Flask app with Flask-Bootstrap, Flask-Nav, WTForms
- **Database**: `v1/database.py` - Peewee ORM with Company and FinancialData models (40+ financial metric columns)
- **Data layer**: `v1/data.py` - CRUD operations and raw SQL queries for rankings
- **Import pipeline**: `v1/import_companies.py` (NASDAQ CSV scraper), `v1/import_financials.py` (Yahoo Finance + Quandl APIs)
- **Calculations**: `v1/calc_financials.py` - computes derived metrics (PE ratio FTM, GARP ratio, Magic Formula) and ranking algorithms
- **Algorithms**: `v1/alg.py` - ranking engine and strategy classes

## Tech Stack

### Backend
- Python 3.x, Flask, SQLAlchemy, Flask-SQLAlchemy, Flask-Migrate (Alembic)
- Flask-Bcrypt (password hashing), itsdangerous (token auth)
- Flask-Script (CLI), Flask-Testing, pytest, pytest-cov
- Gunicorn (production WSGI server)
- PostgreSQL (primary), MySQL and SQLite supported

### Frontend
- React 15.3.1, Redux 3.2.1, React Router 3.0.0
- Material-UI 0.16.4, Bootstrap 3.3.5, Materialize CSS
- Webpack 1.12.11, Babel 6 (es2015/react/stage-0)
- Axios (HTTP), jQuery, SCSS/Sass
- ESLint (Airbnb config), Karma/Mocha (test framework, no tests written)

### Legacy v1 (not actively maintained)
- Peewee ORM, SQLite, Flask-Bootstrap, Flask-Nav, WTForms
- BeautifulSoup (web scraping), Quandl API, Yahoo Finance API
- Python 2.x style code (print statements, StringIO imports)

## Key Files

| File | Purpose |
|------|---------|
| `index.py` | Flask app factory, db and bcrypt initialization |
| `application/app.py` | All REST API routes and view handlers |
| `application/models.py` | User model with password hashing |
| `application/utils/auth.py` | Token generation, verification, `@requires_auth` decorator |
| `config.py` | Flask configuration (BaseConfig, TestingConfig) |
| `manage.py` | Flask-Script CLI (runserver, create_db, db migrations) |
| `commander.sh` | Shell script for setup, start, stop, db operations |
| `static/src/routes.js` | React Router route definitions |
| `static/src/store/configureStore.js` | Redux store with thunk and logger middleware |
| `static/src/index.js` | React entry point (jQuery-based component mounting) |
| `static/package.json` | Frontend dependencies and npm scripts |
| `requirements.txt` | Python dependencies (no version pinning) |
| `Procfile` | Heroku deployment config (`web: gunicorn main:app`) |

## API Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/` | No | Serve SPA index.html |
| POST | `/user/create` | No | Register new user (JSON) |
| POST | `/api/get_token` | No | Login, returns auth token |
| POST | `/api/is_token_valid` | No | Validate an auth token |
| GET | `/login` | Yes | Get current user info |
| GET | `/user/new` | No | User creation form (template) |
| POST | `/user/invite-sent` | No | Send Mailgun invitation email |

## Database

### Current schema (SQLAlchemy)
- **user** table: `id` (PK), `email` (unique, string 255), `password` (bcrypt hash, string 255)

### Legacy v1 schema (Peewee)
- **company** table: `id`, `symbol` (unique), `name`, `sector`, `industry`
- **financialdata** table: `id`, `company` (FK), `symbol` (unique), `date`, plus 40+ financial metric and rank columns

## Authentication Flow

1. User registers via POST `/user/create` with email/password JSON
2. Password hashed with bcrypt, stored in `user` table
3. Token generated via `itsdangerous.TimedJSONWebSignatureSerializer` (2-week expiry)
4. Token contains `{id, email}`, signed with `SECRET_KEY`
5. Frontend stores token in `localStorage`
6. Subsequent requests send token in `Authorization` header
7. `@requires_auth` decorator validates token and populates `g.current_user`

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `DATABASE_URL` | Yes | None | PostgreSQL/MySQL/SQLite connection string |
| `PORT` | No | 3000 | Frontend dev server port |
| `NODE_ENV` | No | development | Node environment flag |

## Development

### Setup
```bash
source commander.sh setup    # creates venv, installs deps, inits db
./commander startapp          # starts Flask (5000) + webpack dev server (3000)
./commander stopapp           # kills both servers
```

### Manual setup
```bash
virtualenv -p python3 venv && source venv/bin/activate
pip3 install -r requirements.txt
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
python manage.py create_db
python manage.py runserver    # backend on :5000
cd static && npm install && npm start  # frontend on :3000
```

### Testing
```bash
python test.py --cov-report=term --cov-report=html --cov=application/ tests/
```

### Build
```bash
cd static && npm run build:production  # webpack production bundle
```

## Known Security Issues

- `SECRET_KEY` hardcoded as `"SO_SECURE"` in `config.py:7`
- Mailgun API key exposed in `application/libs/mailgun/mailgun.py:4`
- Quandl API key exposed in `v1/import_financials.py:26`
- Database credentials hardcoded in `commander.sh:4`
- Auth tokens stored in `localStorage` (vulnerable to XSS)
- No CORS configuration
- No rate limiting on auth endpoints
- Bare `except:` clauses swallow errors silently

## Deployment

- Heroku via `Procfile` (`web: gunicorn main:app`)
- No Docker configuration
- No CI/CD pipeline
- Frontend proxies `/api/*` to Flask backend on `localhost:5000` during development
