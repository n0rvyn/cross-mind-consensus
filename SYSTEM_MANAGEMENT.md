# 🛠️ Cross-Mind Consensus System Management Guide

Complete guide for deploying, monitoring, and cleaning up your Cross-Mind Consensus system.

## 📋 Table of Contents

- [Quick Commands](#quick-commands)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Maintenance](#maintenance)
- [Cleanup](#cleanup)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Commands

### One-Line Operations
```bash
# Deploy everything
./smart-deploy.sh

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Complete cleanup
./smart-uninstall.sh

# Restart everything
docker-compose restart
```

---

## 🚀 Deployment

### Method 1: Smart Deployment (Recommended)
```bash
# Intelligent deployment with environment detection
./smart-deploy.sh
```

**What it does:**
- ✅ Detects your environment (local/cloud)
- ✅ Auto-configures SSL certificates
- ✅ Sets up monitoring stack
- ✅ Validates configuration
- ✅ Starts all services

### Method 2: Manual Deployment
```bash
# Step-by-step manual deployment
cp env.template .env
# Edit .env with your API keys
./generate-ssl.sh
docker-compose up -d --build
```

### Method 3: Development Setup
```bash
# Quick development setup
./auto-setup.sh
```

---

## 📊 Monitoring

### Service Status
```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose ps api
docker-compose ps dashboard
docker-compose ps redis
```

### Logs
```bash
# All services logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f api
docker-compose logs -f dashboard
docker-compose logs -f nginx

# Recent logs only
docker-compose logs --tail=50 api
```

### Health Checks
```bash
# API health
curl -k https://localhost/health

# Detailed health check
curl -k https://localhost/health/detailed

# Nginx status
curl -k https://localhost/nginx-health
```

### Monitoring Dashboards
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Main Dashboard**: https://localhost

---

## 🔧 Maintenance

### Regular Maintenance Tasks

#### Daily
```bash
# Check service health
docker-compose ps

# Review recent logs
docker-compose logs --tail=100 --since="24h"
```

#### Weekly
```bash
# Clean up old logs
find logs/ -name "*.log" -mtime +7 -delete

# Check disk usage
docker system df

# Update base images
docker-compose pull
```

#### Monthly
```bash
# Full system cleanup
docker system prune -a

# Review and rotate logs
docker-compose logs --since="30d" > monthly-logs.txt

# Check SSL certificate expiration
openssl x509 -in ssl/cert.pem -text -noout | grep "Not After"
```

### Performance Monitoring
```bash
# Check resource usage
docker stats

# Monitor API performance
curl -k https://localhost/analytics/performance

# Check cache hit rates
docker exec consensus-redis redis-cli info stats
```

### Backup Operations
```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz .env ssl/ nginx.conf

# Backup data volumes
docker run --rm -v cross-mind-consensus_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup-$(date +%Y%m%d).tar.gz /data

# Backup Grafana data
docker run --rm -v cross-mind-consensus_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup-$(date +%Y%m%d).tar.gz /data
```

---

## 🧹 Cleanup

### Smart Uninstall (Recommended)
```bash
# Complete system cleanup
./smart-uninstall.sh

# Aggressive cleanup (includes dangling images)
./smart-uninstall.sh --aggressive

# System-level cleanup (removes Docker, packages)
./smart-uninstall.sh --system
```

### Manual Cleanup Steps

#### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

#### Remove Containers
```bash
# Remove all project containers
docker ps -a --format "table {{.Names}}" | grep consensus | xargs docker rm -f
```

#### Remove Volumes
```bash
# Remove project volumes
docker volume rm cross-mind-consensus_redis_data
docker volume rm cross-mind-consensus_prometheus_data
docker volume rm cross-mind-consensus_grafana_data
```

#### Remove Images
```bash
# Remove project images
docker images | grep cross-mind-consensus | awk '{print $3}' | xargs docker rmi -f
```

#### Clean Up Files
```bash
# Remove SSL certificates
rm -rf ssl/

# Remove logs
rm -rf logs/

# Remove temporary files
find . -name "*.log" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

---

## 🔄 Common Operations

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart api
docker-compose restart dashboard

# Restart with rebuild
docker-compose up -d --build
```

### Update System
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or use the smart deploy
./smart-deploy.sh
```

### Scale Services
```bash
# Scale API service (if needed)
docker-compose up -d --scale api=3

# Scale dashboard
docker-compose up -d --scale dashboard=2
```

### Configuration Changes
```bash
# Edit configuration
nano .env

# Reload configuration
docker-compose restart

# Or restart specific service
docker-compose restart api
```

---

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs api

# Check configuration
docker-compose config

# Validate environment
cat .env | grep API_KEY
```

### SSL Certificate Issues
```bash
# Regenerate certificates
rm -rf ssl/
./generate-ssl.sh

# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s https://localhost/health

# Monitor Redis performance
docker exec consensus-redis redis-cli info memory
```

### Network Issues
```bash
# Check port conflicts
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Check Docker network
docker network ls
docker network inspect consensus-network
```

### Database/Redis Issues
```bash
# Check Redis connection
docker exec consensus-redis redis-cli ping

# Check Redis memory
docker exec consensus-redis redis-cli info memory

# Clear Redis cache
docker exec consensus-redis redis-cli flushall
```

---

## 📈 Performance Optimization

### Resource Limits
```yaml
# Add to docker-compose.yml for production
services:
  api:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### Caching Optimization
```bash
# Check cache hit rates
curl -k https://localhost/analytics/cache-stats

# Clear cache if needed
curl -X DELETE -k https://localhost/cache
```

### Monitoring Alerts
```bash
# Set up basic monitoring
# Add to your crontab:
# */5 * * * * curl -f https://localhost/health || echo "Service down" | mail -s "Alert" admin@example.com
```

---

## 🔒 Security Management

### SSL Certificate Renewal
```bash
# For Let's Encrypt certificates
docker-compose -f docker-compose.yml -f docker-compose.certbot.yml up certbot

# For self-signed certificates
./generate-ssl.sh
```

### API Key Rotation
```bash
# Update API keys in .env
nano .env

# Restart services
docker-compose restart api
```

### Security Audit
```bash
# Check for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image your-image:latest

# Check open ports
nmap localhost
```

---

## 📊 System Information

### Get System Status
```bash
# Complete system status
./system-status.sh

# Or manually:
echo "=== Docker Status ==="
docker-compose ps

echo "=== Resource Usage ==="
docker stats --no-stream

echo "=== Disk Usage ==="
df -h

echo "=== Memory Usage ==="
free -h
```

### Export Configuration
```bash
# Export current configuration
docker-compose config > docker-compose-exported.yml

# Export environment
env | grep -E "(REDIS|API|ENABLE)" > environment-export.txt
```

---

## 🎯 Best Practices

### Daily Operations
1. **Monitor service health** - Check `docker-compose ps` regularly
2. **Review logs** - Look for errors or warnings
3. **Check resource usage** - Monitor memory and CPU
4. **Verify SSL certificates** - Ensure they're not expiring soon

### Weekly Operations
1. **Clean up old logs** - Remove logs older than 7 days
2. **Update base images** - Pull latest security updates
3. **Review performance metrics** - Check Grafana dashboards
4. **Backup configuration** - Save important config files

### Monthly Operations
1. **Full system cleanup** - Remove unused Docker resources
2. **Security audit** - Check for vulnerabilities
3. **Performance review** - Analyze trends and optimize
4. **Documentation update** - Update runbooks and procedures

---

## 🆘 Emergency Procedures

### Service Down
```bash
# Quick restart
docker-compose restart

# Force restart with rebuild
docker-compose down && docker-compose up -d --build
```

### Data Loss Prevention
```bash
# Emergency backup
docker run --rm -v cross-mind-consensus_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/emergency-backup-$(date +%Y%m%d-%H%M%S).tar.gz /data
```

### Complete Recovery
```bash
# Stop everything
docker-compose down -v

# Clean slate
./smart-uninstall.sh

# Redeploy
./smart-deploy.sh
```

---

## 📞 Support Commands

### Diagnostic Information
```bash
# Collect diagnostic info
docker version > diagnostics.txt
docker-compose version >> diagnostics.txt
docker-compose ps >> diagnostics.txt
docker system df >> diagnostics.txt
free -h >> diagnostics.txt
df -h >> diagnostics.txt
```

### Log Collection
```bash
# Collect all logs
docker-compose logs > all-logs.txt

# Collect recent logs
docker-compose logs --since="1h" > recent-logs.txt
```

This management guide provides everything you need to deploy, monitor, maintain, and clean up your Cross-Mind Consensus system effectively! 🚀 