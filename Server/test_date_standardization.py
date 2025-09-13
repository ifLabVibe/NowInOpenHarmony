#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日期标准化功能
验证新的日期解析算法是否能正确处理各种日期格式
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.openharmony_crawler import OpenHarmonyCrawler
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_date_standardization():
    """测试各种日期格式的标准化能力"""
    crawler = OpenHarmonyCrawler()

    # 测试用例：各种日期格式
    test_cases = [
        # 标准格式
        ("2024-08-31", "2024-08-31"),
        ("2024.08.31", "2024-08-31"),
        ("2024/08/31", "2024-08-31"),

        # 单数字月日
        ("2024-8-31", "2024-08-31"),
        ("2024.8.31", "2024-08-31"),
        ("2024/8/31", "2024-08-31"),
        ("2024-08-3", "2024-08-03"),
        ("2024.8.3", "2024-08-03"),

        # 中文格式
        ("2024年08月31日", "2024-08-31"),
        ("2024年8月31日", "2024-08-31"),
        ("2024年08月31", "2024-08-31"),

        # 只有年月
        ("2024年08月", "2024-08-01"),
        ("2024-08", "2024-08-01"),
        ("2024.08", "2024-08-01"),

        # 复杂格式
        ("2023-12-25 10:30:00", "2023-12-25"),
        ("2023.12.25 10:30:00", "2023-12-25"),

        # 反转格式
        ("31-08-2024", None),  # 应该无法解析，保持原样
        ("31.08.2024", None),  # 应该无法解析，保持原样

        # 无效格式
        ("08-31", None),  # 应该无法解析，保持原样
        ("08.31", None),  # 应该无法解析，保持原样
        ("08/31", None),  # 应该无法解析，保持原样
        ("无效日期", None),  # 应该无法解析，保持原样
        ("", ""),  # 空字符串
        (None, ""),  # None值

        # 边界情况
        ("2024年13月45日", "2024-13-45"),  # 无效日期数值，但格式正确
    ]

    print("开始测试日期标准化功能...")
    print("=" * 80)

    success_count = 0
    total_count = len(test_cases)

    for i, (input_date, expected_output) in enumerate(test_cases, 1):
        try:
            result = crawler._standardize_date(input_date)

            # 判断测试结果
            if expected_output is None:
                # 期望保持原样
                if result == input_date:
                    success_count += 1
                    status = "成功"
                    expected = f"保持原样: '{input_date}'"
                else:
                    status = "失败"
                    expected = f"期望保持原样，但得到: '{result}'"
            else:
                # 期望特定输出
                if result == expected_output:
                    success_count += 1
                    status = "成功"
                    expected = expected_output
                else:
                    status = "失败"
                    expected = f"期望: '{expected_output}', 实际: '{result}'"

            print(f"{i:2d}. {status} | 输入: '{input_date}' -> 输出: '{result}'")
            if status == "失败":
                print(f"    {expected}")

        except Exception as e:
            print(f"{i:2d}. 异常 | 输入: '{input_date}' -> 错误: {e}")

    print("=" * 80)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    print(f"测试结果: {success_count}/{total_count} 成功 ({success_rate:.1f}%)")

    # 测试实际文章数据
    print("\n测试实际文章数据标准化...")
    test_articles = [
        {"title": "测试文章1", "date": "2024.8.15", "url": "http://test1.com"},
        {"title": "测试文章2", "date": "2024-12-25", "url": "http://test2.com"},
        {"title": "测试文章3", "date": "2024年9月1日", "url": "http://test3.com"},
        {"title": "测试文章4", "date": "2024/6/30", "url": "http://test4.com"},
    ]

    print("标准化前:")
    for article in test_articles:
        print(f"  {article['date']} - {article['title']}")

    # 使用_format_article进行完整测试
    formatted_articles = []
    for article in test_articles:
        formatted_article = crawler._format_article(article)
        formatted_articles.append(formatted_article)

    print("标准化后:")
    for article in formatted_articles:
        print(f"  {article['date']} - {article['title']}")

if __name__ == "__main__":
    test_date_standardization()