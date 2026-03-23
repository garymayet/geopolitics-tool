"""WSGI entry point for gunicorn."""
from app import app, startup

# Initialize database, scheduler, and trigger first fetch
startup()
