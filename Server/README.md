# NowInOpenHarmony 后端服务

## 项目概述

NowInOpenHarmony 是一个聚合 OpenHarmony 相关资讯的应用后端服务。该系统从 OpenHarmony 官方网站、技术博客等多源采集新闻数据，进行结构化处理，并对外提供 RESTful 风格的数据接口供 OpenHarmony 客户端调用。采用多线程爬虫架构，支持非阻塞数据更新和智能缓存管理。

## 技术栈

- **编程语言**: Python 3.8+
- **Web框架**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **任务调度**: APScheduler
- **爬虫框架**: Requests + BeautifulSoup + Selenium WebDriver
- **缓存机制**: 内存缓存 + 线程安全 + 状态管理
- **部署**: Docker + Docker Compose + Uvicorn

## 功能特性

### 数据采集模块
- 从 OpenHarmony 官方网站采集新闻和动态
- 从 OpenHarmony 技术博客采集技术文章
- 支持移动端 Banner 图片采集（传统版 + 增强版）
- 多源数据聚合（官方新闻 + 技术博客 + 轮播图）
- 智能数据去重和清洗
- 多线程并发爬虫，支持失败重试机制

### 缓存机制
- **启动预热**: 服务启动时自动执行一次数据爬取（后台线程执行）
- **精细状态管理**: 只有在写入数据库时才设为"准备中"，读取时设为"已准备"
- **后台更新**: 每30分钟自动更新缓存数据（后台线程执行）
- **线程安全**: 使用可重入锁保证数据一致性
- **无缝切换**: 更新时仍使用旧数据，更新完成后切换
- **非阻塞**: 爬虫任务在独立线程执行，不阻塞主服务线程

### API接口模块
- 新闻列表和详情接口
- 支持分页、分类和搜索
- 手动触发爬取接口
- 服务状态监控接口
- 缓存刷新接口

### 定时任务模块
- 每30分钟自动更新缓存
- 每天凌晨2点执行完整爬取
- 支持失败重试机制

### 数据存储模块
- 结构化数据存储
- 支持分类存储
- 数据库索引优化

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
# 方式1: 使用启动脚本
python run.py

# 方式2: 直接使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 访问服务

- 服务地址: http://localhost:8001
- API文档: http://localhost:8001/docs
- 健康检查: http://localhost:8001/health

## API接口

### 新闻接口

- `GET /api/news/` - 获取新闻列表（支持分页、分类、搜索、全部返回）
- `GET /api/news/{article_id}` - 获取新闻详情
- `GET /api/news/openharmony` - 获取OpenHarmony官方新闻
- `GET /api/news/blog` - 获取OpenHarmony技术博客文章
- `POST /api/news/crawl` - 手动触发新闻爬取（支持指定来源）
- `GET /api/news/status/info` - 获取服务状态信息
- `POST /api/news/cache/refresh` - 手动刷新缓存

### 轮播图接口

- `GET /api/banner/mobile` - 获取手机版Banner图片URL列表
- `GET /api/banner/mobile/enhanced` - 增强版爬虫获取Banner图片
- `POST /api/banner/crawl` - 手动触发轮播图爬取
- `GET /api/banner/status` - 获取轮播图服务状态
- `DELETE /api/banner/cache/clear` - 清空轮播图缓存
- `GET /api/banner/cache` - 获取轮播图缓存详细信息

### 基础接口

- `GET /` - 服务信息
- `GET /health` - 健康检查（包含缓存状态）
- `GET /api/health` - 详细API健康检查

## 缓存机制详解

### 服务状态
- **preparing**: 数据更新中，服务暂时不可用
- **ready**: 服务就绪，可以正常访问
- **error**: 服务错误，需要检查日志

### 工作流程
1. **服务启动**: 立即启动HTTP服务，后台线程执行初始数据爬取
2. **爬虫执行**: 爬虫执行期间状态保持为"就绪"，使用现有数据响应请求
3. **数据写入**: 只有在写入数据库时才短暂设为"准备中"
4. **数据就绪**: 写入完成后立即恢复为"就绪"状态
5. **定时更新**: 每30分钟后台线程更新数据，遵循相同的精细状态管理
6. **非阻塞响应**: 整个过程中API接口始终可正常响应请求

### 测试缓存机制
```bash
# 测试日期解析功能
python test_date_parsing.py

# 测试多线程爬虫效果
python test_threading.py

# 测试精细状态管理
python test_fine_grained_status.py

# 演示多线程改进效果
python demo_threading_improvement.py

# 演示精细状态管理
python demo_fine_grained_status.py
```

## 配置说明

### 环境变量

- `HOST`: 服务监听地址 (默认: 0.0.0.0)
- `PORT`: 服务端口 (默认: 8001)
- `RELOAD`: 是否启用热重载 (默认: false)
- `DATABASE_URL`: 数据库连接URL
- `LOG_LEVEL`: 日志级别 (默认: INFO)

### 配置文件

可以通过 `.env` 文件配置应用参数：

```env
# 应用配置
APP_NAME=NowInOpenHarmony API
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
DATABASE_URL=sqlite:///./openharmony_news.db

# 爬虫配置
CRAWLER_DELAY=1.0
CRAWLER_TIMEOUT=10
MAX_RETRIES=3

# 定时任务配置
ENABLE_SCHEDULER=true
CACHE_UPDATE_INTERVAL=30
FULL_CRAWL_HOUR=2

# 缓存配置
ENABLE_CACHE=true
CACHE_INITIAL_LOAD=true
```

## 项目结构

```
Server/
├── api/                    # API接口模块
│   ├── __init__.py
│   ├── news.py            # 新闻接口（完整CRUD + 多源支持）
│   └── banner.py          # 轮播图接口（移动端Banner采集）
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── cache.py           # 缓存管理（内存缓存 + 状态管理）
│   ├── config.py          # 配置管理（Pydantic Settings）
│   ├── database.py        # 数据库管理（SQLAlchemy）
│   ├── logging_config.py  # 日志配置（结构化日志）
│   └── scheduler.py       # 定时任务调度（APScheduler）
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── news.py            # 新闻相关模型（文章 + 响应）
│   └── banner.py          # 轮播图模型（Banner响应）
├── services/               # 服务层（爬虫和业务逻辑）
│   ├── __init__.py
│   ├── news_service.py           # 新闻服务统一管理
│   ├── openharmony_crawler.py    # OpenHarmony官网爬虫
│   ├── openharmony_blog_crawler.py # OpenHarmony技术博客爬虫
│   ├── openharmony_image_crawler.py # OpenHarmony图片爬虫
│   ├── mobile_banner_crawler.py  # 移动端轮播图爬虫（传统版）
│   └── enhanced_mobile_banner_crawler.py # 增强版轮播图爬虫（Selenium）
├── logs/                   # 日志文件目录
├── downloads/              # 下载文件目录（图片等）
├── main.py                 # FastAPI应用入口
├── run.py                  # 增强版启动脚本（IP检测等）
├── test_date_parsing.py    # 日期解析测试脚本
├── requirements.txt        # Python依赖
├── Dockerfile             # Docker镜像配置
├── docker-compose.yml     # 容器编排配置
└── README.md              # 项目说明
```

## 架构增强特性

### 多源数据聚合
- **官方新闻**: OpenHarmony官网新闻和动态
- **技术博客**: OpenHarmony技术博客文章
- **轮播图**: 移动端Banner图片采集（双爬虫架构）
- **统一服务**: NewsService统一管理多源数据

### 多线程爬虫架构
- **ThreadPoolExecutor**: 线程池管理爬虫任务
- **非阻塞执行**: 爬虫任务在后台线程执行
- **状态管理**: 精细状态控制，只在写入时设为"准备中"
- **并发安全**: 线程安全的缓存更新机制

### 轮播图双爬虫策略
- **传统爬虫**: Requests + BeautifulSoup，快速稳定
- **增强爬虫**: Selenium WebDriver，支持动态内容
- **智能回退**: 增强版失败时自动回退到传统版
- **图片下载**: 可选下载图片到本地存储

### 缓存状态管理
- **READY**: 服务就绪，数据可用
- **PREPARING**: 正在更新，短暂状态
- **ERROR**: 服务错误，需要检查日志
- **无缝切换**: 更新过程中保持服务可用

## 多线程改进

### 问题背景
原始实现中，爬虫任务在主线程中同步执行，导致：
- 服务启动时需要等待爬虫完成（6-7分钟）
- 定时更新期间API请求被阻塞
- 用户体验差，服务响应延迟

### 解决方案
采用多线程架构：
- **ThreadPoolExecutor**: 使用线程池管理爬虫任务
- **后台执行**: 爬虫任务在独立线程中执行
- **非阻塞响应**: 主服务线程立即响应API请求
- **状态管理**: 通过缓存状态反映爬虫进度

### 改进效果
- ✅ 服务启动后立即可以响应请求
- ✅ 爬虫执行期间API接口正常响应
- ✅ 支持并发请求，不会阻塞
- ✅ 精细状态管理：只有在写入数据库时才设为"准备中"

### 技术实现
```python
# 使用ThreadPoolExecutor执行爬虫任务
self.thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="CrawlerWorker")

# 提交任务到后台线程
future = self.thread_pool.submit(self._run_crawler_in_thread, "任务名称")

# 精细状态管理
def set_updating(self, is_updating: bool):
    if is_updating:
        self.set_status(ServiceStatus.PREPARING)  # 只在写入时设为准备中
    else:
        self.set_status(ServiceStatus.READY)      # 写入完成后立即恢复就绪
```

## 开发指南

### 添加新的数据源

1. 在 `services/` 目录下创建新的爬虫类，继承基础爬虫接口
2. 实现数据采集和解析逻辑，支持多线程执行
3. 在 `NewsSource` 枚举中添加新数据源
4. 在 `news_service.py` 中集成新数据源
5. 在 `scheduler.py` 中添加定时任务
6. 更新数据库模型（如需要）

### 添加新的API接口

1. 在 `api/` 目录下创建新的路由文件
2. 定义数据模型（如需要）
3. 在 `main.py` 中注册路由
4. 更新API文档

### 数据库迁移

当前使用 SQLite 进行开发，生产环境建议使用 PostgreSQL：

1. 安装 PostgreSQL 驱动: `pip install psycopg2-binary`
2. 更新 `DATABASE_URL` 环境变量
3. 运行数据库初始化脚本
