#!/bin/bash

# 🚀 Cross-Mind Consensus - Automatic Setup Script
# This script will automatically set up everything you need to run the project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="cross-mind-consensus"
DEFAULT_DATA_DIR=""

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
    echo -e "${PURPLE}"
    echo "========================================"
    echo "🤖 Cross-Mind Consensus Auto Setup v2.0"
    echo "========================================"
    echo -e "${NC}"
}

# Detect the best data directory for installation
detect_data_directory() {
    print_status "Detecting optimal data directory..."
    
    # Check for mounted data directories with sufficient space
    local candidates=(
        "/home/$(whoami)/data"
        "/data"
        "/opt/data"
        "/var/lib/docker-data"
        "$(pwd)"
    )
    
    local best_dir=""
    local max_space=0
    
    for dir in "${candidates[@]}"; do
        if [ -d "$dir" ] && [ -w "$dir" ]; then
            # Get available space in GB
            local space=$(df "$dir" 2>/dev/null | tail -1 | awk '{print int($4/1024/1024)}')
            print_status "Found writable directory: $dir (${space}GB available)"
            
            if [ "$space" -gt "$max_space" ]; then
                max_space=$space
                best_dir=$dir
            fi
        fi
    done
    
    # If we found a good candidate with more than 10GB, use it
    if [ -n "$best_dir" ] && [ "$max_space" -gt 10 ]; then
        DEFAULT_DATA_DIR="$best_dir"
        print_success "Selected data directory: $DEFAULT_DATA_DIR (${max_space}GB available)"
    else
        DEFAULT_DATA_DIR="$(pwd)"
        print_warning "Using current directory: $DEFAULT_DATA_DIR"
    fi
    
    export DATA_DIR="${DATA_DIR:-$DEFAULT_DATA_DIR}"
}

# Setup working directory
setup_working_directory() {
    print_status "Setting up working directory..."
    
    # If we're not already in the data directory, create and copy project
    if [ "$DATA_DIR" != "$(pwd)" ] && [ "$DATA_DIR" != "$SCRIPT_DIR" ]; then
        local project_dir="$DATA_DIR/$PROJECT_NAME"
        
        if [ ! -d "$project_dir" ]; then
            print_status "Creating project directory: $project_dir"
            mkdir -p "$project_dir"
            
            print_status "Copying project files to data directory..."
            cp -r "$SCRIPT_DIR/"* "$project_dir/"
            
            # Update working directory
            cd "$project_dir"
            print_success "Working directory set to: $(pwd)"
        else
            cd "$project_dir"
            print_success "Using existing project directory: $(pwd)"
        fi
    else
        print_success "Using current directory: $(pwd)"
    fi
    
    # Create data subdirectories
    mkdir -p data/logs data/redis data/grafana data/prometheus
    print_success "Created data subdirectories"
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
            
            # Add data directory configuration to .env
            echo "" >> .env
            echo "# Data Directory Configuration" >> .env
            echo "DATA_DIR=$(pwd)/data" >> .env
            echo "LOGS_DIR=$(pwd)/data/logs" >> .env
            
            print_success "Created .env file from template"
            print_warning "⚠️  IMPORTANT: You need to add your API keys to the .env file!"
            echo ""
            echo "Available API keys (you need at least ONE):"
            echo "- OPENAI_API_KEY (GPT-4, GPT-3.5)"
            echo "- ANTHROPIC_API_KEY (Claude)"
            echo "- COHERE_API_KEY (Command)"
            echo "- GOOGLE_API_KEY (Gemini)"
            echo "- ERNIE_API_KEY + ERNIE_SECRET_KEY (Baidu)"
            echo "- MOONSHOT_API_KEY (Moonshot)"
            echo "- ZHIPU_API_KEY (GLM)"
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

# Update Docker Compose to use data paths
update_docker_compose() {
    print_status "Updating Docker Compose configuration for data paths..."
    
    # Create a docker-compose override file for data paths
    cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  redis:
    volumes:
      - ./data/redis:/data
    
  api:
    volumes:
      - ./data/logs:/app/logs
      - ./.env:/app/.env:ro
      
  dashboard:
    volumes:
      - ./.env:/app/.env:ro
      
  prometheus:
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./data/prometheus:/prometheus
      
  grafana:
    volumes:
      - ./data/grafana:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/datasources:/etc/grafana/provisioning/datasources:ro

volumes:
  redis_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: $(pwd)/data/redis
  prometheus_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: $(pwd)/data/prometheus
  grafana_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: $(pwd)/data/grafana
EOF
    
    print_success "Created Docker Compose override for data paths"
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

# Display service URLs and data paths
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
    echo "📁 Data Locations:"
    echo "   • Project Dir:    $(pwd)"
    echo "   • Data Dir:       $(pwd)/data"
    echo "   • Logs:           $(pwd)/data/logs"
    echo "   • Redis Data:     $(pwd)/data/redis"
    echo "   • Grafana Data:   $(pwd)/data/grafana"
    echo "   • Prometheus:     $(pwd)/data/prometheus"
    echo ""
    echo "📋 Useful Commands:"
    echo "   • View logs:      docker-compose logs -f"
    echo "   • Stop services:  docker-compose down"
    echo "   • Restart:        docker-compose restart"
    echo "   • Status:         docker-compose ps"
    echo "   • Data usage:     du -sh $(pwd)/data"
    echo ""
    print_warning "⚠️  Note: You'll see a security warning for HTTPS (self-signed certificate)"
    echo "   Click 'Advanced' → 'Proceed to localhost' in your browser"
    echo ""
}

# Check API keys in .env file
check_api_keys() {
    if [ -f .env ]; then
        local has_api_key=false
        
        # Check for any valid API key
        if grep -q "OPENAI_API_KEY=sk-" .env || \
           grep -q "ANTHROPIC_API_KEY=sk-ant-" .env || \
           grep -q "COHERE_API_KEY=" .env | grep -v "=your-" || \
           grep -q "GOOGLE_API_KEY=" .env | grep -v "=your-" || \
           grep -q "ERNIE_API_KEY=" .env | grep -v "=your-" || \
           grep -q "MOONSHOT_API_KEY=" .env | grep -v "=your-" || \
           grep -q "ZHIPU_API_KEY=" .env | grep -v "=your-"; then
            has_api_key=true
        fi
        
        if [ "$has_api_key" = false ]; then
            print_warning "⚠️  No valid API keys configured in .env file"
            print_warning "   The system needs at least one LLM provider API key to function"
            print_warning "   Supported providers: OpenAI, Anthropic, Cohere, Google, Baidu, Moonshot, Zhipu"
        fi
    fi
}

# Main setup function
main() {
    print_header
    
    # Run all setup steps
    detect_data_directory
    setup_working_directory
    check_prerequisites
    check_docker_running
    setup_environment
    setup_ssl_certificates
    update_docker_compose
    setup_nginx_config
    check_api_keys
    stop_existing_containers
    start_services
    wait_for_services
    show_service_urls
    
    print_success "✅ Auto-setup completed successfully!"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Configure API keys in .env file"
    echo "2. Access the dashboard at https://localhost"
    echo "3. Check the API documentation at https://localhost/docs"
}

# Handle script interruption
trap 'print_error "Setup interrupted"; exit 1' INT TERM

# Run main function
main "$@" 