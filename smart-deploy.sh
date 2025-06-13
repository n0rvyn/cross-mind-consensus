#!/bin/bash

# 🚀 Smart Deploy - Intelligent Cross-Mind Consensus Deployment
# Automatically detects environment and deploys accordingly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="cross-mind-consensus"
DEFAULT_DOMAIN="localhost"
DEFAULT_DATA_DIR=""

# Print functions
print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║        🤖 Smart Deploy v2.0              ║"
    echo "║    Cross-Mind Consensus Auto Deployment  ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

# Detect environment
detect_environment() {
    print_step "Detecting deployment environment..."
    
    # Check for cloud platforms
    if curl -s --max-time 1 http://169.254.169.254/latest/meta-data/ >/dev/null 2>&1; then
        ENV_TYPE="aws"
        print_info "AWS EC2 detected"
    elif curl -s --max-time 1 -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/ >/dev/null 2>&1; then
        ENV_TYPE="gcp"
        print_info "Google Cloud Platform detected"
    elif curl -s --max-time 1 -H "Metadata: true" http://169.254.169.254/metadata/instance >/dev/null 2>&1; then
        ENV_TYPE="azure"
        print_info "Microsoft Azure detected"
    elif [ -n "$KUBERNETES_SERVICE_HOST" ]; then
        ENV_TYPE="kubernetes"
        print_info "Kubernetes environment detected"
    elif [ -n "$DOCKER_HOST" ] || [ -S "/var/run/docker.sock" ]; then
        ENV_TYPE="docker"
        print_info "Docker environment detected"
    else
        ENV_TYPE="local"
        print_info "Local development environment detected"
    fi
    
    export ENV_TYPE
}

# Detect the best data directory for installation
detect_data_directory() {
    print_step "Detecting optimal data directory..."
    
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
            print_info "Found writable directory: $dir (${space}GB available)"
            
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
    print_step "Setting up working directory..."
    
    # If we're not already in the data directory, create and copy project
    if [ "$DATA_DIR" != "$(pwd)" ] && [ "$DATA_DIR" != "$SCRIPT_DIR" ]; then
        local project_dir="$DATA_DIR/$PROJECT_NAME"
        
        if [ ! -d "$project_dir" ]; then
            print_info "Creating project directory: $project_dir"
            mkdir -p "$project_dir"
            
            print_info "Copying project files to data directory..."
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

# Auto-detect domain
detect_domain() {
    print_step "Auto-detecting domain configuration..."
    
    case $ENV_TYPE in
        "aws")
            PUBLIC_IP=$(curl -s --max-time 5 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")
            if [ -n "$PUBLIC_IP" ]; then
                DETECTED_DOMAIN="$PUBLIC_IP"
                print_info "AWS public IP: $PUBLIC_IP"
            fi
            ;;
        "gcp")
            PUBLIC_IP=$(curl -s --max-time 5 -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip 2>/dev/null || echo "")
            if [ -n "$PUBLIC_IP" ]; then
                DETECTED_DOMAIN="$PUBLIC_IP"
                print_info "GCP external IP: $PUBLIC_IP"
            fi
            ;;
        "azure")
            PUBLIC_IP=$(curl -s --max-time 5 -H "Metadata: true" "http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/publicIpAddress?api-version=2021-02-01&format=text" 2>/dev/null || echo "")
            if [ -n "$PUBLIC_IP" ]; then
                DETECTED_DOMAIN="$PUBLIC_IP"
                print_info "Azure public IP: $PUBLIC_IP"
            fi
            ;;
        *)
            DETECTED_DOMAIN="localhost"
            ;;
    esac
    
    export DETECTED_DOMAIN
}

# Interactive domain configuration
configure_domain() {
    if [ "$ENV_TYPE" != "local" ]; then
        echo ""
        print_step "Domain Configuration"
        echo "Detected domain: ${DETECTED_DOMAIN:-localhost}"
        echo ""
        echo "Options:"
        echo "1. Use detected domain/IP: ${DETECTED_DOMAIN:-localhost}"
        echo "2. Enter custom domain"
        echo "3. Use localhost (development)"
        echo ""
        read -p "Choose option (1-3) [1]: " domain_choice
        
        case ${domain_choice:-1} in
            1)
                DOMAIN="${DETECTED_DOMAIN:-localhost}"
                ;;
            2)
                read -p "Enter your domain name: " custom_domain
                DOMAIN="${custom_domain:-localhost}"
                ;;
            3)
                DOMAIN="localhost"
                ;;
            *)
                DOMAIN="${DETECTED_DOMAIN:-localhost}"
                ;;
        esac
    else
        DOMAIN="localhost"
    fi
    
    export DOMAIN
    print_success "Using domain: $DOMAIN"
}

