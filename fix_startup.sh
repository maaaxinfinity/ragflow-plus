#!/bin/bash

# RAGFlow Plus 启动问题修复脚本
# 用途: 清理冲突的容器并正确启动服务

set -e

echo "=========================================="
echo "RAGFlow Plus 启动问题修复"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 强制清理所有可能冲突的容器
cleanup_containers() {
    log_info "强制清理可能冲突的容器..."

    # 停止并删除管理系统容器
    docker rm -f ragflowplus-management-frontend 2>/dev/null || true
    docker rm -f ragflowplus-management-backend 2>/dev/null || true

    log_success "容器清理完成"
}

# 重新启动服务
restart_services() {
    log_info "重新启动服务..."

    # 确保主服务正在运行
    cd docker
    log_info "检查主 RAGFlow 服务状态..."
    docker-compose ps

    # 如果主服务没有运行，启动它
    if ! docker-compose ps | grep -q "ragflowplus-server.*Up"; then
        log_info "启动主 RAGFlow 服务..."
        docker-compose up -d
        sleep 15
    else
        log_info "主 RAGFlow 服务已在运行"
    fi

    # 启动管理系统
    cd ../management
    log_info "启动管理系统服务..."
    docker-compose up -d

    cd ..
    log_success "所有服务重新启动完成"
}

# 显示最终状态
show_final_status() {
    log_info "最终服务状态..."

    echo ""
    echo "=========================================="
    echo "服务状态"
    echo "=========================================="

    cd docker
    echo "主 RAGFlow 服务:"
    docker-compose ps

    echo ""
    cd ../management
    echo "管理系统服务:"
    docker-compose ps

    cd ..

    echo ""
    echo "=========================================="
    echo "访问地址"
    echo "=========================================="
    echo "主 RAGFlow 服务: http://localhost:80"
    echo "管理系统前端: http://localhost:8888"
    echo "管理系统后端: http://localhost:5000"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始修复 RAGFlow Plus 启动问题..."

    # 清理冲突容器
    cleanup_containers

    # 重新启动服务
    restart_services

    # 显示最终状态
    show_final_status

    log_success "RAGFlow Plus 启动问题修复完成！"
}

# 执行主函数
main "$@"