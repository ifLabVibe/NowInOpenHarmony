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

"""
增强版手机Banner爬虫 - 支持JavaScript动态加载内容
使用Selenium WebDriver来获取动态渲染的轮播图片
"""

import time
import json
import os
import logging
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional

# 尝试导入Selenium相关模块
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 备选：尝试导入requests-html（另一种处理JS的方案）
try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedMobileBannerCrawler:
    """
    增强版手机Banner爬虫
    支持多种方式获取动态加载的轮播图：
    1. Selenium WebDriver（首选）
    2. requests-html（备选）
    3. 直接API调用（如果能找到接口）
    4. 传统HTML解析（兜底方案）
    """
    
    def __init__(self):
        self.base_url = "https://old.openharmony.cn"
        self.target_url = "https://old.openharmony.cn/mainPlay"
        self.source = "OpenHarmony-Enhanced-Mobile-Banner"
        
        # 手机端User-Agent
        self.mobile_user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        
        # 初始化结果
        self.banner_images = []
        
        logger.info(f"🚀 初始化增强版手机Banner爬虫")
        logger.info(f"   - Selenium可用: {SELENIUM_AVAILABLE}")
        logger.info(f"   - requests-html可用: {REQUESTS_HTML_AVAILABLE}")
    
    def get_webdriver_options(self) -> Options:
        """配置Chrome浏览器选项"""
        import tempfile
        import uuid

        options = Options()

        # 基本设置
        options.add_argument("--headless")  # 无头模式
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # 禁用图片加载以提高速度

        # 修复：使用唯一的临时目录避免冲突
        temp_dir = tempfile.gettempdir()
        unique_user_data_dir = os.path.join(temp_dir, f"chrome_user_data_{uuid.uuid4().hex[:8]}")
        options.add_argument(f"--user-data-dir={unique_user_data_dir}")

        # 禁用缓存相关功能避免权限问题
        options.add_argument("--disable-cache")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disk-cache-size=0")

        # 手机模拟设置
        options.add_argument(f"--user-agent={self.mobile_user_agent}")

        # 手机设备模拟
        mobile_emulation = {
            "deviceMetrics": {
                "width": 390,
                "height": 844,
                "pixelRatio": 3.0
            },
            "userAgent": self.mobile_user_agent
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)

        # 性能优化
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")

        # 禁用自动化检测
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        return options
    
    def crawl_with_selenium(self) -> List[Dict]:
        """使用Selenium获取动态加载的轮播图"""
        if not SELENIUM_AVAILABLE:
            logger.warning("❌ Selenium不可用，跳过此方法")
            return []
        
        logger.info("🎯 使用Selenium获取动态轮播图...")
        
        driver = None
        try:
            # 配置Chrome选项
            options = self.get_webdriver_options()
            
            # 初始化WebDriver
            driver = webdriver.Chrome(options=options)
            
            # 设置页面加载超时
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            logger.info(f"📱 访问页面: {self.target_url}")
            driver.get(self.target_url)
            
            # 等待页面初始加载
            time.sleep(3)
            
            # 等待轮播容器出现
            try:
                wait = WebDriverWait(driver, 15)
                carousel_container = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "el-carousel"))
                )
                logger.info("✅ 轮播容器已加载")
            except TimeoutException:
                logger.warning("⚠️ 轮播容器加载超时，继续执行...")
            
            # 尝试触发轮播图加载的多种方法
            self._trigger_carousel_loading(driver)
            
            # 等待动态内容加载
            time.sleep(5)
            
            # 查找轮播图片
            banner_images = self._extract_images_from_selenium(driver)
            
            logger.info(f"🎉 Selenium方法获取到 {len(banner_images)} 张轮播图")
            return banner_images
            
        except WebDriverException as e:
            logger.error(f"❌ Selenium WebDriver错误: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Selenium方法出现未知错误: {e}")
            return []
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("🔧 已关闭WebDriver")
                except:
                    pass
    
    def _trigger_carousel_loading(self, driver):
        """触发轮播图加载的各种方法"""
        try:
            # 1. 滚动页面
            logger.info("🔄 执行页面滚动...")
            driver.execute_script("window.scrollTo(0, 300);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 2. 模拟鼠标悬停在轮播区域
            try:
                banner_element = driver.find_element(By.CLASS_NAME, "banner")
                webdriver.ActionChains(driver).move_to_element(banner_element).perform()
                logger.info("🖱️ 模拟鼠标悬停")
                time.sleep(2)
            except:
                pass
            
            # 3. 尝试点击轮播指示器
            try:
                indicators = driver.find_elements(By.CSS_SELECTOR, ".el-carousel__indicators li")
                if indicators:
                    indicators[0].click()
                    logger.info("👆 点击轮播指示器")
                    time.sleep(2)
            except:
                pass
            
            # 4. 执行自定义JavaScript触发事件
            js_trigger = """
            // 尝试触发Vue组件的数据加载
            if (window.Vue) {
                console.log('Vue detected, triggering events...');
            }
            
            // 触发resize事件
            window.dispatchEvent(new Event('resize'));
            
            // 触发DOMContentLoaded事件
            window.dispatchEvent(new Event('DOMContentLoaded'));
            
            // 查找并触发轮播组件的方法
            var carousels = document.querySelectorAll('.el-carousel');
            carousels.forEach(function(carousel) {
                if (carousel.__vue__) {
                    console.log('Found Vue carousel component');
                    // 尝试触发Vue组件的更新
                    if (carousel.__vue__.$forceUpdate) {
                        carousel.__vue__.$forceUpdate();
                    }
                }
            });
            """
            
            driver.execute_script(js_trigger)
            logger.info("⚡ 执行JavaScript触发脚本")
            time.sleep(3)
            
        except Exception as e:
            logger.warning(f"⚠️ 触发轮播加载时出错: {e}")
    
    def _extract_images_from_selenium(self, driver) -> List[Dict]:
        """从Selenium页面中提取图片"""
        banner_images = []
        
        try:
            # 获取页面源码用于调试
            page_source = driver.page_source
            
            # 1. 查找轮播容器中的图片
            carousel_selectors = [
                ".el-carousel img",
                ".banner img", 
                ".el-carousel__item img",
                ".carousel img",
                ".swiper-slide img",
                ".banner-img",
                "img[class*='banner']",
                "img[class*='carousel']"
            ]
            
            for selector in carousel_selectors:
                try:
                    images = driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"🔍 选择器 '{selector}' 找到 {len(images)} 个图片元素")
                    
                    for idx, img_element in enumerate(images):
                        img_info = self._extract_image_info_from_element(img_element, f"{selector}-{idx}")
                        if img_info:
                            banner_images.append(img_info)
                            
                except Exception as e:
                    logger.debug(f"选择器 '{selector}' 查找失败: {e}")
            
            # 2. 查找所有img标签，筛选可能的banner图片
            all_images = driver.find_elements(By.TAG_NAME, "img")
            logger.info(f"🔍 页面总共有 {len(all_images)} 个img元素")
            
            for idx, img_element in enumerate(all_images):
                try:
                    src = img_element.get_attribute("src")
                    data_src = img_element.get_attribute("data-src")
                    class_name = img_element.get_attribute("class") or ""
                    
                    # 检查是否是banner相关图片
                    banner_keywords = ['banner', 'carousel', 'slide', 'hero', 'main']
                    
                    if (src and any(keyword in src.lower() for keyword in banner_keywords)) or \
                       (data_src and any(keyword in data_src.lower() for keyword in banner_keywords)) or \
                       any(keyword in class_name.lower() for keyword in banner_keywords):
                        
                        img_info = self._extract_image_info_from_element(img_element, f"potential-banner-{idx}")
                        if img_info:
                            banner_images.append(img_info)
                            logger.info(f"✅ 发现潜在banner图片: {img_info['url']}")
                
                except Exception as e:
                    logger.debug(f"处理图片元素 {idx} 时出错: {e}")
            
            # 3. 尝试执行JavaScript获取动态数据
            try:
                js_get_images = """
                var images = [];
                
                // 查找所有可能的图片数据
                var carouselElements = document.querySelectorAll('.el-carousel, .banner, .carousel');
                carouselElements.forEach(function(el) {
                    var imgs = el.querySelectorAll('img');
                    imgs.forEach(function(img) {
                        if (img.src && img.src.length > 0) {
                            images.push({
                                url: img.src,
                                alt: img.alt || '',
                                className: img.className || ''
                            });
                        }
                    });
                });
                
                // 查找Vue组件中的数据
                if (window.Vue) {
                    var vueComponents = document.querySelectorAll('[data-v-7a548dc3]');
                    vueComponents.forEach(function(el) {
                        if (el.__vue__ && el.__vue__.$data) {
                            console.log('Vue component data:', el.__vue__.$data);
                        }
                    });
                }
                
                return images;
                """
                
                js_result = driver.execute_script(js_get_images)
                if js_result:
                    logger.info(f"🎯 JavaScript执行结果获取到 {len(js_result)} 张图片")
                    for js_img in js_result:
                        img_info = {
                            "id": f"js-{len(banner_images)}",
                            "url": js_img.get("url", ""),
                            "alt": js_img.get("alt", ""),
                            "title": "",
                            "filename": os.path.basename(urlparse(js_img.get("url", "")).path) or "banner_image.jpg",
                            "classes": js_img.get("className", "").split(),
                            "source": self.source,
                            "extracted_at": datetime.now().isoformat(),
                            "page_url": self.target_url,
                            "method": "selenium-javascript"
                        }
                        banner_images.append(img_info)
                        
            except Exception as e:
                logger.warning(f"⚠️ JavaScript执行失败: {e}")
            
            # 去重
            unique_images = []
            seen_urls = set()
            for img in banner_images:
                url = img.get('url', '')
                if url and url not in seen_urls:
                    unique_images.append(img)
                    seen_urls.add(url)
            
            return unique_images
            
        except Exception as e:
            logger.error(f"❌ 提取图片信息时出错: {e}")
            return []
    
    def _extract_image_info_from_element(self, img_element, image_id: str) -> Optional[Dict]:
        """从Selenium图片元素中提取信息"""
        try:
            # 获取图片URL
            src = img_element.get_attribute("src")
            data_src = img_element.get_attribute("data-src")
            data_original = img_element.get_attribute("data-original")
            
            img_url = src or data_src or data_original
            
            if not img_url or img_url.startswith('data:'):
                return None
            
            # 转换为绝对URL
            if not img_url.startswith('http'):
                img_url = urljoin(self.base_url, img_url)
            
            # 获取其他属性
            alt_text = img_element.get_attribute("alt") or ""
            title_text = img_element.get_attribute("title") or ""
            class_names = img_element.get_attribute("class") or ""
            
            # 获取文件名
            filename = os.path.basename(urlparse(img_url).path) or f"banner_image_{image_id}.jpg"
            
            return {
                "id": image_id,
                "url": img_url,
                "alt": alt_text,
                "title": title_text,
                "filename": filename,
                "classes": class_names.split() if class_names else [],
                "source": self.source,
                "extracted_at": datetime.now().isoformat(),
                "page_url": self.target_url,
                "method": "selenium"
            }
            
        except Exception as e:
            logger.debug(f"提取图片元素信息失败: {e}")
            return None
    
    def crawl_with_requests_html(self) -> List[Dict]:
        """使用requests-html获取动态内容（备选方案）"""
        if not REQUESTS_HTML_AVAILABLE:
            logger.warning("❌ requests-html不可用，跳过此方法")
            return []
        
        logger.info("🎯 使用requests-html获取动态内容...")
        
        try:
            session = HTMLSession()
            
            # 设置手机端User-Agent
            session.headers.update({
                'User-Agent': self.mobile_user_agent
            })
            
            response = session.get(self.target_url)
            
            # 渲染JavaScript
            logger.info("⚡ 正在渲染JavaScript...")
            response.html.render(timeout=20, wait=3)
            
            # 查找图片
            banner_images = []
            
            # 使用CSS选择器查找图片
            selectors = [
                '.el-carousel img',
                '.banner img',
                'img[class*="banner"]',
                'img[class*="carousel"]'
            ]
            
            for selector in selectors:
                images = response.html.find(selector)
                logger.info(f"🔍 选择器 '{selector}' 找到 {len(images)} 个图片")
                
                for idx, img in enumerate(images):
                    img_url = img.attrs.get('src') or img.attrs.get('data-src')
                    if img_url:
                        img_info = {
                            "id": f"requests-html-{len(banner_images)}",
                            "url": urljoin(self.base_url, img_url),
                            "alt": img.attrs.get('alt', ''),
                            "title": img.attrs.get('title', ''),
                            "filename": os.path.basename(urlparse(img_url).path) or f"banner_{idx}.jpg",
                            "classes": img.attrs.get('class', '').split(),
                            "source": self.source,
                            "extracted_at": datetime.now().isoformat(),
                            "page_url": self.target_url,
                            "method": "requests-html"
                        }
                        banner_images.append(img_info)
            
            return banner_images
            
        except Exception as e:
            logger.error(f"❌ requests-html方法失败: {e}")
            return []
    
    def crawl_mobile_banners(self, download_images=True, save_directory="downloads/enhanced_banners") -> List[Dict]:
        """
        主要方法：使用多种方式爬取手机版banner图片
        """
        logger.info("🚀 开始增强版手机Banner爬取...")
        logger.info(f"🎯 目标URL: {self.target_url}")
        
        all_banner_images = []
        
        # 方法1：使用Selenium（首选）
        if SELENIUM_AVAILABLE:
            logger.info("📱 尝试方法1: Selenium WebDriver")
            selenium_images = self.crawl_with_selenium()
            all_banner_images.extend(selenium_images)
        
        # 方法2：使用requests-html（备选）
        if not all_banner_images and REQUESTS_HTML_AVAILABLE:
            logger.info("📱 尝试方法2: requests-html")
            requests_html_images = self.crawl_with_requests_html()
            all_banner_images.extend(requests_html_images)
        
        # 方法3：传统方式兜底
        if not all_banner_images:
            logger.info("📱 尝试方法3: 传统HTML解析（兜底）")
            try:
                from services.mobile_banner_crawler import MobileBannerCrawler
                traditional_crawler = MobileBannerCrawler()
                traditional_images = traditional_crawler.crawl_mobile_banners(download_images=False)
                all_banner_images.extend(traditional_images)
            except ImportError:
                logger.warning("⚠️ 无法导入传统爬虫，跳过兜底方案")
        
        # 去重处理
        unique_images = []
        seen_urls = set()
        for img in all_banner_images:
            url = img.get('url', '')
            if url and url not in seen_urls:
                unique_images.append(img)
                seen_urls.add(url)
        
        logger.info(f"🎉 总共获取到 {len(unique_images)} 张唯一的banner图片")
        
        # 下载图片（如果需要）
        if download_images and unique_images:
            self._download_images(unique_images, save_directory)
        
        # 保存结果
        self._save_results(unique_images, save_directory)
        
        return unique_images
    
    def _download_images(self, images: List[Dict], save_directory: str):
        """下载图片到本地"""
        logger.info(f"⬇️ 开始下载 {len(images)} 张图片到: {save_directory}")
        
        os.makedirs(save_directory, exist_ok=True)
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.mobile_user_agent
        })
        
        download_count = 0
        for img_info in images:
            try:
                img_url = img_info['url']
                filename = img_info['filename']
                
                # 确保文件名有扩展名
                if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    filename += '.jpg'
                
                file_path = os.path.join(save_directory, filename)
                
                response = session.get(img_url, timeout=30)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                img_info['local_path'] = file_path
                img_info['file_size'] = len(response.content)
                img_info['downloaded'] = True
                
                download_count += 1
                logger.info(f"✅ 下载成功: {filename} ({len(response.content)} bytes)")
                
                time.sleep(0.5)  # 避免请求过快
                
            except Exception as e:
                logger.error(f"❌ 下载失败: {img_info.get('filename', 'unknown')} - {e}")
                img_info['downloaded'] = False
                img_info['download_error'] = str(e)
        
        logger.info(f"📁 图片下载完成，成功 {download_count}/{len(images)} 张")
    
    def _save_results(self, images: List[Dict], save_directory: str):
        """保存结果到JSON文件"""
        try:
            os.makedirs(save_directory, exist_ok=True)
            
            result_file = os.path.join(save_directory, "enhanced_banner_images.json")
            
            result_data = {
                "crawl_time": datetime.now().isoformat(),
                "target_url": self.target_url,
                "total_images": len(images),
                "methods_used": list(set(img.get('method', 'unknown') for img in images)),
                "selenium_available": SELENIUM_AVAILABLE,
                "requests_html_available": REQUESTS_HTML_AVAILABLE,
                "images": images
            }
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 结果已保存到: {result_file}")
            
        except Exception as e:
            logger.error(f"❌ 保存结果失败: {e}")

def main():
    """测试增强版爬虫"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 增强版OpenHarmony手机Banner爬虫启动...")
    print("=" * 60)
    
    crawler = EnhancedMobileBannerCrawler()
    
    try:
        # 爬取banner图片
        banner_images = crawler.crawl_mobile_banners(
            download_images=True,
            save_directory="downloads/enhanced_mobile_banners"
        )
        
        # 输出结果
        print(f"\n📊 爬取结果:")
        print(f"   总计图片: {len(banner_images)} 张")
        
        if banner_images:
            methods_used = set(img.get('method', 'unknown') for img in banner_images)
            print(f"   使用方法: {', '.join(methods_used)}")
            
            print(f"\n📋 图片列表:")
            for i, img in enumerate(banner_images, 1):
                print(f"   {i}. {img['filename']}")
                print(f"      URL: {img['url']}")
                print(f"      方法: {img.get('method', 'unknown')}")
                print(f"      下载: {'✅' if img.get('downloaded') else '❌'}")
                print()
        
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
