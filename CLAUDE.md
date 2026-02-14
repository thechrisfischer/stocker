# CLAUDE.md - Stocker Project Guide

## Project Overview

Stocker is a stock market analysis and ranking application with a Flask REST API backend and a React/Redux single-page application frontend. It provides user authentication (JWT-based), stock financial data storage, and investment strategy ranking (Magic Formula, GARP, PE ratios, ROA, ROE, dividend yield, etc.).

## Architecture

- **Backend**: Python 3 / Flask monolith serving both REST API and static assets
- **Frontend**: React 15 + Redux SPA with Webpack 1 bundling
- **Database**: SQLAlchemy ORM (currently configured for PostgreSQL, supports MySQL and SQLite)
- **Auth**: JWT tokens via `itsdangerous` with bcrypt password hashing
- **Legacy app**: `v1/` directory contains an older Peewee ORM + Flask-Bootstrap version (not actively deployed)

### Key Entry Points

| File | Purpose |
|------|---------|
| `main.py` | WSGI entry point (used by gunicorn) |
| `index.py` | Flask app, db, and bcrypt initialization |
| `manage.py` | CLI commands (runserver, db migrations, create_db) |
| `application/app.py` | All Flask route definitions |
| `application/models.py` | SQLAlchemy User model |
| `application/utils/auth.py` | JWT token generation/verification, `@requires_auth` decorator |
| `config.py` | Flask configuration classes (BaseConfig, TestingConfig) |
| `static/src/index.js` | React app entry point |
| `static/src/routes.js` | React Router route definitions |
| `static/server.js` | Express dev server with webpack HMR + proxy to Flask |

## Build & Run Commands

### Backend (from project root)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize database tables
python manage.py create_db

# Run database migrations
python manage.py db migrate    # generate migration
python manage.py db upgrade    # apply migration
python manage.py db downgrade  # rollback migration

# Start dev server (port 5000)
python manage.py runserver

# Production server
gunicorn main:app
```

### Frontend (from `static/` directory)

```bash
npm install
npm start                  # dev server with HMR on port 3000 (proxies /api to :5000)
npm run build              # development webpack build
npm run build:production   # production build (minified, output to static/dist/)
npm run lint               # eslint
```

### Scripted Setup (from project root)

```bash
source commander.sh setup     # full setup: venv, pip, npm, db
./commander startapp           # start both servers
./commander stopapp            # kill both servers
./commander refresh_db         # drop and recreate database
```

## Test Commands

```bash
# Run all tests with coverage (from project root)
python test.py --cov-report=term --cov-report=html --cov=application/ tests/

# Or directly with pytest
pytest tests/
```

- Tests use an in-memory SQLite database (`sqlite:///:memory:`) via `TestingConfig`
- Test base class is in `testing_config.py` - creates a default user before each test
- Test files: `tests/test_api.py` (4 tests), `tests/test_models.py` (1 test)

## Code Style & Conventions

- **Python**: No linter configured; follows standard Flask patterns. Imports use relative paths within `application/` package.
- **JavaScript**: ESLint with Airbnb config, 4-space indentation, no camelCase enforcement. Babel with es2015 + react + stage-0 presets.
- **State management**: Redux with thunk middleware. Actions in `static/src/actions/`, reducers in `static/src/reducers/`.
- **API pattern**: JSON request/response. Auth via `Authorization` header with raw JWT token string.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Database connection string (e.g., `postgresql://user:pass@host/db` or `sqlite:///stocker.db`) |
| `NODE_ENV` | No | Set to `production` for production webpack builds |
| `PORT` | No | Frontend dev server port (default: 3000) |

## Current Deployment

- Heroku via `Procfile` (`web: gunicorn main:app`)
- No Docker, no CI/CD pipeline
- Frontend must be pre-built (`npm run build:production`) before deploying

## Known Issues

- `SECRET_KEY` is hardcoded as `"SO_SECURE"` in `config.py` - must be replaced with an environment variable
- `SQLALCHEMY_TRACK_MODIFICATIONS = True` causes unnecessary overhead (should be `False`)
- `Flask-Script` (`manage.py`) is deprecated - Flask has built-in CLI via `flask` command
- `itsdangerous.TimedJSONWebSignatureSerializer` is deprecated in newer versions
- Tests reference `/api/create_user` route which is commented out in `app.py` (active route is `/user/create`)
- Frontend dependencies are all in `devDependencies` (react, redux, etc. should be in `dependencies`)
- Webpack 1, React 15, and many npm packages are severely outdated

