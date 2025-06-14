from typing import Any, Dict, List, Optional
import os
from pydantic import BaseSettings, Field, SecretStr, validator


class Settings(BaseSettings):
    """Application settings with environment variable support and enhanced security"""

    # API Authentication - Remove demo keys for security
    backend_api_keys: List[str] = Field(env="BACKEND_API_KEYS")
    
    @validator('backend_api_keys', pre=True)
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            keys = [key.strip() for key in v.split(",") if key.strip()]
            if not keys:
                raise ValueError("BACKEND_API_KEYS must be provided and non-empty")
            return keys
        return v

    # Model API Keys - Use SecretStr for security
    openai_api_key: SecretStr = Field(env="OPENAI_API_KEY")
    anthropic_api_key: SecretStr = Field(env="ANTHROPIC_API_KEY")
    ernie_api_key: SecretStr = Field(default="", env="ERNIE_API_KEY")
    ernie_secret_key: SecretStr = Field(default="", env="ERNIE_SECRET_KEY")
    moonshot_api_key: SecretStr = Field(default="", env="MOONSHOT_API_KEY")
    zhipu_api_key: SecretStr = Field(default="", env="ZHIPU_API_KEY")
    cohere_api_key: SecretStr = Field(default="", env="COHERE_API_KEY")
    google_api_key: SecretStr = Field(default="", env="GOOGLE_API_KEY")

    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["https://chat.openai.com", "https://chatgpt.com"],
        env="ALLOWED_ORIGINS"
    )
    
    @validator('allowed_origins', pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Model Configuration
    default_temperature: float = 0.6
    default_max_tokens: int = 512
    request_timeout: int = 30
    max_concurrent_requests: int = 10

    # Consensus Scoring
    high_consensus_threshold: float = 0.9
    low_consensus_threshold: float = 0.85

    # Logging
    log_directory: str = "./logs"
    save_embeddings_in_log: bool = False
    max_embedding_log_dims: int = 50  # Limit embedding dimensions in logs

    # Embedding Model
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_cache_enabled: bool = True

    # Advanced Features - Redis Configuration
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: SecretStr = Field(default="", env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")

    # Rate Limiting
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_requests_per_hour: int = 1000

    # Caching
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    cache_embedding_ttl_seconds: int = 86400  # 24 hours

    # WebSocket Configuration
    websocket_max_connections: int = 100
    websocket_heartbeat_interval: int = 30

    # Batch Processing
    max_batch_size: int = 50
    batch_timeout_seconds: int = 300

    # Performance Analytics
    enable_analytics: bool = True
    analytics_retention_days: int = 30

    # Dashboard Configuration
    dashboard_refresh_interval: int = 5  # seconds
    dashboard_max_recent_queries: int = 100

    def get_masked_api_key(self, key: SecretStr) -> str:
        """Return masked version of API key for logging/display"""
        if not key or not key.get_secret_value():
            return "Not configured"
        secret = key.get_secret_value()
        if len(secret) <= 8:
            return "****"
        return f"{secret[:4]}****{secret[-4:]}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()

# Enhanced Model configuration with SecretStr support
def get_model_config() -> Dict[str, Dict[str, Any]]:
    """Get model configuration with proper API key handling"""
    return {
        "openai_gpt4": {
            "type": "openai",
            "api_key": settings.openai_api_key.get_secret_value() if settings.openai_api_key else "",
            "model": "gpt-4o",
            "max_tokens": settings.default_max_tokens,
            "temperature": settings.default_temperature,
        },
        "openai_gpt35": {
            "type": "openai",
            "api_key": settings.openai_api_key.get_secret_value() if settings.openai_api_key else "",
            "model": "gpt-3.5-turbo",
            "max_tokens": settings.default_max_tokens,
            "temperature": settings.default_temperature,
        },
        "anthropic_claude": {
            "type": "anthropic",
            "api_key": settings.anthropic_api_key.get_secret_value() if settings.anthropic_api_key else "",
            "model": "claude-3-opus-20240229",
            "max_tokens": settings.default_max_tokens,
        },
        "anthropic_claude_sonnet": {
            "type": "anthropic",
            "api_key": settings.anthropic_api_key.get_secret_value() if settings.anthropic_api_key else "",
            "model": "claude-3-sonnet-20240229",
            "max_tokens": settings.default_max_tokens,
        },
        "anthropic_claude_haiku": {
            "type": "anthropic",
            "api_key": settings.anthropic_api_key.get_secret_value() if settings.anthropic_api_key else "",
            "model": "claude-3-haiku-20240307",
            "max_tokens": settings.default_max_tokens,
        },
        "baidu_ernie": {
            "type": "baidu",
            "api_key": settings.ernie_api_key.get_secret_value() if settings.ernie_api_key else "",
            "secret_key": settings.ernie_secret_key.get_secret_value() if settings.ernie_secret_key else "",
            "access_token": "",
        },
        "moonshot": {
            "type": "moonshot",
            "api_key": settings.moonshot_api_key.get_secret_value() if settings.moonshot_api_key else "",
            "model": "moonshot-v1-8k",
        },
        "moonshot_32k": {
            "type": "moonshot",
            "api_key": settings.moonshot_api_key.get_secret_value() if settings.moonshot_api_key else "",
            "model": "moonshot-v1-32k",
        },
        "zhipu": {
            "type": "zhipu", 
            "api_key": settings.zhipu_api_key.get_secret_value() if settings.zhipu_api_key else "",
            "model": "glm-4"
        },
        "zhipu_turbo": {
            "type": "zhipu",
            "api_key": settings.zhipu_api_key.get_secret_value() if settings.zhipu_api_key else "",
            "model": "glm-3-turbo",
        },
        "cohere_command": {
            "type": "cohere",
            "api_key": settings.cohere_api_key.get_secret_value() if settings.cohere_api_key else "",
            "model": "command",
            "max_tokens": settings.default_max_tokens,
            "temperature": settings.default_temperature,
        },
        "google_gemini": {
            "type": "google",
            "api_key": settings.google_api_key.get_secret_value() if settings.google_api_key else "",
            "model": "gemini-pro",
            "max_tokens": settings.default_max_tokens,
            "temperature": settings.default_temperature,
        },
    }

MODEL_CONFIG = get_model_config()
