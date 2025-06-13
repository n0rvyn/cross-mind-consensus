# 🖥️ Cross-Mind Consensus 服务器要求指南

## 📋 概述

Cross-Mind Consensus是一个先进的多LLM共识验证系统，本文档提供详细的服务器硬件要求、部署配置和性能优化建议。

## ⚡ 最低配置要求

### **绝对最低配置** (单用户/开发环境)
```
💻 CPU: 2 核心 (2.0+ GHz)
🧠 内存: 4GB RAM
💾 存储: 20GB 可用空间
🌐 网络: 10Mbps 稳定连接
🐧 操作系统: Ubuntu 20.04+, Windows 10+, macOS 11+
```

### **推荐生产配置** (10-50并发用户)
```
💻 CPU: 4 核心 (2.5+ GHz) 
🧠 内存: 8GB RAM
💾 存储: 50GB SSD
🌐 网络: 100Mbps 带宽
🐧 操作系统: Ubuntu 22.04 LTS
```

### **高性能配置** (100+并发用户)
```
💻 CPU: 8+ 核心 (3.0+ GHz)
🧠 内存: 16GB+ RAM  
💾 存储: 100GB+ NVMe SSD
🌐 网络: 1Gbps 带宽
🐧 操作系统: Ubuntu 22.04 LTS + Docker
```

## 📊 资源需求详解

### **内存需求分解**
- **🤖 Sentence Transformer模型**: ~800MB-1.2GB
- **⚡ FastAPI后端**: ~300-600MB
- **📊 Streamlit仪表板**: ~200-400MB  
- **🔄 Redis缓存**: ~100MB-2GB (可配置)
- **📈 分析数据**: ~100-500MB
- **🔧 系统开销**: ~500MB-1GB
- **📦 总计**: 最少4GB，推荐8GB+

### **存储空间分解**
- **📦 应用代码**: ~100MB
- **🐍 Python依赖**: ~2.5GB
- **🐳 Docker镜像**: ~1.5GB
- **📝 日志文件**: ~1-10GB (可配置轮转)
- **💾 模型缓存**: ~500MB-2GB
- **⚙️ 系统空间**: ~10GB
- **📦 总计**: 最少20GB，推荐50GB+

### **CPU需求分析**
- **单核性能**: 重要，影响单请求响应时间
- **多核并发**: 支持多用户同时访问
- **推荐配置**: CPU核心数 × 2 = Worker进程数

### **网络需求**
- **LLM API调用**: 需要稳定的互联网连接
- **用户请求**: 每个请求 ~1-50KB
- **实时WebSocket**: 最小延迟要求
- **带宽计算**: 并发用户数 × 平均请求大小 × 安全系数

## 🐳 部署方式对比

### **1. 轻量级部署** (最小资源)
```bash
# 仅API服务，无缓存
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
**要求**: 2核/3GB/15GB

### **2. 标准部署** (推荐)
```bash
# API + Dashboard + Redis缓存
docker-compose up api dashboard redis
```
**要求**: 4核/6GB/30GB

### **3. 完整部署** (生产环境)
```bash
# 全套监控 + 负载均衡
docker-compose up
```
**要求**: 8核/12GB/60GB

## 🌟 云平台推荐配置

### **阿里云 ECS**
| 配置类型 | 实例规格 | vCPU | 内存 | 存储 | 月费用 |
|---------|---------|------|------|------|--------|
| 最小 | ecs.t6-c2m4.large | 2核 | 4GB | 40GB | ~¥180 |
| 推荐 | ecs.c6.xlarge | 4核 | 8GB | 60GB | ~¥450 |
| 高性能 | ecs.c6.2xlarge | 8核 | 16GB | 120GB | ~¥900 |

### **腾讯云 CVM**
| 配置类型 | 实例规格 | vCPU | 内存 | 存储 | 月费用 |
|---------|---------|------|------|------|--------|
| 最小 | S5.MEDIUM4 | 2核 | 4GB | 40GB | ~¥160 |
| 推荐 | S5.LARGE8 | 4核 | 8GB | 60GB | ~¥400 |
| 高性能 | S5.2XLARGE16 | 8核 | 16GB | 120GB | ~¥800 |

### **AWS EC2**
| 配置类型 | 实例类型 | vCPU | 内存 | 存储 | 月费用(USD) |
|---------|---------|------|------|------|------------|
| 最小 | t3.medium | 2核 | 4GB | 30GB | ~$30 |
| 推荐 | t3.large | 2核 | 8GB | 60GB | ~$60 |
| 高性能 | c5.2xlarge | 8核 | 16GB | 120GB | ~$250 |

### **Google Cloud Platform**
| 配置类型 | 机器类型 | vCPU | 内存 | 存储 | 月费用(USD) |
|---------|---------|------|------|------|------------|
| 最小 | e2-medium | 2核 | 4GB | 30GB | ~$25 |
| 推荐 | e2-standard-4 | 4核 | 16GB | 60GB | ~$120 |
| 高性能 | c2-standard-8 | 8核 | 32GB | 120GB | ~$280 |

## ⚡ 性能优化配置

### **内存优化**
```bash
# Redis内存限制配置
CONFIG SET maxmemory 1gb
CONFIG SET maxmemory-policy allkeys-lru

