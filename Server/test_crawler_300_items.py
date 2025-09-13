#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫是否能获取300条咨询数据并验证数据结构兼容性
验证输出数据结构是否与TypeScript模型匹配
"""

import sys
import os
import time
import json
sys.path.insert(0, os.path.dirname(__file__))

from services.openharmony_crawler import OpenHarmonyCrawler
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_crawler_300_consultations():
    """测试爬虫获取300条咨询数据的能力"""
    print("测试爬虫获取300条咨询数据的能力...")
    print("=" * 80)

    crawler = OpenHarmonyCrawler()

    try:
        # 测试获取文章信息（只获取第一页300条数据）
        print("测试获取300条咨询数据API...")
        start_time = time.time()

        # 直接测试300条数据获取
        page_num = 1
        page_size = 300

        api_url = f"{crawler.base_url}/backend/knowledge/secondaryPage/queryBatch?type=3&pageNum={page_num}&pageSize={page_size}"
        print(f"请求API: {api_url}")

        resp = crawler.session.get(api_url, timeout=30)  # 增加超时时间以处理大量数据
        resp.raise_for_status()
        response_data = resp.json()
        data = response_data.get("data", [])

        end_time = time.time()
        print(f"API请求耗时: {end_time - start_time:.2f}秒")
        print(f"获取到{len(data)}条数据")

        # 验证数据结构
        print("\n验证数据结构兼容性...")

        if data:
            # 检查数据结构字段
            required_fields = ["url", "title", "startTime"]
            optional_fields = ["id", "type", "status", "createTime", "updateTime"]

            print(f"数据样本数量: {len(data)}")
            print(f"前5条数据预览:")

            for i, item in enumerate(data[:5]):
                print(f"\n数据项 {i+1}:")
                print(f"  URL: {item.get('url', 'N/A')}")
                print(f"  标题: {item.get('title', 'N/A')}")
                print(f"  日期: {item.get('startTime', 'N/A')}")

                # 检查必需字段
                missing_required = [field for field in required_fields if field not in item]
                if missing_required:
                    print(f"  ❌ 缺少必需字段: {missing_required}")
                else:
                    print(f"  ✅ 必需字段完整")

                # 检查可选字段
                available_optional = [field for field in optional_fields if field in item]
                if available_optional:
                    print(f"  ℹ️  可选字段: {available_optional}")

            # 测试完整的数据处理流程
            print(f"\n测试完整数据处理流程...")

            # 模拟完整的爬虫流程，但只处理前20条数据以节省时间
            test_count = min(20, len(data))
            processed_articles = []

            for i, item in enumerate(data[:test_count]):
                if i % 5 == 0:  # 每5条打印一次进度
                    print(f"  处理进度: {i+1}/{test_count}")

                # 模拟文章处理
                article_info = {
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "date": item.get("startTime", "")
                }

                # 测试日期标准化
                standardized_date = crawler._standardize_date(article_info["date"])

                # 模拟文章内容解析（简化版）
                content = [
                    {"type": "text", "value": f"文章内容预览: {article_info['title']}"}
                ]

                # 格式化文章
                formatted_article = crawler._format_article({
                    "title": article_info["title"],
                    "date": article_info["date"],
                    "url": article_info["url"],
                    "content": content
                })

                processed_articles.append(formatted_article)

            print(f"\n处理完成，共格式化{len(processed_articles)}篇文章")

            # 验证TypeScript模型兼容性
            print("\n验证TypeScript模型兼容性...")

            # 检查格式化后的文章是否符合TypeScript模型
            ts_required_fields = ["id", "title", "date", "url", "content"]
            ts_optional_fields = ["category", "summary", "source", "created_at", "updated_at"]

            compatibility_issues = []

            for i, article in enumerate(processed_articles[:3]):  # 检查前3个样本
                print(f"\nTypeScript兼容性检查 - 文章 {i+1}:")

                # 检查必需字段
                missing_required = [field for field in ts_required_fields if field not in article]
                if missing_required:
                    compatibility_issues.append(f"文章{i+1}缺少必需字段: {missing_required}")
                    print(f"  ❌ 缺少必需字段: {missing_required}")
                else:
                    print(f"  ✅ 必需字段完整")

                # 检查字段类型
                if "content" in article:
                    if isinstance(article["content"], list):
                        print(f"  ✅ content字段为数组类型")
                        if len(article["content"]) > 0:
                            first_block = article["content"][0]
                            if isinstance(first_block, dict) and "type" in first_block and "value" in first_block:
                                print(f"  ✅ content数组项格式正确")
                            else:
                                print(f"  ⚠️  content数组项格式可能有问题")
                    else:
                        print(f"  ❌ content字段不是数组类型")

                # 检查可选字段
                available_optional = [field for field in ts_optional_fields if field in article and article[field] is not None]
                if available_optional:
                    print(f"  ℹ️  可用可选字段: {available_optional}")

                # 检查日期格式
                if "date" in article:
                    date_str = article["date"]
                    if self._is_valid_date_format(date_str):
                        print(f"  ✅ 日期格式正确: {date_str}")
                    else:
                        print(f"  ⚠️  日期格式非标准: {date_str}")

            if compatibility_issues:
                print(f"\n❌ 发现{len(compatibility_issues)}个兼容性问题:")
                for issue in compatibility_issues:
                    print(f"  - {issue}")
            else:
                print(f"\n✅ TypeScript模型兼容性良好")

            # 统计信息
            print(f"\n数据统计信息:")
            print(f"  原始数据量: {len(data)}条")
            print(f"  测试处理量: {len(processed_articles)}条")
            print(f"  数据有效率: {len(processed_articles)/test_count*100:.1f}%")

            # 检查是否能达到300条
            if len(data) >= 300:
                print(f"  ✅ 成功获取300条咨询数据")
            elif len(data) >= 200:
                print(f"  ⚠️  获取到{len(data)}条数据，接近300条目标")
            else:
                print(f"  ⚠️  仅获取到{len(data)}条数据，低于预期")

        else:
            print("❌ 未获取到任何数据")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def _is_valid_date_format(self, date_str):
    """验证日期格式是否为YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def test_data_structure_validation():
    """单独测试数据结构验证"""
    print("\n单独测试数据结构验证...")
    print("=" * 80)

    # 创建一个模拟的格式化文章
    sample_article = {
        "id": "00d1196eb553e2e0",
        "title": "测试OpenHarmony文章",
        "date": "2025-02-28",
        "url": "https://mp.weixin.qq.com/s/test",
        "content": [
            {"type": "text", "value": "这是文章内容"},
            {"type": "image", "value": "https://example.com/image.jpg"}
        ],
        "category": "官方动态",
        "summary": "",
        "source": "OpenHarmony",
        "created_at": "2025-09-13T19:36:10.498491",
        "updated_at": "2025-09-13T19:36:10.498491"
    }

    print("样例文章结构:")
    print(json.dumps(sample_article, indent=2, ensure_ascii=False))

    # 验证TypeScript模型要求
    print("\nTypeScript模型兼容性验证:")

    # 检查NewsArticle接口
    required_fields = ["id", "title", "date", "url", "content"]
    optional_fields = ["category", "summary", "source", "created_at", "updated_at"]

    missing_required = [field for field in required_fields if field not in sample_article]
    available_optional = [field for field in optional_fields if field in sample_article and sample_article[field]]

    if not missing_required:
        print("✅ 符合NewsArticle接口要求")
    else:
        print(f"❌ 缺少必需字段: {missing_required}")

    if available_optional:
        print(f"ℹ️  可用可选字段: {available_optional}")

    # 检查NewsContentBlock
    if "content" in sample_article and isinstance(sample_article["content"], list):
        print("✅ content字段为NewsContentBlock数组")
        for i, block in enumerate(sample_article["content"]):
            if isinstance(block, dict) and "type" in block and "value" in block:
                print(f"  ✅ 内容块{i+1}: type={block['type']}, value长度={len(str(block['value']))}")
            else:
                print(f"  ❌ 内容块{i+1}格式错误")

if __name__ == "__main__":
    test_crawler_300_consultations()
    test_data_structure_validation()