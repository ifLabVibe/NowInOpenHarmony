# OpenHarmony Server 云端部署指南

## 环境信息
- **服务器系统**: Ubuntu 20.04+
- **面板**: 宝塔面板
- **部署方式**: Docker + Docker Compose

---

## 一、服务器环境准备

### 1.1 安装Docker（如果未安装）

```bash
# 使用宝塔面板安装（推荐）
# 在宝塔面板 -> 软件商店 -> 搜索"Docker" -> 安装

# 或手动安装Docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# 启动Docker服务
systemctl start docker
systemctl enable docker

# 验证安装
docker --version
```

### 1.2 安装Docker Compose

```bash
# 检查是否已安装
docker-compose --version

# 如未安装，使用宝塔面板安装
# 或手动安装
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 1.3 创建部署目录

```bash
# 创建项目部署目录
mkdir -p /www/wwwroot/openharmony-server
cd /www/wwwroot/openharmony-server
```

---

## 二、上传项目文件

### 方式1: 使用宝塔面板上传（推荐）

1. 打开宝塔面板
2. 进入文件管理
3. 导航到 `/www/wwwroot/openharmony-server`
4. 上传 `openharmony-server_XXXXXX.tar.gz` 文件
5. 右键点击文件 -> 解压

### 方式2: 使用SCP命令上传

```bash
# 在本地Windows Git Bash或WSL中执行
cd d:/AITrainingCamp/NowInOpenHarmony/dist
scp openharmony-server_20251012_160938.tar.gz root@your-server-ip:/www/wwwroot/openharmony-server/

# 然后SSH登录服务器解压
ssh root@your-server-ip
cd /www/wwwroot/openharmony-server
tar -xzf openharmony-server_20251012_160938.tar.gz
cd openharmony-server_20251012_160938
```

### 方式3: 使用宝塔SSH终端

1. 打开宝塔面板 -> 终端
2. 使用wget下载（如果文件在网络存储）
   ```bash
   cd /www/wwwroot/openharmony-server
   wget http://your-file-url/openharmony-server_XXXXXX.tar.gz
   tar -xzf openharmony-server_XXXXXX.tar.gz
   ```

---

## 三、配置应用

### 3.1 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
# 或使用宝塔面板的文件编辑器
```

**重要配置项**:
```env
# 应用配置
HOST=0.0.0.0
PORT=8001
DEBUG=false

# 数据库配置（SQLite或PostgreSQL）
DATABASE_URL=sqlite:///./data/openharmony_news.db

# 日志级别
LOG_LEVEL=INFO

# 调度器配置
ENABLE_SCHEDULER=true
CACHE_UPDATE_INTERVAL=30
FULL_CRAWL_HOUR=2
```

### 3.2 配置宝塔安全组/防火墙

```bash
# 在宝塔面板 -> 安全 中放行端口
# 添加放行规则：8001端口

# 或使用命令行
firewall-cmd --zone=public --add-port=8001/tcp --permanent
firewall-cmd --reload

# 如果使用云服务器，还需要在云平台控制台配置安全组
# 例如：阿里云、腾讯云、华为云等
```

---

## 四、部署应用

### 4.1 赋予脚本执行权限

```bash
chmod +x deploy.sh
```

### 4.2 初始化部署

```bash
# 检查环境并构建镜像
./deploy.sh install
```

### 4.3 启动服务

```bash
# 开发环境（使用SQLite）
./deploy.sh start

# 或生产环境（使用PostgreSQL + Nginx）
./deploy.sh start prod
```

### 4.4 验证部署

```bash
# 检查服务状态
./deploy.sh status

# 健康检查
./deploy.sh health

# 查看日志
./deploy.sh logs app
```

---

## 五、访问服务

### 5.1 获取服务器IP

```bash
# 查看服务器公网IP
curl ifconfig.me
```

### 5.2 访问端点

- **主页**: http://your-server-ip:8001/
- **API文档**: http://your-server-ip:8001/docs
- **健康检查**: http://your-server-ip:8001/health
- **全部新闻**: http://your-server-ip:8001/api/news/?all=true
- **官网新闻**: http://your-server-ip:8001/api/news/openharmony
- **技术博客**: http://your-server-ip:8001/api/news/blog
- **Banner图片**: http://your-server-ip:8001/api/banner/mobile

---

## 六、配置Nginx反向代理（可选）

### 6.1 使用宝塔面板配置

1. 打开宝塔面板 -> 网站
2. 添加站点（例如: openharmony.yourdomain.com）
3. 配置反向代理：
   - 目标URL: http://127.0.0.1:8001
   - 发送域名: $host
   - 内容替换: 关闭

### 6.2 手动配置Nginx

```nginx
server {
    listen 80;
    server_name openharmony.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 6.3 配置HTTPS（推荐）

```bash
# 在宝塔面板中
# 网站 -> SSL -> Let's Encrypt -> 申请免费证书