# Python内存优化
export PYTHONHASHSEED=0
export MALLOC_TRIM_THRESHOLD_=100000

# 系统内存优化
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
```

### **CPU优化配置**
```bash
# Gunicorn worker配置
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

### **磁盘I/O优化**
```bash
# 使用SSD并启用trim
echo 'SCHEDULER="deadline"' >> /etc/default/grub

# 优化文件系统
mount -o noatime,nodiratime /dev/sda1 /

# 日志轮转配置
/app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
}
```

### **网络优化**
```bash
# TCP优化
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf
```

## 🔧 组件资源配置

### **FastAPI应用配置**
```python
# uvicorn配置
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    workers=4,  # CPU核心数
    access_log=False,  # 生产环境关闭访问日志
    log_level="info"
)
```

### **Redis配置**
```conf
# redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### **Nginx配置**
```nginx
worker_processes auto;
worker_connections 1024;

upstream api_backend {
    server api:8000;
}

server {
    listen 80;
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📈 负载测试基准

### **性能指标目标**
- **响应时间**: < 2秒 (95%的请求)
- **并发用户**: 50+ (推荐配置)
- **吞吐量**: 100+ 请求/分钟
- **可用性**: 99.9%+

### **负载测试命令**
```bash
# 使用Locust进行负载测试
locust -f tests/performance/locustfile.py \
    --headless \
    -u 50 \
    -r 5 \
    -t 300s \
    --host=http://localhost:8000

# 使用ab进行简单测试
ab -n 1000 -c 10 http://localhost:8000/health
```

## 📋 部署检查清单

### **基础环境检查**
- [ ] 操作系统版本 (Ubuntu 20.04+)
- [ ] Docker版本 (20.10+)
- [ ] Docker Compose版本 (2.0+)
- [ ] Python版本 (3.11+)
- [ ] 可用存储空间 (>20GB)
- [ ] 网络连通性测试

### **安全配置检查**
- [ ] 防火墙配置
- [ ] SSL证书安装
- [ ] API密钥配置
- [ ] 用户权限设置
- [ ] 日志审计启用

### **监控配置检查**
- [ ] Prometheus配置
- [ ] Grafana仪表板
- [ ] 日志聚合
- [ ] 告警规则设置
- [ ] 健康检查端点

### **备份策略检查**
- [ ] 数据库备份
- [ ] 配置文件备份
- [ ] 日志备份
- [ ] 恢复测试

## 💡 成本效益分析

### **开发阶段** (1-2开发者)
- **配置**: 2核/4GB/20GB
- **月成本**: ¥150-200
- **适用场景**: 开发、测试、演示

### **小规模生产** (10-50用户)
- **配置**: 4核/8GB/50GB
- **月成本**: ¥400-500
- **适用场景**: 初创公司、小团队

### **大规模生产** (100+用户)
- **配置**: 8核/16GB/100GB + 负载均衡
- **月成本**: ¥800-1200
- **适用场景**: 企业级应用

### **成本优化建议**
1. **按需扩展**: 从小配置开始，根据使用量逐步升级
2. **预留实例**: 长期使用可购买预留实例节省成本
3. **监控优化**: 使用云平台监控工具优化资源使用
4. **缓存策略**: 合理配置Redis减少API调用成本

## 🚀 快速部署指南

### **最小部署** (5分钟)
```bash
git clone https://github.com/your-repo/cross-mind-consensus.git
cd cross-mind-consensus
cp env.template .env
# 编辑 .env 文件添加API密钥
docker-compose up api redis
```

### **生产部署** (30分钟)
```bash
# 1. 克隆代码
git clone https://github.com/your-repo/cross-mind-consensus.git
cd cross-mind-consensus

# 2. 配置环境
cp env.template .env
# 编辑配置文件

# 3. 启动完整服务
docker-compose up -d

# 4. 验证部署
curl http://localhost:8000/health
```

## 📞 技术支持

如果您在部署过程中遇到问题，请参考：

- **文档**: `/docs` 目录下的详细文档
- **日志**: `docker-compose logs` 查看服务日志
- **健康检查**: `curl http://localhost:8000/health`
- **监控**: 访问 `http://localhost:3000` (Grafana)

---

**最后更新**: 2024年6月
**版本**: v2.0.0
**维护者**: Cross-Mind Consensus Team 