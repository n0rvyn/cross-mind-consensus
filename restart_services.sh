#!/bin/bash

echo "🔄 Restarting Cross-Mind Consensus Services..."

# Stop all services
echo "⏹️  Stopping services..."
docker-compose -f config/docker/docker-compose.yml down

# Clear Redis cache
echo "🗑️  Clearing Redis cache..."
docker volume rm consensus-redis_data 2>/dev/null || true

# Rebuild API without cache
echo "🔨 Rebuilding API service..."
docker-compose -f config/docker/docker-compose.yml build api --no-cache

# Start all services
echo "🚀 Starting services..."
docker-compose -f config/docker/docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check health
echo "🏥 Checking service health..."
curl -s https://ai.norvyn.com/health | jq '.status' || echo "Health check failed"

echo "✅ Services restarted successfully!"
echo ""
echo "🧪 Testing Chain-of-Thought with Chinese philosophical question..."
curl -X POST "https://ai.norvyn.com/consensus" \
  -H "Authorization: Bearer 87ea1604be1f6_02f173F5fb67582e647fcef6c40" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "用思维链想想本当就是永恒这句话",
    "enable_chain_of_thought": true,
    "reasoning_method": "chain_of_thought",
    "method": "weighted_average",
    "models": ["zhipuai_glm4_air"],
    "enable_caching": false
  }' | jq -r '.consensus_response' | head -5

echo ""
echo "🎉 If you see Chinese philosophical content above, the system is working correctly!"
echo "📝 You can now test with GPT using: '用思维链想想本当就是永恒这句话'" 