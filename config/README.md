# Configuration Guide

This directory contains configuration files for the Cross-Mind Consensus API.

## Files Overview

- `models.yaml` - AI models configuration
- `gpt/` - GPT Actions configuration for ChatGPT integration
- `docker/` - Docker and container configurations
- `nginx/` - NGINX reverse proxy configuration
- `monitoring/` - Prometheus and Grafana monitoring setup

## AI Models Configuration

The `models.yaml` file defines all available AI models and their configurations. Each model includes:

- **Provider**: The AI service provider (openai, anthropic, google, zhipuai, etc.)
- **Model Name**: The specific model identifier
- **API Configuration**: Endpoint URLs and authentication
- **Performance Settings**: Token limits, temperature, costs
- **Availability**: Whether the model is enabled

### Enabling ZHIPUAI GLM-4-Air

To enable the ZHIPUAI GLM-4-Air model:

1. **Get API Key**: Sign up at https://open.bigmodel.cn/ and get your API key
2. **Set Environment Variable**: 
   ```bash
   export ZHIPUAI_API_KEY="your_api_key_here"
   ```
3. **Verify Configuration**: The model is already configured in `models.yaml`:
   ```yaml
   zhipuai_glm4_air:
     provider: "zhipuai"
     model_name: "glm-4-air"
     display_name: "GLM-4-Air"
     api_key_env: "ZHIPUAI_API_KEY"
     endpoint: "https://open.bigmodel.cn/api/paas/v4/chat/completions"
     enabled: true
   ```

### Environment Variables Required

Create a `.env` file in the project root with your API keys:

```bash
# API Security - Bearer Token Authentication
# Comma-separated list of valid API keys for accessing the API
BACKEND_API_KEYS=87ea1604be1f6_02f173F5fb67582e647fcef6c40,another_key_here

# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key

# Google AI
GOOGLE_API_KEY=your_google_key

# ZHIPUAI (智谱AI)
ZHIPUAI_API_KEY=your_zhipuai_key

# Cohere
COHERE_API_KEY=your_cohere_key

# Mistral AI
MISTRAL_API_KEY=your_mistral_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

### Default Model Selection

The system uses these models by default (if API keys are available):
- OpenAI GPT-4
- Anthropic Claude 3 Sonnet
- ZHIPUAI GLM-4-Air
- Google Gemini Pro

You can customize the default models by modifying the `default_models` section in `models.yaml`.

### Adding New Models

To add a new AI model:

1. Add the model configuration to `models.yaml`
2. Set the required environment variable for the API key
3. Restart the API service
4. The model will automatically appear in the `/models` endpoint

### Model Status

Check which models are available and enabled:
- **API Endpoint**: `GET /models`
- **Health Check**: `GET /health` (shows model status)

Models are only available if:
- They are marked as `enabled: true` in the configuration
- The required API key environment variable is set
- The API key is valid and accessible

## API Authentication

The API now supports Bearer token authentication for improved security.

### Authentication Setup

1. **Configure API Keys**: Add your API keys to the `.env` file:
   ```bash
   BACKEND_API_KEYS=87ea1604be1f6_02f173F5fb67582e647fcef6c40,another_key_here
   ```

2. **Using Bearer Tokens**: Include the Authorization header in your requests:
   ```bash
   curl -H "Authorization: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40" \
        https://ai.norvyn.com/models
   ```

3. **GPT Integration**: The GPT actions YAML is configured to use Bearer authentication automatically.

### Protected Endpoints

The following endpoints require authentication:
- `POST /consensus` - Get consensus responses
- `POST /consensus/batch` - Batch processing
- `GET /models` - List available models
- `GET /analytics/performance` - Performance metrics

### Public Endpoints

These endpoints remain public for monitoring:
- `GET /health` - System health check
- `GET /docs` - API documentation
- `GET /openapi.json` - OpenAPI schema

## GPT Actions Configuration

The `gpt/gpt_actions.yaml` file defines the OpenAPI specification for ChatGPT integration. It's automatically synchronized with the API implementation.

**Current Version**: 3.1.0

### Available Operations

1. **getConsensus** - Get multi-LLM consensus on a question
2. **getBatchConsensus** - Process multiple questions in batch
3. **getAvailableModels** - List available AI models
4. **getPerformanceAnalytics** - Get system performance metrics
5. **getHealthStatus** - Check system health

## Docker Configuration

The `docker/docker-compose.yml` file orchestrates all services:
- API service (FastAPI)
- Dashboard service (Streamlit)
- Redis cache
- NGINX reverse proxy
- Monitoring stack (Prometheus + Grafana)

## NGINX Configuration

The `nginx/nginx.conf` file handles:
- SSL termination
- Load balancing
- Rate limiting
- Static file serving
- WebSocket support for Streamlit

## Monitoring Configuration

Prometheus and Grafana configurations for:
- API performance metrics
- Model response times
- Cache hit rates
- System resource usage

## Troubleshooting

### Model Not Available
- Check if API key is set: `echo $ZHIPUAI_API_KEY`
- Verify model is enabled in `models.yaml`
- Check API logs for authentication errors

### Configuration Changes
- Restart API service after modifying `models.yaml`
- Clear Redis cache if model configurations change
- Update GPT actions if API schema changes

### Performance Issues
- Monitor model response times in `/analytics/performance`
- Check Redis cache hit rates
- Review NGINX access logs for rate limiting 