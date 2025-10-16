# Ubuntu服务器部署指南

## 服务器环境准备

### 1. 系统要求
- Ubuntu 18.04+ (推荐 20.04 LTS 或 22.04 LTS)
- 最小2GB RAM，推荐4GB+
- 至少20GB可用磁盘空间
- 稳定的网络连接

### 2. 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. 安装必要软件

**安装Docker：**
```bash
# 卸载旧版本
sudo apt-get remove docker docker-engine docker.io containerd runc

# 安装依赖
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加Docker仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

**安装Docker Compose：**
```bash
# 下载最新版本的Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

**配置用户权限：**
```bash
# 将当前用户添加到docker组（避免使用sudo）
sudo usermod -aG docker $USER

# 重新登录或执行以下命令使权限生效
newgrp docker

# 验证权限
docker run hello-world
```

**安装其他工具：**
```bash
sudo apt install -y git curl wget unzip htop
```

## 部署步骤

### 1. 创建项目目录
```bash
# 创建应用目录
sudo mkdir -p /opt/openharmony-server
sudo chown $USER:$USER /opt/openharmony-server
cd /opt/openharmony-server
```

### 2. 克隆代码
```bash
# 如果是从Git仓库克隆
git clone <你的仓库地址> .

# 或者上传代码文件
# 可以使用scp、rsync等工具上传代码
```

### 3. 配置环境
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑环境配置
nano .env
```

**Ubuntu生产环境推荐配置 (.env)：**
```bash
# 服务器配置
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO
DEBUG=false
ENABLE_SCHEDULER=true

# 数据库配置 - 使用PostgreSQL
DATABASE_URL=postgresql://postgres:your_strong_password@postgres:5432/openharmony_news
POSTGRES_PASSWORD=your_strong_password_here

# Redis配置
REDIS_PASSWORD=your_redis_password_here

# 时区设置
TZ=Asia/Shanghai

# 安全配置
SECRET_KEY=your-super-secret-key-change-this-in-production

# 域名配置
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost
```

### 4. 准备SSL证书

**选项1：使用Let's Encrypt（推荐）**
```bash
# 安装Certbot
sudo apt install -y certbot

# 获取SSL证书（需要域名已指向服务器IP）
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# 复制证书到项目目录
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

**选项2：使用自签名证书（仅测试）**
```bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=OpenHarmony/CN=your-domain.com"
```

### 5. 配置防火墙
```bash
# 启用UFW防火墙
sudo ufw enable

# 允许SSH（重要！）
sudo ufw allow ssh

# 允许HTTP和HTTPS
sudo ufw allow 80
sudo ufw allow 443

# 可选：允许直接访问API（开发调试用）
sudo ufw allow 8001

# 查看防火墙状态
sudo ufw status
```

### 6. 部署应用
```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 初始化部署
./deploy.sh install

# 启动生产环境
./deploy.sh start prod

# 检查服务状态
./deploy.sh status
./deploy.sh health
```

## Ubuntu服务器优化

### 1. 系统资源监控
```bash
# 安装系统监控工具
sudo apt install -y htop iotop nethogs

# 实时监控
htop                # CPU和内存使用
iotop               # 磁盘I/O
nethogs             # 网络使用
docker stats        # 容器资源使用
```

### 2. 日志管理
```bash
# 配置日志轮转
sudo nano /etc/logrotate.d/openharmony

# 添加以下内容：
/opt/openharmony-server/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    notifempty
    create 644 $USER $USER
}
```

### 3. 系统服务配置
```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/openharmony.service
```

**systemd服务配置：**
```ini
[Unit]
Description=OpenHarmony API Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/openharmony-server
ExecStart=/opt/openharmony-server/deploy.sh start prod
ExecStop=/opt/openharmony-server/deploy.sh stop prod
TimeoutStartSec=0
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable openharmony.service

# 现在可以使用systemctl管理服务
sudo systemctl start openharmony
sudo systemctl status openharmony
```

### 4. 定时任务设置
```bash
# 编辑crontab
crontab -e

# 添加以下任务：
# 每天凌晨2点备份数据
0 2 * * * cd /opt/openharmony-server && ./deploy.sh backup

# 每周日凌晨清理Docker
0 3 * * 0 docker system prune -f

# 每月更新SSL证书（如果使用Let's Encrypt）
0 4 1 * * sudo certbot renew --quiet && cd /opt/openharmony-server && sudo cp /etc/letsencrypt/live/your-domain.com/*.pem ssl/ && ./deploy.sh restart prod
```

## 常见Ubuntu问题解决

### 1. 权限问题
```bash
# 修复Docker权限
sudo usermod -aG docker $USER
newgrp docker

# 修复文件权限
sudo chown -R $USER:$USER /opt/openharmony-server
chmod +x deploy.sh
```

### 2. 端口占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
sudo netstat -tlnp | grep :8001

# 停止占用端口的服务
sudo systemctl stop apache2  # 如果安装了Apache
sudo systemctl stop nginx    # 如果安装了系统Nginx
```

### 3. 内存不足
```bash
# 创建交换文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用交换
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 4. 磁盘空间不足
```bash
# 清理系统
sudo apt autoremove -y
sudo apt autoclean

# 清理Docker
docker system prune -a -f
docker volume prune -f

# 清理日志
sudo journalctl --vacuum-time=30d
```

## 性能调优

### 1. Docker配置优化
```bash
# 编辑Docker配置
sudo nano /etc/docker/daemon.json

# 添加以下配置：
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  },
  "storage-driver": "overlay2"
}

# 重启Docker服务
sudo systemctl restart docker
```

### 2. 内核参数优化
```bash
# 编辑系统参数
sudo nano /etc/sysctl.conf

# 添加以下优化参数：
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
vm.max_map_count = 262144
fs.file-max = 2097152

# 应用参数
sudo sysctl -p
```

这样配置后，你的Ubuntu服务器就完全可以运行这套Docker部署方案了！有任何Ubuntu相关的问题都可以随时问我。