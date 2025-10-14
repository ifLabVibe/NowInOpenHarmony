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
import os
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging

class OpenHarmonyImageCrawler:
    """OpenHarmony官网banner图片爬虫"""
    
    def __init__(self, download_path="./downloads/images"):
        self.base_url = "https://old.openharmony.cn"
        self.target_url = "https://old.openharmony.cn/mainPlay/"
        self.download_path = download_path
        self.session = requests.Session()
        
        # 设置手机版User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # 创建下载目录
        os.makedirs(self.download_path, exist_ok=True)
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def get_page_content(self, url):
        """获取页面内容"""
        try:
            self.logger.info(f"🌐 正在获取页面: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            self.logger.info(f"✅ 页面获取成功，状态码: {response.status_code}")
            return response.text
        except Exception as e:
            self.logger.error(f"❌ 获取页面失败: {url}, 错误: {e}")
            return None
    
    def find_banner_images(self, html_content):
        """查找页面中所有class为banner-img的图片"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有class包含banner-img的img标签
        banner_images = soup.find_all('img', class_=lambda x: x and 'banner-img' in x)
        
        image_urls = []
        for img in banner_images:
            # 获取图片URL，优先级：data-src > data-original > src
            img_src = (
                img.get('data-src') or 
                img.get('data-original') or 
                img.get('src')
            )
            
            if img_src:
                # 转换为绝对URL
                full_url = urljoin(self.base_url, img_src)
                
                # 获取图片的alt属性作为描述
                alt_text = img.get('alt', '')
                
                # 获取图片的其他属性
                img_class = img.get('class', [])
                img_id = img.get('id', '')
                
                image_info = {
                    'url': full_url,
                    'alt': alt_text,
                    'class': img_class,
                    'id': img_id,
                    'original_src': img_src
                }
                
                image_urls.append(image_info)
                self.logger.info(f"🖼️  发现banner图片: {alt_text or '无描述'} - {full_url}")
        
        self.logger.info(f"📊 共发现 {len(image_urls)} 张banner图片")
        return image_urls
    
    def download_image(self, image_info):
        """下载单张图片"""
        url = image_info['url']
        alt_text = image_info['alt']
        
        try:
            self.logger.info(f"⬇️  正在下载图片: {alt_text or '无描述'}")
            
            # 获取文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # 如果没有文件扩展名，尝试从Content-Type推断
            if not filename or '.' not in filename:
                head_response = self.session.head(url, timeout=10)
                content_type = head_response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    filename = f"banner_image_{int(time.time())}.jpg"
                elif 'png' in content_type:
                    filename = f"banner_image_{int(time.time())}.png"
                elif 'gif' in content_type:
                    filename = f"banner_image_{int(time.time())}.gif"
                elif 'webp' in content_type:
                    filename = f"banner_image_{int(time.time())}.webp"
                else:
                    filename = f"banner_image_{int(time.time())}.jpg"
            
            # 构建完整的文件路径
            file_path = os.path.join(self.download_path, filename)
            
            # 如果文件已存在，添加时间戳避免重复
            if os.path.exists(file_path):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(time.time())}{ext}"
                file_path = os.path.join(self.download_path, filename)
            
            # 下载图片
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 保存图片
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            self.logger.info(f"✅ 图片下载成功: {filename} ({file_size} bytes)")
            
            return {
                'status': 'success',
                'filename': filename,
                'file_path': file_path,
                'file_size': file_size,
                'url': url,
                'alt': alt_text
            }
            
        except Exception as e:
            self.logger.error(f"❌ 图片下载失败: {url}, 错误: {e}")
            return {
                'status': 'failed',
                'url': url,
                'alt': alt_text,
                'error': str(e)
            }
    
    def crawl_banner_images(self):
        """爬取所有banner图片"""
        self.logger.info("🚀 开始爬取OpenHarmony官网banner图片...")
        self.logger.info(f"🎯 目标页面: {self.target_url}")
        self.logger.info(f"📱 使用手机版User-Agent")
        self.logger.info(f"📁 下载目录: {self.download_path}")
        
        # 获取页面内容
        html_content = self.get_page_content(self.target_url)
        if not html_content:
            self.logger.error("❌ 无法获取页面内容，爬取终止")
            return []
        
        # 查找banner图片
        image_infos = self.find_banner_images(html_content)
        if not image_infos:
            self.logger.warning("⚠️  未找到任何banner图片")
            return []
        
        # 下载图片
        download_results = []
        for i, image_info in enumerate(image_infos, 1):
            self.logger.info(f"📥 处理第 {i}/{len(image_infos)} 张图片...")
            result = self.download_image(image_info)
            download_results.append(result)
            
            # 添加延时避免请求过于频繁
            time.sleep(1)
        
        # 统计结果
        successful_downloads = [r for r in download_results if r['status'] == 'success']
        failed_downloads = [r for r in download_results if r['status'] == 'failed']
        
        self.logger.info(f"🎉 爬取完成！")
        self.logger.info(f"✅ 成功下载: {len(successful_downloads)} 张图片")
        self.logger.info(f"❌ 下载失败: {len(failed_downloads)} 张图片")
        
        if successful_downloads:
            self.logger.info("📋 成功下载的图片:")
            for result in successful_downloads:
                self.logger.info(f"  - {result['filename']} ({result['file_size']} bytes)")
        
        if failed_downloads:
            self.logger.info("❌ 下载失败的图片:")
            for result in failed_downloads:
                self.logger.info(f"  - {result['url']} (错误: {result['error']})")
        
        return download_results
    
    def get_banner_image_info(self):
        """只获取banner图片信息，不下载"""
        self.logger.info("🔍 获取OpenHarmony官网banner图片信息...")
        
        html_content = self.get_page_content(self.target_url)
        if not html_content:
            return []
        
        return self.find_banner_images(html_content)


def main():
    """主函数 - 演示爬虫使用"""
    print("🎯 OpenHarmony官网Banner图片爬虫")
    print("=" * 50)
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('banner_crawler.log', encoding='utf-8')
        ]
    )
    
    # 创建爬虫实例
    crawler = OpenHarmonyImageCrawler(download_path="./banner_images")
    
    try:
        # 爬取并下载图片
        results = crawler.crawl_banner_images()
        
        if results:
            print(f"\n📊 爬取结果统计:")
            successful = sum(1 for r in results if r['status'] == 'success')
            failed = sum(1 for r in results if r['status'] == 'failed')
            print(f"  ✅ 成功: {successful} 张")
            print(f"  ❌ 失败: {failed} 张")
            print(f"  📁 保存位置: {crawler.download_path}")
        else:
            print("⚠️  未找到任何banner图片")
            
    except Exception as e:
        print(f"❌ 爬取过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
