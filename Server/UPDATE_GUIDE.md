# 轮播图功能修复更新指南

## 问题诊断

之前的轮播图功能无法工作的原因：
- ❌ Selenium无法在Docker容器中找到Chromium浏览器
- ❌ 缺少Chromium运行时依赖库
- ❌ 未指定ChromeDriver路径

## 本次修复内容

### 1. Selenium配置修复 (services/enhanced_mobile_banner_crawler.py)
```python
# 添加Chromium二进制文件路径
options.binary_location = "/usr/bin/chromium"

# 指定ChromeDriver路径
service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)
```

### 2. Docker依赖完善 (Dockerfile)
添加了Chromium运行所需的18个依赖库：
- fonts-liberation (字体支持)
- libasound2 (音频库)
- libatk-bridge2.0-0, libatk1.0-0 (无障碍工具包)
- libatspi2.0-0 (辅助技术)
- libcups2 (打印支持)
- libdbus-1-3 (进程间通信)
- libdrm2, libgbm1 (图形驱动)
- libgtk-3-0 (GTK图形库)
- libnspr4, libnss3 (网络安全库)
- libwayland-client0 (Wayland显示协议)
- libxcomposite1, libxdamage1, libxfixes3, libxkbcommon0, libxrandr2 (X11扩展)
- xdg-utils (桌面集成工具)

## 部署步骤

### 步骤1：上传新版本到服务器

```bash
# 在本地（Windows）执行
scp d:\AITrainingCamp\NowInOpenHarmony\dist\openharmony-server_20251012_200140.tar.gz \
    root@113.47.8.204:/root/deploy/
```

### 步骤2：在服��器上解压

```bash
# SSH登录到服务器
ssh root@113.47.8.204

# 进入部署目录
cd /root/deploy/

# 解压新版本
tar -xzf openharmony-server_20251012_200140.tar.gz
cd openharmony-server_20251012_200140
```

### 步骤3：停止旧容器

```bash
# 查看运行中的容器
docker ps

# 停止并删除旧容器
docker stop NowInOpenHarmonyServer
docker rm NowInOpenHarmonyServer

# （可选）删除旧镜像以确保使用新配置
docker rmi openharmony-server:latest
```

### 步骤4：重新构建镜像

```bash
# 确保deploy.sh可执行
chmod +x deploy.sh

# 安装/重新构建（会重新构建Docker镜像）
./deploy.sh install
```

**注意**：由于添加了很多新依赖，这次构建会比之前慢，大约需要5-10分钟。

### 步骤5：启动服务

```bash
# 启动生产环境
./deploy.sh start prod

# 或启动开发环境
./deploy.sh start
```

### 步骤6：验证服务

```bash
# 查看容器状态
./deploy.sh status

# 查看日志
./deploy.sh logs app

# 健康检查
./deploy.sh health
```

### 步骤7：测试轮���图接口

```bash
# 等待约2-3分钟让服务完全启动

# 测试轮播图接口
curl http://localhost:8001/api/banner/mobile

# 查看轮播图状态
curl http://localhost:8001/api/banner/status

# 如果还是没数据，手动触发爬取
curl -X POST http://localhost:8001/api/banner/crawl?use_enhanced=true
```

## 预期结果

成功后应该看到：

```json
{
  "success": true,
  "images": [
    {
      "id": "...",
      "url": "https://images.openharmony.cn/...",
      "filename": "4.1releas手机.jpg",
      "source": "OpenHarmony-Enhanced-Mobile-Banner",
      "method": "selenium"
    },
    ...
  ],
  "total": 4,
  "message": "成功获取轮播图",
  "timestamp": "2025-10-12T..."
}
```

## 故障排查

### 如果轮播图仍然失败

1. **查看详细日志**
```bash
docker logs NowInOpenHarmonyServer | grep -A 20 "banner"
docker logs NowInOpenHarmonyServer | grep -A 20 "Selenium"
```

2. **进入容器检查**
```bash
# 进入容器
docker exec -it NowInOpenHarmonyServer bash

# 检查chromium是否存在
which chromium
ls -la /usr/bin/chromium

# 检查chromedriver是否存在
which chromedriver
ls -la /usr/bin/chromedriver

# 测试chromium启动
chromium --version
chromedriver --version

# 退出容器
exit
```

3. **查看错误信息**
```bash
# 查看最近50行日志中的ERROR
docker logs NowInOpenHarmonyServer 2>&1 | grep ERROR | tail -50
```

4. **尝试强制重新爬取**
```bash
# 清空缓存
curl -X DELETE http://localhost:8001/api/banner/cache/clear

# 强制爬取
curl -X POST "http://localhost:8001/api/banner/crawl?use_enhanced=true"
```

### 如果容器构建失败

```bash
# 查看构建日志
docker build -t openharmony-server:latest . 2>&1 | tee build.log

# 检查是否缺少依赖
cat build.log | grep -i "error\|failed"
```

## 版本信息

- **版本号**: 20251012_200140
- **修复内容**: Selenium在Docker中的Chromium支持
- **包大小**: 56KB
- **MD5**: 参见 openharmony-server_20251012_200140.tar.gz.md5

## 回滚方案

如果新版本有问题，可以回滚到之前的版本：

```bash
# 停止新容器
docker stop NowInOpenHarmonyServer
docker rm NowInOpenHarmonyServer

# 使用旧镜像启动（如果没删除）
docker run -d --name NowInOpenHarmonyServer \
    -p 32771:8001 \
    openharmony-server:old

# 或重新部署旧版本
cd /root/deploy/openharmony-server_20251012_175648
./deploy.sh start prod
```

## 技术说明

### 为什么需要这些依赖？

- **fonts-liberation**: 提供Web字体支持，确保页面正确渲染
- **libasound2**: 音频库，虽然headless模式不播放声音，但Chromium需要
- **libgtk-3-0**: GTK图形库，用于渲染UI元素
- **libnss3**: 网络安全服务库，处理HTTPS连接
- **libgbm1**: 图形缓冲管理，GPU加速渲染
- **其他X11库**: 支持无头模式下的图形渲染

### 为什么本地测试正常，服务器失败？

- 本地Windows系统有完整的Chrome浏览器和驱动
- Docker容器是最小化的Linux环境，需要显式安装所有依赖
- 容器中使用的是开源Chromium，不是Chrome

### 轮播图爬取原理

1. 页面使用Vue.js + Element UI的el-carousel组件
2. 轮播图通过JavaScript动态加载
3. 传统requests无法获取JS渲染的内容
4. 必须使用Selenium模拟真实浏览器访问

## 联系与支持

如有问题，请查看：
- 项目文档: [CLAUDE.md](./CLAUDE.md)
- 部署文档: [DEPLOY_TO_SERVER.md](./DEPLOY_TO_SERVER.md)
- GitHub Issues: https://github.com/your-repo/issues
