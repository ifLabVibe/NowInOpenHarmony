#!/usr/bin/env python3
"""
测试日期解析功能
验证新的日期排序算法是否能正确处理各种日期格式
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.cache import NewsCache
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_date_parsing():
    """测试各种日期格式的解析能力"""
    cache = NewsCache()
    
    # 测试用例：各种日期格式
    test_cases = [
        "2024-08-31",      # 标准格式
        "2024.08.31",      # 点分隔
        "2024/08/31",      # 斜线分隔
        "2024-8-31",       # 单数字月日
        "2024.8.31",       # 单数字月日（点）
        "2024/8/31",       # 单数字月日（斜线）
        "2024年08月31日",   # 中文格式
        "2024年8月31日",    # 中文格式（单数字）
        "2024年08月31",     # 中文格式（无日）
        "2023-12-25 10:30:00",  # 带时间
        "2023.12.25 10:30:00",  # 带时间（点）
        "31-08-2024",      # DD-MM-YYYY
        "31.08.2024",      # DD.MM.YYYY  
        "08-31",           # 只有月日
        "08.31",           # 只有月日（点）
        "08/31",           # 只有月日（斜线）
        "无效日期",          # 无效格式
        "",                # 空字符串
        None,              # None值
        "2024年13月45日",   # 无效日期数值
    ]
    
    print("🧪 开始测试日期解析功能...")
    print("=" * 80)
    
    success_count = 0
    total_count = len([tc for tc in test_cases if tc is not None])
    
    for i, date_str in enumerate(test_cases, 1):
        try:
            if date_str is None:
                print(f"{i:2d}. None值 -> 跳过测试")
                continue
                
            parsed_date = cache._parse_date_for_sorting(date_str)
            
            if parsed_date.year > 1970:
                success_count += 1
                status = "✅ 成功"
                result = parsed_date.strftime('%Y-%m-%d')
            else:
                status = "❌ 失败"
                result = "回退到默认时间"
            
            print(f"{i:2d}. {status} | '{date_str}' -> {result}")
            
        except Exception as e:
            print(f"{i:2d}. ❌ 异常 | '{date_str}' -> 错误: {e}")
    
    print("=" * 80)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    print(f"📊 测试结果: {success_count}/{total_count} 成功 ({success_rate:.1f}%)")
    
    # 测试排序功能
    print("\n🔄 测试排序功能...")
    test_dates = ["2024.08.31", "2024-01-15", "2024/12/25", "2023-06-10", "2024年03月20日"]
    
    from models.news import NewsArticle
    test_articles = []
    for i, date_str in enumerate(test_dates):
        article = NewsArticle(
            id=f"test_{i}",
            title=f"测试文章 {i+1}",
            date=date_str,
            url=f"http://test{i}.com",
            content=[{"type": "text", "value": f"测试内容 {i+1}"}]
        )
        test_articles.append(article)
    
    print("排序前:")
    for article in test_articles:
        print(f"  {article.date} - {article.title}")
    
    sorted_articles = cache._sort_articles_by_date(test_articles)
    
    print("排序后:")
    for article in sorted_articles:
        print(f"  {article.date} - {article.title}")

if __name__ == "__main__":
    test_date_parsing()
