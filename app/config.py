"""
Configuration management for the Adaptive Testing Engine.
Loads settings from environment variables with validation.
"""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "adaptive_testing"
    
    # AI Provider Configuration
    ai_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Application Configuration
    app_name: str = "Adaptive Testing Engine"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Testing Configuration
    max_questions_per_session: int = 10
    default_ability: float = 0.0
    ability_min: float = -3.0
    ability_max: float = 3.0
    convergence_threshold: float = 0.3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def validate_ai_config(self) -> None:
        """Validate AI provider configuration."""
        if self.ai_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'")
        if self.ai_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when AI_PROVIDER is 'anthropic'")


# Global settings instance
settings = Settings()
