#!/bin/bash

# 🏥 Cross-Mind Consensus 健康检查脚本 (重构后版本 v2.0)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║    🏥 Cross-Mind Consensus Health Check  ║"
    echo "║         重构后版本 v2.0                   ║"
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

print_critical() {
    echo -e "${RED}[🚨]${NC} $1"
}

# 检查Docker服务状态
check_docker_services() {
    print_step "检查Docker服务状态..."
    
    if [ ! -f "config/docker/docker-compose.yml" ]; then
        print_warning "Docker compose文件不存在，跳过Docker服务检查"
        return 0
    fi
    
    cd config/docker
    
    local services=("redis" "api" "dashboard" "nginx" "prometheus" "grafana")
    local all_running=true
    local critical_services=("redis" "api")
    
    for service in "${services[@]}"; do
        if docker-compose ps "$service" 2>/dev/null | grep -q "Up"; then
            print_success "$service: 运行中"
        else
            if [[ " ${critical_services[@]} " =~ " ${service} " ]]; then
                print_error "$service: 未运行 (关键服务)"
                all_running=false
            else
                print_warning "$service: 未运行 (可选服务)"
            fi
        fi
    done
    
    cd ../..
    
    if [ "$all_running" = true ]; then
        print_success "所有关键Docker服务正常运行"
        return 0
    else
        print_error "部分关键Docker服务未运行"
        return 1
    fi
}

# 检查Redis连接
check_redis_connection() {
    local redis_host=${REDIS_HOST:-localhost}
    local redis_port=${REDIS_PORT:-6379}
    
    if command -v redis-cli &> /dev/null; then
        # Try localhost first (for host-based access), then the configured host
        if redis-cli -h "localhost" -p "$redis_port" ping &> /dev/null; then
            print_success "Redis: 连接正常 (localhost:$redis_port)"
            return 0
        elif [ "$redis_host" != "localhost" ] && redis-cli -h "$redis_host" -p "$redis_port" ping &> /dev/null; then
            print_success "Redis: 连接正常 ($redis_host:$redis_port)"
            return 0
        else
            print_warning "Redis: 无法连接 (尝试了 localhost:$redis_port 和 $redis_host:$redis_port)"
            return 1
        fi
    else
        print_warning "Redis: redis-cli未安装，无法测试连接"
        return 1
    fi
}

# 检查服务端点
check_service_endpoints() {
    print_step "检查服务端点..."
    
    local endpoints=(
        "http://localhost:8000/health|API健康检查|critical"
        "http://localhost:8000/docs|API文档|important"
        "http://localhost:8501|Streamlit仪表板|important"
        "http://localhost:3000|Grafana|optional"
        "http://localhost:9090|Prometheus|optional"
    )
    
    local critical_failed=false
    
    for endpoint_info in "${endpoints[@]}"; do
        local url=$(echo "$endpoint_info" | cut -d'|' -f1)
        local name=$(echo "$endpoint_info" | cut -d'|' -f2)
        local priority=$(echo "$endpoint_info" | cut -d'|' -f3)
        
        if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
            print_success "$name: 可访问"
        else
            if [ "$priority" = "critical" ]; then
                print_error "$name: 无法访问 ($url)"
                critical_failed=true
            else
                print_warning "$name: 无法访问 ($url)"
            fi
        fi
    done
    
    # 单独检查Redis连接
    check_redis_connection
    
    # 检查优化版本API是否运行
    if curl -s --max-time 5 "http://localhost:8001/health" >/dev/null 2>&1; then
        print_success "优化版本API: 可访问 (端口8001)"
    else
        print_info "优化版本API: 未运行 (可选)"
    fi
    
    return $([ "$critical_failed" = false ] && echo 0 || echo 1)
}

