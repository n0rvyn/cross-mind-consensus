#!/bin/bash

# 🚀 Cross-Mind Consensus - Automatic Setup Script
# This script will automatically set up everything you need to run the project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
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
    echo "======================================"
    echo "🤖 Cross-Mind Consensus Auto Setup"
    echo "======================================"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_commands=()
    
    if ! command_exists docker; then
        missing_commands+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_commands+=("docker-compose")
    fi
    
    if ! command_exists openssl; then
        missing_commands+=("openssl")
    fi
    
    if [ ${#missing_commands[@]} -ne 0 ]; then
        print_error "Missing required commands: ${missing_commands[*]}"
        echo "Please install the missing commands and try again."
        echo ""
        echo "Installation guides:"
        echo "- Docker: https://docs.docker.com/get-docker/"
        echo "- Docker Compose: https://docs.docker.com/compose/install/"
        echo "- OpenSSL: Usually comes with your system"
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Check if Docker is running
check_docker_running() {
    print_status "Checking if Docker is running..."
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "Docker is running"
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f env.template ]; then
            cp env.template .env
            print_success "Created .env file from template"
            print_warning "⚠️  IMPORTANT: You need to add your API keys to the .env file!"
            echo ""
            echo "Required API keys:"
            echo "- OPENAI_API_KEY (minimum required)"
            echo "- ANTHROPIC_API_KEY (optional)"
            echo "- COHERE_API_KEY (optional)"
            echo "- GOOGLE_API_KEY (optional)"
            echo ""
            read -p "Do you want to edit the .env file now? (y/N): " edit_env
            if [[ $edit_env =~ ^[Yy]$ ]]; then
                ${EDITOR:-nano} .env
            else
                print_warning "Remember to edit .env file before running the services!"
            fi
        else
            print_error "env.template not found!"
            exit 1
        fi
    else
        print_success ".env file already exists"
    fi
}

# Generate SSL certificates
setup_ssl_certificates() {
    print_status "Setting up SSL certificates..."
    
    if [ ! -d "ssl" ] || [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        print_status "Generating self-signed SSL certificates..."
        
        mkdir -p ssl
        
        # Generate self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/C=US/ST=Development/L=Local/O=CrossMindConsensus/OU=Development/CN=localhost" \
            >/dev/null 2>&1
        
        print_success "SSL certificates generated successfully"
    else
        print_success "SSL certificates already exist"
    fi
}

# Check if nginx.conf exists
setup_nginx_config() {
    print_status "Setting up Nginx configuration..."
    
    if [ ! -f "nginx.conf" ]; then
        print_error "nginx.conf not found! This should have been created."
        print_status "The nginx.conf file is required for HTTPS setup."
        exit 1
    else
        print_success "Nginx configuration found"
    fi
}

# Stop existing containers
stop_existing_containers() {
    print_status "Stopping any existing containers..."
    
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        docker-compose down >/dev/null 2>&1
        print_success "Stopped existing containers"
    else
        print_status "No existing containers to stop"
    fi
}

# Start services
start_services() {
    print_status "Starting Cross-Mind Consensus services..."
    
    # Pull/build images and start services
    if docker-compose up -d --build; then
        print_success "Services started successfully!"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep -q "Up (healthy)"; then
            print_success "Services are healthy and ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_warning "Services may still be starting. Check with: docker-compose ps"
}

# Display service URLs
show_service_urls() {
    echo ""
    print_success "🎉 Setup complete! Your services are running:"
    echo ""
    echo "🌐 Service URLs:"
    echo "   • Main Dashboard:  https://localhost"
    echo "   • API:            https://localhost/docs"
    echo "   • Health Check:   https://localhost/health"
    echo "   • Grafana:        http://localhost:3000 (admin/admin123)"
    echo "   • Prometheus:     http://localhost:9090"
    echo ""
    echo "📋 Useful Commands:"
    echo "   • View logs:      docker-compose logs -f"
    echo "   • Stop services:  docker-compose down"
    echo "   • Restart:        docker-compose restart"
    echo "   • Status:         docker-compose ps"
    echo ""
    print_warning "⚠️  Note: You'll see a security warning for HTTPS (self-signed certificate)"
    echo "   Click 'Advanced' → 'Proceed to localhost' in your browser"
    echo ""
}

# Check API keys in .env file
check_api_keys() {
    if [ -f .env ]; then
        if ! grep -q "OPENAI_API_KEY=sk-" .env; then
            print_warning "⚠️  OPENAI_API_KEY not configured in .env file"
            print_warning "   The system will have limited functionality without API keys"
        fi
    fi
}

# Main setup function
main() {
    print_header
    
    # Run all setup steps
    check_prerequisites
    check_docker_running
    setup_environment
    setup_ssl_certificates
    setup_nginx_config
    check_api_keys
    stop_existing_containers
    start_services
    wait_for_services
    show_service_urls
    
    print_success "✅ Auto-setup completed successfully!"
}

# Handle script interruption
trap 'print_error "Setup interrupted"; exit 1' INT TERM

# Run main function
main "$@" 