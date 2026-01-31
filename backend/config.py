import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_12345'
    
    # Smart Database Selection
    # If DATABASE_URL exists (Cloud), use it. Otherwise use local SQLite.
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///protodo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail Config (Read from Environment Variables)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')