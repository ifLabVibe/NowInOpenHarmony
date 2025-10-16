#!/usr/bin/env python3
"""
测试轮播图爬虫功能
"""
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_mobile_banner_crawler():
    """测试传统Mobile Banner爬虫"""
    print("\n" + "="*80)
    print("[TEST 1] Traditional Mobile Banner Crawler (requests + BeautifulSoup)")
    print("="*80)

    try:
        from services.mobile_banner_crawler import MobileBannerCrawler

        crawler = MobileBannerCrawler()
        logger.info(f"[OK] Mobile Banner crawler initialized successfully")
        logger.info(f"   Base URL: {crawler.base_url}")
        logger.info(f"   Target URL: {crawler.target_url}")

        # 执行爬取（不下载图片）
        banner_images = crawler.crawl_mobile_banners(
            download_images=False,
            save_directory=""
        )

        if banner_images:
            logger.info(f"[OK] Successfully fetched {len(banner_images)} banner images")
            logger.info(f"\n[LIST] Banner images:")
            for i, img in enumerate(banner_images[:5], 1):  # 只显示前5张
                logger.info(f"   {i}. URL: {img.get('url', 'N/A')[:100]}")
                logger.info(f"      Filename: {img.get('filename', 'N/A')}")
                logger.info(f"      Alt: {img.get('alt', 'N/A') or 'None'}")

            if len(banner_images) > 5:
                logger.info(f"   ... and {len(banner_images) - 5} more images")

            return True, len(banner_images)
        else:
            logger.warning("[WARNING] No banner images found")
            return False, 0

    except Exception as e:
        logger.error(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def test_enhanced_banner_crawler():
    """测试增强版Banner爬虫"""
    print("\n" + "="*80)
    print("[TEST 2] Enhanced Banner Crawler (Selenium)")
    print("="*80)

    try:
        from services.enhanced_mobile_banner_crawler import EnhancedMobileBannerCrawler

        crawler = EnhancedMobileBannerCrawler()
        logger.info(f"[OK] Enhanced Banner crawler initialized successfully")
        logger.info(f"   Base URL: {crawler.base_url}")
        logger.info(f"   Target URL: {crawler.target_url}")

        # 执行爬取（不下载图片）
        banner_images = crawler.crawl_mobile_banners(
            download_images=False,
            save_directory=""
        )

        if banner_images:
            logger.info(f"[OK] Successfully fetched {len(banner_images)} banner images")
            logger.info(f"\n[LIST] Banner images:")
            for i, img in enumerate(banner_images[:5], 1):
                logger.info(f"   {i}. URL: {img.get('url', 'N/A')[:100]}")
                logger.info(f"      Filename: {img.get('filename', 'N/A')}")

            if len(banner_images) > 5:
                logger.info(f"   ... and {len(banner_images) - 5} more images")

            return True, len(banner_images)
        else:
            logger.warning("[WARNING] Enhanced crawler found no banners (will fallback to traditional)")
            return False, 0

    except Exception as e:
        logger.warning(f"[WARNING] Enhanced crawler test failed (will fallback): {e}")
        logger.info("   System will automatically fallback to traditional crawler")
        return False, 0

def test_api_fallback():
    """测试API的降级机制"""
    print("\n" + "="*80)
    print("[TEST 3] API Fallback Mechanism")
    print("="*80)

    try:
        from api.banner import _crawl_mobile_banners

        logger.info("Testing API automatic fallback mechanism...")
        banner_images = _crawl_mobile_banners()

        if banner_images:
            logger.info(f"[OK] API fallback working, fetched {len(banner_images)} banner images")
            return True, len(banner_images)
        else:
            logger.warning("[WARNING] API fallback executed but no banners found")
            return False, 0

    except Exception as e:
        logger.error(f"[ERROR] API fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("OpenHarmony Banner Crawler Functionality Test")
    print("="*80)

    results = []

    # Test 1: Traditional crawler
    success1, count1 = test_mobile_banner_crawler()
    results.append(("Traditional Mobile Banner Crawler", success1, count1))

    # Test 2: Enhanced crawler (may fail, that's normal)
    success2, count2 = test_enhanced_banner_crawler()
    results.append(("Enhanced Banner Crawler", success2, count2))

    # Test 3: API fallback mechanism
    success3, count3 = test_api_fallback()
    results.append(("API Fallback Mechanism", success3, count3))

    # 输出测试总结
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for name, success, count in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {name}: Fetched {count} images")

    # 判断整体测试结果
    print("\n" + "="*80)
    if results[0][1] or results[2][1]:  # 传统爬虫或API降级机制任一成功即可
        print("[SUCCESS] Banner functionality test passed!")
        print("\nCore Features:")
        print("   - Traditional crawler can fetch banner images normally")
        print("   - API has comprehensive fallback mechanism")
        print("   - System works even if Selenium fails")
        print("\nRecommendations:")
        print("   - Banner functionality is fully operational")
        print("   - Ready for server deployment")
        print("   - Access via /api/banner/mobile endpoint")
        return 0
    else:
        print("[FAILED] Banner functionality test failed!")
        print("\nPossible Causes:")
        print("   1. Network connection issues")
        print("   2. OpenHarmony website structure changed")
        print("   3. Incorrect URL address")
        print("\nSolutions:")
        print("   - Check network connection")
        print("   - Verify https://old.openharmony.cn/mainPlay is accessible")
        print("   - Review detailed log output")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
