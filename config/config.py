import os

class Config:
    """Application Configuration"""

    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG') or True

    # Database Configuration
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'energy.db')

    # API Configuration
    API_HOST = os.environ.get('API_HOST') or '0.0.0.0'
    API_PORT = int(os.environ.get('API_PORT') or 5000)

    # AI Model Configuration
    PREDICTION_ALPHA = 0.3  # Level smoothing for exponential smoothing
    PREDICTION_BETA = 0.1   # Trend smoothing for exponential smoothing
    ANOMALY_THRESHOLD = 2.5  # Z-score threshold for anomaly detection

    # Electricity Rates (per kWh in INR)
    DEFAULT_ELECTRICITY_RATE = 8   # ₹8 per kWh average in India

    # Alert Thresholds
    HIGH_CONSUMPTION_THRESHOLD = 15   # kWh per day typical home
    COST_ALERT_THRESHOLD = 3000       # ₹ per month alert
 
    # Cloud Configuration (for deployment)
    CLOUD_PROVIDER = os.environ.get('CLOUD_PROVIDER') or 'AWS'
    AWS_REGION = os.environ.get('AWS_REGION') or 'us-east-1'
    AZURE_REGION = os.environ.get('AZURE_REGION') or 'eastus'
    GCP_REGION = os.environ.get('GCP_REGION') or 'us-central1'

    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or '*'

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    TESTING = False
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')

class TestingConfig(Config):
    """Testing Configuration"""
    DEBUG = True
    TESTING = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
