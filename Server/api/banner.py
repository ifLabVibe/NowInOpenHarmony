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

from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional, List
import logging
from datetime import datetime
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from services.mobile_banner_crawler import MobileBannerCrawler
from services.enhanced_mobile_banner_crawler import EnhancedMobileBannerCrawler
from models.banner import BannerResponse
from core.cache import get_banner_cache
from core.scheduler import get_scheduler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/banner", tags=["banner"])

# 全局线程池和爬虫缓存
_thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="BannerCrawler")
_last_banner_images: List[str] = []
_crawl_lock = threading.Lock()

@router.get("/mobile", response_model=BannerResponse)
async def get_mobile_banners(
    force_crawl: bool = Query(False, description="是否强制重新爬取")
):
    """
    获取OpenHarmony官网手机版Banner图片URL列表
    
    参数说明：
    - force_crawl: 是否强制重新爬取（否则返回缓存结果）
    """
    try:
        banner_cache = get_banner_cache()
        cache_status = banner_cache.get_status()
        
        # 检查缓存状态
        if cache_status["status"] == "error":
            raise HTTPException(
                status_code=503, 
                detail=f"轮播图服务错误: {cache_status.get('error_message', '未知错误')}"
            )
        
        # 如果服务正在准备中且不强制爬取，返回提示信息
        if cache_status["status"] == "preparing" and not force_crawl:
            return BannerResponse(
                success=False,
                images=[],
                total=0,
                message="轮播图服务正在准备中，请稍后再试或使用force_crawl=true强制爬取"
            )
        
        # 如果有缓存数据且不强制爬取，返回缓存结果
        if not force_crawl and cache_status["cache_count"] > 0:
            cached_images = banner_cache.get_banner_images()
            image_urls = [img.get('url', '') for img in cached_images if img.get('url')]
            
            logger.info("📋 返回缓存的Banner图片URL列表")
            return BannerResponse(
                success=True,
                images=image_urls,
                total=len(image_urls),
                message=f"获取手机版Banner图片成功（缓存），共 {len(image_urls)} 张"
            )
        
        logger.info("🚀 开始爬取手机版Banner图片URL")
        
        # 在线程池中执行爬取任务
        loop = asyncio.get_event_loop()
        banner_images = await loop.run_in_executor(
            _thread_pool, 
            _crawl_mobile_banners
        )
        
        if not banner_images:
            return BannerResponse(
                success=False,
                images=[],
                total=0,
                message="未找到任何Banner图片"
            )
        
        # 提取图片URL列表
        image_urls = [img.get('url', '') for img in banner_images if img.get('url')]
        
        # 更新缓存
        banner_cache.update_cache(banner_images)
        
        logger.info(f"✅ Banner爬取完成，共获取 {len(image_urls)} 张图片")
        
        return BannerResponse(
            success=True,
            images=image_urls,
            total=len(image_urls),
            message=f"获取手机版Banner图片成功，共 {len(image_urls)} 张"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取Banner图片失败: {e}", exc_info=True)
        return BannerResponse(
            success=False,
            images=[],
            total=0,
            message=f"获取Banner图片失败: {str(e)}"
        )

@router.get("/mobile/enhanced", response_model=BannerResponse)
async def get_mobile_banners_enhanced(
    force_crawl: bool = Query(False, description="是否强制重新爬取"),
    download_images: bool = Query(False, description="是否下载图片到本地")
):
    """
    使用增强版爬虫获取OpenHarmony官网手机版Banner图片
    
    参数说明：
    - force_crawl: 是否强制重新爬取（否则返回缓存结果）
    - download_images: 是否下载图片到本地
    """
    try:
        logger.info("🚀 使用增强版爬虫获取手机版Banner图片")
        
        # 在线程池中执行增强版爬取任务
        loop = asyncio.get_event_loop()
        banner_images = await loop.run_in_executor(
            _thread_pool, 
            _crawl_enhanced_banners,
            download_images
        )
        
        if not banner_images:
            return BannerResponse(
                success=False,
                images=[],
                total=0,
                message="增强版爬虫未找到任何Banner图片"
            )
        
        # 提取图片URL列表
        image_urls = [img.get('url', '') for img in banner_images if img.get('url')]
        
        logger.info(f"✅ 增强版Banner爬取完成，共获取 {len(image_urls)} 张图片")
        
        return BannerResponse(
            success=True,
            images=image_urls,
            total=len(image_urls),
            message=f"增强版爬虫获取手机版Banner图片成功，共 {len(image_urls)} 张"
        )
        
    except Exception as e:
        logger.error(f"❌ 增强版Banner爬虫失败: {e}", exc_info=True)
        return BannerResponse(
            success=False,
            images=[],
            total=0,
            message=f"增强版Banner爬虫失败: {str(e)}"
        )

def _crawl_enhanced_banners(download_images: bool = False) -> list:
    """
    同步执行增强版Banner爬取任务
    """
    try:
        logger.info("🔄 执行增强版Banner爬取任务")
        
        enhanced_crawler = EnhancedMobileBannerCrawler()
        banner_images = enhanced_crawler.crawl_mobile_banners(
            download_images=download_images,
            save_directory="downloads/api_banners" if download_images else ""
        )
        
        logger.info(f"✅ 增强版Banner爬取任务完成，获取 {len(banner_images)} 张图片")
        return banner_images
        
    except Exception as e:
        logger.error(f"❌ 增强版Banner爬取任务执行失败: {e}", exc_info=True)
        return []

def _crawl_mobile_banners() -> list:
    """
    同步执行Banner爬取任务
    优先使用增强版爬虫，失败时回退到传统爬虫
    """
    try:
        logger.info("🔄 执行Banner爬取任务")
        
        # 优先尝试增强版爬虫
        try:
            logger.info("🚀 尝试使用增强版爬虫...")
            enhanced_crawler = EnhancedMobileBannerCrawler()
            banner_images = enhanced_crawler.crawl_mobile_banners(
                download_images=False,  # 不下载图片，只获取URL
                save_directory=""
            )
            
            if banner_images:
                logger.info(f"✅ 增强版爬虫成功，获取 {len(banner_images)} 张图片")
                return banner_images
            else:
                logger.warning("⚠️ 增强版爬虫返回空结果，尝试传统爬虫")
                
        except Exception as enhanced_error:
            logger.warning(f"⚠️ 增强版爬虫失败: {enhanced_error}")
            logger.info("🔄 回退到传统爬虫...")
        
        # 回退到传统爬虫
        try:
            crawler = MobileBannerCrawler()
            banner_images = crawler.crawl_mobile_banners(
                download_images=False,  # 不下载图片，只获取URL
                save_directory=""
            )
            
            logger.info(f"✅ 传统爬虫完成，获取 {len(banner_images)} 张图片")
            return banner_images
            
        except Exception as traditional_error:
            logger.error(f"❌ 传统爬虫也失败: {traditional_error}")
            raise traditional_error
        
    except Exception as e:
        logger.error(f"❌ Banner爬取任务执行失败: {e}", exc_info=True)
        return []

@router.get("/status")
async def get_banner_status():
    """
    获取轮播图服务状态
    """
    try:
        banner_cache = get_banner_cache()
        status = banner_cache.get_status()
        
        # 添加调度器信息
        scheduler = get_scheduler()
        jobs = scheduler.get_jobs()
        banner_jobs = [job for job in jobs if 'banner' in job.id.lower()]
        
        return {
            "service": "banner",
            "cache_status": status,
            "scheduler_jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                } for job in banner_jobs
            ],
            "api_endpoints": {
                "mobile_banners": "/api/banner/mobile",
                "enhanced_banners": "/api/banner/mobile/enhanced",
                "status": "/api/banner/status",
                "manual_crawl": "/api/banner/crawl",
                "clear_cache": "/api/banner/cache/clear",
                "cache_info": "/api/banner/cache"
            },
            "status_explanation": {
                "preparing": "轮播图服务正在准备中，首次爬取尚未完成或当前正在更新",
                "ready": "轮播图服务就绪，可以正常获取轮播图数据",
                "error": "轮播图服务出现错误，需要检查日志或手动重新爬取"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取轮播图状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取轮播图状态失败: {str(e)}")

@router.post("/crawl")
async def manual_banner_crawl(
    use_enhanced: bool = Query(True, description="是否使用增强版爬虫"),
    download_images: bool = Query(False, description="是否下载图片到本地")
):
    """
    手动触发轮播图爬取任务
    """
    try:
        logger.info(f"🚀 手动触发轮播图爬取 - 增强版: {use_enhanced}, 下载: {download_images}")
        
        # 触发调度器的手动爬取任务
        scheduler = get_scheduler()
        await scheduler.manual_banner_crawl()
        
        # 同时执行一次API爬取来立即返回结果
        if use_enhanced:
            loop = asyncio.get_event_loop()
            banner_images = await loop.run_in_executor(
                _thread_pool, 
                _crawl_enhanced_banners,
                download_images
            )
        else:
            loop = asyncio.get_event_loop()
            banner_images = await loop.run_in_executor(
                _thread_pool, 
                _crawl_mobile_banners
            )
        
        # 提取图片URL列表
        image_urls = [img.get('url', '') for img in banner_images if img.get('url')]
        
        return {
            "success": True,
            "message": f"手动爬取完成，共获取 {len(image_urls)} 张图片",
            "images": image_urls,
            "total": len(image_urls),
            "used_enhanced": use_enhanced,
            "downloaded": download_images,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 手动轮播图爬取失败: {e}")
        raise HTTPException(status_code=500, detail=f"手动轮播图爬取失败: {str(e)}")

@router.delete("/cache/clear")
async def clear_banner_cache():
    """
    清空轮播图缓存
    """
    try:
        banner_cache = get_banner_cache()
        
        # 清空缓存
        with banner_cache._cache_lock:
            original_count = len(banner_cache._cache)
            banner_cache._cache.clear()
            banner_cache._last_update = None
            banner_cache._update_count = 0
            
        logger.info(f"🗑️ 轮播图缓存已清空，原有 {original_count} 张图片")
        
        return {
            "success": True,
            "message": f"轮播图缓存已清空，原有 {original_count} 张图片",
            "cleared_count": original_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 清空轮播图缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空轮播图缓存失败: {str(e)}")

@router.get("/cache")
async def get_banner_cache_info():
    """
    获取轮播图缓存详细信息
    """
    try:
        banner_cache = get_banner_cache()
        
        with banner_cache._cache_lock:
            cache_data = banner_cache._cache.copy()
        
        # 提取缓存中的图片信息
        cache_summary = []
        for item in cache_data:
            cache_summary.append({
                "url": item.get("url", ""),
                "alt": item.get("alt", ""),
                "filename": item.get("filename", ""),
                "extracted_at": item.get("extracted_at", ""),
                "source": item.get("source", "")
            })
        
        status = banner_cache.get_status()
        
        return {
            "cache_status": status,
            "cached_images": cache_summary,
            "summary": {
                "total_images": len(cache_data),
                "last_update": status.get("last_update"),
                "update_count": status.get("update_count", 0)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取轮播图缓存信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取轮播图缓存信息失败: {str(e)}")