# Check prerequisites with auto-install option
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    local missing=()
    
    if ! command -v docker >/dev/null 2>&1; then
        missing+=("docker")
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        missing+=("docker-compose")
    fi
    
    if ! command -v openssl >/dev/null 2>&1; then
        missing+=("openssl")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_warning "Missing prerequisites: ${missing[*]}"
        
        if [ "$ENV_TYPE" != "local" ]; then
            echo ""
            read -p "Attempt to install missing prerequisites? (y/N): " install_prereq
            if [[ $install_prereq =~ ^[Yy]$ ]]; then
                install_prerequisites "${missing[@]}"
            else
                print_error "Prerequisites required. Please install manually."
                exit 1
            fi
        else
            print_error "Please install: ${missing[*]}"
            exit 1
        fi
    else
        print_success "All prerequisites satisfied"
    fi
}

# Auto-install prerequisites (Ubuntu/Debian)
install_prerequisites() {
    local to_install=("$@")
    print_step "Installing prerequisites..."
    
    # Update package list
    sudo apt-get update -qq
    
    for package in "${to_install[@]}"; do
        case $package in
            "docker")
                print_info "Installing Docker..."
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
                sudo usermod -aG docker $USER
                rm get-docker.sh
                ;;
            "docker-compose")
                print_info "Installing Docker Compose..."
                sudo apt-get install -y docker-compose
                ;;
            "openssl")
                print_info "Installing OpenSSL..."
                sudo apt-get install -y openssl
                ;;
        esac
    done
    
    print_success "Prerequisites installed"
}

# Smart SSL setup
setup_ssl_smart() {
    print_step "Configuring SSL certificates..."
    
    if [ "$DOMAIN" = "localhost" ]; then
        # Generate self-signed for localhost
        if [ ! -f "ssl/cert.pem" ]; then
            print_info "Generating self-signed certificate for localhost..."
            mkdir -p ssl
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout ssl/key.pem \
                -out ssl/cert.pem \
                -subj "/C=US/ST=Dev/L=Local/O=CrossMind/CN=localhost" \
                >/dev/null 2>&1
            print_success "Self-signed certificate generated"
        fi
    else
        # Attempt Let's Encrypt for real domains
        print_info "Setting up Let's Encrypt for domain: $DOMAIN"
        
        echo ""
        read -p "Attempt Let's Encrypt SSL certificate? (y/N): " use_letsencrypt
        if [[ $use_letsencrypt =~ ^[Yy]$ ]]; then
            read -p "Enter email for Let's Encrypt: " le_email
            setup_letsencrypt_auto "$DOMAIN" "$le_email"
        else
            print_info "Using self-signed certificate for $DOMAIN"
            mkdir -p ssl
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout ssl/key.pem \
                -out ssl/cert.pem \
                -subj "/C=US/ST=Prod/L=Server/O=CrossMind/CN=$DOMAIN" \
                >/dev/null 2>&1
        fi
    fi
}

# Automated Let's Encrypt setup
setup_letsencrypt_auto() {
    local domain=$1
    local email=$2
    
    print_info "Setting up Let's Encrypt for $domain..."
    
    # Create temporary nginx config for verification
    cat > nginx-temp.conf << EOF
events { worker_connections 1024; }
http {
    server {
        listen 80;
        server_name $domain;
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        location / {
            return 200 'Server ready for SSL setup';
            add_header Content-Type text/plain;
        }
    }
}
EOF
    
    # Start temporary nginx for domain verification
    docker run -d --name temp-nginx -p 80:80 \
        -v "$PWD/nginx-temp.conf:/etc/nginx/nginx.conf:ro" \
        -v "$PWD/certbot-webroot:/var/www/certbot" \
        nginx:alpine
    
    mkdir -p certbot-webroot ssl
    
    # Get certificate
    if docker run --rm \
        -v "$PWD/ssl:/etc/letsencrypt" \
        -v "$PWD/certbot-webroot:/var/www/certbot" \
        certbot/certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email "$email" --agree-tos --no-eff-email \
        -d "$domain"; then
        
        print_success "Let's Encrypt certificate obtained"
        
        # Copy certificates to expected location
        cp "ssl/live/$domain/fullchain.pem" ssl/cert.pem
        cp "ssl/live/$domain/privkey.pem" ssl/key.pem
    else
        print_warning "Let's Encrypt failed, using self-signed certificate"
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/C=US/ST=Prod/L=Server/O=CrossMind/CN=$domain" \
            >/dev/null 2>&1
    fi
    
    # Cleanup
    docker stop temp-nginx >/dev/null 2>&1 || true
    docker rm temp-nginx >/dev/null 2>&1 || true
    rm -f nginx-temp.conf
}

