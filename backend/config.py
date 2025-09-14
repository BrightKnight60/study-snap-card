import os
from datetime import timedelta

class Config:
    """Flask application configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']

    # Database settings
    DATABASE = os.environ.get('DATABASE_PATH') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flashcards.db')

    # File upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_uploads')
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 5 * 1024 * 1024))  # 5MB default
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

    # Anthropic API settings
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

    # Server settings
    FLASK_PORT = int(os.environ.get('FLASK_PORT', 5001))  # Default to 5001 to avoid macOS AirPlay conflict

    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')

    @staticmethod
    def validate_config():
        """Validate that required configuration is present"""
        required_vars = ['ANTHROPIC_API_KEY']
        missing_vars = []

        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Add production-specific settings here

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}