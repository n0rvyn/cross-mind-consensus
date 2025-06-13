from typing import Any, Dict, List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Authentication
    backend_api_keys: List[str] = Field(
        default_factory=lambda: ["test-key", "another-key"], env="BACKEND_API_KEYS"
    )

    # Model API Keys
    openai_api_key: str = Field(default="sk-xxx", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="sk-ant-xxx", env="ANTHROPIC_API_KEY")
    ernie_api_key: str = Field(default="", env="ERNIE_API_KEY")
    ernie_secret_key: str = Field(default="", env="ERNIE_SECRET_KEY")
    moonshot_api_key: str = Field(default="", env="MOONSHOT_API_KEY")
    zhipu_api_key: str = Field(default="", env="ZHIPU_API_KEY")
    cohere_api_key: str = Field(default="", env="COHERE_API_KEY")
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")

    # Model Configuration
    default_temperature: float = 0.6
    default_max_tokens: int = 512
    request_timeout: int = 30

    # Consensus Scoring
    high_consensus_threshold: float = 0.9
    low_consensus_threshold: float = 0.85

    # Logging
    log_directory: str = "./logs"
    save_embeddings_in_log: bool = False

    # Embedding Model
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Advanced Features - Redis Configuration
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()

# Enhanced Model configuration with new providers
MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
    "openai_gpt4": {
        "type": "openai",
        "api_key": settings.openai_api_key,
        "model": "gpt-4o",
        "max_tokens": settings.default_max_tokens,
        "temperature": settings.default_temperature,
    },
    "openai_gpt35": {
        "type": "openai",
        "api_key": settings.openai_api_key,
        "model": "gpt-3.5-turbo",
        "max_tokens": settings.default_max_tokens,
        "temperature": settings.default_temperature,
    },
    "anthropic_claude": {
        "type": "anthropic",
        "api_key": settings.anthropic_api_key,
        "model": "claude-3-opus-20240229",
        "max_tokens": settings.default_max_tokens,
    },
    "anthropic_claude_sonnet": {
        "type": "anthropic",
        "api_key": settings.anthropic_api_key,
        "model": "claude-3-sonnet-20240229",
        "max_tokens": settings.default_max_tokens,
    },
    "anthropic_claude_haiku": {
        "type": "anthropic",
        "api_key": settings.anthropic_api_key,
        "model": "claude-3-haiku-20240307",
        "max_tokens": settings.default_max_tokens,
    },
    "baidu_ernie": {
        "type": "baidu",
        "api_key": settings.ernie_api_key,
        "secret_key": settings.ernie_secret_key,
        "access_token": "",
    },
    "moonshot": {
        "type": "moonshot",
        "api_key": settings.moonshot_api_key,
        "model": "moonshot-v1-8k",
    },
    "moonshot_32k": {
        "type": "moonshot",
        "api_key": settings.moonshot_api_key,
        "model": "moonshot-v1-32k",
    },
    "zhipu": {"type": "zhipu", "api_key": settings.zhipu_api_key, "model": "glm-4"},
    "zhipu_turbo": {
        "type": "zhipu",
        "api_key": settings.zhipu_api_key,
        "model": "glm-3-turbo",
    },
    "cohere_command": {
        "type": "cohere",
        "api_key": settings.cohere_api_key,
        "model": "command",
        "max_tokens": settings.default_max_tokens,
        "temperature": settings.default_temperature,
    },
    "google_gemini": {
        "type": "google",
        "api_key": settings.google_api_key,
        "model": "gemini-pro",
        "max_tokens": settings.default_max_tokens,
        "temperature": settings.default_temperature,
    },
}
