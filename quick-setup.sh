#!/bin/bash

# 🚀 Quick Setup - Space-Efficient Installation
# Uses pre-built images to avoid Docker build space issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}"
    echo "========================================"
    echo "🚀 Cross-Mind Consensus Quick Setup"
    echo "Space-Efficient Installation"
    echo "========================================"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f .env ]; then
        cp env.template .env
        print_success "Created .env file from template"
        
        print_warning "⚠️  IMPORTANT: You need to add your API keys to the .env file!"
        echo ""
        echo "Available API keys (you need at least ONE):"
        echo "- OPENAI_API_KEY (GPT-4, GPT-3.5)"
        echo "- ANTHROPIC_API_KEY (Claude)"
        echo "- COHERE_API_KEY (Command)"
        echo "- GOOGLE_API_KEY (Gemini)"
        echo "- And others..."
        echo ""
        read -p "Do you want to edit the .env file now? (y/N): " edit_env
        if [[ $edit_env =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        print_success ".env file already exists"
    fi
}

# Generate SSL certificates
setup_ssl() {
    print_status "Setting up SSL certificates..."
    
    if [ ! -d "ssl" ] || [ ! -f "ssl/cert.pem" ]; then
        mkdir -p ssl
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/C=US/ST=Dev/L=Local/O=CrossMind/CN=localhost" \
            >/dev/null 2>&1
        print_success "SSL certificates generated"
    else
        print_success "SSL certificates already exist"
    fi
}

# Create required directories
setup_directories() {
    print_status "Creating required directories..."
    mkdir -p logs grafana/dashboards grafana/datasources
    print_success "Directories created"
}

# Pull images first to avoid build issues
pull_images() {
    print_status "Pulling Docker images (this may take a few minutes)..."
    
    docker pull python:3.11-slim
    docker pull redis:7-alpine
    docker pull nginx:alpine
    docker pull prom/prometheus:latest
    docker pull grafana/grafana:latest
    
    print_success "Docker images pulled successfully"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Stop any existing services
    docker-compose -f docker-compose.simple.yml down >/dev/null 2>&1 || true
    
    # Start with the simple compose file
    docker-compose -f docker-compose.simple.yml up -d
    
    print_success "Services started successfully"
}

# Wait for services
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local max_wait=120
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "API service is ready!"
            break
        fi
        echo -n "."
        sleep 5
        waited=$((waited + 5))
    done
    
    if [ $waited -ge $max_wait ]; then
        print_warning "Services may still be starting. Check with: docker-compose -f docker-compose.simple.yml ps"
    fi
}

# Show results
show_results() {
    echo ""
    print_success "🎉 Quick Setup Complete!"
    echo ""
    echo "🌐 Service URLs:"
    echo "   • Dashboard:  https://localhost (or http://localhost:8501)"
    echo "   • API Docs:   http://localhost:8000/docs"
    echo "   • Health:     http://localhost:8000/health"
    echo "   • Grafana:    http://localhost:3000 (admin/admin123)"
    echo "   • Prometheus: http://localhost:9090"
    echo ""
    echo "📋 Management Commands:"
    echo "   • Status:     docker-compose -f docker-compose.simple.yml ps"
    echo "   • Logs:       docker-compose -f docker-compose.simple.yml logs -f"
    echo "   • Stop:       docker-compose -f docker-compose.simple.yml down"
    echo "   • Restart:    docker-compose -f docker-compose.simple.yml restart"
    echo ""
    echo "🔧 Next Steps:"
    echo "1. Configure API keys in .env file if not done already"
    echo "2. Test the API at http://localhost:8000/docs"
    echo "3. Access the dashboard at https://localhost"
    echo ""
    print_warning "⚠️  For HTTPS, you'll see a security warning (self-signed certificate)"
    echo "   Click 'Advanced' → 'Proceed to localhost' in your browser"
}

# Main function
main() {
    print_header
    
    check_prerequisites
    setup_environment
    setup_ssl
    setup_directories
    pull_images
    start_services
    wait_for_services
    show_results
    
    print_success "✅ Installation completed successfully!"
}

# Handle interruption
trap 'print_error "Setup interrupted"; exit 1' INT TERM

# Run main function
main "$@" 