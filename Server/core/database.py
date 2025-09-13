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

import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator
import os

logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./openharmony_news.db")
DB_PATH = "./openharmony_news.db"

def init_database():
    """初始化数据库，创建表结构"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 创建新闻表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    category TEXT,
                    summary TEXT,
                    source TEXT,
                    content TEXT,  -- JSON格式存储内容块
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建话题表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    author TEXT,
                    reply_count INTEGER DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    tags TEXT,  -- JSON格式存储标签
                    url TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建版本发布表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS releases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    title TEXT NOT NULL,
                    release_date TEXT NOT NULL,
                    description TEXT,
                    features TEXT,  -- JSON格式存储功能列表
                    bug_fixes TEXT,  -- JSON格式存储修复列表
                    compatibility TEXT,
                    download_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_date ON news_articles(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_category ON news_articles(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_url ON news_articles(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_topics_created ON topics(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_releases_version ON releases(version)')
            
            conn.commit()
            logger.info("数据库初始化完成")
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """获取数据库连接的上下文管理器"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        yield conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: tuple = ()) -> list:
    """执行查询语句"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"查询执行失败: {e}")
        raise

def execute_update(query: str, params: tuple = ()) -> int:
    """执行更新语句，返回影响的行数"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        logger.error(f"更新执行失败: {e}")
        raise 