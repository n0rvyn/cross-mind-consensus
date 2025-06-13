#!/bin/bash

# 🧹 Smart Uninstall - Cross-Mind Consensus Cleanup Script
# Comprehensive cleanup for development and production environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║        🧹 Smart Uninstall v1.0           ║"
    echo "║    Cross-Mind Consensus Cleanup Tool     ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Configuration
PROJECT_NAME="cross-mind-consensus"
CONTAINER_PREFIX="consensus"
VOLUME_PREFIX="cross-mind-consensus"

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Stop and remove Docker containers
cleanup_containers() {
    print_status "Stopping and removing Docker containers..."
    
    # Stop all project containers
    if docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_PREFIX"; then
        print_status "Found project containers, stopping them..."
        docker ps -a --format "table {{.Names}}" | grep "$CONTAINER_PREFIX" | awk '{print $1}' | xargs -r docker stop
        
        print_status "Removing project containers..."
        docker ps -a --format "table {{.Names}}" | grep "$CONTAINER_PREFIX" | awk '{print $1}' | xargs -r docker rm -f
        
        print_success "Docker containers cleaned up"
    else
        print_status "No project containers found"
    fi
}

# Remove Docker volumes
cleanup_volumes() {
    print_status "Removing Docker volumes..."
    
    # List of volumes to remove
    volumes_to_remove=(
        "${VOLUME_PREFIX}_redis_data"
        "${VOLUME_PREFIX}_prometheus_data"
        "${VOLUME_PREFIX}_grafana_data"
        "consensus-network"
    )
    
    for volume in "${volumes_to_remove[@]}"; do
        if docker volume ls -q | grep -q "^${volume}$"; then
            print_status "Removing volume: $volume"
            docker volume rm "$volume" 2>/dev/null || print_warning "Could not remove volume $volume"
        fi
    done
    
    print_success "Docker volumes cleaned up"
}

# Remove Docker images
cleanup_images() {
    print_status "Removing Docker images..."
    
    # Remove project images
    if docker images --format "table {{.Repository}}" | grep -q "$PROJECT_NAME"; then
        print_status "Removing project images..."
        docker images --format "table {{.Repository}}" | grep "$PROJECT_NAME" | xargs -I {} docker rmi -f {}
        print_success "Project images removed"
    else
        print_status "No project images found"
    fi
    
    # Remove dangling images (optional)
    if [ "$1" = "--aggressive" ]; then
        print_status "Removing dangling images..."
        docker image prune -f
        print_success "Dangling images removed"
    fi
}

# Clean up SSL certificates and config files
cleanup_ssl_and_config() {
    print_status "Cleaning up SSL certificates and configuration..."
    
    # Remove SSL directory
    if [ -d "ssl" ]; then
        print_status "Removing SSL certificates..."
        rm -rf ssl/
        print_success "SSL certificates removed"
    fi
    
    # Remove generated config files
    config_files=(
        "nginx-letsencrypt.conf"
        "docker-compose.certbot.yml"
        "certbot-webroot"
    )
    
    for file in "${config_files[@]}"; do
        if [ -e "$file" ]; then
            print_status "Removing $file..."
            rm -rf "$file"
        fi
    done
    
    print_success "Configuration files cleaned up"
}

# Clean up logs and temporary files
cleanup_logs_and_temp() {
    print_status "Cleaning up logs and temporary files..."
    
    # Remove log files
    if [ -d "logs" ]; then
        print_status "Removing log files..."
        rm -rf logs/
        print_success "Log files removed"
    fi
    
    # Remove temporary files
    temp_files=(
        "*.log"
        "*.tmp"
        "*.pid"
        "__pycache__"
        "*.pyc"
        ".pytest_cache"
        ".coverage"
        "htmlcov"
    )
    
    for pattern in "${temp_files[@]}"; do
        find . -name "$pattern" -type f -delete 2>/dev/null || true
        find . -name "$pattern" -type d -exec rm -rf {} + 2>/dev/null || true
    done
    
    print_success "Logs and temporary files cleaned up"
}

# Clean up environment files
cleanup_env_files() {
    print_status "Cleaning up environment files..."
    
    # Ask before removing .env file
    if [ -f ".env" ]; then
        echo ""
        read -p "Do you want to remove the .env file? (y/N): " remove_env
        if [[ $remove_env =~ ^[Yy]$ ]]; then
            rm -f .env
            print_success ".env file removed"
        else
            print_status "Keeping .env file"
        fi
    fi
    
    # Remove backup files
    backup_files=(
        "backend/main_backup.py"
        "backend/enhanced_backup.py"
    )
    
    for file in "${backup_files[@]}"; do
        if [ -f "$file" ]; then
            rm -f "$file"
        fi
    done
    
    print_success "Environment files cleaned up"
}

# Clean up Python virtual environment
cleanup_python_env() {
    print_status "Checking for Python virtual environment..."
    
    if [ -d ".venv" ] || [ -d "venv" ]; then
        echo ""
        read -p "Do you want to remove the Python virtual environment? (y/N): " remove_venv
        if [[ $remove_venv =~ ^[Yy]$ ]]; then
            if [ -d ".venv" ]; then
                rm -rf .venv/
                print_success "Virtual environment (.venv) removed"
            fi
            if [ -d "venv" ]; then
                rm -rf venv/
                print_success "Virtual environment (venv) removed"
            fi
        else
            print_status "Keeping virtual environment"
        fi
    else
        print_status "No virtual environment found"
    fi
}

