import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_12345'
    
    # === DATABASE CONFIGURATION ===
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///protodo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # === CRITICAL FIX FOR RENDER SSL ERRORS ===
    # pool_pre_ping: Checks connection alive before using (Fixes "EOF detected")
    # pool_recycle: Refreshes connection every 5 mins to prevent timeouts
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # === MAIL CONFIGURATION ===
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')