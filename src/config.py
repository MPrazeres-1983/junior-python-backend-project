"""
Application configuration module.

This module provides configuration classes for different environments:
- DevelopmentConfig: For local development
- TestingConfig: For running tests
- ProductionConfig: For production deployment

Environment variables are loaded from .env file.
"""

import os
from datetime import timedelta
from typing import Optional, Type


class Config:
    """Base configuration class with common settings."""

    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_APP: str = os.getenv("FLASK_APP", "src.app:create_app")

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900"))  # 15 minutes
    )
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(
        seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800"))  # 7 days
    )
    JWT_TOKEN_LOCATION: list = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"

    # Security
    BCRYPT_LOG_ROUNDS: int = int(os.getenv("BCRYPT_LOG_ROUNDS", "12"))
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["Content-Type", "Authorization"]
    CORS_SUPPORTS_CREDENTIALS: bool = True

    # Rate Limiting
    RATELIMIT_ENABLED: bool = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"
    RATELIMIT_STORAGE_URL: str = "memory://"
    RATELIMIT_DEFAULT: str = os.getenv("RATELIMIT_DEFAULT", "100 per minute")
    RATELIMIT_HEADERS_ENABLED: bool = True

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))

    # Application Info
    APP_NAME: str = os.getenv("APP_NAME", "Issue Tracker API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    @staticmethod
    def get_cors_origins() -> list:
        """Parse CORS_ORIGINS string into a list."""
        cors_origins = Config.CORS_ORIGINS
        if cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in cors_origins.split(",")]


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG: bool = True
    TESTING: bool = False
    
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/issue_tracker"
    )
    
    SQLALCHEMY_ECHO: bool = True  # Log SQL queries in development
    
    # Less restrictive rate limiting for development
    RATELIMIT_DEFAULT: str = "1000 per minute"


class TestingConfig(Config):
    """Testing environment configuration."""

    DEBUG: bool = True
    TESTING: bool = True
    
    # Use SQLite in-memory for fast tests
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:"
    )

    # SQLite does not support pool_size or max_overflow
    SQLALCHEMY_ENGINE_OPTIONS: dict = {}
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED: bool = False
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS: int = 4
    
    # Short token expiry for tests
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(hours=1)


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG: bool = False
    TESTING: bool = False
    
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "")
    
    # Strict production settings
    SQLALCHEMY_ECHO: bool = False
    
    # Ensure critical secrets are set
    def __init__(self):
        super().__init__()
        if not os.getenv("SECRET_KEY") or Config.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be set in production")
        if not os.getenv("JWT_SECRET_KEY") or Config.JWT_SECRET_KEY == "jwt-secret-key-change-in-production":
            raise ValueError("JWT_SECRET_KEY must be set in production")
        if not os.getenv("DATABASE_URL"):
            raise ValueError("DATABASE_URL must be set in production")


# Configuration dictionary for easy access
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: Optional[str] = None) -> Type[Config]:
    """
    Get configuration class by name.
    
    Args:
        config_name: Name of the configuration (development, testing, production)
        
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    
    return config_by_name.get(config_name, DevelopmentConfig)
