# Copyright (c) 2025 XBXyftx
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import asyncio

from core.config import settings
from core.logging_config import setup_logging
from core.database import init_database
from core.scheduler import start_scheduler, stop_scheduler, get_scheduler
from core.cache import init_cache, get_news_cache

# 导入API路由
from api import news, banner

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NowInOpenHarmony项目后端API服务",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Process Time: {process_time:.3f}s"
    )
    
    return response

# 异常处理中间件
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常处理: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )

# 注册路由
app.include_router(news.router)
app.include_router(banner.router)

# 根路径
@app.get("/")
async def root():
    return {
        "message": "NowInOpenHarmony API服务",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康检查
@app.get("/health")
async def health_check():
    try:
        # 获取缓存状态
        cache = get_news_cache()
        cache_status = cache.get_status()
        
        return {
            "status": "healthy" if cache_status["status"] != "error" else "degraded",
            "timestamp": time.time(),
            "version": settings.app_version,
            "cache_status": cache_status["status"],
            "cache_count": cache_status["cache_count"]
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "version": settings.app_version,
            "error": str(e)
        }

# API健康检查（服务状态检测接口）
@app.get("/api/health")
async def api_health_check():
    """
    服务状态检测接口 - 检测所有新闻源的状态
    """
    try:
        from services.news_service import get_news_service
        
        # 获取缓存状态
        cache = get_news_cache()
        cache_status = cache.get_status()
        
        # 获取新闻服务信息
        news_service = get_news_service()
        news_sources = news_service.get_news_sources()
        
        # 判断整体服务状态
        overall_status = "healthy"
        if cache_status["status"] == "error":
            overall_status = "unhealthy"
        elif cache_status["status"] == "preparing":
            overall_status = "preparing"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "version": settings.app_version,
            "services": {
                "cache": {
                    "status": cache_status["status"],
                    "cache_count": cache_status["cache_count"],
                    "last_update": cache_status.get("last_update"),
                    "error_message": cache_status.get("error_message")
                },
                "news_sources": news_sources
            },
            "endpoints": {
                "openharmony_news": "/api/news/openharmony",
                "all_news": "/api/news/",
                "manual_crawl": "/api/news/crawl",
                "service_status": "/api/news/status/info",
                "banner_images": "/api/banner/",
                "download_banners": "/api/banner/download",
                "banner_urls": "/api/banner/urls",
                "banner_status": "/api/banner/status"
            }
        }
    except Exception as e:
        logger.error(f"API健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "version": settings.app_version,
            "error": str(e)
        }

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("应用启动中...")
    
    # 初始化数据库
    try:
        init_database()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    
    # 初始化缓存
    try:
        init_cache()
        logger.info("缓存初始化完成")
    except Exception as e:
        logger.error(f"缓存初始化失败: {e}")
        raise
    
    # 启动定时任务调度器
    if settings.enable_scheduler:
        try:
            start_scheduler()
            logger.info("定时任务调度器启动完成")
        except Exception as e:
            logger.error(f"定时任务调度器启动失败: {e}")
    
    # 执行初始缓存加载
    try:
        logger.info("开始执行初始缓存加载...")
        scheduler = get_scheduler()
        await scheduler.initial_cache_load()
        logger.info("初始缓存加载完成")
    except Exception as e:
        logger.error(f"初始缓存加载失败: {e}")
        # 不抛出异常，让服务继续启动
    
    logger.info("应用启动完成")

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用关闭中...")
    
    # 停止定时任务调度器
    if settings.enable_scheduler:
        try:
            stop_scheduler()
            logger.info("定时任务调度器已停止")
        except Exception as e:
            logger.error(f"停止定时任务调度器失败: {e}")
    
    logger.info("应用关闭完成")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )