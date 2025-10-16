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

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Optional
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from .cache import get_news_cache, get_banner_cache, ServiceStatus
from services.news_service import get_news_service, NewsSource

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.thread_pool = ThreadPoolExecutor(max_workers=6, thread_name_prefix="CrawlerWorker")
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        try:
            # 每6小时更新一次所有新闻源（降低频率以减少资源与流量）
            self.scheduler.add_job(
                lambda: self._update_cache_job(NewsSource.ALL),
                trigger=IntervalTrigger(hours=6),
                id='update_cache_all',
                name='更新所有新闻源缓存',
                replace_existing=True
            )
            
            # 每6小时更新一次轮播图（与新闻更新时间间隔一致）
            self.scheduler.add_job(
                self._update_banner_cache_job,
                trigger=IntervalTrigger(hours=6),
                id='update_banner_cache',
                name='更新轮播图缓存',
                replace_existing=True
            )
            
            # 每天凌晨2点执行完整爬取（作为备份）
            self.scheduler.add_job(
                self._full_crawl_job,
                trigger=CronTrigger(hour=2, minute=0),
                id='full_crawl',
                name='完整爬取任务',
                replace_existing=True
            )
            
            logger.info("定时任务设置完成")
            
        except Exception as e:
            logger.error(f"设置定时任务失败: {e}")
    
    def _run_crawler_in_thread(self, task_name: str, source: NewsSource = NewsSource.ALL):
        """在线程中执行爬虫任务"""
        try:
            logger.info(f"🚀 开始执行{task_name} - 来源: {source.value}")
            
            # 获取缓存实例和新闻服务
            cache = get_news_cache()
            news_service = get_news_service()
            
            logger.info(f"📊 {task_name} - 准备并行爬取数据...")
            
            # 执行爬取（分批写入模式，数据已经在爬取过程中写入缓存）
            articles = news_service.crawl_news(source)
            
            logger.info(f"🔍 {task_name} - 爬取完成，原始文章数: {len(articles)}")
            
            # 验证文章数据
            valid_articles = news_service.validate_articles(articles)
            
            logger.info(f"✅ {task_name} - 验证完成，有效文章数: {len(valid_articles)}")
            
            # 🔥 重要：根据是否首次加载决定更新策略
            if cache._is_first_load:
                # 首次加载：数据已经通过分批写入，只需确保状态正确
                cache_status = cache.get_status()
                if cache_status['cache_count'] > 0 and cache_status['status'] != 'ready':
                    logger.info(f"🎯 {task_name} - 确保缓存状态为就绪")
                    cache.set_status(ServiceStatus.READY)
                logger.info(f"🎉 {task_name}完成（首次加载），缓存中共有 {cache_status['cache_count']} 篇文章")
            else:
                # 后续更新：完整替换缓存，避免数据倒退
                logger.info(f"🔄 {task_name} - 执行完整缓存更新（非首次加载）")
                cache.update_cache(valid_articles)
                cache_status = cache.get_status()
                logger.info(f"🎉 {task_name}完成（完整更新），缓存中共有 {cache_status['cache_count']} 篇文章")
            
        except Exception as e:
            logger.error(f"❌ {task_name}失败: {e}", exc_info=True)
            # 设置错误状态
            cache = get_news_cache()
            cache.set_status(ServiceStatus.ERROR, str(e))
    
    async def _update_cache_job(self, source: NewsSource = NewsSource.ALL):
        """定时更新缓存任务"""
        try:
            # 在线程池中执行爬虫任务
            task_name = f"定时缓存更新任务 - {source.value}"
            future = self.thread_pool.submit(self._run_crawler_in_thread, task_name, source)
            # 不等待完成，让任务在后台执行
            logger.info(f"{task_name}已提交到后台线程")
            
        except Exception as e:
            logger.error(f"提交定时缓存更新任务失败: {e}")
    
    async def _full_crawl_job(self):
        """完整爬取任务（所有来源）"""
        try:
            # 在线程池中执行爬虫任务
            future = self.thread_pool.submit(self._run_crawler_in_thread, "完整爬取任务", NewsSource.ALL)
            # 不等待完成，让任务在后台执行
            logger.info("完整爬取任务已提交到后台线程")
            
        except Exception as e:
            logger.error(f"提交完整爬取任务失败: {e}")
    
    def _run_banner_crawler_in_thread(self, task_name: str):
        """在线程中执行轮播图爬虫任务"""
        try:
            logger.info(f"🖼️ 开始执行{task_name}")
            
            # 获取轮播图缓存实例
            banner_cache = get_banner_cache()
            
            # 设置为正在更新状态（这会将状态设为PREPARING）
            banner_cache.set_updating(True)
            
            # 优先使用增强版爬虫，如果失败则回退到传统爬虫
            banner_info_list = []
            
            import os
            use_enhanced = os.getenv("BANNER_USE_ENHANCED", "true").lower() == "true"
            try:
                if use_enhanced:
                    # 尝试使用增强版爬虫
                    from services.enhanced_mobile_banner_crawler import EnhancedMobileBannerCrawler
                    enhanced_crawler = EnhancedMobileBannerCrawler()
                    banner_info_list = enhanced_crawler.crawl_mobile_banners(
                        download_images=False,  # 定时任务不下载图片
                        save_directory=""
                    )
                    logger.info(f"✅ 使用增强版爬虫成功，获取 {len(banner_info_list)} 张图片")
                else:
                    logger.info("⏭️ 已通过环境变量禁用增强版爬虫，直接使用传统爬虫")
                    raise Exception("Enhanced crawler disabled by env")
            except Exception as enhanced_error:
                logger.warning(f"⚠️ 增强版爬虫不可用或失败，尝试传统爬虫: {enhanced_error}")
                # 回退到传统爬虫（与API一致，使用MobileBannerCrawler）
                try:
                    from services.mobile_banner_crawler import MobileBannerCrawler
                    crawler = MobileBannerCrawler()
                    banner_info_list = crawler.crawl_mobile_banners(download_images=False)
                    logger.info(f"✅ 使用传统爬虫成功，获取 {len(banner_info_list)} 张图片")
                except Exception as traditional_error:
                    logger.error(f"❌ 传统爬虫也失败: {traditional_error}")
                    raise traditional_error
            
            # 更新缓存（update_cache方法会根据数据情况设置正确的状态）
            banner_cache.update_cache(banner_info_list)
            
            if banner_info_list:
                logger.info(f"✅ {task_name}完成，共更新 {len(banner_info_list)} 张轮播图，状态已设为READY")
            else:
                logger.warning(f"⚠️ {task_name}完成，但未找到任何轮播图，状态保持PREPARING")
            
        except Exception as e:
            logger.error(f"❌ {task_name}失败: {e}", exc_info=True)
            # 设置错误状态
            banner_cache = get_banner_cache()
            banner_cache.set_status(ServiceStatus.ERROR, str(e))
            banner_cache.set_updating(False)  # 确保停止更新状态
    
    async def _update_banner_cache_job(self):
        """定时更新轮播图缓存任务"""
        try:
            # 在线程池中执行轮播图爬虫任务
            task_name = "定时轮播图更新任务"
            future = self.thread_pool.submit(self._run_banner_crawler_in_thread, task_name)
            # 不等待完成，让任务在后台执行
            logger.info(f"{task_name}已提交到后台线程")
            
        except Exception as e:
            logger.error(f"提交定时轮播图更新任务失败: {e}")
    
    async def initial_cache_load(self):
        """初始缓存加载（服务启动时执行）"""
        try:
            logger.info("开始执行初始缓存加载")
            
            # 获取缓存实例，但不立即设置为准备中状态
            # 让分批写入逻辑来决定何时设置为READY
            cache = get_news_cache()
            logger.info("📦 分批写入模式：将在第一批数据写入后立即变为可用状态")
            
            # 在线程池中执行爬虫任务
            future = self.thread_pool.submit(self._run_crawler_in_thread, "初始缓存加载", NewsSource.ALL)
            
            # 同时启动轮播图初始加载
            banner_future = self.thread_pool.submit(self._run_banner_crawler_in_thread, "初始轮播图加载")
            
            # 不等待完成，让任务在后台执行，服务可以立即启动
            logger.info("初始缓存加载任务已提交到后台线程，服务可以立即响应请求")
            logger.info("初始轮播图加载任务已提交到后台线程")
            
        except Exception as e:
            logger.error(f"提交初始缓存加载任务失败: {e}")
            # 设置错误状态
            cache = get_news_cache()
            cache.set_status(ServiceStatus.ERROR, str(e))
    
    async def manual_crawl(self, source: NewsSource = NewsSource.ALL):
        """手动触发爬取任务"""
        try:
            logger.info(f"开始执行手动爬取任务 - 来源: {source.value}")
            
            # 在线程池中执行爬虫任务
            task_name = f"手动爬取任务 - {source.value}"
            future = self.thread_pool.submit(self._run_crawler_in_thread, task_name, source)
            
            # 不等待完成，让任务在后台执行
            logger.info(f"{task_name}已提交到后台线程")
            
        except Exception as e:
            logger.error(f"提交手动爬取任务失败: {e}")
            # 设置错误状态
            cache = get_news_cache()
            cache.set_status(ServiceStatus.ERROR, str(e))
    
    async def manual_banner_crawl(self):
        """手动触发轮播图爬取任务"""
        try:
            logger.info("开始执行手动轮播图爬取任务")
            
            # 在线程池中执行轮播图爬虫任务
            task_name = "手动轮播图爬取任务"
            future = self.thread_pool.submit(self._run_banner_crawler_in_thread, task_name)
            
            # 不等待完成，让任务在后台执行
            logger.info(f"{task_name}已提交到后台线程")
            
        except Exception as e:
            logger.error(f"提交手动轮播图爬取任务失败: {e}")
            # 设置错误状态
            banner_cache = get_banner_cache()
            banner_cache.set_status(ServiceStatus.ERROR, str(e))
    
    def start(self):
        """启动调度器"""
        try:
            self.scheduler.start()
            logger.info("定时任务调度器已启动")
        except Exception as e:
            logger.error(f"启动调度器失败: {e}")
    
    def stop(self):
        """停止调度器"""
        try:
            self.scheduler.shutdown()
            self.thread_pool.shutdown(wait=True)
            logger.info("定时任务调度器已停止")
        except Exception as e:
            logger.error(f"停止调度器失败: {e}")
    
    def add_job(self, func, trigger, **kwargs):
        """添加新的定时任务"""
        try:
            self.scheduler.add_job(func, trigger=trigger, **kwargs)
            logger.info(f"添加定时任务成功: {kwargs.get('name', '未命名任务')}")
        except Exception as e:
            logger.error(f"添加定时任务失败: {e}")
    
    def remove_job(self, job_id):
        """移除定时任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"移除定时任务成功: {job_id}")
        except Exception as e:
            logger.error(f"移除定时任务失败: {e}")
    
    def get_jobs(self):
        """获取所有定时任务"""
        return self.scheduler.get_jobs()

# 全局调度器实例
_scheduler: Optional[TaskScheduler] = None

def get_scheduler() -> TaskScheduler:
    """获取调度器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler

def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()
    scheduler.start()

def stop_scheduler():
    """停止调度器"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None 
