"""Configuration settings for the marketplace application."""

# Python imports
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """
    Database configuration settings.
    
    Attributes:
        host: The host of the database.
        port: The port of the database.
        name: The name of the database.
        user: The user of the database.
        password: The password of the database.
    """
    
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    name: str = Field(default="marketplace", env="DB_NAME")
    user: str = Field(default="postgres", env="DB_USER")
    password: str = Field(default="password", env="DB_PASSWORD")
    
    @property
    def url(self) -> str:
        """
        Get database URL.

        Returns:
            str: The database URL.
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_url(self) -> str:
        """
        Get async database URL.

        Returns:
            str: The async database URL.
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """
    Redis configuration settings.
    
    Attributes:
        host: The host of the Redis server.
        port: The port of the Redis server.
        password: The password of the Redis server.
        db: The database number of the Redis server.
    """
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    
    @property
    def url(self) -> str:
        """
        Get Redis URL.

        Returns:
            str: The Redis URL.
        """
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class AppSettings(BaseSettings):
    """
    Application configuration settings.
    
    Attributes:
        debug: Whether the application is in debug mode.
        secret_key: The secret key for the application.
        algorithm: The algorithm for the application.
        access_token_expire_minutes: The number of minutes the access token is valid for.
    """

    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXIRE_MINUTES")
    
    # Database settings
    database: DatabaseSettings = DatabaseSettings()
    
    # Redis settings
    redis: RedisSettings = RedisSettings()
    
    class Config:
        """
        Configuration for the application settings.
        
        Attributes:
            env_file: The environment file to load.
            env_file_encoding: The encoding of the environment file.
        """
        
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = AppSettings() 