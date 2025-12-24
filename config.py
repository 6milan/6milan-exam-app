# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production!'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration (Gmail example)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # e.g., yourgmail@gmail.com
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # App password (not login password)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    SUPABASE_STORAGE_BUCKET = os.environ.get('SUPABASE_STORAGE_BUCKET', '6mila-exam-app')

    SQLALCHEMY_ENGINE_OPTIONS = {
        'client_encoding': 'utf8',
    }
    db_url = os.environ.get('DATABASE_URL', '')
    if 'pooler.supabase.com' in db_url:
        SQLALCHEMY_ENGINE_OPTIONS.update({
            'poolclass': None,
            'connect_args': {'sslmode': 'require', 'connect_timeout': 10}
        })