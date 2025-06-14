# Cross-Mind Consensus

A multi-LLM consensus system for enhanced AI decision making. This system gathers responses from multiple AI models and provides a consensus answer, improving reliability and reducing bias.

## Overview

The Cross-Mind Consensus system includes:

- FastAPI backend for handling consensus requests
- Redis for caching responses
- Streamlit dashboard for visualization
- NGINX as a reverse proxy

## Features

- **Multi-model consensus**: Gather responses from different LLM models (GPT-4, Claude, Gemini, etc.)
- **Flexible consensus methods**: Support for expert roles, direct consensus, and debate approaches
- **Performance analytics**: Track model performance, response times, and consensus scores
- **Caching**: Redis-based caching for improved performance and reduced costs
- **Scalable architecture**: Containerized deployment with Docker Compose
- **GPT integration**: Ready-to-use integration with OpenAI's GPT platform
- **Interactive dashboard**: Real-time visualization of consensus results and analytics

## Installation

### Prerequisites

- Docker and Docker Compose
- 2GB+ RAM for the lightweight deployment
- SSL certificates (self-signed included for testing)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/cross-mind-consensus.git
   cd cross-mind-consensus
   ```

2. Deploy with Docker Compose:
   ```bash
   docker-compose -f docker-compose.simple.yml up -d
```

## Deployment

The system is deployed using Docker Compose:

```bash
docker-compose -f docker-compose.simple.yml up -d
```

This will start the following services:
- Redis (port 6379)
- FastAPI backend (port 8000)
- Streamlit dashboard (port 8501)
- NGINX reverse proxy (ports 80/443)

### Environment Variables

Key environment variables you can configure:

- `REDIS_HOST`: Redis hostname (default: redis)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_PASSWORD`: Redis password (optional)
- `ENABLE_CACHING`: Enable response caching (default: true)
- `ENABLE_ANALYTICS`: Enable analytics collection (default: false)
- `ENABLE_RATE_LIMITING`: Enable API rate limiting (default: false)
- `API_KEYS`: Comma-separated list of valid API keys

## API Usage

### Authentication

Add your API key to requests using the `X-API-Key` header:

```bash
curl -X POST https://ai.norvyn.com/consensus \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{ ... }'
```

### Consensus Endpoint

```bash
curl -X POST https://ai.norvyn.com/consensus -H "Content-Type: application/json" -d '{
  "question": "What is the best programming language?",
  "options": [
    {"id": "python", "text": "Python"},
    {"id": "javascript", "text": "JavaScript"},
    {"id": "go", "text": "Go"}
  ]
}'
```

### Response Format

```json
{
  "consensus": {
    "selected_option": {
      "id": "python",
      "text": "Python"
    },
    "agreement_percentage": 66.7,
    "vote_count": 3
  },
  "model_responses": [
    {
      "model": "gpt-4",
      "selected_option_id": "python",
      "confidence": 0.93,
      "reasoning": "This is mock reasoning from gpt-4...",
      "processing_time": 0.2
    },
    ...
  ],
  "query": "What is the best programming language?",
  "processing_time": 0.622
}
```

### Health Check

```bash
curl https://ai.norvyn.com/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-14T05:21:52.070019",
  "services": {
    "api": "up",
    "redis": "up",
    "models": {
      "gpt-4": "up",
      "claude-3": "up",
      "gemini-pro": "up"
    }
  },
  "system_metrics": {
    "cpu_usage": 11.03,
    "memory_usage": 22.99,
    "cache_size": 221
  }
}
```

## GPT Integration

The system can be integrated with OpenAI's GPT platform using the files in the `config/gpt/` directory:

- `gpt_actions.yaml`: OpenAPI specification
- `gpt_manifest.json`: Manifest file for GPT platform
- `gpt_client.yaml`: Client configuration
- `gpt_config/host.md`: System prompt for the consensus host

### Setting Up GPT Integration

1. Update the `baseUrl` and `apiKey` in `config/gpt/gpt_client.yaml`
2. Upload the `gpt_manifest.json` to the GPT platform
3. Configure the verification tokens as needed

## Dashboard

Access the Streamlit dashboard at `https://your-domain/` to:

- Submit consensus queries through the UI
- View real-time results and visualizations
- Explore analytics and model performance
- Compare different consensus methods

## Examples

See the `examples/` directory for code examples showing how to use the API:

- Python client examples
- JavaScript/Node.js integration
- Batch processing examples
- Custom consensus method implementations

## SSL Configuration

The system uses self-signed SSL certificates for HTTPS. For production use, replace the certificates in the `ssl/` directory with proper certificates from a trusted certificate authority.

To generate new self-signed certificates:

```bash
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/CN=your-domain.com"
```

## File Structure

- `backend/main.py`: Main API implementation
- `src/simple_dashboard.py`: Streamlit dashboard
- `config/`: Configuration files
  - `nginx/`: NGINX configuration
  - `gpt/`: GPT integration files
  - `docker/`: Docker configuration
  - `monitoring/`: Prometheus and Grafana configuration
- `examples/`: Usage examples
- `ssl/`: SSL certificates

## Troubleshooting

Common issues and solutions:

- **502 Bad Gateway**: Check if the API container is running (`docker ps`)
- **Redis connection errors**: Verify Redis password and connectivity
- **SSL certificate issues**: Ensure certificates are properly mounted in NGINX

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.