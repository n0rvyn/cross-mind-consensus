# 🌐 Public Access Setup Guide for Cross-Mind Consensus API

## Current Status
- ✅ API running on `localhost:8001` with real GLM-4-AIR integration
- ✅ Public IP: `35.229.146.254`
- ❌ Public access blocked by Google Cloud firewall

## 🚀 Quick Solutions for GPT Access

### Option 1: SSH Port Forwarding (Recommended for Testing)

**From your local machine, run:**
```bash
ssh -L 8001:localhost:8001 norvyn@35.229.146.254
```

**Then update GPT configuration to use:**
```yaml
servers:
  - url: http://localhost:8001
    description: SSH tunneled API with GLM-4-AIR
```

**Test with:**
```bash
curl -H "Authorization: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40" \
     http://localhost:8001/models
```

### Option 2: Google Cloud Firewall Rule (Production)

**If you have gcloud CLI access:**
```bash
# Create firewall rule
gcloud compute firewall-rules create allow-cross-mind-api \
  --allow tcp:8001 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow Cross-Mind Consensus API with GLM-4-AIR"

# Verify rule
gcloud compute firewall-rules list --filter="name:allow-cross-mind-api"
```

**Then update GPT configuration to use:**
```yaml
servers:
  - url: http://35.229.146.254:8001
    description: Public API with GLM-4-AIR integration
```

**Test with:**
```bash
curl -H "Authorization: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40" \
     http://35.229.146.254:8001/models
```

### Option 3: Google Cloud Console (Web Interface)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **VPC network** > **Firewall**
3. Click **Create Firewall Rule**
4. Configure:
   - **Name**: `allow-cross-mind-api`
   - **Direction**: Ingress
   - **Action**: Allow
   - **Targets**: All instances in the network
   - **Source IP ranges**: `0.0.0.0/0`
   - **Protocols and ports**: TCP, port `8001`
5. Click **Create**

## 🧪 Testing Your Setup

### Test Local API
```bash
curl -H "Authorization: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40" \
     http://localhost:8001/consensus \
     -H "Content-Type: application/json" \
     -d '{"question": "What is 2+2?", "models": ["zhipuai_glm4_air"], "max_models": 1}'
```

### Test Public API (after firewall setup)
```bash
curl -H "Authorization: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40" \
     http://35.229.146.254:8001/consensus \
     -H "Content-Type: application/json" \
     -d '{"question": "What is 2+2?", "models": ["zhipuai_glm4_air"], "max_models": 1}'
```

## 🤖 GPT Configuration Examples

### For SSH Tunnel (Option 1)
```yaml
openapi: 3.1.0
info:
  title: Cross-Mind Consensus API
  version: 3.1.0

servers:
  - url: http://localhost:8001
    description: SSH tunneled API with real GLM-4-AIR

security:
  - BearerAuth: []

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### For Public Access (Option 2)
```yaml
openapi: 3.1.0
info:
  title: Cross-Mind Consensus API
  version: 3.1.0

servers:
  - url: http://35.229.146.254:8001
    description: Public API with real GLM-4-AIR integration

security:
  - BearerAuth: []

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

## 🔐 Authentication

**Bearer Token:** `87ea1604be1f6_02f173F5fb67582e647fcef6c40`

**Usage in requests:**
```bash
Authorization: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40
```

## 📊 Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/models` | GET | List available models |
| `/consensus` | POST | Get multi-model consensus |
| `/health` | GET | API health status |
| `/docs` | GET | Interactive API documentation |

## 🎯 Model Usage

### Real AI Model
- `zhipuai_glm4_air` - 智谱AI GLM-4-AIR (真实AI响应)

### Intelligent Fallback Models
- `openai_gpt4` - GPT-4 (智能规则响应)
- `anthropic_claude3_sonnet` - Claude 3 Sonnet (智能规则响应)
- `google_gemini_pro` - Gemini Pro (智能规则响应)

## 🔧 Troubleshooting

### Common Issues

1. **403 Forbidden**
   - Check Bearer token
   - Verify server URL

2. **Connection Timeout**
   - Check firewall rules
   - Verify server is running: `ps aux | grep uvicorn`

3. **SSH Tunnel Issues**
   - Ensure SSH key is configured
   - Check port forwarding: `netstat -tlnp | grep 8001`

### Debug Commands

```bash
# Check API server status
curl -s http://localhost:8001/health | jq .

# Check public access (after firewall setup)
curl -s http://35.229.146.254:8001/health | jq .

# Check server logs
tail -f /var/log/nginx/access.log  # If using nginx
```

## 🌟 Features Available

- ✅ Real GLM-4-AIR integration with your API credits
- ✅ Multi-model consensus (real + intelligent fallbacks)
- ✅ Chinese and English language support
- ✅ Chain-of-thought reasoning
- ✅ Performance monitoring
- ✅ Rate limiting and security
- ✅ Interactive API documentation

---

**Status**: ✅ API ready for public access (pending firewall configuration)
**GLM-4-AIR**: Working with real API responses
**Public IP**: 35.229.146.254:8001
**Auth Token**: 87ea1604be1f6_02f173F5fb67582e647fcef6c40 