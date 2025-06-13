#!/bin/bash

# 🚀 Cross-Mind Consensus 部署脚本 (重构后版本)
# 适应新的目录结构

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║    🤖 Cross-Mind Consensus Deploy        ║"
    echo "║         重构后版本 v1.0                   ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

# 检查目录结构
check_directory_structure() {
    print_step "检查目录结构..."
    
    local required_dirs=(
        "src"
        "config/docker"
        "config/monitoring"
        "scripts/deployment"
        "backend"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            print_error "缺少目录: $dir"
            exit 1
        fi
    done
    
    print_success "目录结构检查通过"
}

# 检查必要文件
check_required_files() {
    print_step "检查必要文件..."
    
    local required_files=(
        "config/docker/docker-compose.yml"
        "config/docker/Dockerfile"
        "config/monitoring/prometheus.yml"
        ".env"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "缺少文件: $file"
            exit 1
        fi
    done
    
    print_success "必要文件检查通过"
}

# 停止现有服务
stop_services() {
    print_step "停止现有服务..."
    
    cd config/docker
    if docker-compose ps -q | grep -q .; then
        docker-compose down
        print_success "服务已停止"
    else
        print_info "没有运行的服务"
    fi
    cd ../..
}

# 构建和启动服务
start_services() {
    print_step "构建和启动服务..."
    
    cd config/docker
    
    # 构建镜像
    print_info "构建Docker镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    print_info "启动服务..."
    docker-compose up -d
    
    cd ../..
    print_success "服务启动完成"
}

# 健康检查
health_check() {
    print_step "执行健康检查..."
    
    local services=("redis" "api" "dashboard" "nginx" "prometheus" "grafana")
    local max_wait=60
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        local all_healthy=true
        
        for service in "${services[@]}"; do
            if ! docker-compose -f config/docker/docker-compose.yml ps "$service" | grep -q "Up"; then
                all_healthy=false
                break
            fi
        done
        
        if [ "$all_healthy" = true ]; then
            print_success "所有服务健康检查通过"
            return 0
        fi
        
        print_info "等待服务启动... ($wait_time/$max_wait 秒)"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    
    print_error "健康检查超时"
    return 1
}

# 显示服务信息
show_service_info() {
    print_step "服务信息"
    echo ""
    echo -e "${GREEN}🎉 部署完成！服务访问地址：${NC}"
    echo ""
    echo "📊 主仪表板:     http://localhost"
    echo "🔧 API文档:      http://localhost:8000/docs"
    echo "❤️  健康检查:     http://localhost:8000/health"
    echo "📈 Grafana:      http://localhost:3000 (admin/admin123)"
    echo "📊 Prometheus:   http://localhost:9090"
    echo ""
    echo -e "${YELLOW}💡 提示：${NC}"
    echo "- 查看日志: docker-compose -f config/docker/docker-compose.yml logs -f"
    echo "- 停止服务: docker-compose -f config/docker/docker-compose.yml down"
    echo "- 重启服务: docker-compose -f config/docker/docker-compose.yml restart"
    echo ""
}

# 主函数
main() {
    print_banner
    
    check_directory_structure
    check_required_files
    stop_services
    start_services
    
    if health_check; then
        show_service_info
    else
        print_error "部署失败，请检查日志"
        docker-compose -f config/docker/docker-compose.yml logs
        exit 1
    fi
}

# 运行主函数
main "$@" 