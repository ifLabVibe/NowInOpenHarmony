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

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    app_name: str = "NowInOpenHarmony API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据库配置
    database_url: str = "sqlite:///./openharmony_news.db"
    db_path: str = "./openharmony_news.db"
    
    # API配置
    api_prefix: str = "/api"
    cors_origins: list = ["*"]
    
    # 爬虫配置
    crawler_delay: float = 1.0  # 爬虫请求间隔（秒）
    crawler_timeout: int = 10   # 请求超时时间（秒）
    max_retries: int = 3        # 最大重试次数
    
    # 定时任务配置
    enable_scheduler: bool = True
    cache_update_interval: int = 30  # 缓存更新间隔（分钟）
    full_crawl_hour: int = 2         # 完整爬取时间（小时）
    
    # 缓存配置
    enable_cache: bool = True
    cache_initial_load: bool = True  # 是否在启动时加载缓存
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 数据源配置
    openharmony_base_url: str = "https://www.openharmony.cn"
    csdn_search_url: str = "https://so.csdn.net/so/search"
    zhihu_search_url: str = "https://www.zhihu.com/search"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
settings = Settings()

def get_settings() -> Settings:
    """获取配置实例"""
    return settings 