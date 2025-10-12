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

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
import logging
from datetime import datetime

from services.openharmony_news_crawler import OpenHarmonyNewsCrawler
from services.news_service import get_news_service, NewsSource
from models.news import NewsArticle, NewsResponse
from core.database import get_db
from core.scheduler import get_scheduler
from core.cache import get_news_cache, ServiceStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/", response_model=NewsResponse)
async def get_news(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="新闻分类"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    all: bool = Query(False, description="是否返回全部新闻不分页")
):
    """
    获取新闻列表，支持分页、分类和搜索
    
    参数说明：
    - page: 页码（当all=True时忽略）
    - page_size: 每页数量（当all=True时忽略）
    - category: 新闻分类过滤
    - search: 搜索关键词
    - all: 是否返回全部新闻不分页，为true时返回所有匹配的新闻
    """
    try:
        # 从缓存获取数据
        cache = get_news_cache()
        cache_status = cache.get_status()
        
        # 检查服务状态
        if cache_status["status"] == ServiceStatus.ERROR.value:
            raise HTTPException(
                status_code=503, 
                detail=f"服务暂时不可用: {cache_status.get('error_message', '未知错误')}"
            )
        
        # 如果服务正在准备中，返回提示信息
        if cache_status["status"] == ServiceStatus.PREPARING.value:
            return NewsResponse(
                articles=[],
                total=0,
                page=page,
                page_size=page_size,
                has_next=False,
                has_prev=False
            )
        
        # 从缓存获取数据
        if all:
            # 如果要返回全部数据，设置一个很大的page_size来获取所有数据
            result = cache.get_news(page=1, page_size=10000, 
                                  category=category, search=search)
            # 重新设置分页信息，表示这是全部数据
            result.page = 1
            result.page_size = result.total
            result.has_next = False
            result.has_prev = False
        else:
            # 正常分页逻辑
            result = cache.get_news(page=page, page_size=page_size, 
                                  category=category, search=search)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取新闻列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取新闻列表失败")

@router.get("/openharmony", response_model=NewsResponse)
async def get_openharmony_news(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取OpenHarmony官网最新资讯
    """
    try:
        # 从缓存获取数据，过滤OpenHarmony来源
        cache = get_news_cache()
        cache_status = cache.get_status()
        
        # 检查服务状态
        if cache_status["status"] == ServiceStatus.ERROR.value:
            raise HTTPException(
                status_code=503, 
                detail=f"服务暂时不可用: {cache_status.get('error_message', '未知错误')}"
            )
        
        # 如果服务正在准备中，返回提示信息
        if cache_status["status"] == ServiceStatus.PREPARING.value:
            return NewsResponse(
                articles=[],
                total=0,
                page=page,
                page_size=page_size,
                has_next=False,
                has_prev=False
            )
        
        # 从缓存获取数据，只返回OpenHarmony来源的文章
        result = cache.get_news(page=page, page_size=page_size, 
                              category="官方动态", search=search)
        
        # 过滤只保留OpenHarmony来源的文章
        filtered_articles = [
            article for article in result.articles 
            if getattr(article, 'source', None) == 'OpenHarmony'
        ]
        
        return NewsResponse(
            articles=filtered_articles,
            total=len(filtered_articles),
            page=page,
            page_size=page_size,
            has_next=len(filtered_articles) == page_size,
            has_prev=page > 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OpenHarmony官网新闻失败: {e}")
        raise HTTPException(status_code=500, detail="获取OpenHarmony官网新闻失败")

@router.get("/blog", response_model=NewsResponse)
async def get_openharmony_blog(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取OpenHarmony技术博客文章
    """
    try:
        # 从缓存获取数据，过滤技术博客来源
        cache = get_news_cache()
        cache_status = cache.get_status()
        
        # 检查服务状态
        if cache_status["status"] == ServiceStatus.ERROR.value:
            raise HTTPException(
                status_code=503, 
                detail=f"服务暂时不可用: {cache_status.get('error_message', '未知错误')}"
            )
        
        # 如果服务正在准备中，返回提示信息
        if cache_status["status"] == ServiceStatus.PREPARING.value:
            return NewsResponse(
                articles=[],
                total=0,
                page=page,
                page_size=page_size,
                has_next=False,
                has_prev=False
            )
        
        # 从缓存获取数据，只返回技术博客来源的文章
        result = cache.get_news(page=page, page_size=page_size, 
                              category="技术博客", search=search)
        
        # 过滤只保留OpenHarmony技术博客来源的文章
        filtered_articles = [
            article for article in result.articles 
            if getattr(article, 'source', None) == 'OpenHarmony技术博客'
        ]
        
        return NewsResponse(
            articles=filtered_articles,
            total=len(filtered_articles),
            page=page,
            page_size=page_size,
            has_next=len(filtered_articles) == page_size,
            has_prev=page > 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OpenHarmony技术博客失败: {e}")
        raise HTTPException(status_code=500, detail="获取OpenHarmony技术博客失败")


@router.post("/crawl")
async def crawl_news(
    source: NewsSource = Query(NewsSource.ALL, description="新闻来源"),
    limit: int = Query(10, ge=1, le=100, description="返回数量限制")
):
    """
    手动触发新闻爬取（会更新缓存）
    """
    try:
        # 获取调度器并执行手动爬取
        scheduler = get_scheduler()
        await scheduler.manual_crawl(source)
        
        return {
            "message": f"爬取任务已启动 - 来源: {source.value}",
            "source": source.value,
            "timestamp": datetime.now().isoformat(),
            "note": "爬取任务在后台执行，请稍后查看缓存更新状态"
        }
        
    except Exception as e:
        logger.error(f"启动爬取任务失败: {e}")
        raise HTTPException(status_code=500, detail="启动爬取任务失败")

@router.get("/{article_id}", response_model=NewsArticle)
async def get_article_detail(article_id: str):
    """
    获取单篇新闻详情
    """
    try:
        # 从缓存中查找指定文章
        cache = get_news_cache()
        cache_status = cache.get_status()
        
        # 检查服务状态
        if cache_status["status"] == ServiceStatus.ERROR.value:
            raise HTTPException(
                status_code=503, 
                detail=f"服务暂时不可用: {cache_status.get('error_message', '未知错误')}"
            )
        
        # 获取所有文章并查找指定ID
        all_news = cache.get_news(page=1, page_size=1000)
        for article in all_news.articles:
            if article.id == article_id:
                return article
        
        # 如果没找到，返回404
        raise HTTPException(status_code=404, detail="文章不存在")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取文章详情失败")

@router.get("/status/info")
async def get_service_status():
    """
    获取服务状态信息
    """
    try:
        cache = get_news_cache()
        status_info = cache.get_status()
        
        # 获取新闻服务信息
        news_service = get_news_service()
        news_sources = news_service.get_news_sources()
        
        return {
            "service_status": status_info,
            "news_sources": news_sources,
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "all_news": "/api/news/",
                "openharmony_news": "/api/news/openharmony",
                "openharmony_blog": "/api/news/blog",
                "news_detail": "/api/news/{article_id}",
                "manual_crawl": "/api/news/crawl",
                "service_status": "/api/news/status/info",
                "cache_refresh": "/api/news/cache/refresh"
            }
        }
        
    except Exception as e:
        logger.error(f"获取服务状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取服务状态失败")

@router.post("/cache/refresh")
async def refresh_cache():
    """
    手动刷新缓存
    """
    try:
        # 获取调度器并执行初始缓存加载
        scheduler = get_scheduler()
        await scheduler.initial_cache_load()
        
        return {
            "message": "缓存刷新成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"刷新缓存失败: {e}")
        raise HTTPException(status_code=500, detail="刷新缓存失败")