import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


def _set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_app(config_name=None):
    app = Flask(__name__, static_folder="./static/dist", template_folder="./static")

    if config_name == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.BaseConfig")

    # Setup logging
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, log_level, logging.INFO),
    )

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Enable SQLite WAL mode for better concurrent read performance
    if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
        with app.app_context():
            event.listen(db.engine, "connect", _set_sqlite_pragmas)

    return app


# Create the default app instance for backwards compatibility
app = create_app()
