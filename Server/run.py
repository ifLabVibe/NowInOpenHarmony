#!/usr/bin/env python3
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
NowInOpenHarmony 后端服务启动脚本
"""

import uvicorn
import os
import sys
import socket
import subprocess
import platform
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import settings
from core.logging_config import setup_logging

def get_local_ip_addresses():
    """
    获取所有本地网络接口的IP地址
    """
    ip_addresses = []
    
    try:
        # 方法1: 使用socket获取主要IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 连接到一个远程地址（不会实际发送数据）
            s.connect(("8.8.8.8", 80))
            primary_ip = s.getsockname()[0]
            ip_addresses.append(("主要IP", primary_ip))
        except Exception:
            pass
        finally:
            s.close()
        
        # 方法2: 获取本机hostname对应的IP
        try:
            hostname = socket.gethostname()
            host_ip = socket.gethostbyname(hostname)
            if host_ip not in [ip[1] for ip in ip_addresses]:
                ip_addresses.append(("主机IP", host_ip))
        except Exception:
            pass
        
        # 方法3: 针对Windows系统使用ipconfig命令
        if platform.system().lower() == "windows":
            try:
                result = subprocess.run(
                    ["ipconfig"], 
                    capture_output=True, 
                    text=True, 
                    encoding='gbk'
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        line = line.strip()
                        if "IPv4" in line and ":" in line:
                            ip = line.split(":")[-1].strip()
                            # 过滤掉回环地址和无效IP
                            if ip and not ip.startswith("127.") and "." in ip:
                                # 检查是否已存在
                                if ip not in [addr[1] for addr in ip_addresses]:
                                    # 判断网络类型
                                    if ip.startswith("192.168."):
                                        ip_addresses.append(("局域网IP", ip))
                                    elif ip.startswith("10."):
                                        ip_addresses.append(("内网IP", ip))
                                    elif ip.startswith("172."):
                                        ip_addresses.append(("内网IP", ip))
                                    else:
                                        ip_addresses.append(("公网IP", ip))
            except Exception:
                pass
        
        # 方法4: 针对Linux/Mac系统
        elif platform.system().lower() in ["linux", "darwin"]:
            try:
                result = subprocess.run(
                    ["ifconfig"], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "inet " in line and "127.0.0.1" not in line:
                            parts = line.strip().split()
                            for i, part in enumerate(parts):
                                if part == "inet" and i + 1 < len(parts):
                                    ip = parts[i + 1]
                                    if ip not in [addr[1] for addr in ip_addresses]:
                                        if ip.startswith("192.168."):
                                            ip_addresses.append(("局域网IP", ip))
                                        elif ip.startswith("10."):
                                            ip_addresses.append(("内网IP", ip))
                                        else:
                                            ip_addresses.append(("网络IP", ip))
            except Exception:
                pass
        
        # 如果没有找到任何IP，添加默认的本地地址
        if not ip_addresses:
            ip_addresses.append(("本地回环", "127.0.0.1"))
            
    except Exception as e:
        print(f"获取IP地址时出错: {e}")
        ip_addresses.append(("本地回环", "127.0.0.1"))
    
    return ip_addresses

def print_startup_info(host, port):
    """
    打印启动信息和所有可访问的地址
    """
    print("=" * 60)
    print("🚀 NowInOpenHarmony API 服务启动成功!")
    print("=" * 60)
    
    # 获取所有IP地址
    ip_addresses = get_local_ip_addresses()
    
    print("\n📡 服务可通过以下地址访问:")
    print("-" * 40)
    
    for name, ip in ip_addresses:
        print(f"  {name:>8}: http://{ip}:{port}")
        print(f"  {'API文档':>8}: http://{ip}:{port}/docs")
        print(f"  {'健康检查':>8}: http://{ip}:{port}/health")
        print(f"  {'全部新闻':>8}: http://{ip}:{port}/api/news/?all=true")
        print(f"  {'Banner图片':>8}: http://{ip}:{port}/api/banner/mobile")
        print("-" * 40)
    
    # 选择优先显示的IP地址（优先局域网IP）
    preferred_ip = ip_addresses[0][1]  # 默认使用第一个
    for name, ip in ip_addresses:
        if ip.startswith('192.168.'):
            preferred_ip = ip
            break
    
    print("\n🎯 主要API端点:")
    print(f"  📰 全部新闻: http://{preferred_ip}:{port}/api/news/?all=true")
    print(f"  🌐 官网新闻: http://{preferred_ip}:{port}/api/news/openharmony")
    print(f"  📚 技术博客: http://{preferred_ip}:{port}/api/news/blog")
    print(f"  📱 Banner图片: http://{preferred_ip}:{port}/api/banner/mobile")
    print(f"  ⚡ 服务状态: http://{preferred_ip}:{port}/api/health")
    
    print("\n📋 完整API路径列表:")
    print("-" * 60)
    
    # 基础服务
    base_ip = preferred_ip
    print(f"🔧 基础服务:")
    print(f"  根路径: http://{base_ip}:{port}/")
    print(f"  API文档: http://{base_ip}:{port}/docs")
    print(f"  ReDoc文档: http://{base_ip}:{port}/redoc")
    print(f"  健康检查: http://{base_ip}:{port}/health")
    print(f"  API健康检查: http://{base_ip}:{port}/api/health")
    
    # 新闻相关API
    print(f"\n📰 新闻API:")
    print(f"  全部新闻: http://{base_ip}:{port}/api/news/")
    print(f"  分页新闻: http://{base_ip}:{port}/api/news/?page=1&page_size=20")
    print(f"  搜索新闻: http://{base_ip}:{port}/api/news/?search=关键词")
    print(f"  分类新闻: http://{base_ip}:{port}/api/news/?category=官方动态")
    print(f"  OpenHarmony官网: http://{base_ip}:{port}/api/news/openharmony")
    print(f"  OpenHarmony技术博客: http://{base_ip}:{port}/api/news/blog")
    print(f"  手动爬取: http://{base_ip}:{port}/api/news/crawl (POST)")
    print(f"  新闻服务状态: http://{base_ip}:{port}/api/news/status/info")
    
    # Banner相关API
    print(f"\n🖼️ Banner轮播图API:")
    print(f"  手机版Banner: http://{base_ip}:{port}/api/banner/mobile")
    print(f"  增强版Banner: http://{base_ip}:{port}/api/banner/mobile/enhanced")
    print(f"  Banner状态: http://{base_ip}:{port}/api/banner/status")
    print(f"  手动爬取Banner: http://{base_ip}:{port}/api/banner/crawl (POST)")
    print(f"  Banner缓存信息: http://{base_ip}:{port}/api/banner/cache")
    print(f"  清空Banner缓存: http://{base_ip}:{port}/api/banner/cache/clear (DELETE)")
    
    print("\n📊 API参数示例:")
    print(f"  强制爬取全部新闻: http://{base_ip}:{port}/api/news/crawl?source=all&limit=50")
    print(f"  爬取官网新闻: http://{base_ip}:{port}/api/news/crawl?source=openharmony")
    print(f"  爬取技术博客: http://{base_ip}:{port}/api/news/crawl?source=openharmony_blog")
    print(f"  强制爬取Banner: http://{base_ip}:{port}/api/banner/mobile?force_crawl=true")
    print(f"  下载Banner图片: http://{base_ip}:{port}/api/banner/mobile/enhanced?download_images=true")
    print(f"  增强版爬取: http://{base_ip}:{port}/api/banner/crawl?use_enhanced=true")
    
    print("\n💡 提示:")
    print("  - 局域网IP可供同一网络下的其他设备访问")
    print("  - GET请求可直接在浏览器中访问")
    print("  - POST/DELETE请求需要使用API工具(如Postman)或curl命令")
    print("  - 使用 Ctrl+C 停止服务")
    print("=" * 60)

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    reload = os.getenv("RELOAD", "false").lower() == "true" or settings.debug
    
    # 显示启动信息和所有可访问的IP地址
    print_startup_info(host, port)
    
    print(f"\n⚙️  启动配置:")
    print(f"  绑定地址: {host}")
    print(f"  端口: {port}")
    print(f"  调试模式: {reload}")
    print(f"  日志级别: {settings.log_level}")
    print("=" * 60)
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main() 