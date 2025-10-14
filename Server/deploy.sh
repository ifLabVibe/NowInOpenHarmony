#!/bin/bash

# OpenHarmony Server 部署脚本
# Copyright (c) 2025 XBXyftx

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    log_success "Docker 环境检查通过"
}

# 检查环境变量文件
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，复制示例文件..."
        cp .env.example .env
        log_warning "请编辑 .env 文件并设置正确的环境变量"
        read -p "是否要现在编辑 .env 文件? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p ssl logs data nginx/conf.d monitoring/grafana/provisioning sql redis
    log_success "目录创建完成"
}

# 构建镜像
build_image() {
    log_info "构建 Docker 镜像..."
    docker-compose build
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    local env_type=${1:-dev}

    if [ "$env_type" = "prod" ]; then
        log_info "启动生产环境服务..."
        docker-compose -f docker-compose.prod.yml up -d
    else
        log_info "启动开发环境服务..."
        docker-compose up -d
    fi

    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    local env_type=${1:-dev}

    if [ "$env_type" = "prod" ]; then
        log_info "停止生产环境服务..."
        docker-compose -f docker-compose.prod.yml down
    else
        log_info "停止开发环境服务..."
        docker-compose down
    fi

    log_success "服务停止完成"
}

# 查看服务状态
status_services() {
    log_info "查看服务状态..."
    docker-compose ps
}

# 查看日志
logs_services() {
    local service=${1:-app}
    log_info "查看 ${service} 服务日志..."
    docker-compose logs -f $service
}

# 重启服务
restart_services() {
    local env_type=${1:-dev}
    stop_services $env_type
    start_services $env_type
}

# 清理数据
clean_data() {
    log_warning "这将删除所有数据卷，确认要继续吗？"
    read -p "输入 'yes' 确认: " confirm
    if [ "$confirm" = "yes" ]; then
        docker-compose down -v
        docker system prune -f
        log_success "数据清理完成"
    else
        log_info "操作已取消"
    fi
}

# 备份数据
backup_data() {
    local backup_dir="backup/$(date +%Y%m%d_%H%M%S)"
    log_info "备份数据到 ${backup_dir}..."

    mkdir -p $backup_dir

    # 备份数据库
    docker-compose exec postgres pg_dump -U postgres openharmony_news > $backup_dir/database.sql

    # 备份数据卷
    docker run --rm -v openharmony_app_data:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/app_data.tar.gz -C /data .

    log_success "数据备份完成: $backup_dir"
}

# 更新服务
update_services() {
    log_info "更新服务..."

    # 拉取最新代码
    if [ -d ".git" ]; then
        git pull
    fi

    # 重新构建并启动
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d

    log_success "服务更新完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."

    sleep 10  # 等待服务启动

    # 检查API健康状态
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_success "API 服务健康"
    else
        log_error "API 服务不健康"
        return 1
    fi

    # 检查数据库连接
    if docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; then
        log_success "数据库连接正常"
    else
        log_error "数据库连接失败"
        return 1
    fi

    log_success "健康检查通过"
}

# 显示帮助信息
show_help() {
    cat << EOF
OpenHarmony Server 部署脚本

用法: $0 [命令] [选项]

命令:
    install         初始化部署（检查环境、创建目录、构建镜像）
    start [env]     启动服务 (env: dev|prod，默认dev)
    stop [env]      停止服务 (env: dev|prod，默认dev)
    restart [env]   重启服务 (env: dev|prod，默认dev)
    status          查看服务状态
    logs [service]  查看服务日志 (service: app|postgres|nginx|redis)
    update          更新服务
    backup          备份数据
    clean           清理所有数据（危险操作）
    health          健康检查
    help            显示此帮助信息

示例:
    $0 install              # 初始化部署
    $0 start                # 启动开发环境
    $0 start prod           # 启动生产环境
    $0 logs app             # 查看应用日志
    $0 backup               # 备份数据
    $0 health               # 健康检查

EOF
}

# 主函数
main() {
    case "$1" in
        install)
            check_docker
            check_env
            create_directories
            build_image
            log_success "安装完成，使用 '$0 start' 启动服务"
            ;;
        start)
            start_services $2
            sleep 5
            health_check
            ;;
        stop)
            stop_services $2
            ;;
        restart)
            restart_services $2
            sleep 5
            health_check
            ;;
        status)
            status_services
            ;;
        logs)
            logs_services $2
            ;;
        update)
            update_services
            ;;
        backup)
            backup_data
            ;;
        clean)
            clean_data
            ;;
        health)
            health_check
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"