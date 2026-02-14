import click
from index import app, db


@app.cli.command("create-db")
def create_db():
    """Create all database tables."""
    db.create_all()
    click.echo("Database tables created.")


@app.cli.command("drop-db")
def drop_db():
    """Drop all database tables."""
    if click.confirm("Are you sure you want to drop all tables?"):
        db.drop_all()
        click.echo("Database tables dropped.")
