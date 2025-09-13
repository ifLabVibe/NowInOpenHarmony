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


import json
import logging
import threading
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from models.news import NewsArticle, NewsResponse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.openharmony_image_crawler import OpenHarmonyImageCrawler

logger = logging.getLogger(__name__)

class ServiceStatus(str, Enum):
    """服务状态枚举"""
    READY = "ready"           # 服务就绪
    PREPARING = "preparing"   # 准备中（数据更新中）
    ERROR = "error"           # 错误状态

class NewsCache:
    """新闻数据缓存管理器"""
    
    def __init__(self):
        self._cache: List[NewsArticle] = []
        self._cache_lock = threading.RLock()  # 可重入锁
        self._status = ServiceStatus.READY  # 初始状态为就绪，等待数据分批写入
        self._last_update = None
        self._update_count = 0
        self._error_message = None
        self._is_updating = False  # 标记是否正在更新
        self._is_first_load = True  # 标记是否为首次加载
        
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        with self._cache_lock:
            return {
                "status": self._status.value,
                "last_update": self._last_update,
                "cache_count": len(self._cache),
                "update_count": self._update_count,
                "error_message": self._error_message,
                "is_updating": self._is_updating,
                "is_first_load": self._is_first_load  # 添加首次加载标识
            }
    
    def set_status(self, status: ServiceStatus, error_message: Optional[str] = None):
        """设置服务状态"""
        with self._cache_lock:
            self._status = status
            self._error_message = error_message
            logger.info(f"服务状态更新: {status.value}")
    
    def set_updating(self, is_updating: bool):
        """设置更新状态"""
        with self._cache_lock:
            self._is_updating = is_updating
            if is_updating:
                logger.info("开始数据更新，状态设为准备中")
                self.set_status(ServiceStatus.PREPARING)
            else:
                logger.info("数据更新完成，状态设为就绪")
                self.set_status(ServiceStatus.READY)
    
    def get_news(self, page: int = 1, page_size: int = 20, 
                 category: Optional[str] = None, 
                 search: Optional[str] = None) -> NewsResponse:
        """获取新闻数据（带分页和过滤）"""
        with self._cache_lock:
            if self._status == ServiceStatus.ERROR:
                raise Exception(f"服务错误: {self._error_message}")
            
            # 过滤数据
            filtered_news = self._cache.copy()
            
            # 分类过滤
            if category:
                filtered_news = [news for news in filtered_news if news.category == category]
            
            # 搜索过滤
            if search:
                search_lower = search.lower()
                filtered_news = [
                    news for news in filtered_news 
                    if search_lower in news.title.lower() or 
                       (news.summary and search_lower in news.summary.lower())
                ]
            
            # 🔥 改进：由于缓存写入时已经排序，这里只做轻量级验证
            # 检查是否需要重新排序（防御性编程）
            try:
                if len(filtered_news) > 1:
                    # 检查前两篇文章的日期顺序
                    first_date = self._parse_date_for_sorting(filtered_news[0].date)
                    second_date = self._parse_date_for_sorting(filtered_news[1].date)
                    
                    # 如果顺序不对，重新排序
                    if first_date < second_date:
                        logger.info("🔄 [读取排序] 检测到顺序异常，执行重新排序")
                        filtered_news.sort(key=lambda x: self._parse_date_for_sorting(x.date), reverse=True)
                    else:
                        logger.debug("✅ [读取排序] 日期顺序正确，无需重新排序")
            except Exception as e:
                logger.warning(f"⚠️ [读取排序] 日期顺序检查失败，使用原始顺序: {e}")
            
            # 分页处理
            total = len(filtered_news)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_news = filtered_news[start:end]
            
            return NewsResponse(
                articles=paginated_news,
                total=total,
                page=page,
                page_size=page_size,
                has_next=end < total,
                has_prev=page > 1
            )
    
    def _parse_date_for_sorting(self, date_str: str) -> datetime:
        """
        解析日期字符串用于排序，支持多种日期格式
        支持格式：2024-08-31, 2024.08.31, 2024/08/31, 2024年08月31日等
        """
        try:
            if not date_str or not isinstance(date_str, str):
                logger.warning(f"无效的日期字符串: {date_str}")
                return datetime(1970, 1, 1)
            
            # 清理日期字符串
            date_str = date_str.strip()
            
            # 1. 优先使用正则表达式提取日期组件，支持更多格式
            import re
            
            # 匹配 YYYY-MM-DD, YYYY.MM.DD, YYYY/MM/DD 格式（支持单数字月/日）
            date_patterns = [
                r'(\d{4})[-./](\d{1,2})[-./](\d{1,2})',  # 2024-08-31, 2024.08.31, 2024/08/31
                r'(\d{4})年(\d{1,2})月(\d{1,2})日?',      # 2024年08月31日
                r'(\d{4})年(\d{1,2})月(\d{1,2})',        # 2024年08月31
                r'(\d{1,2})[-./](\d{1,2})[-./](\d{4})',  # 31-08-2024, 31.08.2024 (DD-MM-YYYY)
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    groups = match.groups()
                    try:
                        if len(groups) == 3:
                            # 检查是否是DD-MM-YYYY格式
                            if pattern.startswith(r'(\d{1,2})'):
                                day, month, year = groups
                            else:
                                year, month, day = groups
                            
                            year = int(year)
                            month = int(month)
                            day = int(day)
                            
                            # 验证日期有效性
                            if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100:
                                parsed_date = datetime(year, month, day)
                                logger.debug(f"✅ 日期解析成功: {date_str} -> {parsed_date.strftime('%Y-%m-%d')}")
                                return parsed_date
                    except (ValueError, TypeError) as e:
                        logger.debug(f"正则匹配但转换失败: {date_str}, 错误: {e}")
                        continue
            
            # 2. 如果正则匹配失败，尝试标准datetime格式
            date_formats = [
                '%Y-%m-%d',           # 2024-08-31
                '%Y.%m.%d',           # 2024.08.31
                '%Y/%m/%d',           # 2024/08/31
                '%Y-%m-%d %H:%M:%S',  # 2024-08-31 10:30:00
                '%Y.%m.%d %H:%M:%S',  # 2024.08.31 10:30:00
                '%Y/%m/%d %H:%M:%S',  # 2024/08/31 10:30:00
                '%Y年%m月%d日',        # 2024年08月31日
                '%Y年%m月%d',          # 2024年08月31
                '%m-%d',              # 08-31 (假设为当年)
                '%m.%d',              # 08.31 (假设为当年)
                '%m/%d',              # 08/31 (假设为当年)
            ]
            
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, date_format)
                    # 如果只有月日，补充当前年份
                    if '%Y' not in date_format:
                        parsed_date = parsed_date.replace(year=datetime.now().year)
                    logger.debug(f"✅ strptime解析成功: {date_str} -> {parsed_date.strftime('%Y-%m-%d')}")
                    return parsed_date
                except ValueError:
                    continue
            
            # 3. 最后的尝试：提取任何可能的数字组合
            number_match = re.findall(r'\d+', date_str)
            if len(number_match) >= 3:
                try:
                    # 假设第一个是年份（如果是4位数），否则按顺序处理
                    nums = [int(x) for x in number_match[:3]]
                    
                    # 判断年份位置
                    if nums[0] > 1900:  # 第一个数字是年份
                        year, month, day = nums[0], nums[1], nums[2]
                    elif nums[2] > 1900:  # 第三个数字是年份
                        day, month, year = nums[0], nums[1], nums[2]
                    else:
                        # 默认当前年份
                        year = datetime.now().year
                        month, day = nums[0], nums[1]
                    
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        parsed_date = datetime(year, month, day)
                        logger.debug(f"✅ 数字提取解析成功: {date_str} -> {parsed_date.strftime('%Y-%m-%d')}")
                        return parsed_date
                except (ValueError, IndexError):
                    pass
            
            # 最后的fallback：返回Unix纪元时间
            logger.warning(f"⚠️ 无法解析日期格式: '{date_str}'，使用默认时间")
            return datetime(1970, 1, 1)
            
        except Exception as e:
            logger.error(f"❌ 日期解析异常: '{date_str}', 错误: {e}")
            return datetime(1970, 1, 1)
    
    def _sort_articles_by_date(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        按日期对文章进行排序（由近到远）
        在数据合并时统一触发排序，确保数据一致性
        """
        try:
            if not articles:
                return articles
            
            logger.info(f"🔄 [缓存排序] 开始对 {len(articles)} 篇文章进行日期排序...")
            
            # 统计日期解析情况
            parse_stats = {"success": 0, "failed": 0, "examples": []}
            
            def sort_key_with_stats(article):
                parsed_date = self._parse_date_for_sorting(article.date)
                if parsed_date.year > 1970:
                    parse_stats["success"] += 1
                    if len(parse_stats["examples"]) < 3:
                        parse_stats["examples"].append(f"{article.date} -> {parsed_date.strftime('%Y-%m-%d')}")
                else:
                    parse_stats["failed"] += 1
                return parsed_date
            
            # 执行排序
            sorted_articles = sorted(articles, key=sort_key_with_stats, reverse=True)
            
            # 输出统计信息
            total = len(articles)
            success_rate = (parse_stats["success"] / total * 100) if total > 0 else 0
            
            logger.info(f"✅ [缓存排序] 排序完成！")
            logger.info(f"📊 [缓存排序] 成功解析: {parse_stats['success']}/{total} ({success_rate:.1f}%)")
            if parse_stats["failed"] > 0:
                logger.warning(f"⚠️ [缓存排序] 解析失败: {parse_stats['failed']} 篇文章")
            
            if parse_stats["examples"]:
                logger.info(f"📅 [缓存排序] 解析示例: {', '.join(parse_stats['examples'])}")
            
            # 显示排序后的前几篇文章的日期
            if sorted_articles:
                latest_dates = [article.date for article in sorted_articles[:3]]
                logger.info(f"📈 [缓存排序] 最新文章日期: {latest_dates}")
            
            return sorted_articles
            
        except Exception as e:
            logger.error(f"❌ [缓存排序] 排序失败: {e}")
            return articles  # 排序失败时返回原列表
    
    def update_cache(self, news_data: List[NewsArticle]):
        """更新缓存数据（完全替换）"""
        with self._cache_lock:
            try:
                # 设置更新状态为True，状态变为准备中
                self.set_updating(True)
                
                # 🔥 关键改进：在数据合并时触发日期排序
                logger.info(f"🔄 [完整更新] 开始更新缓存，原始数据: {len(news_data)} 篇文章")
                sorted_news_data = self._sort_articles_by_date(news_data.copy())
                
                # 更新缓存
                self._cache = sorted_news_data
                self._last_update = datetime.now().isoformat()
                self._update_count += 1
                
                # 🔥 重要：标记首次加载完成，后续不再使用分批写入
                if self._is_first_load:
                    self._is_first_load = False
                    logger.info("🏁 首次完整加载完成，后续更新将使用完整替换模式")
                
                # 设置更新状态为False，状态变为就绪
                self.set_updating(False)
                
                logger.info(f"🔄 缓存完整更新成功，共 {len(news_data)} 条新闻")
                
            except Exception as e:
                error_msg = f"缓存更新失败: {str(e)}"
                self.set_status(ServiceStatus.ERROR, error_msg)
                self._is_updating = False
                logger.error(error_msg)
                raise
    
    def append_to_cache(self, new_articles: List[NewsArticle]):
        """增量追加新文章到缓存（仅用于首次加载的分批写入）"""
        with self._cache_lock:
            try:
                if not new_articles:
                    return
                
                # 🔥 重要：只在首次加载时才允许分批写入
                if not self._is_first_load:
                    logger.warning("⚠️ 非首次加载，忽略分批写入，等待完整更新")
                    return
                
                # 获取现有文章的URL集合，用于去重
                existing_urls = {article.url for article in self._cache}
                
                # 过滤掉重复的文章
                unique_articles = [
                    article for article in new_articles 
                    if article.url not in existing_urls
                ]
                
                if unique_articles:
                    # 追加新文章
                    self._cache.extend(unique_articles)
                    
                    # 🔥 关键改进：分批写入后立即触发排序，保持数据一致性
                    logger.info(f"🔄 [分批更新] 追加 {len(unique_articles)} 篇文章后触发排序")
                    self._cache = self._sort_articles_by_date(self._cache)
                    
                    self._last_update = datetime.now().isoformat()
                    
                    # 🔥 关键修改：如果缓存中有文章了，就设置状态为READY
                    if len(self._cache) > 0 and self._status == ServiceStatus.PREPARING:
                        logger.info("🎉 缓存中已有数据，状态设为就绪，用户可以开始查看文章")
                        self.set_status(ServiceStatus.READY)
                    
                    logger.info(f"📝 [首次加载] 增量追加 {len(unique_articles)} 篇新文章到缓存（跳过 {len(new_articles) - len(unique_articles)} 篇重复）")
                    logger.info(f"📊 [首次加载] 缓存总数: {len(self._cache)} 篇文章")
                else:
                    logger.info(f"📝 [首次加载] 本批次 {len(new_articles)} 篇文章全部为重复，跳过")
                
            except Exception as e:
                error_msg = f"增量更新缓存失败: {str(e)}"
                logger.error(error_msg)
                raise
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        with self._cache_lock:
            return {
                "cache_size": len(self._cache),
                "last_update": self._last_update,
                "update_count": self._update_count,
                "status": self._status.value,
                "error_message": self._error_message,
                "is_updating": self._is_updating
            }
    
    def clear_cache(self):
        """清空缓存"""
        with self._cache_lock:
            self._cache.clear()
            self._last_update = None
            self._update_count = 0
            self.set_updating(True)  # 清空时设为准备中
            logger.info("缓存已清空")

# 全局缓存实例
_news_cache: Optional[NewsCache] = None

def get_news_cache() -> NewsCache:
    """获取新闻缓存实例"""
    global _news_cache
    if _news_cache is None:
        _news_cache = NewsCache()
    return _news_cache

def init_cache():
    """初始化缓存"""
    global _news_cache, _banner_cache
    _news_cache = NewsCache()
    _banner_cache = BannerCache()
    logger.info("新闻缓存初始化完成")
    logger.info("轮播图缓存初始化完成")


class BannerCache:
    """轮播图缓存管理器"""
    
    def __init__(self):
        self._cache: List[Dict[str, Any]] = []
        self._cache_lock = threading.RLock()
        self._status = ServiceStatus.PREPARING  # 初始状态为准备中，等待首次爬取
        self._last_update = None
        self._update_count = 0
        self._error_message = None
        self._is_updating = False
        self._first_load_completed = False  # 标记是否完成首次加载
        
    def get_status(self) -> Dict[str, Any]:
        """获取轮播图服务状态"""
        with self._cache_lock:
            return {
                "status": self._status.value,
                "last_update": self._last_update,
                "cache_count": len(self._cache),
                "update_count": self._update_count,
                "error_message": self._error_message,
                "is_updating": self._is_updating,
                "first_load_completed": self._first_load_completed
            }
    
    def set_status(self, status: ServiceStatus, error_message: Optional[str] = None):
        """设置服务状态"""
        with self._cache_lock:
            self._status = status
            self._error_message = error_message
            logger.info(f"轮播图服务状态更新: {status.value}")
    
    def set_updating(self, is_updating: bool):
        """设置更新状态"""
        with self._cache_lock:
            self._is_updating = is_updating
            if is_updating:
                logger.info("开始轮播图数据更新，状态设为准备中")
                self.set_status(ServiceStatus.PREPARING)
            else:
                logger.info("轮播图数据更新完成，状态设为就绪")
                self.set_status(ServiceStatus.READY)
    
    def get_banner_images(self) -> List[Dict[str, Any]]:
        """获取轮播图数据"""
        with self._cache_lock:
            if self._status == ServiceStatus.ERROR:
                raise Exception(f"轮播图服务错误: {self._error_message}")
            
            return self._cache.copy()
    
    def update_cache(self, banner_data: List[Dict[str, Any]]):
        """更新轮播图缓存数据"""
        with self._cache_lock:
            try:
                # 设置更新状态
                self.set_updating(True)
                
                # 更新缓存
                self._cache = banner_data.copy()
                self._last_update = datetime.now().isoformat()
                self._update_count += 1
                
                # 标记首次加载完成
                if not self._first_load_completed:
                    self._first_load_completed = True
                    logger.info("🎉 轮播图首次加载完成")
                
                # 设置完成状态 - 只有在有数据时才设为READY
                if len(banner_data) > 0:
                    self.set_updating(False)  # 这会设置为READY
                    logger.info(f"🖼️ 轮播图缓存更新成功，共 {len(banner_data)} 张图片，状态：READY")
                else:
                    # 如果没有数据，保持PREPARING状态
                    self._is_updating = False
                    self._status = ServiceStatus.PREPARING
                    logger.warning("⚠️ 轮播图缓存更新完成，但未获取到数据，状态保持：PREPARING")
                
            except Exception as e:
                error_msg = f"轮播图缓存更新失败: {str(e)}"
                self.set_status(ServiceStatus.ERROR, error_msg)
                self._is_updating = False
                logger.error(error_msg)
                raise
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取轮播图缓存信息"""
        with self._cache_lock:
            return {
                "cache_size": len(self._cache),
                "last_update": self._last_update,
                "update_count": self._update_count,
                "status": self._status.value,
                "error_message": self._error_message,
                "is_updating": self._is_updating
            }
    
    def clear_cache(self):
        """清空轮播图缓存"""
        with self._cache_lock:
            self._cache.clear()
            self._last_update = None
            self._update_count = 0
            self.set_updating(True)
            logger.info("轮播图缓存已清空")


# 全局轮播图缓存实例
_banner_cache: Optional[BannerCache] = None

def get_banner_cache() -> BannerCache:
    """获取轮播图缓存实例"""
    global _banner_cache
    if _banner_cache is None:
        _banner_cache = BannerCache()
    return _banner_cache 