# 检查日志错误
check_logs() {
    print_step "检查最近的错误日志..."
    
    if [ ! -f "config/docker/docker-compose.yml" ]; then
        print_info "Docker compose文件不存在，跳过日志检查"
        return 0
    fi
    
    cd config/docker
    
    local services=("api" "dashboard")
    local has_errors=false
    
    for service in "${services[@]}"; do
        if docker-compose ps "$service" 2>/dev/null | grep -q "Up"; then
            local error_count=$(docker-compose logs --tail=50 "$service" 2>/dev/null | grep -i "error\|exception\|failed\|traceback" | wc -l)
            
            if [ "$error_count" -gt 10 ]; then
                print_error "$service: 发现 $error_count 个错误日志条目 (严重)"
                has_errors=true
                # 显示最近的几个错误
                print_info "最近的错误:"
                docker-compose logs --tail=5 "$service" 2>/dev/null | grep -i "error\|exception\|failed" | head -3 | sed 's/^/  /'
            elif [ "$error_count" -gt 0 ]; then
                print_warning "$service: 发现 $error_count 个错误日志条目"
            else
                print_success "$service: 无错误日志"
            fi
        else
            print_warning "$service: 服务未运行，无法检查日志"
        fi
    done
    
    cd ../..
    
    if [ "$has_errors" = false ]; then
        print_success "日志检查通过"
    fi
}

# 检查磁盘空间并清理
check_and_cleanup_disk() {
    print_step "检查磁盘空间..."
    
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    local available_gb=$(df -h . | tail -1 | awk '{print $4}')
    
    if [ "$disk_usage" -lt 70 ]; then
        print_success "磁盘使用率: ${disk_usage}% (可用: $available_gb)"
    elif [ "$disk_usage" -lt 85 ]; then
        print_warning "磁盘使用率: ${disk_usage}% (可用: $available_gb) - 建议清理"
    elif [ "$disk_usage" -lt 95 ]; then
        print_error "磁盘使用率: ${disk_usage}% (可用: $available_gb) - 需要立即清理"
        suggest_cleanup
    else
        print_critical "磁盘使用率: ${disk_usage}% (可用: $available_gb) - 严重不足！"
        suggest_cleanup
        return 1
    fi
    
    return 0
}

# 建议清理操作
suggest_cleanup() {
    print_info "💡 磁盘清理建议:"
    echo "  1. 清理Docker镜像: docker system prune -a"
    echo "  2. 清理日志文件: sudo journalctl --vacuum-time=7d"
    echo "  3. 清理临时文件: sudo apt-get clean && sudo apt-get autoremove"
    echo "  4. 检查大文件: du -h --max-depth=1 | sort -hr | head -10"
    
    # 自动清理建议
    read -p "是否自动清理Docker未使用的镜像和容器? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "正在清理Docker资源..."
        docker system prune -f
        print_success "Docker清理完成"
    fi
}

# 检查资源使用情况
check_resource_usage() {
    print_step "检查资源使用情况..."
    
    # 检查内存使用
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    local mem_available=$(free -h | grep Mem | awk '{print $7}')
    
    if [ "$mem_usage" -lt 70 ]; then
        print_success "内存使用率: ${mem_usage}% (可用: $mem_available)"
    elif [ "$mem_usage" -lt 85 ]; then
        print_warning "内存使用率: ${mem_usage}% (可用: $mem_available)"
    else
        print_error "内存使用率: ${mem_usage}% (可用: $mem_available) - 内存不足"
    fi
    
    # 检查CPU负载
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local cpu_cores=$(nproc)
    local load_percentage=$(echo "$load_avg $cpu_cores" | awk '{printf "%.0f", ($1/$2)*100}')
    
    if [ "$load_percentage" -lt 70 ]; then
        print_success "CPU负载: ${load_avg} (${load_percentage}%)"
    elif [ "$load_percentage" -lt 90 ]; then
        print_warning "CPU负载: ${load_avg} (${load_percentage}%)"
    else
        print_error "CPU负载: ${load_avg} (${load_percentage}%) - 负载过高"
    fi
    
    # 检查Docker容器资源
    if command -v docker &> /dev/null && docker ps -q &> /dev/null; then
        print_info "Docker容器资源使用:"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | head -7 || print_warning "无法获取Docker统计信息"
    fi
}

