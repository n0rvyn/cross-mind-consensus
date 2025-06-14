# Cross-Mind Consensus GPT Configuration

This directory contains configuration files for integrating Cross-Mind Consensus with OpenAI's GPT platform and other AI assistants.

## Files

- `gpt_actions.yaml`: OpenAPI specification for the Cross-Mind Consensus API
- `gpt_manifest.json`: Manifest file for OpenAI's GPT platform
- `gpt_client.yaml`: Client configuration for applications integrating with the API
- `gpt_config/host.md`: System prompt for the consensus host

## Usage

### OpenAI GPT Integration

To integrate with OpenAI's GPT platform:

1. Use the `gpt_manifest.json` file when creating a custom GPT
2. Ensure your API is accessible at `http://localhost:8000` (or `https://ai.norvyn.com` once SSL is properly configured)
3. Make sure the OpenAPI specification is available at `http://localhost:8000/openapi.json`

### API Keys

The API uses bearer token authentication. Use one of the API keys defined in your environment configuration:

```
BACKEND_API_KEYS=test-key,another-key,your-secure-key
```

## Endpoints

The main endpoints available are:

- `POST /consensus`: Get consensus on a question from multiple models
- `GET /models`: List available models
- `GET /analytics/performance`: Get system performance analytics

For detailed API documentation, visit `http://localhost:8000/docs`

# GPT Actions Configuration for Cross-Mind Consensus API

## 🚀 Quick Start

The Cross-Mind Consensus API is now running with **real GLM-4-AIR integration**!

### Server Configuration
- **Primary Server**: `http://localhost:8001` (with real GLM-4-AIR)
- **Fallback Server**: `http://localhost:8000` (legacy mock responses)
- **Authentication**: Bearer token required

### Available Models

#### Real AI Models
- `zhipuai_glm4_air` - 智谱AI GLM-4-AIR (真实AI响应)

#### Intelligent Fallback Models
- `openai_gpt4` - GPT-4 (智能规则响应)
- `anthropic_claude3_sonnet` - Claude 3 Sonnet (智能规则响应)
- `google_gemini_pro` - Gemini Pro (智能规则响应)

## 📝 Usage Examples

### Single Model Query (GLM-4-AIR)
```json
{
  "question": "What is 2+2?",
  "models": ["zhipuai_glm4_air"],
  "max_models": 1,
  "enable_caching": false
}
```

### Multi-Model Consensus
```json
{
  "question": "What are the benefits of renewable energy?",
  "models": ["zhipuai_glm4_air", "openai_gpt4", "anthropic_claude3_sonnet"],
  "max_models": 3,
  "enable_caching": false
}
```

### Chinese Questions
```json
{
  "question": "请简单介绍一下Python编程语言",
  "models": ["zhipuai_glm4_air"],
  "max_models": 1
}
```

## 🔧 Troubleshooting

### 403 Error Solutions
1. **Check Server URL**: Ensure GPT is pointing to `http://localhost:8001`
2. **Verify Authentication**: Use the correct Bearer token
3. **Test Endpoint**: Try `/models` endpoint first to verify connectivity

### Model Availability
- GLM-4-AIR provides real AI responses (0.8-12 seconds response time)
- Other models use intelligent rule-based fallbacks (instant response)
- All models support both English and Chinese questions

## 🎯 Best Practices

1. **Use GLM-4-AIR for important questions** - it provides real AI analysis
2. **Enable multi-model consensus** for comprehensive perspectives
3. **Disable caching** for fresh responses during testing
4. **Specify models explicitly** for predictable results

## 📊 Response Format

```json
{
  "consensus_response": "Final consensus answer",
  "consensus_score": 0.85,
  "individual_responses": [
    {
      "model": "zhipuai_glm4_air",
      "response": "Real AI response",
      "confidence": 0.85,
      "response_time": 1.2,
      "provider": "zhipuai",
      "success": true
    }
  ],
  "method_used": "expert_roles",
  "total_response_time": 1.5,
  "models_used": ["zhipuai_glm4_air"],
  "cache_hit": false
}
```

## 🌟 Features

- ✅ Real GLM-4-AIR integration with your API key
- ✅ Intelligent fallback for other models
- ✅ Multi-language support (English/Chinese)
- ✅ Consensus scoring and analysis
- ✅ Performance monitoring
- ✅ Caching support
- ✅ Chain-of-thought reasoning (experimental)

---

**Status**: ✅ Fully operational with real AI integration
**Last Updated**: 2025-06-14
**GLM-4-AIR**: Working with your API credits 