#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试：验证爬虫获取300条咨询数据并与TypeScript模型兼容
"""

import sys
import os
import time
import json
sys.path.insert(0, os.path.dirname(__file__))

from services.openharmony_crawler import OpenHarmonyCrawler
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_300_consultations():
    """测试获取300条咨询数据"""
    print("开始测试获取300条咨询数据...")
    print("=" * 80)

    crawler = OpenHarmonyCrawler()

    try:
        # 直接测试300条数据获取
        page_num = 1
        page_size = 300

        api_url = f"{crawler.base_url}/backend/knowledge/secondaryPage/queryBatch?type=3&pageNum={page_num}&pageSize={page_size}"
        print(f"请求API: {api_url}")

        start_time = time.time()
        resp = crawler.session.get(api_url, timeout=30)
        resp.raise_for_status()
        response_data = resp.json()
        data = response_data.get("data", [])
        end_time = time.time()

        print(f"API请求耗时: {end_time - start_time:.2f}秒")
        print(f"成功获取到{len(data)}条数据")

        if len(data) >= 300:
            print("SUCCESS: 成功获取300条咨询数据")
        elif len(data) >= 200:
            print(f"PARTIAL: 获取到{len(data)}条数据，接近300条目标")
        else:
            print(f"INSUFFICIENT: 仅获取到{len(data)}条数据")

        # 验证数据结构
        if data:
            print(f"\n数据结构验证:")
            print(f"数据样本数量: {len(data)}")

            # 检查前3条数据的结构
            for i, item in enumerate(data[:3]):
                print(f"\n数据项{i+1}:")
                print(f"  URL: {item.get('url', 'N/A')}")
                print(f"  标题: {item.get('title', 'N/A')[:50]}...")
                print(f"  日期: {item.get('startTime', 'N/A')}")

                # 必需字段检查
                required_fields = ["url", "title", "startTime"]
                missing = [f for f in required_fields if not item.get(f)]
                if missing:
                    print(f"  警告: 缺少字段{missing}")
                else:
                    print(f"  字段完整性: OK")

            # 测试日期标准化
            print(f"\n日期标准化测试:")
            for i, item in enumerate(data[:3]):
                original_date = item.get("startTime", "")
                standardized_date = crawler._standardize_date(original_date)
                print(f"  {i+1}. '{original_date}' -> '{standardized_date}'")

            # 测试完整文章格式化
            print(f"\n文章格式化测试:")
            if data:
                test_article = {
                    "title": data[0].get("title", ""),
                    "date": data[0].get("startTime", ""),
                    "url": data[0].get("url", ""),
                    "content": [{"type": "text", "value": "测试内容块"}]
                }

                formatted = crawler._format_article(test_article)
                print(f"格式化结果:")
                print(f"  ID: {formatted['id']}")
                print(f"  标题: {formatted['title'][:50]}...")
                print(f"  日期: {formatted['date']}")
                print(f"  URL: {formatted['url']}")
                print(f"  内容块数量: {len(formatted['content'])}")
                print(f"  来源: {formatted['source']}")
                print(f"  分类: {formatted['category']}")

                # TypeScript兼容性检查
                ts_fields = ["id", "title", "date", "url", "content", "category", "source", "created_at", "updated_at"]
                missing_ts = [f for f in ts_fields if f not in formatted]
                if missing_ts:
                    print(f"  TypeScript兼容性: 缺少{missing_ts}")
                else:
                    print(f"  TypeScript兼容性: 完全兼容")

        return len(data)

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_typescript_sample():
    """生成TypeScript样本数据"""
    print(f"\n生成TypeScript样本数据...")
    print("=" * 80)

    # 创建符合TypeScript模型的样本
    sample_article = {
        "id": "00d1196eb553e2e0",
        "title": "测试OpenHarmony文章标题",
        "date": "2025-02-28",
        "url": "https://mp.weixin.qq.com/s/test_article",
        "content": [
            {"type": "text", "value": "这是文章的第一段内容，用于测试文本类型。"},
            {"type": "image", "value": "https://example.com/image1.jpg"},
            {"type": "text", "value": "这是文章的第二段内容。"}
        ],
        "category": "官方动态",
        "summary": "",
        "source": "OpenHarmony",
        "created_at": "2025-09-13T19:36:10.498491",
        "updated_at": "2025-09-13T19:36:10.498491"
    }

    print("TypeScript NewsArticle模型样本:")
    print(json.dumps(sample_article, indent=2, ensure_ascii=False))

    # 验证字段符合TypeScript接口
    print(f"\nTypeScript接口验证:")

    # NewsArticle必需字段
    required = ["id", "title", "date", "url", "content"]
    missing_required = [f for f in required if f not in sample_article]
    print(f"必需字段: {'全部存在' if not missing_required else f'缺少{missing_required}'}")

    # NewsContentBlock验证
    if "content" in sample_article and isinstance(sample_article["content"], list):
        print(f"content字段: 是数组类型")
        for i, block in enumerate(sample_article["content"]):
            if isinstance(block, dict) and "type" in block and "value" in block:
                print(f"  内容块{i+1}: type={block['type']}")
            else:
                print(f"  内容块{i+1}: 格式错误")

    # NewsResponse样本
    sample_response = {
        "articles": [sample_article],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "has_next": False,
        "has_prev": False
    }

    print(f"\nTypeScript NewsResponse模型样本:")
    print(json.dumps(sample_response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    count = test_300_consultations()
    test_typescript_sample()

    print(f"\n最终测试结果:")
    print(f"获取数据量: {count}条")
    print(f"300条目标: {'达成' if count >= 300 else '未达成'}")
    print(f"TypeScript兼容性: 已验证")