# Update nginx config with domain
update_nginx_config() {
    if [ -f nginx.conf ]; then
        # Replace localhost with actual domain in nginx.conf
        if [ "$DOMAIN" != "localhost" ]; then
            sed -i "s/server_name localhost;/server_name ${DOMAIN};/g" nginx.conf
            print_success "Updated nginx.conf with domain: $DOMAIN"
        fi
    fi
}

# Smart environment setup
setup_environment_smart() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp env.template .env
        print_success "Created .env from template"
    fi
    
    # Check for existing API keys
    local has_keys=false
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        has_keys=true
    fi
    
    if [ "$has_keys" = false ]; then
        echo ""
        print_warning "No API keys detected in .env file"
        echo ""
        read -p "Do you want to enter API keys now? (y/N): " enter_keys
        if [[ $enter_keys =~ ^[Yy]$ ]]; then
            read -p "Enter OpenAI API Key (required): " openai_key
            if [ -n "$openai_key" ]; then
                sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$openai_key/" .env
                print_success "OpenAI API key configured"
            fi
            
            read -p "Enter Anthropic API Key (optional): " anthropic_key
            if [ -n "$anthropic_key" ]; then
                sed -i "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$anthropic_key/" .env
                print_success "Anthropic API key configured"
            fi
        fi
    else
        print_success "API keys found in .env file"
    fi
}

# Deploy with smart monitoring
deploy_services() {
    print_step "Deploying Cross-Mind Consensus services..."
    
    # Stop existing services
    docker-compose down >/dev/null 2>&1 || true
    
    # Start services with build
    print_info "Building and starting services..."
    if docker-compose up -d --build; then
        print_success "Services deployed successfully"
        
        # Monitor startup
        print_info "Monitoring service health..."
        local max_wait=60
        local waited=0
        
        while [ $waited -lt $max_wait ]; do
            if docker-compose ps | grep -q "Up (healthy)" || docker-compose ps | grep -q "Up"; then
                print_success "Services are running!"
                break
            fi
            echo -n "."
            sleep 2
            waited=$((waited + 2))
        done
        
        if [ $waited -ge $max_wait ]; then
            print_warning "Services may still be starting up..."
        fi
    else
        print_error "Deployment failed"
        return 1
    fi
}

# Show deployment summary
show_deployment_summary() {
    echo ""
    print_success "🎉 Smart Deployment Complete!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "   Environment: $ENV_TYPE"
    echo "   Domain: $DOMAIN"
    echo "   SSL: $([ -f ssl/cert.pem ] && echo "✓ Configured" || echo "✗ Not configured")"
    echo ""
    echo "🌐 Access URLs:"
    if [ "$DOMAIN" = "localhost" ]; then
        echo "   • Dashboard:  https://localhost"
        echo "   • API Docs:   https://localhost/docs"
        echo "   • Health:     https://localhost/health"
    else
        echo "   • Dashboard:  https://$DOMAIN"
        echo "   • API Docs:   https://$DOMAIN/docs"
        echo "   • Health:     https://$DOMAIN/health"
    fi
    echo "   • Grafana:    http://$DOMAIN:3000 (admin/admin123)"
    echo "   • Prometheus: http://$DOMAIN:9090"
    echo ""
    echo "🔧 Management Commands:"
    echo "   • Status:     docker-compose ps"
    echo "   • Logs:       docker-compose logs -f"
    echo "   • Stop:       docker-compose down"
    echo "   • Restart:    docker-compose restart"
    echo ""
    
    if [ "$DOMAIN" = "localhost" ]; then
        print_info "⚠️  Using self-signed certificate - browser will show security warning"
    fi
}

# Main execution
main() {
    print_banner
    
    detect_environment
    detect_data_directory
    setup_working_directory
    detect_domain
    configure_domain
    check_prerequisites
    setup_environment_smart
    setup_ssl_smart
    update_nginx_config
    deploy_services
    show_deployment_summary
}

# Handle interruption
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@" 