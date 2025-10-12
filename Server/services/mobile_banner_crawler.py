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
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class MobileBannerCrawler:
    """
    专门用于爬取OpenHarmony官网手机版的banner图片爬虫
    模拟手机浏览器UA访问，获取手机版页面的banner-img类名图片
    """
    
    def __init__(self):
        self.base_url = "https://old.openharmony.cn"
        self.target_url = "https://old.openharmony.cn/mainPlay"
        self.source = "OpenHarmony-Mobile-Banner"
        self.session = requests.Session()
        
        # 手机端User-Agent池
        self.mobile_user_agents = [
            # iPhone Safari
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            
            # Android Chrome
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36',
            
            # Huawei/Honor手机
            'Mozilla/5.0 (Linux; Android 12; NOH-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; ELS-AN00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
            
            # 小米手机
            'Mozilla/5.0 (Linux; Android 13; MI 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; MI 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
            
            # iPad
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        ]
        
        # 设置手机端请求头
        self.setup_mobile_headers()
    
    def setup_mobile_headers(self):
        """设置手机端请求头"""
        import random
        
        mobile_ua = random.choice(self.mobile_user_agents)
        
        self.session.headers.update({
            'User-Agent': mobile_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            # 模拟手机端viewport
            'Viewport-Width': '390',
            'Device-Memory': '8',
            'DPR': '3',
        })
        
        logger.info(f"📱 已设置手机端请求头，User-Agent: {mobile_ua[:50]}...")
    
    def get_mobile_page_content(self, url):
        """
        获取手机版页面内容
        """
        try:
            logger.info(f"📱 正在请求手机版页面: {url}")
            
            # 重新设置随机的手机端UA，防止被识别
            self.setup_mobile_headers()
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # 检查响应是否是手机版
            content_length = len(response.text)
            logger.info(f"📱 页面加载成功，内容长度: {content_length} 字符")
            
            # 简单检查是否获取到了移动版本
            if 'viewport' in response.text.lower() or 'mobile' in response.text.lower():
                logger.info("✅ 成功获取手机版页面内容")
            else:
                logger.warning("⚠️ 可能未获取到手机版页面，但继续处理")
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 请求手机版页面失败: {url}, 错误: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取手机版页面内容时发生未知错误: {e}")
            return None
    
    def extract_banner_images(self, html_content):
        """
        从HTML内容中提取banner相关的图片
        包括banner-img类名、轮播图、主要展示图片等
        """
        banner_images = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            logger.info("🔍 开始解析HTML内容，查找banner相关图片...")
            
            # 1. 查找所有包含banner-img类名的元素
            banner_img_elements = soup.find_all(class_=re.compile(r'.*banner-img.*'))
            logger.info(f"🔍 找到 {len(banner_img_elements)} 个包含 banner-img 类名的元素")
            
            # 2. 查找其他banner相关的类名
            banner_class_patterns = [
                r'.*banner.*',
                r'.*swiper.*slide.*',
                r'.*carousel.*',
                r'.*slider.*',
                r'.*hero.*',
                r'.*main.*banner.*',
                r'.*top.*banner.*'
            ]
            
            for pattern in banner_class_patterns:
                elements = soup.find_all(class_=re.compile(pattern, re.IGNORECASE))
                banner_img_elements.extend(elements)
                logger.info(f"🔍 通过模式 '{pattern}' 找到 {len(elements)} 个元素")
            
            # 3. 处理找到的banner元素
            for idx, element in enumerate(banner_img_elements):
                logger.debug(f"处理第 {idx + 1} 个banner元素: {element.name}, class: {element.get('class')}")
                
                # 处理img标签
                if element.name == 'img':
                    img_url = self.extract_image_url(element)
                    if img_url:
                        image_info = self.create_image_info(img_url, element, f"banner-img-{idx + 1}")
                        banner_images.append(image_info)
                        logger.info(f"✅ 提取到banner图片: {img_url}")
                
                # 处理包含img子元素的容器
                img_tags = element.find_all('img')
                for img_idx, img_tag in enumerate(img_tags):
                    img_url = self.extract_image_url(img_tag)
                    if img_url:
                        image_info = self.create_image_info(img_url, img_tag, f"banner-container-{idx + 1}-{img_idx + 1}")
                        banner_images.append(image_info)
                        logger.info(f"✅ 提取到嵌套banner图片: {img_url}")
                
                # 处理CSS背景图片
                bg_url = self.extract_background_image(element)
                if bg_url:
                    image_info = self.create_image_info(bg_url, element, f"banner-bg-{idx + 1}")
                    banner_images.append(image_info)
                    logger.info(f"✅ 提取到banner背景图片: {bg_url}")
            
            # 4. 查找页面中所有较大的图片（可能是banner）
            all_images = soup.find_all('img')
            logger.info(f"🔍 页面总共有 {len(all_images)} 张图片，筛选可能的banner图片...")
            
            for idx, img in enumerate(all_images):
                img_url = self.extract_image_url(img)
                if img_url:
                    # 检查图片URL是否包含banner相关关键词
                    banner_keywords = ['banner', 'slide', 'carousel', 'hero', 'main', 'top', 'header']
                    img_url_lower = img_url.lower()
                    
                    if any(keyword in img_url_lower for keyword in banner_keywords):
                        image_info = self.create_image_info(img_url, img, f"potential-banner-{idx + 1}")
                        banner_images.append(image_info)
                        logger.info(f"✅ 发现可能的banner图片（通过URL关键词）: {img_url}")
                    
                    # 检查img标签的class或其他属性
                    class_list = img.get('class', [])
                    class_str = ' '.join(class_list) if isinstance(class_list, list) else str(class_list)
                    
                    if any(keyword in class_str.lower() for keyword in banner_keywords):
                        image_info = self.create_image_info(img_url, img, f"class-banner-{idx + 1}")
                        banner_images.append(image_info)
                        logger.info(f"✅ 发现可能的banner图片（通过class）: {img_url}")
            
            # 5. 额外查找：通过data属性查找可能的banner图片
            data_banner_elements = soup.find_all(attrs={"data-banner": True}) + soup.find_all(attrs={"data-bg": True})
            for idx, element in enumerate(data_banner_elements):
                for attr in ['data-banner', 'data-bg', 'data-src', 'data-original']:
                    img_url = element.get(attr)
                    if img_url and self.is_valid_image_url(img_url):
                        img_url = urljoin(self.base_url, img_url)
                        image_info = self.create_image_info(img_url, element, f"data-banner-{idx + 1}")
                        banner_images.append(image_info)
                        logger.info(f"✅ 通过data属性提取到图片: {img_url}")
                        break
            
            # 6. 去重
            unique_images = []
            seen_urls = set()
            for img in banner_images:
                if img['url'] not in seen_urls:
                    unique_images.append(img)
                    seen_urls.add(img['url'])
            
            logger.info(f"🎯 共提取到 {len(unique_images)} 张唯一的banner相关图片")
            
            # 7. 如果还是没有找到图片，记录页面结构用于调试
            if len(unique_images) == 0:
                logger.warning("🔍 未找到banner图片，分析页面结构...")
                self._debug_page_structure(soup)
            
            return unique_images
            
        except Exception as e:
            logger.error(f"❌ 解析banner图片时发生错误: {e}")
            return []
    
    def _debug_page_structure(self, soup):
        """
        调试页面结构，输出关键信息
        """
        try:
            # 查找所有包含图片的元素
            img_count = len(soup.find_all('img'))
            logger.info(f"📊 页面调试信息：")
            logger.info(f"   - 总图片数量: {img_count}")
            
            # 输出前5个图片的信息
            images = soup.find_all('img')[:5]
            for i, img in enumerate(images):
                src = img.get('src', img.get('data-src', '无'))
                class_name = img.get('class', '无')
                alt = img.get('alt', '无')
                logger.info(f"   - 图片{i+1}: src={src[:50]}..., class={class_name}, alt={alt}")
            
            # 查找所有可能的轮播或banner容器
            possible_containers = soup.find_all(['div', 'section'], class_=re.compile(r'.*(banner|swiper|carousel|slider|hero).*', re.IGNORECASE))
            logger.info(f"   - 可能的banner容器数量: {len(possible_containers)}")
            
            for i, container in enumerate(possible_containers[:3]):
                class_name = container.get('class', '无')
                child_imgs = len(container.find_all('img'))
                logger.info(f"   - 容器{i+1}: class={class_name}, 包含图片={child_imgs}张")
                
        except Exception as e:
            logger.error(f"调试页面结构时出错: {e}")
    
    def extract_image_url(self, img_element):
        """
        从img元素中提取图片URL
        """
        # 尝试多种可能的图片URL属性
        url_attributes = ['src', 'data-src', 'data-original', 'data-lazy', 'data-echo', 'srcset']
        
        for attr in url_attributes:
            img_url = img_element.get(attr)
            if img_url:
                # 处理srcset属性（可能包含多个URL）
                if attr == 'srcset':
                    # srcset格式: "url1 1x, url2 2x" 或 "url1 480w, url2 800w"
                    urls = re.findall(r'(https?://[^\s,]+)', img_url)
                    if urls:
                        img_url = urls[0]  # 使用第一个URL
                    else:
                        continue
                
                if self.is_valid_image_url(img_url):
                    return urljoin(self.base_url, img_url)
        
        return None
    
    def extract_background_image(self, element):
        """
        从元素的style属性中提取背景图片URL
        """
        style = element.get('style', '')
        if 'background-image' in style:
            # 匹配 background-image: url('...') 或 background-image: url("...")
            bg_match = re.search(r'background-image:\s*url\([\'"]?([^\'"()]+)[\'"]?\)', style)
            if bg_match:
                bg_url = bg_match.group(1)
                if self.is_valid_image_url(bg_url):
                    return urljoin(self.base_url, bg_url)
        
        return None
    
    def is_valid_image_url(self, url):
        """
        验证是否是有效的图片URL
        """
        if not url or len(url.strip()) == 0:
            return False
        
        # 检查是否是图片扩展名
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        url_lower = url.lower()
        
        # 直接检查扩展名
        for ext in image_extensions:
            if ext in url_lower:
                return True
        
        # 检查是否包含图片相关路径
        image_keywords = ['image', 'img', 'pic', 'photo', 'banner', 'bg']
        for keyword in image_keywords:
            if keyword in url_lower:
                return True
        
        # 如果URL看起来像是base64数据，跳过
        if url.startswith('data:'):
            return True if 'image' in url else False
        
        return False
    
    def create_image_info(self, img_url, element, image_id):
        """
        创建图片信息对象
        """
        # 获取图片的alt属性或其他描述信息
        alt_text = element.get('alt', '')
        title_text = element.get('title', '')
        class_names = element.get('class', [])
        
        # 尝试从URL中提取文件名
        parsed_url = urlparse(img_url)
        filename = os.path.basename(parsed_url.path) or f"banner_image_{image_id}"
        
        return {
            "id": image_id,
            "url": img_url,
            "alt": alt_text,
            "title": title_text,
            "filename": filename,
            "classes": class_names if isinstance(class_names, list) else [class_names] if class_names else [],
            "source": self.source,
            "extracted_at": datetime.now().isoformat(),
            "page_url": self.target_url
        }
    
    def download_image(self, image_info, save_directory="downloads/banners"):
        """
        下载图片到本地
        """
        try:
            # 创建保存目录
            os.makedirs(save_directory, exist_ok=True)
            
            img_url = image_info['url']
            filename = image_info['filename']
            
            # 确保文件名有扩展名
            if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                # 从URL中尝试获取扩展名
                url_ext = os.path.splitext(urlparse(img_url).path)[1]
                if url_ext:
                    filename += url_ext
                else:
                    filename += '.jpg'  # 默认扩展名
            
            file_path = os.path.join(save_directory, filename)
            
            logger.info(f"⬇️ 开始下载图片: {img_url}")
            
            response = self.session.get(img_url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            logger.info(f"✅ 图片下载成功: {file_path} (大小: {file_size} bytes)")
            
            # 更新图片信息
            image_info['local_path'] = file_path
            image_info['file_size'] = file_size
            image_info['downloaded'] = True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 下载图片失败: {img_url}, 错误: {e}")
            image_info['downloaded'] = False
            image_info['download_error'] = str(e)
            return False
    
    def crawl_mobile_banners(self, download_images=True, save_directory="downloads/banners"):
        """
        主要方法：爬取手机版banner图片
        
        Args:
            download_images: 是否下载图片到本地
            save_directory: 图片保存目录
            
        Returns:
            包含所有banner图片信息的列表
        """
        logger.info(f"🚀 开始爬取OpenHarmony手机版banner图片")
        logger.info(f"🎯 目标URL: {self.target_url}")
        
        # 获取手机版页面内容
        html_content = self.get_mobile_page_content(self.target_url)
        if not html_content:
            logger.error("❌ 无法获取页面内容，爬取失败")
            return []
        
        # 提取banner图片
        banner_images = self.extract_banner_images(html_content)
        
        if not banner_images:
            logger.warning("⚠️ 未找到任何banner图片")
            return []
        
        logger.info(f"🎉 成功提取到 {len(banner_images)} 张banner图片")
        
        # 下载图片（如果需要）
        if download_images:
            logger.info(f"⬇️ 开始下载图片到目录: {save_directory}")
            download_success_count = 0
            
            for img_info in banner_images:
                if self.download_image(img_info, save_directory):
                    download_success_count += 1
                time.sleep(0.5)  # 避免请求过快
            
            logger.info(f"📁 图片下载完成，成功下载 {download_success_count}/{len(banner_images)} 张图片")
        
        # 保存结果到JSON文件
        result_file = os.path.join(save_directory, "banner_images_info.json")
        try:
            os.makedirs(os.path.dirname(result_file), exist_ok=True)
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "crawl_time": datetime.now().isoformat(),
                    "target_url": self.target_url,
                    "total_images": len(banner_images),
                    "images": banner_images
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 图片信息已保存到: {result_file}")
        except Exception as e:
            logger.error(f"❌ 保存图片信息失败: {e}")
        
        return banner_images
    
    def get_banner_summary(self, banner_images):
        """
        获取banner图片的统计摘要
        """
        if not banner_images:
            return {"total": 0, "downloaded": 0, "failed": 0, "success_rate": "0%"}
        
        total = len(banner_images)
        downloaded = sum(1 for img in banner_images if img.get('downloaded', False))
        failed = total - downloaded
        
        success_rate = f"{(downloaded / total * 100):.1f}%" if total > 0 else "0%"
        return {
            "total": total,
            "downloaded": downloaded,
            "failed": failed,
            "success_rate": success_rate
        }

def main():
    """
    主函数：演示如何使用MobileBannerCrawler
    """
    print("📱 OpenHarmony手机版Banner图片爬虫启动...")
    print("=" * 60)
    
    crawler = MobileBannerCrawler()
    
    try:
        # 爬取banner图片
        banner_images = crawler.crawl_mobile_banners(
            download_images=True,
            save_directory="downloads/mobile_banners"
        )
        
        # 输出统计信息
        summary = crawler.get_banner_summary(banner_images)
        print(f"\n📊 爬取结果统计:")
        print(f"   总计图片: {summary['total']} 张")
        print(f"   下载成功: {summary['downloaded']} 张")
        print(f"   下载失败: {summary['failed']} 张")
        print(f"   成功率: {summary['success_rate']}")
        
        # 显示图片列表
        if banner_images:
            print(f"\n📋 Banner图片列表:")
            for i, img in enumerate(banner_images, 1):
                print(f"   {i}. {img['filename']}")
                print(f"      URL: {img['url']}")
                print(f"      Alt: {img['alt'] or '无'}")
                print(f"      下载状态: {'✅ 成功' if img.get('downloaded') else '❌ 失败'}")
                print()
        
    except Exception as e:
        print(f"❌ 爬取过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()
