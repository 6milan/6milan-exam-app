import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class Config:
    # Flask secret key (always required)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production!'

    # --- Database configuration ---
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # Fix old-style postgres:// URLs to postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # Parse URL to modify connection parameters
        parsed = urlparse(database_url)
        
        # Add SSL for production Supabase
        if "supabase.co" in parsed.hostname and not parsed.query:
            database_url += "?sslmode=require"
        elif "supabase.co" in parsed.hostname and "sslmode" not in parsed.query:
            # Ensure sslmode is set
            query_parts = parsed.query.split('&')
            if 'sslmode=require' not in query_parts:
                query_parts.append('sslmode=require')
            database_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/{parsed.path}?{'&'.join(query_parts)}"

        SQLALCHEMY_DATABASE_URI = database_url
        print(f"✅ Database: {parsed.hostname} (SSL enabled)")
    else:
        # Local SQLite fallback (development only)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///6milan_exam.db'
        print("⚠️  Using local SQLite (development mode)")

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Supabase configuration ---
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    SUPABASE_STORAGE_BUCKET = os.environ.get('SUPABASE_STORAGE_BUCKET', '6milan-exam-app')

    # Validate Supabase config
    if not all([SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY]):
        print("⚠️  Missing Supabase URL or Service Role Key - uploads will fail")

    # --- Engine options (optimized for Supabase) ---
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Detect stale connections
        "pool_recycle": 300,    # Recycle connections every 5 minutes
        "echo": False,          # Set to True for SQL logging
        "future": True,         # Enable SQLAlchemy 2.0 style
    }

    # Supabase-specific connection args
    if "supabase.co" in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_ENGINE_OPTIONS.update({
            "connect_args": {
                "sslmode": "require",
                "connect_timeout": 10,
                "options": "-c search_path=public"
            }
        })

    # --- Development vs Production ---
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('FLASK_TESTING', 'False').lower() == 'true'

    # Flask-WTF CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # Session configuration
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # File upload limits
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max upload size

    # Rate limiting (optional)
    # RATELIMIT_STORAGE_URL = "redis://localhost:6379/0"

    # Security headers
    @property
    def SECURITY_HEADERS(self):
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }