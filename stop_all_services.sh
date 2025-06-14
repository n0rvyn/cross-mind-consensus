#!/bin/bash

echo "🛑 Stopping All Cross-Mind Consensus Services"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[ℹ]${NC} $1"
}

# Function to stop Docker services
stop_docker_services() {
    print_step "Stopping Docker services..."
    
    # Stop main consensus services
    if [ -f "config/docker/docker-compose.yml" ]; then
        print_info "Stopping main consensus services..."
        docker-compose -f config/docker/docker-compose.yml down
        print_success "Main consensus services stopped"
    fi
    
    # Stop simple docker compose if exists
    if [ -f "docker-compose.simple.yml" ]; then
        print_info "Stopping simple services..."
        docker-compose -f docker-compose.simple.yml down
        print_success "Simple services stopped"
    fi
    
    # Stop any remaining consensus containers
    print_info "Stopping individual consensus containers..."
    docker stop consensus-api consensus-dashboard consensus-redis consensus-nginx consensus-prometheus consensus-grafana 2>/dev/null || true
    docker rm consensus-api consensus-dashboard consensus-redis consensus-nginx consensus-prometheus consensus-grafana 2>/dev/null || true
    
    # Stop health tracker containers
    print_info "Stopping health tracker containers..."
    docker stop ai-health-api ai-health-dashboard ai-health-postgres ai-health-nginx 2>/dev/null || true
    docker rm ai-health-api ai-health-dashboard ai-health-postgres ai-health-nginx 2>/dev/null || true
    
    print_success "Docker services stopped"
}

# Function to stop direct processes
stop_direct_processes() {
    print_step "Stopping direct processes..."
    
    # Stop uvicorn processes (API servers)
    print_info "Stopping uvicorn/API processes..."
    pkill -f "uvicorn.*backend.main" 2>/dev/null || true
    pkill -f "gunicorn.*backend.main" 2>/dev/null || true
    pkill -f "python.*backend.main" 2>/dev/null || true
    
    # Stop streamlit processes (dashboards)
    print_info "Stopping streamlit processes..."
    pkill -f "streamlit.*dashboard" 2>/dev/null || true
    pkill -f "streamlit.*streamlit_app" 2>/dev/null || true
    
    # Stop any remaining python processes related to our project
    print_info "Stopping remaining project processes..."
    pkill -f "python.*cross-mind-consensus" 2>/dev/null || true
    
    print_success "Direct processes stopped"
}

# Function to stop system services
stop_system_services() {
    print_step "Stopping system services..."
    
    # Stop nginx if it's running our config
    if pgrep nginx > /dev/null; then
        print_info "Stopping nginx..."
        sudo systemctl stop nginx 2>/dev/null || true
        print_success "Nginx stopped"
    fi
    
    # Stop redis if it's running standalone
    if pgrep redis-server > /dev/null; then
        print_info "Stopping redis..."
        sudo systemctl stop redis 2>/dev/null || pkill redis-server 2>/dev/null || true
        print_success "Redis stopped"
    fi
}

# Function to clean up ports
cleanup_ports() {
    print_step "Cleaning up ports..."
    
    local ports=(8000 8001 8501 6379 80 443 9090 3000)
    
    for port in "${ports[@]}"; do
        local pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$pid" ]; then
            print_info "Killing process on port $port (PID: $pid)"
            kill -9 $pid 2>/dev/null || true
        fi
    done
    
    print_success "Ports cleaned up"
}

# Function to show final status
show_status() {
    print_step "Final status check..."
    
    echo ""
    echo "🔍 Remaining processes:"
    ps aux | grep -E "(uvicorn|streamlit|redis|nginx|prometheus|grafana)" | grep -v grep || echo "No related processes found"
    
    echo ""
    echo "🐳 Remaining Docker containers:"
    docker ps --filter "name=consensus" --filter "name=ai-health" || echo "No related containers found"
    
    echo ""
    echo "🔌 Port usage:"
    netstat -tlnp 2>/dev/null | grep -E ":(8000|8001|8501|6379|80|443|9090|3000)" || echo "Target ports are free"
}

# Main execution
main() {
    echo "⚠️  This will stop ALL Cross-Mind Consensus services"
    echo "   - Docker containers"
    echo "   - Direct Python processes"
    echo "   - System services (nginx, redis)"
    echo ""
    
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 0
    fi
    
    echo ""
    stop_docker_services
    echo ""
    stop_direct_processes
    echo ""
    stop_system_services
    echo ""
    cleanup_ports
    echo ""
    show_status
    
    echo ""
    echo -e "${GREEN}🎉 All services stopped successfully!${NC}"
    echo ""
    echo "💡 To restart services:"
    echo "   - Docker: docker-compose -f config/docker/docker-compose.yml up -d"
    echo "   - Direct: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001"
    echo "   - Health: ./health-check.sh"
}

# Run main function
main "$@" 