# 或使用Certbot手���申请
certbot --nginx -d openharmony.yourdomain.com
```

---

## 七、常用运维命令

### 7.1 服务管理

```bash
# 查看状态
./deploy.sh status

# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看日志
./deploy.sh logs app          # 应用日志
./deploy.sh logs postgres     # 数据库日志（生产环境）
./deploy.sh logs nginx        # Nginx日志（生产环境）
```

### 7.2 数据管理

```bash
# 数据备份
./deploy.sh backup

# 查看数据卷
docker volume ls

# 进入容器
docker-compose exec app bash
```

### 7.3 更新部署

```bash
# 拉取最新代码（如果使用git）
git pull

# 或上传新的tar.gz包并解压

# 重新构建并启动
./deploy.sh update
```

### 7.4 监控和调试

```bash
# 实时查看日志
docker-compose logs -f app

# 查看容器资源使用
docker stats

# 进入容器调试
docker-compose exec app bash
python -c "from services.openharmony_news_crawler import OpenHarmonyNewsCrawler; c=OpenHarmonyNewsCrawler(); print(c.base_url)"
```

---

## 八、故障排查

### 8.1 服务无法访问

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 检查端口占用
netstat -tunlp | grep 8001

# 3. 检查防火墙
firewall-cmd --list-ports

# 4. 查看容器日志
docker-compose logs app
```

### 8.2 数据库连接失败

```bash
# 检查数据库容器状态（生产环境）
docker-compose exec postgres pg_isready -U postgres

# 检查SQLite文件权限（开发环境）
ls -l data/openharmony_news.db

# 重置数据库
docker-compose down -v
docker-compose up -d
```

### 8.3 爬虫无法获取数据

```bash
# 进入容器测试网络
docker-compose exec app bash
curl -I https://old.openharmony.cn

# 测试爬虫
python -c "from services.openharmony_news_crawler import OpenHarmonyNewsCrawler; print('OK')"

# 手动触发爬取
curl -X POST http://localhost:8001/api/news/crawl
```

### 8.4 内存不足

```bash
# 查看系统内存
free -h

# 清理Docker缓存
docker system prune -a

# 限制容器内存（修改docker-compose.yml）
services:
  app:
    mem_limit: 1g
    mem_reservation: 512m
```

---

## 九、性能优化

### 9.1 启用生产模式

```bash
# 使用生产环境配置
./deploy.sh start prod
```

### 9.2 配置Redis缓存（可选）

```yaml
# 在docker-compose.prod.yml中已包含Redis服务
# 可以修改应用代码使用Redis替代内存缓存
```

### 9.3 数据库优化

```sql
-- PostgreSQL性能优化
-- 连接到数据库
docker-compose exec postgres psql -U postgres -d openharmony_news

-- 创建索引
CREATE INDEX idx_news_date ON news_articles(date);
CREATE INDEX idx_news_source ON news_articles(source);
CREATE INDEX idx_news_category ON news_articles(category);

-- 分析表
ANALYZE news_articles;
```

### 9.4 监控配置

```bash
# 使用宝塔面板的监控功能
# 或安装第三方监控工具如Prometheus + Grafana
```

---

## 十、安全建议

### 10.1 修改默认端口

```env
# 修改.env文件
PORT=8888  # 使用非标准端口
```

### 10.2 配置访问控制

```nginx
# Nginx配置IP白名单
location / {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://127.0.0.1:8001;
}
```

### 10.3 启用HTTPS

```bash
# 使用宝塔面板或Certbot配置SSL证书
# 强制HTTPS重定向
```

### 10.4 定期更新

```bash
# 定期更新系统和Docker
apt update && apt upgrade -y

# 更新应用代码
./deploy.sh update
```

---

## 附录

### A. 项目文件结构

```
openharmony-server_XXXXXX/
├── api/                    # API接口
├── core/                   # 核心功能
├── models/                 # 数据模型
├── services/               # 爬虫服务
├── main.py                 # 应用入口
├── run.py                  # 启动脚本
├── Dockerfile              # Docker镜像配置
├── docker-compose.yml      # 开发环境配置
├── docker-compose.prod.yml # 生产环境配置
├── deploy.sh               # 部署脚本
├── .env.example            # 环境变量模板
├── DEPLOY_GUIDE.txt        # 快速部署指南
└── VERSION.txt             # 版本信息
```

### B. 端口说明

- **8001**: 应用主端口（FastAPI）
- **5432**: PostgreSQL数据库（生产环境）
- **6379**: Redis缓存（生产环境）
- **80/443**: Nginx反向代理（可选）

### C. 数据持久化

```bash
# Docker volumes（生产环境）
- postgres_data: 数据库数据
- app_data: 应用数据（SQLite）
- app_logs: 应用日志
- redis_data: Redis数据
```

---

## 技术支持

如有问题，请查看：
- 项目README.md
- CLAUDE.md（架构说明）
- 或提交Issue到项目仓库

---

**版本**: 1.0.0
**更新日期**: 2025-10-12
**适用环境**: Ubuntu 20.04+ / 宝塔面板 / Docker
