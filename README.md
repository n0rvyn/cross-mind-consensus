# 🤖 Cross-Mind Consensus

**Enterprise-grade Multi-LLM Consensus Platform** - 整合多个大语言模型的智能共识系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 🌟 项目特色

Cross-Mind Consensus 是一个企业级的多LLM共识平台，通过整合多个顶级大语言模型的响应，提供更准确、更可靠的AI决策支持。

### 🎯 核心功能

- **多模型整合**: 支持 GPT-4, Claude, Cohere, Google Gemini, Baidu, Moonshot, Zhipu 等主流模型
- **智能共识算法**: 先进的响应聚合和质量评估机制
- **企业级架构**: FastAPI + Streamlit + Redis + Nginx + 监控系统
- **完整监控**: Prometheus + Grafana 实时监控和告警
- **容器化部署**: Docker Compose 一键部署
- **SSL支持**: 自动HTTPS配置
- **智能部署**: 环境自适应部署脚本

## 📁 项目结构 (重构后)

```
cross-mind-consensus/
├── README.md                           # 项目说明
├── LICENSE                            # 开源协议
├── .env                               # 环境配置
├── requirements.txt                   # Python依赖
├── deploy.sh                          # 🚀 快速部署脚本
├── health-check.sh                    # 🏥 健康检查脚本
│
├── src/                               # 📦 应用源代码
│   ├── config.py                      # 配置模块
│   ├── dashboard.py                   # 主仪表板
│   ├── streamlit_dashboard.py         # Streamlit界面
│   ├── run.py                        # 应用启动器
│   └── test_system.py                # 系统测试
│
├── backend/                           # 🔧 后端API
│   └── main.py                       # FastAPI应用
│
├── config/                           # ⚙️ 配置文件
│   ├── docker/                       # Docker配置
│   │   ├── docker-compose.yml        # 主要编排文件
│   │   ├── docker-compose.simple.yml # 简化版本
│   │   └── Dockerfile               # 镜像构建文件
│   ├── monitoring/                   # 监控配置
│   │   ├── prometheus.yml           # Prometheus配置
│   │   └── grafana/                 # Grafana配置
│   │       ├── dashboards/          # 仪表板定义
│   │       └── datasources/         # 数据源配置
│   │           └── prometheus.yml   # Grafana数据源
│   ├── nginx/                       # Nginx配置
│   │   └── nginx.conf              # 反向代理配置
│   ├── gpt/                        # GPT相关配置
│   │   ├── gpt_actions.yaml        # GPT Actions定义
│   │   └── gpt_config/             # GPT配置文件
│   ├── env.template                # 环境变量模板
│   ├── production.env              # 生产环境配置
│   └── demo-config.conf            # 演示配置
│
├── scripts/                          # 🛠️ 部署和管理脚本
│   ├── deployment/                   # 部署脚本
│   │   ├── auto-setup.sh            # 自动安装脚本
│   │   ├── smart-deploy.sh          # 智能部署脚本
│   │   ├── smart-uninstall.sh       # 卸载脚本
│   │   ├── quick-setup.sh           # 快速安装
│   │   └── install-config.sh        # 安装配置工具
│   ├── ssl/                         # SSL脚本
│   │   ├── generate-ssl.sh          # SSL证书生成
│   │   └── setup-letsencrypt.sh     # Let's Encrypt配置
│   └── utilities/                   # 工具脚本
│       └── get-docker.sh           # Docker安装脚本
│
├── docs/                            # 📚 文档目录
│   ├── deployment/                  # 部署文档
│   │   ├── DEPLOYMENT.md           # 部署指南
│   │   ├── INSTALLATION_PATHS.md   # 安装路径配置
│   │   └── SERVER_REQUIREMENTS.md  # 服务器要求
│   ├── development/                 # 开发文档
│   ├── maintenance/                 # 维护文档
│   ├── features/                   # 功能文档
│   └── community/                  # 社区文档
│
├── data/                           # 📊 运行时数据
│   ├── grafana/                    # Grafana数据
│   ├── prometheus/                 # Prometheus数据
│   ├── redis/                      # Redis数据
│   └── logs/                       # 应用日志
│
└── tests/                          # 🧪 测试文件
    └── performance/                # 性能测试
```

## 🚀 快速开始

### 方法一：一键部署 (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/cross-mind-consensus.git
cd cross-mind-consensus

# 2. 配置环境变量 (至少需要一个API密钥)
cp config/env.template .env
# 编辑 .env 文件，添加你的API密钥

# 3. 一键部署
./deploy.sh
```

### 方法二：传统部署

```bash
# 1. 进入Docker配置目录
cd config/docker

# 2. 构建和启动服务
docker-compose build
docker-compose up -d

# 3. 检查服务状态
docker-compose ps
```

## 🏥 健康检查

```bash
# 运行完整的健康检查
./health-check.sh

# 或者手动检查各个服务
curl http://localhost:8000/health    # API健康检查
curl http://localhost:8501           # Streamlit仪表板
curl http://localhost:3000           # Grafana
curl http://localhost:9090           # Prometheus
```

## 🌐 服务访问

部署成功后，可以通过以下地址访问各个服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🏠 主仪表板 | http://localhost | Nginx反向代理入口 |
| 🔧 API文档 | http://localhost:8000/docs | FastAPI自动生成的API文档 |
| ❤️ 健康检查 | http://localhost:8000/health | API健康状态检查 |
| 📊 Streamlit | http://localhost:8501 | 交互式数据仪表板 |
| 📈 Grafana | http://localhost:3000 | 监控仪表板 (admin/admin123) |
| 📊 Prometheus | http://localhost:9090 | 指标收集和查询 |

## 🛠️ 管理命令

```bash
# 查看服务状态
docker-compose -f config/docker/docker-compose.yml ps

# 查看服务日志
docker-compose -f config/docker/docker-compose.yml logs -f [service_name]

# 重启特定服务
docker-compose -f config/docker/docker-compose.yml restart [service_name]

# 停止所有服务
docker-compose -f config/docker/docker-compose.yml down

# 重新构建并启动
docker-compose -f config/docker/docker-compose.yml up -d --build
```

## ⚙️ 配置说明

### API密钥配置

在 `.env` 文件中配置至少一个LLM提供商的API密钥：

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key

# Cohere
COHERE_API_KEY=your_cohere_key

# Google
GOOGLE_API_KEY=your_google_key

# 其他配置...
```

**注意**: 你只需要配置至少一个API密钥即可开始使用，不需要全部配置。

### 自定义安装路径

如果你想自定义安装路径，可以使用：

```bash
# 交互式配置安装路径
./scripts/deployment/install-config.sh

# 使用预定义配置
./scripts/deployment/smart-deploy.sh --use-config
```

## 📊 监控和告警

系统内置了完整的监控解决方案：

- **Prometheus**: 指标收集和存储
- **Grafana**: 可视化仪表板和告警
- **健康检查**: 自动化服务状态监控

访问 Grafana (http://localhost:3000) 查看：
- 系统性能指标
- API响应时间
- 错误率统计
- 资源使用情况

## 🔧 故障排除

### 常见问题

1. **端口冲突**: 确保端口 80, 443, 3000, 6379, 8000, 8501, 9090 未被占用
2. **权限问题**: 确保Docker有足够权限访问项目目录
3. **磁盘空间**: 确保有足够的磁盘空间 (建议至少10GB)
4. **API密钥**: 确保至少配置了一个有效的LLM API密钥

### 日志查看

```bash
# 查看所有服务日志
docker-compose -f config/docker/docker-compose.yml logs

# 查看特定服务日志
docker-compose -f config/docker/docker-compose.yml logs api
docker-compose -f config/docker/docker-compose.yml logs dashboard
```

## 🤝 贡献指南

我们欢迎社区贡献！请查看 [docs/community/CONTRIBUTING.md](docs/community/CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

- 📖 查看 [docs/](docs/) 目录获取详细文档
- 🐛 提交 Issue 报告问题
- 💬 参与 Discussions 讨论

---

**🎉 享受使用 Cross-Mind Consensus！** 