#!/bin/bash

# RAGFlow Plus 一键构建和启动脚本
# 作者: AI Assistant
# 用途: 构建 Docker 镜像并启动完整的 RAGFlow Plus 服务栈
#
# 使用方法:
#   ./build_and_start.sh           # 使用缓存构建
#   ./build_and_start.sh --no-cache # 不使用缓存构建

set -e  # 遇到错误立即退出

# 解析命令行参数
NO_CACHE=false
for arg in "$@"; do
    case $arg in
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        *)
            # 未知参数
            ;;
    esac
done

echo "=========================================="
echo "RAGFlow Plus 一键构建和启动脚本"
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

# 停止并清理现有服务
cleanup_all() {
    log_info "停止并清理现有服务..."

    # 停止管理系统服务（先停止避免依赖问题）
    cd management
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        log_info "停止管理系统服务..."
        docker-compose down --remove-orphans
    fi

    # 停止主服务
    cd ../docker
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        log_info "停止主 RAGFlow 服务..."
        docker-compose down --remove-orphans
    fi

    cd ..

    # 强制删除可能存在的容器（确保清理干净）
    log_info "清理残留容器..."
    docker rm -f ragflowplus-management-frontend 2>/dev/null || true
    docker rm -f ragflowplus-management-backend 2>/dev/null || true
    docker rm -f ragflowplus-server 2>/dev/null || true
    docker rm -f ragflow-mysql 2>/dev/null || true
    docker rm -f ragflow-es-01 2>/dev/null || true
    docker rm -f ragflow-redis 2>/dev/null || true
    docker rm -f ragflow-minio 2>/dev/null || true

    # 清理旧镜像
    log_info "清理旧镜像..."
    docker rmi -f zstar1003/ragflowplus:v0.5.0 2>/dev/null || true
    docker rmi -f zstar1003/ragflowplus-management-web:v0.5.0 2>/dev/null || true
    docker rmi -f zstar1003/ragflowplus-management-server:v0.5.0 2>/dev/null || true

    # 清理悬空镜像
    docker image prune -f

    log_success "清理完成"
}

# 构建主 RAGFlow 镜像
build_main_image() {
    log_info "构建主 RAGFlow 镜像..."

    if [ "$NO_CACHE" = true ]; then
        log_info "使用 --no-cache 构建主镜像..."
        docker build --no-cache -t zstar1003/ragflowplus:v0.5.0 .
    else
        log_info "使用缓存构建主镜像..."
        docker build -t zstar1003/ragflowplus:v0.5.0 .
    fi

    log_success "主 RAGFlow 镜像构建完成"
}

# 构建管理系统镜像
build_management_images() {
    log_info "构建管理系统镜像..."

    cd management

    if [ "$NO_CACHE" = true ]; then
        log_info "使用 --no-cache 构建管理系统镜像..."
        docker-compose build --no-cache management-backend management-frontend
    else
        log_info "使用缓存构建管理系统镜像..."
        docker-compose build management-backend management-frontend
    fi

    cd ..
    log_success "管理系统镜像构建完成"
}

# 启动所有服务
start_all_services() {
    log_info "启动所有服务..."

    # 启动主服务
    cd docker
    log_info "启动主 RAGFlow 服务..."
    docker-compose up -d

    # 等待主服务启动并确保网络存在
    log_info "等待主服务启动..."
    sleep 15

    # 检查网络是否存在
    log_info "检查 Docker 网络..."
    if ! docker network ls | grep -q "docker_ragflow"; then
        log_warning "docker_ragflow 网络不存在，重新启动主服务..."
        docker-compose down
        docker-compose up -d
        sleep 10
    fi

    # 验证主服务状态
    log_info "验证主服务状态..."
    docker-compose ps

    log_success "所有服务启动完成"
}

# 显示服务状态和访问信息
show_final_status() {
    log_info "最终服务状态检查..."

    echo ""
    echo "=========================================="
    echo "服务状态"
    echo "=========================================="

    cd docker
    echo "所有服务状态:"
    docker-compose ps

    cd ..

    echo ""
    echo "=========================================="
    echo "访问地址"
    echo "=========================================="
    echo "主 RAGFlow 服务: http://localhost:10080"
    echo "管理系统前端: http://localhost:8888"
    echo "管理系统后端: http://localhost:5000"
    echo "MySQL: localhost:5455"
    echo "Elasticsearch: http://localhost:1200"
    echo "Redis: localhost:6379"
    echo "MinIO: http://localhost:9000 (Console: http://localhost:9001)"
    echo "=========================================="

    # 健康检查
    log_info "执行健康检查..."

    # 检查主服务
    if docker-compose -f docker/docker-compose.yml ps | grep -q "ragflowplus-server.*Up"; then
        log_success "主 RAGFlow 服务运行正常"
    else
        log_warning "主 RAGFlow 服务可能存在问题"
    fi

    # 检查管理系统
    if docker-compose -f management/docker-compose.yml ps | grep -q "ragflowplus-management.*Up"; then
        log_success "管理系统服务运行正常"
    else
        log_warning "管理系统服务可能存在问题"
    fi
}

# 主函数
main() {
    log_info "开始 RAGFlow Plus 构建和启动流程..."

    # 检查 Docker
    check_docker

    # 停止并清理现有服务
    cleanup_all

    # 构建镜像
    build_main_image
    build_management_images

    # 启动服务
    start_all_services

    # 确保回到根目录
    cd "$SCRIPT_ROOT"

    # 显示最终状态
    show_final_status

    echo ""
    log_success "🎉 RAGFlow Plus 构建和启动完成！"
    echo ""
    echo "💡 提示："
    echo "   - 如果服务没有立即可用，请等待 1-2 分钟让服务完全启动"
    echo "   - 如果遇到问题，请检查 Docker 日志: docker-compose logs -f"
    echo "   - 要停止所有服务，请运行:"
    echo "     cd docker && docker-compose down"
    echo "     cd management && docker-compose down"
}

# 执行主函数
main "$@"