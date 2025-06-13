#!/bin/bash

# 🏥 Cross-Mind Consensus 健康检查脚本 (重构后版本)

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
    echo "║    🏥 Cross-Mind Consensus Health Check  ║"
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

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

# 检查Docker服务状态
check_docker_services() {
    print_step "检查Docker服务状态..."
    
    cd config/docker
    
    local services=("redis" "api" "dashboard" "nginx" "prometheus" "grafana")
    local all_running=true
    
    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "Up"; then
            print_success "$service: 运行中"
        else
            print_error "$service: 未运行"
            all_running=false
        fi
    done
    
    cd ../..
    
    if [ "$all_running" = true ]; then
        print_success "所有Docker服务正常运行"
        return 0
    else
        print_error "部分Docker服务未运行"
        return 1
    fi
}

# 检查服务端点
check_service_endpoints() {
    print_step "检查服务端点..."
    
    local endpoints=(
        "http://localhost:8000/health|API健康检查"
        "http://localhost:8000/docs|API文档"
        "http://localhost:8501|Streamlit仪表板"
        "http://localhost:3000|Grafana"
        "http://localhost:9090|Prometheus"
        "http://localhost:6379|Redis"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        local url=$(echo "$endpoint_info" | cut -d'|' -f1)
        local name=$(echo "$endpoint_info" | cut -d'|' -f2)
        
        if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
            print_success "$name: 可访问"
        else
            print_warning "$name: 无法访问 ($url)"
        fi
    done
}

# 检查日志错误
check_logs() {
    print_step "检查最近的错误日志..."
    
    cd config/docker
    
    local services=("api" "dashboard")
    local has_errors=false
    
    for service in "${services[@]}"; do
        local error_count=$(docker-compose logs --tail=50 "$service" 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)
        
        if [ "$error_count" -gt 0 ]; then
            print_warning "$service: 发现 $error_count 个错误日志条目"
            has_errors=true
        else
            print_success "$service: 无错误日志"
        fi
    done
    
    cd ../..
    
    if [ "$has_errors" = false ]; then
        print_success "日志检查通过"
    fi
}

# 检查资源使用情况
check_resource_usage() {
    print_step "检查资源使用情况..."
    
    # 检查磁盘空间
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 80 ]; then
        print_success "磁盘使用率: ${disk_usage}%"
    else
        print_warning "磁盘使用率较高: ${disk_usage}%"
    fi
    
    # 检查内存使用
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$mem_usage" -lt 80 ]; then
        print_success "内存使用率: ${mem_usage}%"
    else
        print_warning "内存使用率较高: ${mem_usage}%"
    fi
    
    # 检查Docker容器资源
    print_info "Docker容器资源使用:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -7
}

# 显示服务信息
show_service_info() {
    print_step "服务访问信息"
    echo ""
    echo -e "${GREEN}🌐 服务访问地址：${NC}"
    echo ""
    echo "📊 主仪表板:     http://localhost"
    echo "🔧 API文档:      http://localhost:8000/docs"
    echo "❤️  健康检查:     http://localhost:8000/health"
    echo "📈 Grafana:      http://localhost:3000 (admin/admin123)"
    echo "📊 Prometheus:   http://localhost:9090"
    echo ""
    echo -e "${YELLOW}🛠️  管理命令：${NC}"
    echo ""
    echo "查看日志:   docker-compose -f config/docker/docker-compose.yml logs -f [service]"
    echo "重启服务:   docker-compose -f config/docker/docker-compose.yml restart [service]"
    echo "停止服务:   docker-compose -f config/docker/docker-compose.yml down"
    echo "启动服务:   docker-compose -f config/docker/docker-compose.yml up -d"
    echo ""
}

# 主函数
main() {
    print_banner
    
    local overall_health=true
    
    if ! check_docker_services; then
        overall_health=false
    fi
    
    check_service_endpoints
    check_logs
    check_resource_usage
    
    echo ""
    if [ "$overall_health" = true ]; then
        print_success "🎉 系统整体健康状况良好！"
    else
        print_error "⚠️  系统存在问题，请检查上述错误"
    fi
    
    show_service_info
}

# 运行主函数
main "$@" 