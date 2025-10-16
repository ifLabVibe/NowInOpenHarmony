# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NowInOpenHarmony Server is a Python-based backend service that aggregates OpenHarmony-related news and information from various sources. It provides RESTful APIs for a companion client application with sophisticated caching, scheduling, and web scraping capabilities.

## Common Development Tasks

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment (recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Server

```bash
# Development server with enhanced startup script (recommended)
python run.py

# Direct FastAPI development server with hot reload
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Docker deployment
docker-compose up -d
docker-compose down
```

### Testing and Quality Assurance

```bash
# Manual API testing - service endpoints
http://localhost:8001/health          # Health check with cache status
http://localhost:8001/docs            # Swagger UI documentation
http://localhost:8001/redoc           # ReDoc documentation

# Test specific crawler functionality manually
# Note: Currently no automated test suite exists
```

### Environment Configuration

```bash
# Environment variables (can be set via .env file or system environment)
HOST=0.0.0.0                         # Server bind address
PORT=8001                            # Server port
DATABASE_URL=sqlite:///./openharmony_news.db  # Database connection
LOG_LEVEL=INFO                       # Logging level (DEBUG, INFO, WARNING, ERROR)
ENABLE_SCHEDULER=true                # Enable background task scheduler
```

### Docker Deployment

```bash
# 完整Docker部署 - 使用部署脚本（推荐）
./deploy.sh install          # 初始化部署环境
./deploy.sh start            # 启动开发环境
./deploy.sh start prod       # 启动生产环境
./deploy.sh status           # 查看服务状态
./deploy.sh logs app         # 查看应用日志
./deploy.sh health           # 健康检查
./deploy.sh stop             # 停止服务

# 手动Docker部署
docker-compose up -d                    # 开发环境部署
docker-compose -f docker-compose.prod.yml up -d  # 生产环境部署
docker-compose down                     # 停止服务
docker-compose logs -f app              # 查看日志

# Docker镜像构建
docker build -t openharmony-server .
docker run -p 8001:8001 openharmony-server
```

### Database Management

```bash
# Database is automatically initialized on startup
# SQLite file location: ./data/openharmony_news.db (Docker volume)
# For PostgreSQL, update DATABASE_URL in .env file

# Docker数据库管理
docker-compose exec postgres psql -U postgres -d openharmony_news
./deploy.sh backup           # 数据备份
```

## Architecture Overview

### Multi-Layer Architecture

1. **API Layer** (`api/`): FastAPI routers handling HTTP requests
   - `news.py`: News-related endpoints with pagination, search, filtering
   - `banner.py`: Mobile banner image endpoints

2. **Service Layer** (`services/`): Business logic and data aggregation
   - `news_service.py`: Unified news service managing multiple sources
   - `openharmony_news_crawler.py`: Official OpenHarmony website news scraper
   - `openharmony_blog_crawler.py`: Technical blog scraper
   - `mobile_banner_crawler.py`: Mobile banner scraper

3. **Core Layer** (`core/`): Infrastructure and cross-cutting concerns
   - `cache.py`: Thread-safe memory cache with status management
   - `scheduler.py`: APScheduler-based task scheduling
   - `database.py`: SQLAlchemy database connection management
   - `config.py`: Pydantic settings management

4. **Models Layer** (`models/`): Pydantic data models
   - `news.py`: News article and response models
   - `banner.py`: Banner image models

### Key Architectural Patterns

**Multi-Threaded Crawling**: All scrapers run in ThreadPoolExecutor to prevent blocking main API threads. Status transitions are carefully managed to ensure non-blocking operation.

**Cache System**: Memory-based cache with three states (READY/PREPARING/ERROR) that allows background updates without service interruption. Updates only set PREPARING status during database writes.

**Service Status Management**: Each service maintains independent status that reflects crawler health and data freshness.

### Configuration System

Configuration is managed through `core/config.py` using Pydantic Settings with `.env` file support. Key configurations:

- **Database**: SQLite for development, PostgreSQL for production
- **Scheduler**: 30-minute cache updates, daily full crawls at 2 AM
- **Crawler**: Configurable delays, timeouts, and retry mechanisms
- **Cache**: Enable/disable caching and initial load behavior

### API Patterns

All API endpoints follow consistent patterns:
- Pagination with `page` and `page_size` parameters
- Search and filtering support
- Standardized error responses
- Cache-aware responses with status information

## Development Guidelines

### Adding New Data Sources

1. Create crawler class in `services/` implementing scraping logic
2. Add data source to `NewsSource` enum in `news_service.py`
3. Integrate into unified service or create dedicated endpoints
4. Update scheduler configuration if needed

### Adding New API Endpoints

1. Create router in `api/` with appropriate prefix
2. Define request/response models in `models/`
3. Register router in `main.py`
4. Follow existing patterns for pagination, error handling

### Error Handling

- Use HTTPException with appropriate status codes
- Log errors with context using structured logging
- Return meaningful error messages to clients
- Handle service status appropriately in cache-aware endpoints

### Testing Approach

Current testing is limited to manual scripts. When adding features:
- Test date parsing with various formats
- Verify multi-threading doesn't cause race conditions
- Check cache behavior during updates
- Validate API responses match expected schemas