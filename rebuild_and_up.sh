#!/bin/bash

# RAGFlow Plus 重新构建所有镜像并启动服务脚本
# 作者: AI Assistant
# 用途: 重新构建所有 Docker 镜像并启动完整的 RAGFlow Plus 服务栈

set -e  # 遇到错误立即退出

echo "=========================================="
echo "RAGFlow Plus 重新构建和启动脚本"
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

# 检查 Docker 是否运行
check_docker() {
    log_info "检查 Docker 服务状态..."
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker 未运行或无法访问，请启动 Docker 服务"
        exit 1
    fi
    log_success "Docker 服务正常运行"
}

# 停止现有服务
stop_services() {
    log_info "停止现有服务..."
    
    # 停止主服务
    cd docker
    if docker-compose ps -q | grep -q .; then
        log_info "停止主 RAGFlow 服务..."
        docker-compose down
    fi
    
    # 停止管理系统服务
    cd ../management
    if docker-compose ps -q | grep -q .; then
        log_info "停止管理系统服务..."
        docker-compose down
    fi
    
    cd ..
    log_success "所有服务已停止"
}

# 清理旧镜像
cleanup_images() {
    log_info "清理旧镜像..."
    
    # 删除 RAGFlow Plus 相关镜像
    docker rmi -f zstar1003/ragflowplus:v0.5.0 2>/dev/null || true
    docker rmi -f zstar1003/ragflowplus-management-web:v0.5.0 2>/dev/null || true
    docker rmi -f zstar1003/ragflowplus-management-server:v0.5.0 2>/dev/null || true
    
    # 清理悬空镜像
    docker image prune -f
    
    log_success "镜像清理完成"
}

# 构建主 RAGFlow 镜像
build_main_ragflow() {
    log_info "构建主 RAGFlow 镜像..."
    
    # 构建主镜像
    docker build -t zstar1003/ragflowplus:v0.5.0 .
    
    log_success "主 RAGFlow 镜像构建完成"
}

# 构建管理系统镜像
build_management() {
    log_info "构建管理系统镜像..."
    
    cd management
    
    # 构建管理系统前端和后端镜像
    docker-compose build --no-cache management-backend management-frontend
    
    cd ..
    log_success "管理系统镜像构建完成"
}

# 启动所有服务
start_services() {
    log_info "启动所有服务..."
    
    # 启动主服务
    cd docker
    log_info "启动主 RAGFlow 服务..."
    docker-compose up -d
    
    # 等待主服务启动
    log_info "等待主服务启动..."
    sleep 10
    
    # 启动管理系统
    cd ../management
    log_info "启动管理系统服务..."
    docker-compose up -d
    
    cd ..
    log_success "所有服务启动完成"
}

# 显示服务状态
show_status() {
    log_info "服务状态检查..."
    
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
    echo "MySQL: localhost:5455"
    echo "Elasticsearch: http://localhost:1200"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始 RAGFlow Plus 重新构建和部署流程..."
    
    # 检查 Docker
    check_docker
    
    # 停止现有服务
    stop_services
    
    # 清理旧镜像
    cleanup_images
    
    # 构建主 RAGFlow 镜像
    build_main_ragflow
    
    # 构建管理系统镜像
    build_management
    
    # 启动所有服务
    start_services
    
    # 显示服务状态
    show_status
    
    log_success "RAGFlow Plus 重新构建和部署完成！"
}

# 执行主函数
main "$@"