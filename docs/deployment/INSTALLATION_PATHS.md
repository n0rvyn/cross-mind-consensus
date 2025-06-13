# 🎯 User-Defined Installation Paths

Cross-Mind Consensus now supports **full user control** over where everything gets installed, addressing the common issue of packages being installed in system-wide directories without user control.

## 🚨 The Problem We Solved

**Before:** 
- Docker volumes went to `/var/lib/docker/volumes/` (system location)
- Python packages installed inside containers (not persistent/controllable)
- No control over data storage locations
- Fixed installation paths
- Space issues on root filesystem

**Now:**
- ✅ User defines ALL installation locations
- ✅ Persistent data on user-chosen disks
- ✅ Configurable Docker data root
- ✅ Complete control over package installation
- ✅ Support for mounted disks and custom paths

---

## 📁 Installation Architecture Overview

### Current System Components & Their Locations:

| Component | Current Location | User-Configurable Location |
|-----------|------------------|----------------------------|
| **Project Files** | `~/cross-mind-consensus` | `$INSTALL_DIR` |
| **Docker Data** | `/var/lib/docker/` | `$DOCKER_ROOT` |
| **Application Data** | Docker volumes | `$DATA_DIR/{redis,grafana,prometheus}` |
| **Logs** | Mixed locations | `$LOGS_DIR/{api,dashboard,nginx}` |
| **SSL Certificates** | `./ssl/` | `$CONFIG_DIR/ssl/` |
| **Cache** | System temp | `$CACHE_DIR/{pip,docker-build}` |
| **Python Packages** | Container temp | `$CACHE_DIR/pip` (persistent) |

---

## 🚀 Quick Start: Using Mounted Data Disk

Perfect for your use case with the mounted disk at `/home/norvyn/data`:

### Option 1: Interactive Configuration
```bash
# Configure installation paths interactively
./install-config.sh

# Follow prompts to set:
# - Installation: /home/norvyn/data/cross-mind-consensus
# - Data Storage: /home/norvyn/data/cross-mind-consensus/data  
# - Docker Root: /home/norvyn/data/docker
# - Etc.

# Deploy with custom configuration
./smart-deploy.sh --use-config
```

### Option 2: Pre-configured Setup
```bash
# Use the demo configuration (already set for your data disk)
cp demo-config.conf install-paths.conf

# Deploy immediately
./smart-deploy.sh --use-config
```

### Option 3: Manual Configuration
```bash
# Create your own config
cat > install-paths.conf << 'EOF'
INSTALL_DIR="/home/norvyn/data/cross-mind-consensus"
DATA_DIR="/home/norvyn/data/cross-mind-consensus/data"
LOGS_DIR="/home/norvyn/data/cross-mind-consensus/logs"
CONFIG_DIR="/home/norvyn/data/cross-mind-consensus/config"
CACHE_DIR="/home/norvyn/data/cross-mind-consensus/cache"
DOCKER_ROOT="/home/norvyn/data/docker"
USE_CUSTOM_DOCKER_ROOT=true
EOF

# Load configuration and deploy
source install-paths.conf
./smart-deploy.sh --use-config
```

---

## 📊 Benefits of User-Defined Paths

### 🎯 **Space Management**
- Use your 48GB mounted disk instead of 9.7GB root filesystem
- No more "no space left" errors during Docker builds
- Separate fast/slow storage as needed

### 🔒 **Security & Isolation**
- Keep all data in user-controlled locations
- No system-wide installations required
- Easy backup/restore of specific directories

### 📈 **Performance**
- Put data on faster disks
- Separate logs from data storage
- Configure cache on appropriate storage

### 🛠️ **Management**
- Easy cleanup: just remove the configured directories
- Clear separation of different data types
- Portable configurations across environments

---

## 🗂️ Directory Structure Created

When you use user-defined paths, this structure is created:

