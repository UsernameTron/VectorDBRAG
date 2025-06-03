"""
Configuration management for the file search and retrieval system.
Loads environment variables and provides config access.
"""
import os
import logging
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

# Model configurations for the unified agent system
CEO_MODEL = os.getenv("CEO_MODEL", "gpt-4")
FAST_MODEL = os.getenv("FAST_MODEL", "gpt-3.5-turbo")
EXECUTOR_MODEL_ORIGINAL = os.getenv("EXECUTOR_MODEL_ORIGINAL", "gpt-4")
EXECUTOR_MODEL_DISTILLED = os.getenv("EXECUTOR_MODEL_DISTILLED", "gpt-3.5-turbo")

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Config:
    """Configuration loader using environment variables."""
    
    def __init__(self, env_name: str | None = None):
        """Initialize configuration with environment-specific settings."""
        self.ENV = env_name or os.getenv("ENV", "development")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
        self.TIMEOUT = int(os.getenv("TIMEOUT", "30"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "false").lower() == "true"
        
        # Flask-specific configuration
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        self.MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))  # 16MB
        self.UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
        
        # Environment-specific settings
        if self.ENV == Environment.PRODUCTION:
            self.DEBUG = False
            self.TESTING = False
        elif self.ENV == Environment.STAGING:
            self.DEBUG = False
            self.TESTING = True
        else:  # development
            self.DEBUG = True
            self.TESTING = False

    def validate(self):
        """Validate required configuration values."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required in environment variables.")

    def configure_logging(self):
        """Configure logging based on current settings."""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL.upper(), logging.INFO),
            format="%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary for Flask app.config.update()."""
        return {
            'ENV': self.ENV,
            'DEBUG': self.DEBUG,
            'TESTING': self.TESTING,
            'SECRET_KEY': self.SECRET_KEY,
            'MAX_CONTENT_LENGTH': self.MAX_CONTENT_LENGTH,
            'UPLOAD_FOLDER': self.UPLOAD_FOLDER,
            'OPENAI_API_KEY': self.OPENAI_API_KEY,
            'EMBEDDING_MODEL': self.EMBEDDING_MODEL,
            'CHUNK_SIZE': self.CHUNK_SIZE,
            'TIMEOUT': self.TIMEOUT,
            'LOG_LEVEL': self.LOG_LEVEL,
            'MONITORING_ENABLED': self.MONITORING_ENABLED
        }
