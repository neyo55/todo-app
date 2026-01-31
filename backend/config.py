import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_12345'
    
    # === DATABASE CONFIGURATION ===
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///protodo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database Stability Settings (Keeps connection alive)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # === SCHEDULER SETTINGS (Fix for "Skipped" errors) ===
    # Allow up to 3 overlapping jobs so emails don't get blocked if server is slow
    SCHEDULER_API_ENABLED = True
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }

    # === MAIL CONFIGURATION ===
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')