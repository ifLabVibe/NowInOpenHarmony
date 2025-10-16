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
from urllib.parse import urljoin
from datetime import datetime

class OpenHarmonyNewsCrawler:
    def __init__(self):
        self.base_url = "https://old.openharmony.cn"
        self.source = "OpenHarmony"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_page_content(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"获取页面失败: {url}, 错误: {e}")
            return None

    def get_all_article_infos(self):
        """分页遍历API，获取所有新闻的url、title、date，去重并校验有效性"""
        all_infos = {}
        page_num = 1
        page_size = 300  # 设置为300，一次性获取更多数据，减少API请求次数

        print(f"🚀 开始高效获取OpenHarmony文章信息，每页{page_size}条数据...")

        while True:
            api_url = f"{self.base_url}/backend/knowledge/secondaryPage/queryBatch?type=3&pageNum={page_num}&pageSize={page_size}"
            print(f"📡 请求API: 第{page_num}页")
            try:
                resp = self.session.get(api_url, timeout=15)  # 增加超时时间
                resp.raise_for_status()
                response_data = resp.json()
                data = response_data.get("data", [])

                # 打印响应信息用于调试
                print(f"📊 第{page_num}页获取到{len(data)}条数据")

            except Exception as e:
                print(f"❌ API请求失败: {e}")
                break

            if not data:
                print(f"✅ 第{page_num}页无数据，爬取完成")
                break

            # 处理本页数据
            page_count = 0
            for item in data:
                url = item.get("url")
                title = item.get("title", "")
                date = item.get("startTime", "")

                # 标准化日期格式
                standardized_date = self._standardize_date(date)

                if url and url not in all_infos:
                    all_infos[url] = {"title": title, "date": standardized_date}
                    page_count += 1

            print(f"📈 第{page_num}页新增{page_count}条有效数据，累计{len(all_infos)}条")

            # 如果本页数据量小于page_size，说明已经获取完所有数据
            if len(data) < page_size:
                print(f"🎯 第{page_num}页数据量({len(data)})小于页面大小({page_size})，爬取完成")
                break

            page_num += 1
            time.sleep(0.3)  # 减少等待时间，从0.5秒降到0.3秒

        print(f"📋 共���取到{len(all_infos)}条有效文章信息")

        # 快速有效性校验（只检查前10个URL，如果大部分有效就认为全部有效）
        print("🔍 进行快速有效性校验...")
        test_urls = list(all_infos.keys())[:min(10, len(all_infos))]
        valid_test_count = 0

        for url in test_urls:
            try:
                r = self.session.head(url, timeout=3)  # 减少超时时间
                if r.status_code == 200:
                    valid_test_count += 1
            except:
                continue

        validity_rate = valid_test_count / len(test_urls) if test_urls else 0
        print(f"✅ 快速校验完成：{valid_test_count}/{len(test_urls)} 有效，有效率{validity_rate:.1%}")

        # 如果有效率高，直接返回所有数据，否则进行完整校验
        if validity_rate >= 0.8:  # 80%以上有效就直接使用
            print("🚀 有效率高，跳过完整校验，直接返回所有数据")
            return [{"url": url, "title": info["title"], "date": info["date"]}
                    for url, info in all_infos.items()]
        else:
            print("🐌 有效率较低，进行完整URL有效性校验...")
            valid_infos = []
            for url, info in all_infos.items():
                try:
                    r = self.session.head(url, timeout=5)
                    if r.status_code == 200:
                        valid_infos.append({"url": url, "title": info["title"], "date": info["date"]})
                except:
                    continue
            print(f"✅ 完整校验完成，有效URL数量: {len(valid_infos)}")
            return valid_infos

    def parse_article_content(self, article_url):
        content = self.get_page_content(article_url)
        if not content:
            return []
        soup = BeautifulSoup(content, 'html.parser')
        result_data = []
        article_container = (
            soup.find(id='js_content') or
            soup.find(class_='rich_media_content') or
            soup.find(id='page-content') or
            soup.find(class_='rich_media_area_primary') or
            soup.find(class_=re.compile(r'article|content|detail', re.I)) or
            soup.find('article') or
            soup.find(id=re.compile(r'article|content|detail', re.I))
        )
        if not article_container:
            article_container = soup.find('body')
        if article_container:
            for element in article_container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'img', 'video']):
                if element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']:
                    text = element.get_text().strip()
                    if text and len(text) > 10:
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
                    for source in element.find_all('source'):
                        video_src = source.get('src')
                        if video_src:
                            video_url = urljoin(self.base_url, video_src)
                            result_data.append({"type": "video", "value": video_url})
        return result_data

    def _standardize_date(self, date_str):
        """标准化日期格式，将多种日期格式统一为YYYY-MM-DD格式"""
        if not date_str:
            return ''

        try:
            # 匹配多种日期格式：2025.9.13, 2025-9-13, 2025/9/13, 2025年9月13日
            date_pattern = r'(\d{4})[.\-\/年](\d{1,2})[.\-\/月](\d{1,2})[日]?'
            match = re.search(date_pattern, str(date_str))

            if match:
                year, month, day = match.groups()
                # 格式化为统一的YYYY-MM-DD格式
                return f"{year}-{int(month):02d}-{int(day):02d}"
            else:
                # 尝试直接解析日期字符串
                # 处理只有年月的情况
                month_pattern = r'(\d{4})[.\-\/年](\d{1,2})[月]?'
                month_match = re.search(month_pattern, str(date_str))
                if month_match:
                    year, month = month_match.groups()
                    return f"{year}-{int(month):02d}-01"  # 默认设置为当月第一天

                # 如果都无法匹配，返回原始字符串并记录日志
                print(f"⚠️ 无法解析日期格式: {date_str}，保持原样")
                return date_str
        except Exception as e:
            print(f"❌ 日期标准化失败: {date_str}, 错误: {e}")
            return date_str

    def _format_article(self, article):
        """将文章格式化为统一的新闻格式"""
        import hashlib

        # 生成文章ID（基于URL的哈希）
        article_id = hashlib.md5(article['url'].encode()).hexdigest()[:16]

        # 标准化日期格式
        standardized_date = self._standardize_date(article.get('date', ''))

        # 返回统一格式，符合TypeScript接口规范
        return {
            "id": article_id,
            "title": article['title'],
            "date": standardized_date,  # 使用标准化后的日期
            "url": article['url'],
            "content": article.get('content', []),
            "category": "官方动态",
            "summary": article.get('summary', ''),
            "source": "OpenHarmony",  # 明确标注来源为OpenHarmony官网
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def crawl_openharmony_news(self, batch_callback=None, batch_size=20):
        import logging
        logger = logging.getLogger(__name__)

        logger.info("🌐 开始爬取OpenHarmony官网新闻...")
        if batch_callback:
            logger.info(f"📦 启用分批处理模式，每 {batch_size} 篇文章执行一次回调")

        articles_info = self.get_all_article_infos()
        logger.info(f"📋 获取到 {len(articles_info)} 篇文章信息")

        all_articles_data = []
        batch_articles = []

        for i, info in enumerate(articles_info):
            title = info["title"]
            date = info["date"]
            article_url = info["url"]
            logger.info(f"🔍 正在处理第 {i+1}/{len(articles_info)} 篇文章: {title}")
            logger.debug(f"🔗 文章URL: {article_url}")

            article_data = self.parse_article_content(article_url)
            if article_data:
                article_info = self._format_article({
                    "title": title,
                    "date": date,
                    "url": article_url,
                    "content": article_data
                })
                all_articles_data.append(article_info)
                batch_articles.append(article_info)
                logger.info(f"✅ 成功解析文章，共 {len(article_data)} 个内容块")

                # 检查是否达到批处理大小
                if len(batch_articles) >= batch_size and batch_callback:
                    try:
                        logger.info(f"📦 [分批处理] 达到批处理大小 {batch_size}，执行回调...")
                        batch_callback(batch_articles.copy())
                        batch_articles.clear()  # 清空当前批次
                        logger.info(f"✅ [分批处理] 回调执行成功，继续处理后续文章")
                    except Exception as callback_e:
                        logger.error(f"❌ [分批处理] 回调执行失败: {callback_e}")
            else:
                logger.warning(f"⚠️ 文章内容解析失败: {title}")
            time.sleep(1)

        # 处理剩余的批次
        if batch_articles and batch_callback:
            try:
                logger.info(f"📦 [分批处理] 处理最后剩余的 {len(batch_articles)} 篇文章...")
                batch_callback(batch_articles.copy())
                logger.info(f"✅ [分批处理] 最后批次处理完成")
            except Exception as callback_e:
                logger.error(f"❌ [分批处理] 最后批次处理失败: {callback_e}")

        logger.info(f"🎉 OpenHarmony官网爬取完成，共处理 {len(all_articles_data)} 篇文章")
        return all_articles_data

def main():
    print("OpenHarmony官网新闻爬虫启动...")
    print("注意：此脚本需要安装以下依赖:")
    print("  pip install requests beautifulsoup4")
    print("-" * 50)
    crawler = OpenHarmonyNewsCrawler()
    try:
        results = crawler.crawl_openharmony_news()
        if results:
            print(f"\n爬取完成，共处理 {len(results)} 篇文章")
        else:
            print("\n爬取完成，但未找到任何文章")
    except Exception as e:
        print(f"爬取过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
