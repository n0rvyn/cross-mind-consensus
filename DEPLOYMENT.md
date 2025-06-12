# 🚀 Cross-Mind Consensus Deployment Guide

Complete deployment instructions for development and production environments.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Manual Deployment](#manual-deployment)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### One-Command Development Setup
```bash
# Clone and deploy in one go
git clone <repository-url>
cd cross-mind-consensus
./auto-setup.sh
```

### One-Command Production Setup
```bash
# Intelligent production deployment
./smart-deploy.sh
```

---

## 🛠️ Development Deployment

### Prerequisites
- Docker & Docker Compose
- OpenSSL (usually pre-installed)
- At least 4GB RAM available

### Method 1: Automatic Setup (Recommended)

```bash
# 1. Navigate to project directory
cd cross-mind-consensus

# 2. Run automatic setup
./auto-setup.sh

# 3. Access your services
# • Dashboard: https://localhost
# • API: https://localhost/docs
# • Grafana: http://localhost:3000 (admin/admin123)
```

**What `auto-setup.sh` does:**
- ✅ Checks prerequisites (Docker, Docker Compose, OpenSSL)
- ✅ Creates `.env` from template
- ✅ Generates self-signed SSL certificates
- ✅ Configures Nginx for HTTPS
- ✅ Builds and starts all services
- ✅ Monitors service health
- ✅ Displays service URLs

### Method 2: Manual Development Setup

```bash
# 1. Setup environment
cp env.template .env

# 2. Edit .env file with your API keys
nano .env  # Add your OPENAI_API_KEY at minimum

# 3. Generate SSL certificates
./generate-ssl.sh

# 4. Start services
docker-compose up -d --build

# 5. Check status
docker-compose ps
```

### Development Configuration

**Required API Keys in `.env` file:**
```env
# Minimum required
OPENAI_API_KEY=sk-your-openai-key-here

# Optional for enhanced functionality
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
COHERE_API_KEY=your-cohere-key
```

**Development URLs:**
- **Main Dashboard**: https://localhost
- **API Documentation**: https://localhost/docs
- **API Health Check**: https://localhost/health  
- **Grafana Monitoring**: http://localhost:3000
- **Prometheus Metrics**: http://localhost:9090

---

## 🌐 Production Deployment

### Prerequisites
- Linux server (Ubuntu/Debian recommended)
- Docker & Docker Compose
- Domain name pointed to your server
- Email address for SSL certificates
- 8GB+ RAM recommended

### Method 1: Smart Deployment (Recommended)

```bash
# 1. Clone repository on your server
git clone <repository-url>
cd cross-mind-consensus

# 2. Run smart deployment
./smart-deploy.sh

# 3. Follow interactive prompts:
#    - Choose domain configuration
#    - Enter Let's Encrypt email
#    - Configure API keys
```

**Smart Deploy Features:**
- 🤖 **Auto-detects environment** (AWS, GCP, Azure, etc.)
- 🌐 **Smart domain configuration** (auto-detects public IPs)
- 🔒 **Let's Encrypt SSL** (free, automatic renewal)
- 📦 **Auto-installs prerequisites** (on supported systems)
- 📊 **Advanced monitoring** and health checks

### Method 2: Manual Production Setup

#### Step 1: Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Logout and login again for Docker group
```

#### Step 2: SSL Certificate Setup

**Option A: Let's Encrypt (Recommended)**
```bash
# Setup Let's Encrypt
./setup-letsencrypt.sh yourdomain.com your-email@example.com

# Get certificate
docker-compose -f docker-compose.yml -f docker-compose.certbot.yml up certbot

# Use Let's Encrypt nginx config
cp nginx-letsencrypt.conf nginx.conf
```

**Option B: Self-Signed Certificate**
```bash
# Generate self-signed certificate
./generate-ssl.sh
```

#### Step 3: Environment Configuration
```bash
# Setup environment
cp env.template .env

# Configure for production
nano .env
```

**Production `.env` example:**
```env
# Production API Keys
OPENAI_API_KEY=sk-your-production-openai-key
ANTHROPIC_API_KEY=sk-ant-your-production-anthropic-key
COHERE_API_KEY=your-production-cohere-key

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
ENABLE_CACHING=true

# Security Settings
ENABLE_RATE_LIMITING=true
ENABLE_ANALYTICS=true
BACKEND_API_KEYS=your-secure-api-key-1,your-secure-api-key-2
```

#### Step 4: Deploy Services
```bash
# Start production services
docker-compose up -d --build

# Monitor startup
docker-compose logs -f
```

### Production Security Checklist

- [ ] **Firewall configured** (only ports 80, 443, 22 open)
- [ ] **SSL certificates** properly configured
- [ ] **API keys** in production `.env` file
- [ ] **Backend API keys** configured for authentication
- [ ] **Rate limiting** enabled
- [ ] **Regular backups** scheduled
- [ ] **Monitoring** alerts configured

---

## 📖 Manual Deployment

If you prefer full control over the deployment process:

### Prerequisites Check
```bash
# Check Docker
docker --version
docker-compose --version

# Check system resources
free -h  # At least 4GB RAM recommended
df -h    # At least 10GB disk space
```

### Step-by-Step Manual Process

1. **Environment Setup**
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

2. **SSL Certificate Generation**
   ```bash
   mkdir -p ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/key.pem -out ssl/cert.pem \
     -subj "/C=US/ST=State/L=City/O=Org/CN=localhost"
   ```

3. **Nginx Configuration**
   ```bash
   # Verify nginx.conf exists and is properly configured
   cat nginx.conf
   ```

4. **Service Deployment**
   ```bash
   # Stop any existing services
   docker-compose down
   
   # Build and start services
   docker-compose up -d --build
   
   # Monitor startup
   docker-compose ps
   docker-compose logs -f
   ```

---

## 🎯 Post-Deployment

### Verify Deployment
```bash
# Check service status
docker-compose ps

# Test API endpoints
curl -k https://localhost/health
curl -k https://localhost/docs

# Check logs
docker-compose logs api
docker-compose logs dashboard
```

### Access Services
- **Main Application**: https://your-domain.com
- **API Documentation**: https://your-domain.com/docs
- **Grafana Dashboard**: http://your-domain.com:3000
- **Prometheus Metrics**: http://your-domain.com:9090

### Management Commands
```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update and restart
git pull
docker-compose up -d --build
```

---

## 🔧 Troubleshooting

### Common Issues

#### SSL Certificate Errors
```bash
# Regenerate certificates
rm -rf ssl/
./generate-ssl.sh

# Or for production
./setup-letsencrypt.sh yourdomain.com your-email@example.com
```

#### Services Not Starting
```bash
# Check logs
docker-compose logs

# Check system resources
docker system df
free -h

# Restart services
docker-compose down
docker-compose up -d --build
```

#### API Key Issues
```bash
# Verify .env file
cat .env | grep API_KEY

# Test API connection
curl -k https://localhost/health
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Stop conflicting services
sudo systemctl stop apache2  # If Apache is running
sudo systemctl stop nginx    # If system Nginx is running
```

### Health Checks
```bash
# API Health
curl -k https://localhost/health

# Service Status
docker-compose ps

# Resource Usage
docker stats

# Logs
docker-compose logs -f --tail=50
```

### Performance Optimization
```bash
# Clean up Docker
docker system prune -a

# Monitor resource usage
htop
docker stats

# Check service performance
curl -k https://localhost/analytics/performance
```

---

## 📞 Support

### Log Collection
```bash
# Collect all logs
docker-compose logs > deployment-logs.txt

# System information
docker version > system-info.txt
docker-compose version >> system-info.txt
```

### Backup Important Files
```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz .env ssl/ nginx.conf
```

---

## 🎉 Quick Reference

### Development
```bash
./auto-setup.sh                    # One-command setup
https://localhost                   # Access dashboard
docker-compose logs -f             # View logs
```

### Production  
```bash
./smart-deploy.sh                  # Intelligent deployment
https://yourdomain.com             # Access application
docker-compose ps                  # Check status
```

### Management
```bash
docker-compose down                # Stop services
docker-compose up -d --build      # Start/restart services
docker-compose logs -f [service]   # View specific logs
``` 