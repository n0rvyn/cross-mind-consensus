#!/bin/bash

# 🎯 Cross-Mind Consensus Installation Configuration
# User-defined installation paths and configuration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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
    echo "=================================================="
    echo "🎯 Cross-Mind Consensus Installation Config"
    echo "User-Defined Installation Paths"
    echo "=================================================="
    echo -e "${NC}"
}

# Default paths
DEFAULT_INSTALL_DIR="/opt/cross-mind-consensus"
DEFAULT_DATA_DIR="/opt/cross-mind-consensus/data"
DEFAULT_LOGS_DIR="/opt/cross-mind-consensus/logs"
DEFAULT_CONFIG_DIR="/opt/cross-mind-consensus/config"
DEFAULT_CACHE_DIR="/opt/cross-mind-consensus/cache"

# Configuration file
CONFIG_FILE="install-paths.conf"

# Load existing configuration
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        print_success "Loaded existing configuration from $CONFIG_FILE"
    else
        # Set defaults
        INSTALL_DIR="$DEFAULT_INSTALL_DIR"
        DATA_DIR="$DEFAULT_DATA_DIR"
        LOGS_DIR="$DEFAULT_LOGS_DIR"
        CONFIG_DIR="$DEFAULT_CONFIG_DIR"
        CACHE_DIR="$DEFAULT_CACHE_DIR"
        DOCKER_ROOT="/var/lib/docker"
        USE_CUSTOM_DOCKER_ROOT=false
    fi
}

# Interactive configuration
configure_paths() {
    echo ""
    print_status "Configure Installation Paths"
    echo ""
    
    # Installation directory
    echo "1. Main Installation Directory"
    echo "   Current: ${INSTALL_DIR}"
    read -p "   Enter new path (or press Enter to keep current): " new_install
    if [ -n "$new_install" ]; then
        INSTALL_DIR="$new_install"
    fi
    
    # Data directory
    echo ""
    echo "2. Data Storage Directory (Redis, Grafana, Prometheus)"
    echo "   Current: ${DATA_DIR}"
    read -p "   Enter new path (or press Enter to keep current): " new_data
    if [ -n "$new_data" ]; then
        DATA_DIR="$new_data"
    fi
    
    # Logs directory
    echo ""
    echo "3. Logs Directory"
    echo "   Current: ${LOGS_DIR}"
    read -p "   Enter new path (or press Enter to keep current): " new_logs
    if [ -n "$new_logs" ]; then
        LOGS_DIR="$new_logs"
    fi
    
    # Configuration directory
    echo ""
    echo "4. Configuration Directory (SSL, nginx, env files)"
    echo "   Current: ${CONFIG_DIR}"
    read -p "   Enter new path (or press Enter to keep current): " new_config
    if [ -n "$new_config" ]; then
        CONFIG_DIR="$new_config"
    fi
    
    # Cache directory
    echo ""
    echo "5. Cache Directory (pip cache, temporary files)"
    echo "   Current: ${CACHE_DIR}"
    read -p "   Enter new path (or press Enter to keep current): " new_cache
    if [ -n "$new_cache" ]; then
        CACHE_DIR="$new_cache"
    fi
    
    # Docker root (advanced)
    echo ""
    echo "6. Docker Data Root (Advanced - requires Docker restart)"
    echo "   Current: ${DOCKER_ROOT}"
    echo "   Default: /var/lib/docker"
    read -p "   Do you want to customize Docker data location? (y/N): " custom_docker
    if [[ $custom_docker =~ ^[Yy]$ ]]; then
        USE_CUSTOM_DOCKER_ROOT=true
        read -p "   Enter Docker data root path: " new_docker_root
        if [ -n "$new_docker_root" ]; then
            DOCKER_ROOT="$new_docker_root"
        fi
    fi
}

# Validate paths
validate_paths() {
    print_status "Validating paths..."
    
    local errors=0
    
    # Check if parent directories exist or can be created
    for dir in "$INSTALL_DIR" "$DATA_DIR" "$LOGS_DIR" "$CONFIG_DIR" "$CACHE_DIR"; do
        local parent_dir=$(dirname "$dir")
        if [ ! -d "$parent_dir" ] && ! mkdir -p "$parent_dir" 2>/dev/null; then
            print_error "Cannot create parent directory: $parent_dir"
            errors=$((errors + 1))
        fi
    done
    
    # Check write permissions
    for dir in "$INSTALL_DIR" "$DATA_DIR" "$LOGS_DIR" "$CONFIG_DIR" "$CACHE_DIR"; do
        if [ -d "$dir" ] && [ ! -w "$dir" ]; then
            print_error "No write permission for: $dir"
            errors=$((errors + 1))
        fi
    done
    
    # Check available space
    local required_space_gb=10
    for dir in "$INSTALL_DIR" "$DATA_DIR"; do
        local available_space=$(df "$dir" 2>/dev/null | tail -1 | awk '{print int($4/1024/1024)}' || echo 0)
        if [ "$available_space" -lt "$required_space_gb" ]; then
            print_warning "Low disk space in $dir: ${available_space}GB available (recommended: ${required_space_gb}GB)"
        fi
    done
    
    if [ $errors -gt 0 ]; then
        print_error "Path validation failed with $errors errors"
        return 1
    fi
    
    print_success "All paths validated successfully"
}

