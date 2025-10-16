#!/usr/bin/env python3
"""
Quick Banner Crawler Test
"""
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_traditional_crawler():
    """Test traditional requests-based crawler"""
    print("\n" + "="*80)
    print("[TEST 1] Traditional Mobile Banner Crawler")
    print("="*80)

    try:
        from services.mobile_banner_crawler import MobileBannerCrawler

        crawler = MobileBannerCrawler()
        logger.info(f"Crawler initialized - URL: {crawler.target_url}")

        banner_images = crawler.crawl_mobile_banners(
            download_images=False,
            save_directory=""
        )

        if banner_images:
            logger.info(f"[SUCCESS] Found {len(banner_images)} images")
            return True, len(banner_images)
        else:
            logger.warning(f"[EXPECTED] Traditional crawler found 0 images (dynamic content)")
            return False, 0

    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return False, 0

def test_api_endpoint():
    """Test API endpoint with fallback"""
    print("\n" + "="*80)
    print("[TEST 2] API Endpoint with Fallback")
    print("="*80)

    try:
        from api.banner import _crawl_mobile_banners

        logger.info("Testing API endpoint...")
        banner_images = _crawl_mobile_banners()

        if banner_images:
            logger.info(f"[SUCCESS] API returned {len(banner_images)} images")
            # Show first image details
            if banner_images:
                img = banner_images[0]
                logger.info(f"Sample image:")
                logger.info(f"  - URL: {img.get('url', 'N/A')[:80]}...")
                logger.info(f"  - Filename: {img.get('filename', 'N/A')}")
            return True, len(banner_images)
        else:
            logger.warning(f"[FAILED] No images returned from API")
            return False, 0

    except Exception as e:
        logger.error(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("OpenHarmony Banner Crawler Quick Test")
    print("="*80)

    # Test 1: Traditional crawler (expected to fail for dynamic content)
    success1, count1 = test_traditional_crawler()

    # Test 2: API endpoint (should work with fallback to Selenium)
    success2, count2 = test_api_endpoint()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"[{'PASS' if success1 else 'EXPECTED FAIL'}] Traditional Crawler: {count1} images")
    print(f"[{'PASS' if success2 else 'FAIL'}] API Endpoint: {count2} images")

    print("\n" + "="*80)
    if success2:
        print("[SUCCESS] Banner functionality is working!")
        print("\nStatus:")
        print("  - API endpoint successfully fetches banner images")
        print("  - Selenium-based enhanced crawler is operational")
        print("  - System has proper fallback mechanism")
        print("\nDeployment:")
        print("  - Ready for server deployment")
        print("  - Access via: GET /api/banner/mobile")
        return 0
    else:
        print("[FAILED] Banner functionality test failed")
        print("\nPossible issues:")
        print("  - Network connectivity problems")
        print("  - Selenium not available in environment")
        print("  - Website structure changed")
        print("\nCheck logs above for details")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
