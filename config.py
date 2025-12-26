import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()


class Config:
    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production!')

    # --- Database configuration ---
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # Fix old-style postgres:// URLs
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Local fallback
        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Supabase settings ---
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    SUPABASE_STORAGE_BUCKET = os.environ.get('SUPABASE_STORAGE_BUCKET', '6milan-exam-app')

    # --- SQLAlchemy Engine Options ---
    SQLALCHEMY_ENGINE_OPTIONS = {}

    # Detect Supabase transaction pooler
    if database_url and "pooler.supabase.com" in database_url:
        # Serverless friendly settings
        SQLALCHEMY_ENGINE_OPTIONS.update({
            "connect_args": {
                "sslmode": "require",
                "connect_timeout": 10
            }
        })