```
$INSTALL_DIR/                           # Main installation
├── backend/                            # Application code
├── ssl/                               # SSL certificates  
├── docker-compose.yml                 # Container config
└── install-paths.conf                 # Your configuration

$DATA_DIR/                             # Persistent data
├── redis/                             # Redis database
├── grafana/                           # Grafana dashboards  
└── prometheus/                        # Metrics storage

$LOGS_DIR/                             # Application logs
├── api/                               # API service logs
├── dashboard/                         # Dashboard logs
└── nginx/                             # Web server logs

$CONFIG_DIR/                           # Configuration
├── ssl/                               # SSL certificates
└── nginx/                             # Nginx configs

$CACHE_DIR/                            # Cache & temporary
├── pip/                               # Python packages cache
└── docker-build/                      # Docker build cache

$DOCKER_ROOT/                          # Docker system data
├── containers/                        # Container data
├── images/                            # Docker images
└── volumes/                           # Docker volumes
```

---

## ⚡ Advanced Features

### Custom Docker Data Root
Move Docker's data directory to your mounted disk:
```bash
# This moves ALL Docker data (images, containers, volumes)
DOCKER_ROOT="/home/norvyn/data/docker"
USE_CUSTOM_DOCKER_ROOT=true
```

**Benefits:**
- Docker builds use your data disk space
- Container storage on faster/larger disk
- Easy Docker data backup

### Persistent Python Package Cache
```bash
# Packages downloaded once, cached forever
PIP_CACHE_DIR="/home/norvyn/data/cross-mind-consensus/cache/pip"

# In Docker containers:
pip install --cache-dir $PIP_CACHE_DIR package_name
```

### Separate Log Management
```bash
# Different log retention policies per service
LOGS_DIR="/home/norvyn/data/cross-mind-consensus/logs"

# Structured logging:
# - API logs: JSON format for analysis
# - Nginx logs: Web access patterns
# - Application logs: Debug information
```

---

## 🔧 Installation Commands Summary

| Task | Command |
|------|---------|
| **Configure paths interactively** | `./install-config.sh` |
| **Use pre-made config** | `cp demo-config.conf install-paths.conf` |
| **Deploy with custom paths** | `./smart-deploy.sh --use-config` |
| **Deploy normally** | `./smart-deploy.sh` |
| **Quick setup (no config)** | `./quick-setup.sh` |
| **View current config** | `cat install-paths.conf` |
| **Clean up everything** | `./smart-uninstall.sh` |

---

## 💡 Examples for Common Scenarios

### 1. **Mounted Data Disk** (Your Scenario)
```bash
# Everything on the 48GB mounted disk
INSTALL_DIR="/home/norvyn/data/cross-mind-consensus"
DATA_DIR="/home/norvyn/data/cross-mind-consensus/data"
DOCKER_ROOT="/home/norvyn/data/docker"
```

### 2. **Network Storage**
```bash
# Using NFS or shared storage
INSTALL_DIR="/mnt/shared/cross-mind-consensus"
DATA_DIR="/mnt/shared/data"
LOGS_DIR="/mnt/shared/logs"
```

### 3. **Development Environment**
```bash
# Local development with custom paths
INSTALL_DIR="$HOME/projects/cross-mind-consensus"
DATA_DIR="$HOME/data/cross-mind"
CACHE_DIR="/tmp/cross-mind-cache"
```

### 4. **Production Server**
```bash
# Enterprise production setup
INSTALL_DIR="/opt/cross-mind-consensus"
DATA_DIR="/var/lib/cross-mind/data"
LOGS_DIR="/var/log/cross-mind"
CONFIG_DIR="/etc/cross-mind"
```

---

## 🎯 Next Steps

1. **Choose your installation approach:**
   - Interactive: `./install-config.sh`
   - Pre-configured: `cp demo-config.conf install-paths.conf`
   - Quick: `./quick-setup.sh`

2. **Deploy the system:**
   ```bash
   ./smart-deploy.sh --use-config
   ```

3. **Verify your installation:**
   ```bash
   df -h $DATA_DIR  # Check disk usage
   ls -la $INSTALL_DIR  # Verify structure
   docker info | grep "Docker Root Dir"  # Check Docker location
   ```

This gives you **complete control** over where everything gets installed, solving the space and control issues you identified! 🚀 