---

## Modernization Recommendations: Single EC2 Instance + SQLite

The following is a phased plan to modernize Stocker for deployment on a single EC2 instance with SQLite as the database. Each phase is independent and can be done incrementally.

### Phase 1: Switch to SQLite and Fix Configuration

**Why**: Eliminate the PostgreSQL/MySQL dependency. SQLite is ideal for a single-instance deployment - zero configuration, no separate process, and the data lives in a single file that's easy to back up.

**Changes needed**:

1. **`config.py`** - Read `SECRET_KEY` and `DATABASE_URL` from environment variables with sensible defaults:
   ```python
   import os

   class BaseConfig:
       SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
       DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
       SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///stocker.db")
       SQLALCHEMY_TRACK_MODIFICATIONS = False
   ```

2. **`requirements.txt`** - Remove `psycopg2` and `mysql-connector` (not needed for SQLite). SQLite support is built into Python's standard library.

3. **`commander.sh`** - Replace all PostgreSQL commands with SQLite initialization:
   ```bash
   export DATABASE_URL="sqlite:///stocker.db"
   ```

4. **WAL mode for SQLite** - Enable Write-Ahead Logging for better concurrent read performance. Add to app initialization:
   ```python
   from sqlalchemy import event
   @event.listens_for(db.engine, "connect")
   def set_sqlite_pragma(dbapi_connection, connection_record):
       cursor = dbapi_connection.cursor()
       cursor.execute("PRAGMA journal_mode=WAL")
       cursor.execute("PRAGMA foreign_keys=ON")
       cursor.close()
   ```

5. **SQLite backups** - Add a cron job or script to periodically copy the `.db` file to S3 or EBS snapshots. SQLite's file-based nature makes backups trivial: `sqlite3 stocker.db ".backup /backups/stocker-$(date +%Y%m%d).db"`

### Phase 2: Replace Deprecated Python Dependencies

**Why**: Several core dependencies are deprecated or abandoned, creating security and compatibility risks.

| Current | Replace With | Reason |
|---------|-------------|--------|
| `Flask-Script` (manage.py) | Flask built-in CLI (`flask` command) | Flask-Script is unmaintained; Flask 2.x+ has `click`-based CLI built in |
| `itsdangerous.TimedJSONWebSignatureSerializer` | `PyJWT` library | `TimedJSONWebSignatureSerializer` was removed in `itsdangerous` 2.1+ |
| `Flask-Bcrypt` | Keep, but pin version | Still maintained, just pin it |
| `py-bcrypt` | Remove | Redundant with `Flask-Bcrypt` which wraps `bcrypt` directly |
| `GitHub-Flask` | Remove | Not used anywhere in the codebase |

**Concrete steps**:
- Replace `manage.py` with a `cli.py` using `@app.cli.command()` decorators. Run with `flask create-db`, `flask run`, etc.
- Replace JWT handling with `PyJWT`: `jwt.encode(payload, secret, algorithm="HS256")` / `jwt.decode(token, secret, algorithms=["HS256"])`
- Update `requirements.txt` with pinned versions for reproducible builds

### Phase 3: Modernize the Frontend Build

**Why**: Webpack 1, React 15, Babel 6, and most npm packages are 7+ years old with known vulnerabilities and no security patches.

**Recommended approach**:

1. **Vite + React 18** - Replace Webpack entirely with Vite. Vite is dramatically simpler to configure, has fast HMR, and produces optimized production builds out of the box.

2. **Migration steps**:
   - Create a new `frontend/` directory (replaces `static/`)
   - `npm create vite@latest frontend -- --template react` to scaffold
   - Port components from class-based React 15 to functional components with hooks
   - Replace Redux with lighter state management (React Context + `useReducer`, or Zustand) - the current state is simple enough that full Redux is overkill
   - Replace Material-UI 0.16 with MUI 5+ (or drop it entirely for Tailwind CSS)
   - Replace `axios` calls with native `fetch` API
   - Configure Vite to proxy `/api` to Flask during development

3. **Build output** - Configure Vite to output to `static/dist/` so Flask can serve it without changes to `index.py`

