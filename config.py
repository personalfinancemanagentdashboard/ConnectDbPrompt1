import os


class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    # SQLite database configuration for local system connection
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/smartfinance.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
