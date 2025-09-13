#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的OpenHarmony爬虫
验证API接口优化和日期标准化的效果
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from services.openharmony_crawler import OpenHarmonyCrawler
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_crawler_optimization():
    """测试爬虫优化效果"""
    print("开始测试优化后的OpenHarmony爬虫...")
    print("=" * 80)

    crawler = OpenHarmonyCrawler()

    try:
        # 测试获取文章信息（只获取第一页，避免测试时间过长）
        print("测试获取文章信息API...")
        start_time = time.time()

        # 模拟获取少量数据进行测试
        all_infos = {}
        page_num = 1
        page_size = 10  # 测试用小数据量

        api_url = f"{crawler.base_url}/backend/knowledge/secondaryPage/queryBatch?type=3&pageNum={page_num}&pageSize={page_size}"
        print(f"请求API: {api_url}")

        resp = crawler.session.get(api_url, timeout=15)
        resp.raise_for_status()
        response_data = resp.json()
        data = response_data.get("data", [])

        end_time = time.time()
        print(f"API请求耗时: {end_time - start_time:.2f}秒")
        print(f"获取到{len(data)}条数据")

        if data:
            # 测试日期标准化
            print("\n测试日期标准化功能...")
            for i, item in enumerate(data[:5]):  # 只测试前5条
                original_date = item.get("startTime", "")
                title = item.get("title", "")
                standardized_date = crawler._standardize_date(original_date)
                print(f"{i+1}. 原标题: '{original_date}' -> 标准化: '{standardized_date}' | {title}")

            # 测试文章格式化
            print("\n测试文章格式化功能...")
            test_article = {
                "title": data[0].get("title", ""),
                "date": data[0].get("startTime", ""),
                "url": data[0].get("url", ""),
                "content": [{"type": "text", "value": "测试内容"}]
            }

            formatted_article = crawler._format_article(test_article)
            print("格式化后的文章:")
            for key, value in formatted_article.items():
                if key != "content":  # 内容太长，不打印
                    print(f"  {key}: {value}")

        print("\n" + "=" * 80)
        print("测试完成！优化后的爬虫功能正常")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_performance_comparison():
    """性能对比测试"""
    print("\n性能对比测试...")
    print("=" * 80)

    crawler = OpenHarmonyCrawler()

    # 测试不同页面大小的性能
    page_sizes = [20, 50, 100]
    results = []

    for page_size in page_sizes:
        print(f"\n测试页面大小: {page_size}")
        start_time = time.time()

        try:
            api_url = f"{crawler.base_url}/backend/knowledge/secondaryPage/queryBatch?type=3&pageNum=1&pageSize={page_size}"
            resp = crawler.session.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json().get("data", [])

            end_time = time.time()
            duration = end_time - start_time

            results.append({
                "page_size": page_size,
                "duration": duration,
                "data_count": len(data),
                "efficiency": len(data) / duration if duration > 0 else 0
            })

            print(f"  请求耗时: {duration:.3f}秒")
            print(f"  获取数据: {len(data)}条")
            print(f"  效率: {len(data)/duration:.1f}条/秒")

        except Exception as e:
            print(f"  请求失败: {e}")

    if results:
        print("\n性能对比结果:")
        print(f"{'页面大小':<10} {'耗时(秒)':<10} {'数据量':<10} {'效率(条/秒)':<15}")
        print("-" * 50)
        for result in results:
            print(f"{result['page_size']:<10} {result['duration']:<10.3f} {result['data_count']:<10} {result['efficiency']:<15.1f}")

if __name__ == "__main__":
    test_crawler_optimization()
    test_performance_comparison()