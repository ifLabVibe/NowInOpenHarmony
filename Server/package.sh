#!/bin/bash

# OpenHarmony Server 项目打包脚本
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

# 获取项目信息
PROJECT_NAME="openharmony-server"
VERSION=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="${PROJECT_NAME}_${VERSION}"
DIST_DIR="../dist"
TEMP_DIR="${DIST_DIR}/${PACKAGE_NAME}"

log_info "开始打包 OpenHarmony Server 项目..."
log_info "项目名称: ${PROJECT_NAME}"
log_info "版本标识: ${VERSION}"

# 创建临时目录
log_info "创建临时目录..."
mkdir -p "${TEMP_DIR}"

# 需要打包的文件和目录
FILES_TO_COPY=(
    "api"
    "core"
    "models"
    "services"
    "main.py"
    "run.py"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    "docker-compose.prod.yml"
    "deploy.sh"
    ".env.example"
    "README.md"
    "CLAUDE.md"
)

# 复制文件到临时目录
log_info "复制项目文件..."
for item in "${FILES_TO_COPY[@]}"; do
    if [ -e "$item" ]; then
        if [ -d "$item" ]; then
            log_info "  复制目录: $item/"
            cp -r "$item" "${TEMP_DIR}/"
        else
            log_info "  复制文件: $item"
            cp "$item" "${TEMP_DIR}/"
        fi
    else
        log_warning "  文件不存在，跳过: $item"
    fi
done

# 创建必要的空目录
log_info "创建必要的目录结构..."
mkdir -p "${TEMP_DIR}/logs"
mkdir -p "${TEMP_DIR}/data"
mkdir -p "${TEMP_DIR}/downloads/images"
mkdir -p "${TEMP_DIR}/nginx/conf.d"

# 复制nginx配置（如果存在）
if [ -d "nginx" ]; then
    log_info "复制nginx配置..."
    cp -r nginx/* "${TEMP_DIR}/nginx/" 2>/dev/null || true
fi

# 清理Python缓存
log_info "清理Python缓存文件..."
find "${TEMP_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${TEMP_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${TEMP_DIR}" -type f -name "*.pyo" -delete 2>/dev/null || true

# 创建版本信息文件
log_info "创建版本信息文件..."
cat > "${TEMP_DIR}/VERSION.txt" <<EOF
项目名称: OpenHarmony Server
版本: ${VERSION}
打包时间: $(date '+%Y-%m-%d %H:%M:%S')
打包主机: $(hostname)
Git提交: $(git rev-parse --short HEAD 2>/dev/null || echo "未知")
Git分支: $(git branch --show-current 2>/dev/null || echo "未知")
EOF

# 创建部署说明
log_info "创建部署说明..."
cat > "${TEMP_DIR}/DEPLOY_GUIDE.txt" <<EOF
OpenHarmony Server 部署指南
========================================

一、环境要求
  - Ubuntu 20.04+ 或其他Linux发行版
  - Docker 20.10+
  - Docker Compose 1.29+
  - 至少2GB可用内存

二、快速部署步骤

1. 解压文件
   tar -xzf ${PACKAGE_NAME}.tar.gz
   cd ${PACKAGE_NAME}

2. 配置环境变量（可选）
   cp .env.example .env
   # 编辑.env文件，根据需要修改配置
   vim .env

3. 赋予脚本执行权限
   chmod +x deploy.sh

4. 初始化部署
   ./deploy.sh install

5. 启动服务
   # 开发环境
   ./deploy.sh start

   # 生产环境
   ./deploy.sh start prod

6. 验证服务
   ./deploy.sh health
   # 或访问 http://服务器IP:8001/health

三、常用命令

  查看服务状态:   ./deploy.sh status
  查看日志:       ./deploy.sh logs app
  重启服务:       ./deploy.sh restart
  停止服务:       ./deploy.sh stop
  备份数据:       ./deploy.sh backup
  更新服务:       ./deploy.sh update

四、访问服务

  主页:          http://服务器IP:8001/
  API文档:       http://服务器IP:8001/docs
  健康检查:      http://服务器IP:8001/health
  全部新闻:      http://服务器IP:8001/api/news/?all=true

五、故障排查

  1. 查看服务日志:
     docker-compose logs -f app

  2. 进入容器调试:
     docker-compose exec app bash

  3. 重置服务:
     docker-compose down -v
     ./deploy.sh start

六、更多信息

  详细文档请参考: README.md
  技术架构说明: CLAUDE.md

========================================
打包版本: ${VERSION}
打包时间: $(date '+%Y-%m-%d %H:%M:%S')
EOF

# 进入dist目录进行打包
cd "${DIST_DIR}"

# 创建tar.gz压缩包
log_info "创建tar.gz压缩包..."
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"

# 获取文件大小
PACKAGE_SIZE=$(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)

# 清理临时目录
log_info "清理临时目录..."
rm -rf "${PACKAGE_NAME}"

# 生成MD5校验和
log_info "生成MD5校验和..."
if command -v md5sum &> /dev/null; then
    md5sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.md5"
elif command -v md5 &> /dev/null; then
    md5 "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.md5"
fi

# 输出成功信息
echo ""
log_success "=========================================="
log_success "项目打包完成！"
log_success "=========================================="
log_success "包文件: ${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
log_success "文件大小: ${PACKAGE_SIZE}"
if [ -f "${PACKAGE_NAME}.tar.gz.md5" ]; then
    log_success "MD5文件: ${DIST_DIR}/${PACKAGE_NAME}.tar.gz.md5"
fi
echo ""
log_info "后续步骤："
log_info "1. 将压缩包上传到服务器"
log_info "   scp ${PACKAGE_NAME}.tar.gz user@server:/path/to/deploy/"
log_info ""
log_info "2. 在服务器上解压"
log_info "   tar -xzf ${PACKAGE_NAME}.tar.gz"
log_info "   cd ${PACKAGE_NAME}"
log_info ""
log_info "3. 执行部署"
log_info "   chmod +x deploy.sh"
log_info "   ./deploy.sh install"
log_info "   ./deploy.sh start"
log_info ""
log_success "=========================================="