### Phase 4: Consolidate the v1 Legacy Code

**Why**: The `v1/` directory contains the actual stock data models (`Company`, `FinancialData`) and ranking logic that the main app's frontend references but has no backend for. The main app only has a `User` model.

**Options**:
- **Option A (Recommended)**: Port the v1 Peewee models to SQLAlchemy and merge into `application/models.py`. Port the ranking logic from `v1/alg.py` into the main app. Delete `v1/`.
- **Option B**: Keep v1 as a separate data pipeline that writes to the same SQLite database. The main app reads from it.

**For SQLAlchemy migration of v1 models**:
```python
class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(255))
    sector = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    financials = db.relationship('FinancialData', backref='company', lazy=True)

class FinancialData(db.Model):
    __tablename__ = 'financial_data'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    symbol = db.Column(db.String(10), unique=True)
    # ... remaining fields ported from v1/database.py
```

### Phase 5: EC2 Deployment Setup

**Why**: Replace Heroku with a single EC2 instance running everything.

**Recommended stack on EC2**:

```
EC2 Instance (t3.small or t3.medium)
├── Caddy (reverse proxy + automatic HTTPS via Let's Encrypt)
├── Gunicorn (Flask WSGI server, 2-4 workers)
├── SQLite database file (on EBS volume)
└── Static files (Vite build output served by Caddy directly)
```

**Why Caddy over Nginx**: Automatic HTTPS certificate provisioning and renewal, simpler configuration, and HTTP/2 out of the box. Single binary with no dependencies.

**Deployment files to add**:

1. **`Caddyfile`**:
   ```
   yourdomain.com {
       handle /api/* {
           reverse_proxy localhost:8000
       }
       handle {
           root * /opt/stocker/static/dist
           file_server
           try_files {path} /index.html
       }
   }
   ```

2. **`systemd` service file** (`/etc/systemd/system/stocker.service`):
   ```ini
   [Unit]
   Description=Stocker Flask App
   After=network.target

   [Service]
   User=stocker
   WorkingDirectory=/opt/stocker
   Environment=DATABASE_URL=sqlite:////opt/stocker/data/stocker.db
   Environment=SECRET_KEY=<generate-a-real-secret>
   ExecStart=/opt/stocker/venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 main:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **SQLite data directory** - Store the database on the EBS volume at `/opt/stocker/data/stocker.db` so it persists independently.

4. **Backup script** (cron daily):
   ```bash
   #!/bin/bash
   sqlite3 /opt/stocker/data/stocker.db ".backup /tmp/stocker-backup.db"
   aws s3 cp /tmp/stocker-backup.db s3://your-bucket/backups/stocker-$(date +%Y%m%d).db
   ```

### Phase 6: Add CI/CD with GitHub Actions

**Why**: No CI/CD exists. Automate testing and deployment.

```yaml
# .github/workflows/deploy.yml
name: Test and Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=application/
        env:
          DATABASE_URL: "sqlite:///:memory:"

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to EC2
        # SSH into EC2, git pull, restart service
        run: |
          ssh stocker@${{ secrets.EC2_HOST }} "cd /opt/stocker && git pull && source venv/bin/activate && pip install -r requirements.txt && cd frontend && npm ci && npm run build && sudo systemctl restart stocker"
```

### Phase 7: Additional Improvements (Optional)

- **Add rate limiting** - Use `Flask-Limiter` to protect auth endpoints from brute force
- **Add structured logging** - Replace `print()` calls with Python `logging` module
- **Add health check endpoint** - `GET /api/health` returning 200 for monitoring
- **Add `.env` file support** - Use `python-dotenv` to load environment variables from `.env` in development
- **Dockerize for local dev** - Even though production runs directly on EC2, a `docker-compose.yml` for local development makes onboarding easier

### Recommended Priority Order

1. **Phase 1** (SQLite + config) - Unblocks the EC2 deployment
2. **Phase 5** (EC2 setup) - Get it running on EC2
3. **Phase 2** (Python deps) - Fix deprecated/broken code
4. **Phase 4** (Consolidate v1) - Unify the codebase
5. **Phase 6** (CI/CD) - Automate deployments
6. **Phase 3** (Frontend) - Largest effort, do last
7. **Phase 7** (Polish) - Nice-to-haves