# Clean up system packages (optional)
cleanup_system_packages() {
    if [ "$1" = "--system" ]; then
        print_status "Cleaning up system packages (optional)..."
        
        echo ""
        read -p "Do you want to remove Docker and related packages? (y/N): " remove_docker
        if [[ $remove_docker =~ ^[Yy]$ ]]; then
            if command_exists docker; then
                print_status "Removing Docker..."
                if command_exists apt; then
                    sudo apt remove -y docker.io docker-compose
                    sudo apt autoremove -y
                elif command_exists yum; then
                    sudo yum remove -y docker docker-compose
                elif command_exists brew; then
                    brew uninstall docker docker-compose
                fi
                print_success "Docker removed"
            fi
        fi
        
        echo ""
        read -p "Do you want to remove Python packages? (y/N): " remove_python
        if [[ $remove_python =~ ^[Yy]$ ]]; then
            if [ -f "requirements.txt" ]; then
                print_status "Removing Python packages..."
                pip uninstall -y -r requirements.txt 2>/dev/null || true
                print_success "Python packages removed"
            fi
        fi
    fi
}

# Clean up network configurations
cleanup_network() {
    print_status "Cleaning up network configurations..."
    
    # Remove custom networks
    if docker network ls --format "table {{.Name}}" | grep -q "$VOLUME_PREFIX"; then
        print_status "Removing custom networks..."
        docker network ls --format "table {{.Name}}" | grep "$VOLUME_PREFIX" | xargs -r docker network rm
        print_success "Custom networks removed"
    fi
    
    # Clean up iptables rules (if any were added)
    if command_exists iptables; then
        print_status "Cleaning up iptables rules..."
        sudo iptables -D INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
        sudo iptables -D INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || true
        sudo iptables -D INPUT -p tcp --dport 8000 -j ACCEPT 2>/dev/null || true
        sudo iptables -D INPUT -p tcp --dport 8501 -j ACCEPT 2>/dev/null || true
        print_success "Iptables rules cleaned up"
    fi
}

# Clean up Let's Encrypt certificates
cleanup_letsencrypt() {
    print_status "Cleaning up Let's Encrypt certificates..."
    
    if [ -d "/etc/letsencrypt/live" ]; then
        echo ""
        read -p "Do you want to remove Let's Encrypt certificates? (y/N): " remove_letsencrypt
        if [[ $remove_letsencrypt =~ ^[Yy]$ ]]; then
            print_status "Removing Let's Encrypt certificates..."
            sudo rm -rf /etc/letsencrypt/live/*
            sudo rm -rf /etc/letsencrypt/archive/*
            sudo rm -rf /etc/letsencrypt/renewal/*
            print_success "Let's Encrypt certificates removed"
        fi
    fi
}

# Show cleanup summary
show_cleanup_summary() {
    echo ""
    print_success "🧹 Cleanup Summary:"
    echo ""
    echo "✅ Docker containers: Removed"
    echo "✅ Docker volumes: Removed"
    echo "✅ Docker images: Removed"
    echo "✅ SSL certificates: Removed"
    echo "✅ Configuration files: Removed"
    echo "✅ Log files: Removed"
    echo "✅ Temporary files: Removed"
    echo "✅ Network configurations: Cleaned"
    echo ""
    print_success "🎉 Cross-Mind Consensus system has been completely removed!"
    echo ""
    echo "📋 What was cleaned up:"
    echo "   • All Docker containers and images"
    echo "   • All project volumes and networks"
    echo "   • SSL certificates and config files"
    echo "   • Log files and temporary data"
    echo "   • Generated configuration files"
    echo ""
    echo "💡 To reinstall, run: ./smart-deploy.sh"
    echo ""
}

# Main cleanup function
main() {
    print_header
    
    # Parse command line arguments
    AGGRESSIVE=false
    SYSTEM=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --aggressive)
                AGGRESSIVE=true
                shift
                ;;
            --system)
                SYSTEM=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --aggressive    Remove dangling images and more thorough cleanup"
                echo "  --system        Remove system packages (Docker, Python packages)"
                echo "  --help, -h      Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0              # Standard cleanup"
                echo "  $0 --aggressive # Thorough cleanup including dangling images"
                echo "  $0 --system     # Remove system packages as well"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Confirm cleanup
    echo ""
    print_warning "⚠️  This will completely remove the Cross-Mind Consensus system!"
    echo ""
    echo "This will delete:"
    echo "   • All Docker containers and images"
    echo "   • All project data and volumes"
    echo "   • SSL certificates and configuration"
    echo "   • Log files and temporary data"
    echo ""
    
    if [ "$AGGRESSIVE" = true ]; then
        print_warning "🔧 Aggressive mode: Will also remove dangling images"
    fi
    
    if [ "$SYSTEM" = true ]; then
        print_warning "🖥️  System mode: Will also remove system packages"
    fi
    
    echo ""
    read -p "Are you sure you want to continue? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_status "Cleanup cancelled"
        exit 0
    fi
    
    # Run cleanup steps
    cleanup_containers
    cleanup_volumes
    cleanup_images "$AGGRESSIVE"
    cleanup_ssl_and_config
    cleanup_logs_and_temp
    cleanup_env_files
    cleanup_python_env
    cleanup_network
    cleanup_letsencrypt
    cleanup_system_packages "$SYSTEM"
    
    # Show summary
    show_cleanup_summary
}

# Handle script interruption
trap 'print_error "Cleanup interrupted"; exit 1' INT TERM

# Run main function
main "$@" 