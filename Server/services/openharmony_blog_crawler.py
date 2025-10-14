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

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import logging
import hashlib
from urllib.parse import urljoin
from datetime import datetime
from typing import List, Dict, Optional, Callable

logger = logging.getLogger(__name__)

class OpenHarmonyBlogCrawler:
    """
    OpenHarmony技术博客爬虫
    爬取OpenHarmony官网技术博客文章内容
    """
    
    def __init__(self):
        self.base_url = "https://old.openharmony.cn"
        self.api_url = "https://old.openharmony.cn/backend/knowledge/secondaryPage/queryBatch"
        self.source = "OpenHarmony技术博客"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://old.openharmony.cn/',
            'Cache-Control': 'no-cache'
        })
        
    def get_page_content(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            logger.warning(f"⚠️ [OpenHarmony博客] 获取页面失败: {url}, 错误: {e}")
            return None

    def get_all_blog_articles(self) -> List[Dict]:
        """
        分页获取所有技术博客文章信息
        type=2 表示技术博客类型
        """
        all_articles = []
        page_num = 1
        page_size = 200  # 根据用户要求设置为200
        total_pages = 1
        
        logger.info(f"🚀 [OpenHarmony博客] 开始获取技术博客文章列表，页面大小: {page_size}")
        
        while page_num <= total_pages:
            try:
                # 构造API请求URL
                api_url = f"{self.api_url}?type=2&pageNum={page_num}&pageSize={page_size}"
                logger.info(f"📡 [OpenHarmony博客] 请求第 {page_num} 页: {api_url}")
                
                response = self.session.get(api_url, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                # 检查响应格式
                if data.get("code") != 0:
                    logger.error(f"❌ [OpenHarmony博客] API返回错误: {data.get('msg', '未知错误')}")
                    break
                
                articles = data.get("data", [])
                total_pages = data.get("totalPage", 1)
                total_num = data.get("totalNum", 0)
                
                logger.info(f"📄 [OpenHarmony博客] 第 {page_num}/{total_pages} 页，本页 {len(articles)} 篇文章，总计 {total_num} 篇")
                
                if not articles:
                    logger.info(f"📋 [OpenHarmony博客] 第 {page_num} 页无数据，停止获取")
                    break
                
                # 处理文章数据
                for article in articles:
                    try:
                        article_info = self._extract_article_info(article)
                        if article_info:
                            all_articles.append(article_info)
                    except Exception as e:
                        logger.warning(f"⚠️ [OpenHarmony博客] 解析文章信息失败: {e}")
                        continue
                
                page_num += 1
                
                # 添加请求间隔，避免过于频繁
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ [OpenHarmony博客] 获取第 {page_num} 页失败: {e}")
                break
        
        logger.info(f"✅ [OpenHarmony博客] 共获取到 {len(all_articles)} 篇有效文章信息")
        return all_articles

    def _extract_article_info(self, article_data: Dict) -> Optional[Dict]:
        """从API响应中提取文章信息"""
        try:
            # 提取基本信息
            title = article_data.get("title", "").strip()
            url = article_data.get("url", "").strip()
            content_summary = article_data.get("content", "").strip()
            start_time = article_data.get("startTime", "")
            
            # 验证必要字段
            if not title or not url:
                logger.warning(f"⚠️ [OpenHarmony博客] 文章缺少必要字段: title={title}, url={url}")
                return None
            
            # 处理日期格式
            formatted_date = self._format_date(start_time)
            
            return {
                "title": title,
                "url": url,
                "date": formatted_date,
                "summary": content_summary
            }
            
        except Exception as e:
            logger.error(f"❌ [OpenHarmony博客] 提取文章信息失败: {e}")
            return None

    def _format_date(self, date_str: str) -> str:
        """格式化日期字符串"""
        try:
            if not date_str:
                return datetime.now().strftime('%Y-%m-%d')
            
            # 处理常见的日期格式
            if '.' in date_str:
                # 格式: 2024.06.06
                date_str = date_str.replace('.', '-')
            
            # 尝试解析日期
            try:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                # 如果解析失败，返回原始字符串
                return date_str
                
        except Exception as e:
            logger.warning(f"⚠️ [OpenHarmony博客] 日期格式化失败: {date_str}, 错误: {e}")
            return datetime.now().strftime('%Y-%m-%d')

    def parse_article_content(self, article_url: str) -> List[Dict]:
        """
        解析文章内容，仿照OpenHarmony爬虫的逻辑
        """
        content = self.get_page_content(article_url)
        if not content:
            logger.warning(f"⚠️ [OpenHarmony博客] 无法获取文章内容: {article_url}")
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        result_data = []
        
        # 尝试多种容器选择器，仿照原有逻辑
        article_container = (
            soup.find(id='js_content') or
            soup.find(class_='rich_media_content') or
            soup.find(id='page-content') or
            soup.find(class_='rich_media_area_primary') or
            soup.find(class_=re.compile(r'article|content|detail|main', re.I)) or
            soup.find('article') or
            soup.find(id=re.compile(r'article|content|detail|main', re.I)) or
            soup.find(class_='content') or
            soup.find(class_='article-content')
        )
        
        if not article_container:
            article_container = soup.find('body')
            logger.info(f"📄 [OpenHarmony博客] 使用body作为文章容器: {article_url}")
        
        if article_container:
            # 解析各种元素类型
            for element in article_container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'img', 'video', 'pre', 'code']):
                try:
                    if element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']:
                        text = element.get_text().strip()
                        if text and len(text) > 10:  # 过滤太短的文本
                            result_data.append({"type": "text", "value": text})
                    
                    elif element.name == 'img':
                        img_src = element.get('data-src') or element.get('data-original') or element.get('src')
                        if img_src:
                            img_url = urljoin(self.base_url, img_src)
                            result_data.append({"type": "image", "value": img_url})
                    
                    elif element.name == 'video':
                        video_src = element.get('src')
                        if video_src:
                            video_url = urljoin(self.base_url, video_src)
                            result_data.append({"type": "video", "value": video_url})
                        
                        # 处理video标签内的source元素
                        for source in element.find_all('source'):
                            video_src = source.get('src')
                            if video_src:
                                video_url = urljoin(self.base_url, video_src)
                                result_data.append({"type": "video", "value": video_url})
                    
                    elif element.name in ['pre', 'code']:
                        code_text = element.get_text().strip()
                        if code_text:
                            result_data.append({"type": "code", "value": code_text})
                
                except Exception as e:
                    logger.warning(f"⚠️ [OpenHarmony博客] 解析元素失败: {e}")
                    continue
        
        logger.info(f"📝 [OpenHarmony博客] 解析文章内容完成，共 {len(result_data)} 个内容块: {article_url}")
        return result_data

    def _format_article(self, article):
        """将文章格式化为统一的新闻格式，与OpenHarmony爬虫保持一致"""
        import hashlib
        
        # 生成文章ID（基于URL的哈希，与OpenHarmony爬虫保持一致的16位长度）
        article_id = hashlib.md5(article['url'].encode()).hexdigest()[:16]
        
        # 返回统一格式，符合TypeScript接口规范
        return {
            "id": article_id,
            "title": article['title'],
            "date": article.get('date', ''),
            "url": article['url'],
            "content": article.get('content', []),
            "category": "技术博客",  # 区别于官方动态
            "summary": article.get('summary', ''),
            "source": "OpenHarmony技术博客",  # 明确标注来源
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def crawl_openharmony_blog_news(self, batch_callback=None, batch_size=20):
        """
        爬取OpenHarmony技术博客新闻，完全仿照OpenHarmony爬虫的逻辑
        
        Args:
            batch_callback: 分批处理回调函数
            batch_size: 每批处理的文章数量
            
        Returns:
            处理后的文章列表
        """
        logger.info("🚀 [OpenHarmony博客] 开始爬取OpenHarmony技术博客新闻...")
        if batch_callback:
            logger.info(f"📦 [OpenHarmony博客] 启用分批处理模式，每 {batch_size} 篇文章执行一次回调")
        
        # 1. 获取所有文章信息
        articles_info = self.get_all_blog_articles()
        logger.info(f"📋 [OpenHarmony博客] 获取到 {len(articles_info)} 篇文章信息")
        
        if not articles_info:
            logger.warning("⚠️ [OpenHarmony博客] 未获取到任何文章信息")
            return []
        
        # 2. 逐篇处理文章内容，完全仿照OpenHarmony爬虫的逻辑
        all_articles_data = []
        batch_articles = []
        
        for i, info in enumerate(articles_info):
            title = info["title"]
            date = info["date"]
            article_url = info["url"]
            summary = info.get("summary", "")
            
            logger.info(f"🔍 [OpenHarmony博客] 正在处理第 {i+1}/{len(articles_info)} 篇文章: {title}")
            logger.debug(f"🔗 [OpenHarmony博客] 文章URL: {article_url}")
            
            # 解析文章详细内容
            article_data = self.parse_article_content(article_url)
            if article_data:
                # 使用_format_article方法格式化数据，确保与OpenHarmony爬虫一致
                article_info = self._format_article({
                    "title": title,
                    "date": date,
                    "url": article_url,
                    "content": article_data,
                    "summary": summary
                })
                all_articles_data.append(article_info)
                batch_articles.append(article_info)
                logger.info(f"✅ [OpenHarmony博客] 成功解析文章，共 {len(article_data)} 个内容块")
                
                # 检查是否达到批处理大小
                if len(batch_articles) >= batch_size and batch_callback:
                    try:
                        logger.info(f"📦 [OpenHarmony博客分批处理] 达到批处理大小 {batch_size}，执行回调...")
                        batch_callback(batch_articles.copy())
                        batch_articles.clear()  # 清空当前批次
                        logger.info(f"✅ [OpenHarmony博客分批处理] 回调执行成功，继续处理后续文章")
                    except Exception as callback_e:
                        logger.error(f"❌ [OpenHarmony博客分批处理] 回调执行失败: {callback_e}")
            else:
                logger.warning(f"⚠️ [OpenHarmony博客] 文章内容解析失败: {title}")
            
            # 添加请求间隔，避免过于频繁
            time.sleep(1)
        
        # 处理剩余的批次
        if batch_articles and batch_callback:
            try:
                logger.info(f"📦 [OpenHarmony博客分批处理] 处理最后剩余的 {len(batch_articles)} 篇文章...")
                batch_callback(batch_articles.copy())
                logger.info(f"✅ [OpenHarmony博客分批处理] 最后批次处理完成")
            except Exception as callback_e:
                logger.error(f"❌ [OpenHarmony博客分批处理] 最后批次处理失败: {callback_e}")
        
        logger.info(f"🎉 [OpenHarmony博客] 爬取完成，共处理 {len(all_articles_data)} 篇文章")
        return all_articles_data

    def validate_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        验证文章数据完整性
        """
        valid_articles = []
        
        for article in articles:
            try:
                # 检查必要字段
                required_fields = ['id', 'title', 'url', 'content', 'source']
                if not all(field in article for field in required_fields):
                    logger.warning(f"⚠️ [OpenHarmony博客] 文章缺少必要字段: {article.get('title', '未知标题')}")
                    continue
                
                # 检查内容是否为空
                if not article.get('content') or len(article.get('content', [])) == 0:
                    logger.warning(f"⚠️ [OpenHarmony博客] 文章内容为空: {article.get('title', '未知标题')}")
                    continue
                
                # 检查URL有效性
                if not article.get('url') or not article['url'].startswith('http'):
                    logger.warning(f"⚠️ [OpenHarmony博客] 文章URL无效: {article.get('title', '未知标题')}")
                    continue
                
                valid_articles.append(article)
                
            except Exception as e:
                logger.error(f"❌ [OpenHarmony博客] 验证文章时发生错误: {e}")
                continue
        
        logger.info(f"✅ [OpenHarmony博客] 文章验证完成，有效文章: {len(valid_articles)}/{len(articles)}")
        return valid_articles