# Create directories
create_directories() {
    print_status "Creating directory structure..."
    
    # Create main directories
    for dir in "$INSTALL_DIR" "$DATA_DIR" "$LOGS_DIR" "$CONFIG_DIR" "$CACHE_DIR"; do
        if mkdir -p "$dir"; then
            print_success "Created: $dir"
        else
            print_error "Failed to create: $dir"
            return 1
        fi
    done
    
    # Create subdirectories
    mkdir -p "$DATA_DIR"/{redis,grafana,prometheus}
    mkdir -p "$CONFIG_DIR"/{ssl,nginx}
    mkdir -p "$LOGS_DIR"/{api,dashboard,nginx}
    mkdir -p "$CACHE_DIR"/{pip,docker-build}
    
    print_success "Directory structure created"
}

# Save configuration
save_config() {
    print_status "Saving configuration..."
    
    cat > "$CONFIG_FILE" << EOF
# Cross-Mind Consensus Installation Configuration
# Generated on $(date)

# Main installation directory
INSTALL_DIR="$INSTALL_DIR"

# Data storage directory
DATA_DIR="$DATA_DIR"

# Logs directory  
LOGS_DIR="$LOGS_DIR"

# Configuration directory
CONFIG_DIR="$CONFIG_DIR"

# Cache directory
CACHE_DIR="$CACHE_DIR"

# Docker configuration
DOCKER_ROOT="$DOCKER_ROOT"
USE_CUSTOM_DOCKER_ROOT=$USE_CUSTOM_DOCKER_ROOT

# Derived paths
PROJECT_DIR="$INSTALL_DIR"
SSL_DIR="$CONFIG_DIR/ssl"
NGINX_CONFIG_DIR="$CONFIG_DIR/nginx"
PIP_CACHE_DIR="$CACHE_DIR/pip"
DOCKER_BUILD_CACHE="$CACHE_DIR/docker-build"

# Export for scripts
export INSTALL_DIR DATA_DIR LOGS_DIR CONFIG_DIR CACHE_DIR
export PROJECT_DIR SSL_DIR NGINX_CONFIG_DIR PIP_CACHE_DIR DOCKER_BUILD_CACHE
export DOCKER_ROOT USE_CUSTOM_DOCKER_ROOT
EOF
    
    print_success "Configuration saved to $CONFIG_FILE"
}

# Show configuration summary
show_summary() {
    echo ""
    print_success "📋 Installation Configuration Summary"
    echo ""
    echo "📁 Directory Structure:"
    echo "   ├── Installation: $INSTALL_DIR"
    echo "   ├── Data Storage: $DATA_DIR"
    echo "   │   ├── Redis:     $DATA_DIR/redis"
    echo "   │   ├── Grafana:   $DATA_DIR/grafana"
    echo "   │   └── Prometheus: $DATA_DIR/prometheus"
    echo "   ├── Logs:        $LOGS_DIR"
    echo "   ├── Config:      $CONFIG_DIR"
    echo "   │   ├── SSL:      $CONFIG_DIR/ssl"
    echo "   │   └── Nginx:    $CONFIG_DIR/nginx"
    echo "   └── Cache:       $CACHE_DIR"
    echo "       ├── Pip:      $CACHE_DIR/pip"
    echo "       └── Docker:   $CACHE_DIR/docker-build"
    echo ""
    
    if [ "$USE_CUSTOM_DOCKER_ROOT" = true ]; then
        echo "🐳 Docker Data Root: $DOCKER_ROOT"
        echo ""
    fi
    
    echo "💾 Disk Space Check:"
    for dir in "$INSTALL_DIR" "$DATA_DIR"; do
        if [ -d "$dir" ]; then
            local space=$(df -h "$dir" | tail -1 | awk '{print $4}')
            echo "   $dir: $space available"
        fi
    done
    echo ""
    
    echo "🔧 Next Steps:"
    echo "1. Run: source $CONFIG_FILE"
    echo "2. Run: ./smart-deploy.sh --use-config"
    echo "3. All data will be stored in your specified locations"
}

# Configure Docker daemon (if requested)
configure_docker() {
    if [ "$USE_CUSTOM_DOCKER_ROOT" = true ]; then
        print_status "Configuring Docker data root..."
        
        local docker_config="/etc/docker/daemon.json"
        local backup_config="/etc/docker/daemon.json.backup.$(date +%Y%m%d_%H%M%S)"
        
        # Backup existing config
        if [ -f "$docker_config" ]; then
            sudo cp "$docker_config" "$backup_config"
            print_success "Backed up existing Docker config to $backup_config"
        fi
        
        # Create new config
        sudo mkdir -p /etc/docker
        echo "{" | sudo tee "$docker_config" > /dev/null
        echo "  \"data-root\": \"$DOCKER_ROOT\"" | sudo tee -a "$docker_config" > /dev/null
        echo "}" | sudo tee -a "$docker_config" > /dev/null
        
        print_success "Docker daemon.json configured"
        print_warning "⚠️  Docker needs to be restarted for changes to take effect"
        echo ""
        read -p "Restart Docker now? (y/N): " restart_docker
        if [[ $restart_docker =~ ^[Yy]$ ]]; then
            sudo systemctl stop docker
            sudo systemctl start docker
            print_success "Docker restarted with new data root"
        fi
    fi
}

# Main function
main() {
    print_header
    
    load_config
    configure_paths
    validate_paths
    create_directories
    save_config
    configure_docker
    show_summary
    
    echo ""
    print_success "✅ Installation configuration completed!"
    print_status "Configuration saved to: $(pwd)/$CONFIG_FILE"
}

# Run if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi 