# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NowInOpenHarmony Server is a Python-based backend service that aggregates OpenHarmony-related news and information from various sources. It provides RESTful APIs for a companion client application with sophisticated caching, scheduling, and web scraping capabilities.

## Common Development Tasks

### Running the Server

```bash
# Development server with enhanced startup script
python run.py

# Direct FastAPI development server with hot reload
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Docker deployment
docker-compose up -d
docker-compose down
```

### Testing

```bash
# Test date parsing functionality
python test_date_parsing.py

# Manual API testing - service endpoints
http://localhost:8001/health          # Health check with cache status
http://localhost:8001/docs            # Swagger UI documentation
http://localhost:8001/redoc           # ReDoc documentation
```

### Database Management

```bash
# Database is automatically initialized on startup
# SQLite file location: ./openharmony_news.db
# For PostgreSQL, update DATABASE_URL in .env file
```

## Architecture Overview

### Multi-Layer Architecture

1. **API Layer** (`api/`): FastAPI routers handling HTTP requests
   - `news.py`: News-related endpoints with pagination, search, filtering
   - `banner.py`: Mobile banner image endpoints

2. **Service Layer** (`services/`): Business logic and data aggregation
   - `news_service.py`: Unified news service managing multiple sources
   - `openharmony_crawler.py`: Official OpenHarmony website scraper
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