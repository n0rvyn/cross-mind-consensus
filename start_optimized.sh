#!/bin/bash

# Cross-Mind Consensus API - Optimized Version Startup Script
# This script starts the optimized API with performance enhancements

set -e

echo "🚀 Starting Cross-Mind Consensus API (Optimized Version)"
echo "========================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Please copy env.template to .env and configure your API keys:"
    echo "   cp env.template .env"
    echo "   # Then edit .env with your actual API keys"
    exit 1
fi

# Check if required environment variables are set
echo "🔍 Checking environment configuration..."

# Source the .env file
export $(grep -v '^#' .env | xargs)

# Check required variables
REQUIRED_VARS=("BACKEND_API_KEYS" "OPENAI_API_KEY" "ANTHROPIC_API_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_*" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing or unconfigured environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "📝 Please edit .env file and set these variables with actual values."
    exit 1
fi

echo "✅ Environment configuration looks good!"

# Check if Redis is running
echo "🔍 Checking Redis connection..."
REDIS_HOST=${REDIS_HOST:-localhost}
REDIS_PORT=${REDIS_PORT:-6379}

if command -v redis-cli &> /dev/null; then
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping &> /dev/null; then
        echo "✅ Redis is running at $REDIS_HOST:$REDIS_PORT"
    else
        echo "⚠️  Redis is not responding at $REDIS_HOST:$REDIS_PORT"
        echo "🐳 You can start Redis with Docker:"
        echo "   docker run -d --name redis -p 6379:6379 redis:7-alpine"
        echo ""
        echo "🔄 Continuing without Redis (caching will be disabled)..."
    fi
else
    echo "⚠️  redis-cli not found, skipping Redis check"
fi

# Install dependencies if needed
if [ ! -d "venv" ] && [ ! -f "requirements.txt" ]; then
    echo "❌ No virtual environment or requirements.txt found"
    exit 1
fi

# Check if we're in a virtual environment or if dependencies are installed
echo "🔍 Checking Python dependencies..."
if ! python -c "import fastapi, httpx, redis" &> /dev/null; then
    echo "📦 Installing/updating dependencies..."
    pip install -r requirements.txt
else
    echo "✅ Dependencies are installed"
fi

# Set performance-related environment variables
export PYTHONUNBUFFERED=1
export UVICORN_LOOP=uvloop  # Use high-performance event loop on Unix

# Determine the number of workers based on CPU cores
WORKERS=${WORKERS:-$(python -c "import os; print(min(4, os.cpu_count() or 1))")}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

echo ""
echo "🔧 Configuration:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Workers: $WORKERS"
echo "   Event Loop: ${UVICORN_LOOP:-asyncio}"
echo "   Max Concurrent Requests: ${MAX_CONCURRENT_REQUESTS:-10}"
echo ""

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use!"
    echo "🔄 You can specify a different port with: PORT=8001 ./start_optimized.sh"
    exit 1
fi

# Start the optimized API
echo "🚀 Starting optimized API server..."
echo "📡 API will be available at: http://$HOST:$PORT"
echo "📊 Health check: http://$HOST:$PORT/health"
echo "📚 API docs: http://$HOST:$PORT/docs"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Use uvicorn with optimizations
exec uvicorn backend.main_optimized:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --loop "${UVICORN_LOOP:-asyncio}" \
    --access-log \
    --log-level info \
    --reload-dir backend \
    --reload-dir src 