# OpenHarmony Server Docker 部署指南

## 快速开始

### 1. 环境准备

确保服务器已安装以下软件：
- Docker (>= 20.10)
- Docker Compose (>= 1.29)
- Git

```bash
# 检查Docker版本
docker --version
docker-compose --version
```

### 2. 克隆项目

```bash
git clone <repository-url>
cd NowInOpenHarmony/Server
```

### 3. 使用部署脚本（推荐）

```bash
# 一键安装和部署
chmod +x deploy.sh
./deploy.sh install
./deploy.sh start

# 查看服务状态
./deploy.sh status
./deploy.sh health
```

## 详细部署步骤

### 开发环境部署

1. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置相关参数
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **验证部署**
```bash
curl http://localhost:8001/health
```

### 生产环境部署

1. **配置生产环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，设置生产环境配置：
# - 设置强密码（POSTGRES_PASSWORD, REDIS_PASSWORD）
# - 配置SSL证书路径
# - 设置合适的日志级别
```

2. **准备SSL证书**
```bash
mkdir -p ssl
# 将SSL证书文件放入ssl目录：
# - cert.pem (证书文件)
# - key.pem (私钥文件)
```

3. **启动生产环境**
```bash
./deploy.sh start prod
# 或手动启动
docker-compose -f docker-compose.prod.yml up -d
```

4. **配置域名和防火墙**
```bash
# 开放必要端口
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8001  # 如果需要直接访问API

# 配置域名DNS解析到服务器IP
```

## 服务架构

部署后的服务架构包括：

- **应用服务 (app)**: FastAPI应用，端口8001
- **数据库 (postgres)**: PostgreSQL数据库，端口5432
- **缓存 (redis)**: Redis缓存，端口6379
- **反向代理 (nginx)**: Nginx代理，端口80/443
- **监控 (prometheus/grafana)**: 可选监控服务

## 常用操作命令

### 服务管理

```bash
# 启动所有服务
./deploy.sh start

# 启动生产环境
./deploy.sh start prod

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看服务状态
./deploy.sh status
docker-compose ps
```

### 日志管理

```bash
# 查看应用日志
./deploy.sh logs app
docker-compose logs -f app

# 查看数据库日志
./deploy.sh logs postgres

# 查看Nginx日志
./deploy.sh logs nginx

# 查看所有服务日志
docker-compose logs -f
```

### 数据管理

```bash
# 备份数据
./deploy.sh backup

# 进入数据库
docker-compose exec postgres psql -U postgres -d openharmony_news

# 查看数据库大小
docker-compose exec postgres du -sh /var/lib/postgresql/data

# 清理所有数据（危险操作）
./deploy.sh clean
```

### 健康检查

```bash
# 执行健康检查
./deploy.sh health

# 手动检查API
curl http://localhost:8001/health
curl http://localhost:8001/docs

# 检查数据库连接
docker-compose exec postgres pg_isready -U postgres
```

## 监控和维护

### 服务监控

1. **Prometheus监控**: http://localhost:9090
2. **Grafana仪表板**: http://localhost:3000 (admin/admin123)
3. **API文档**: http://localhost:8001/docs

### 日常维护

```bash
# 更新服务
./deploy.sh update

# 查看资源使用
docker stats

# 清理未使用的镜像
docker system prune -f

# 查看磁盘使用
df -h
docker system df
```

### 性能调优

1. **调整容器资源限制**
   - 编辑 `docker-compose.prod.yml` 中的 `deploy.resources` 部分

2. **数据库优化**
   - 调整PostgreSQL配置参数
   - 定期执行 `VACUUM` 和 `ANALYZE`

3. **缓存优化**
   - 配置Redis内存策略
   - 监控缓存命中率

## 故障排除

### 常见问题

1. **端口冲突**
```bash
# 检查端口占用
netstat -tlnp | grep :8001
# 修改端口配置或停止冲突服务
```

2. **权限问题**
```bash
# 检查文件权限
ls -la logs/ data/
# 修复权限
sudo chown -R $USER:$USER logs/ data/
```

3. **内存不足**
```bash
# 检查内存使用
free -h
docker stats
# 调整容器内存限制
```

4. **数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U postgres
# 查看数据库日志
docker-compose logs postgres
```

### 紧急恢复

1. **服务重启**
```bash
./deploy.sh restart prod
```

2. **数据恢复**
```bash
# 从备份恢复
docker-compose exec postgres psql -U postgres -d openharmony_news < backup/database.sql
```

3. **配置回滚**
```bash
git checkout HEAD~1 -- docker-compose.prod.yml
./deploy.sh restart prod
```

## 安全注意事项

1. **定期更新密码**
   - 数据库密码
   - Redis密码
   - Grafana管理员密码

2. **SSL证书管理**
   - 定期检查证书有效期
   - 配置自动续期

3. **网络安全**
   - 配置防火墙规则
   - 使用VPN或内网访问管理端口

4. **数据备份**
   - 定期执行数据备份
   - 测试备份恢复流程

## 扩展部署

### 负载均衡

如需处理更高并发，可以部署多个应用实例：

```yaml
# 在docker-compose.prod.yml中添加
app2:
  extends: app
  container_name: openharmony-api-prod-2

app3:
  extends: app
  container_name: openharmony-api-prod-3
```

### 数据库集群

对于高可用需求，可以配置PostgreSQL主从复制或集群。

### 监控告警

配置Prometheus告警规则和Grafana通知渠道，实现异常情况的自动通知。