# 检查API性能
check_api_performance() {
    print_step "检查API性能..."
    
    local api_url="http://localhost:8000/health"
    local optimized_url="http://localhost:8001/health"
    
    # 测试标准API
    if curl -s --max-time 5 "$api_url" >/dev/null 2>&1; then
        local response_time=$(curl -o /dev/null -s -w "%{time_total}" --max-time 10 "$api_url")
        if (( $(echo "$response_time < 1.0" | bc -l) )); then
            print_success "标准API响应时间: ${response_time}s"
        elif (( $(echo "$response_time < 3.0" | bc -l) )); then
            print_warning "标准API响应时间: ${response_time}s (较慢)"
        else
            print_error "标准API响应时间: ${response_time}s (过慢)"
        fi
    fi
    
    # 测试优化API
    if curl -s --max-time 5 "$optimized_url" >/dev/null 2>&1; then
        local opt_response_time=$(curl -o /dev/null -s -w "%{time_total}" --max-time 10 "$optimized_url")
        if (( $(echo "$opt_response_time < 1.0" | bc -l) )); then
            print_success "优化API响应时间: ${opt_response_time}s"
        else
            print_warning "优化API响应时间: ${opt_response_time}s"
        fi
    fi
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
    echo "⚡ 优化版API:    http://localhost:8001/docs (如果运行)"
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
    echo -e "${CYAN}⚡ 优化版本命令：${NC}"
    echo ""
    echo "启动优化版:  ./start_optimized.sh"
    echo "性能测试:    python scripts/performance_comparison.py"
    echo "运行测试:    pytest tests/ -v"
    echo ""
}

# 生成健康报告
generate_health_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="health_report_$(date '+%Y%m%d_%H%M%S').txt"
    
    {
        echo "Cross-Mind Consensus 健康检查报告"
        echo "生成时间: $timestamp"
        echo "========================================"
        echo ""
        
        # 重新运行检查并捕获输出
        check_docker_services 2>&1
        echo ""
        check_service_endpoints 2>&1
        echo ""
        check_logs 2>&1
        echo ""
        check_and_cleanup_disk 2>&1
        echo ""
        check_resource_usage 2>&1
        echo ""
        check_api_performance 2>&1
        
    } > "$report_file"
    
    print_info "健康报告已保存到: $report_file"
}

# 主函数
main() {
    print_banner
    
    local overall_health=true
    local critical_issues=0
    
    # 检查各个组件
    if ! check_docker_services; then
        overall_health=false
        ((critical_issues++))
    fi
    
    if ! check_service_endpoints; then
        overall_health=false
        ((critical_issues++))
    fi
    
    check_logs
    
    if ! check_and_cleanup_disk; then
        overall_health=false
        ((critical_issues++))
    fi
    
    check_resource_usage
    check_api_performance
    
    echo ""
    
    # 总结健康状况
    if [ "$overall_health" = true ]; then
        print_success "🎉 系统整体健康状况良好！"
    elif [ "$critical_issues" -eq 1 ]; then
        print_warning "⚠️  系统存在 1 个关键问题，请检查上述错误"
    else
        print_error "🚨 系统存在 $critical_issues 个关键问题，需要立即处理！"
    fi
    
    show_service_info
    
    # 询问是否生成详细报告
    if [ "$critical_issues" -gt 0 ]; then
        read -p "是否生成详细健康报告? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            generate_health_report
        fi
    fi
}

# 检查bc命令是否可用（用于浮点数比较）
if ! command -v bc &> /dev/null; then
    print_warning "bc命令未安装，某些性能检查可能不准确"
    print_info "安装命令: sudo apt-get install bc"
fi

# 运行主函数
main "$@" 