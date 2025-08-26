#!/usr/bin/env python3
"""
Setup script for Web Scraping version of Notion Reddit Analysis Tool
No API credentials required!
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary project directories"""
    directories = [
        'data',
        'models', 
        'reports',
        'visualizations'
    ]
    
    print("📁 Creating project directories...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")

def check_requirements():
    """Check if scraping requirements are installed"""
    print("\n📋 Checking scraping requirements...")
    
    required_packages = [
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('lxml', 'lxml'),
        ('fake_useragent', 'fake-useragent'),
        ('pandas', 'pandas'), 
        ('scikit-learn', 'sklearn'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('wordcloud', 'wordcloud'),
        ('textblob', 'textblob')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name}")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements_scraper.txt")
        return False
    
    print("\n✅ All requirements satisfied!")
    return True

def test_internet_connection():
    """Test if we can reach Reddit"""
    print("\n🌐 Testing internet connection to Reddit...")
    
    try:
        import requests
        response = requests.get('https://www.reddit.com/r/test.json', timeout=10)
        
        if response.status_code == 200:
            print("  ✅ Can reach Reddit successfully")
            return True
        else:
            print(f"  ⚠️  Reddit returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Cannot reach Reddit: {e}")
        print("  🔧 Check your internet connection")
        return False

def test_scraper():
    """Test the web scraper functionality"""
    print("\n🧪 Testing web scraper...")
    
    try:
        from reddit_scraper import RedditWebScraper
        
        scraper = RedditWebScraper()
        
        # Test JSON API method with very small request
        posts = scraper.scrape_subreddit_json('Notion', 'hot', 3)
        
        if posts and len(posts) > 0:
            print(f"  ✅ Scraper working! Found {len(posts)} test posts")
            print(f"  📋 Sample: '{posts[0]['title'][:50]}...'")
            return True
        else:
            print("  ⚠️  Scraper returned no posts")
            print("  🔧 This might be temporary - try running again")
            return False
            
    except Exception as e:
        print(f"  ❌ Scraper test failed: {e}")
        return False

def main():
    """Main setup function for web scraping version"""
    print("🕷️ Setting up Notion Reddit Web Scraping Tool")
    print("=" * 55)
    print("✨ NO API CREDENTIALS REQUIRED!")
    print("🌐 Uses public Reddit endpoints")
    
    # Create directories
    create_directories()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup incomplete - please install missing requirements")
        print("Run: pip install -r requirements_scraper.txt")
        return False
    
    # Test internet connection
    internet_ok = test_internet_connection()
    
    # Test scraper if internet is working
    scraper_ok = False
    if internet_ok:
        scraper_ok = test_scraper()
    
    print("\n" + "=" * 55)
    
    if internet_ok and scraper_ok:
        print("🎉 Setup complete! Web scraper is ready!")
        print("\n🚀 Next steps:")
        print("  🧪 Test scraper: python main_pipeline_scraper.py test")
        print("  ⚡ Quick start: python main_pipeline_scraper.py quick")
        print("  📊 Full analysis: python main_pipeline_scraper.py full")
        print("  📈 Dashboard: streamlit run dashboard.py")
        
        print("\n💡 Advantages of web scraping:")
        print("  • No API credentials needed")
        print("  • No rate limiting issues")
        print("  • Access to public Reddit data")
        print("  • Works immediately after setup")
        
        return True
    else:
        print("⚠️ Setup completed with warnings")
        
        if not internet_ok:
            print("  🌐 Internet connection issue - check network")
        if internet_ok and not scraper_ok:
            print("  🕷️ Scraper test failed - might be temporary")
            print("  🔄 Try running: python main_pipeline_scraper.py test")
        
        print("\n📋 You can still proceed:")
        print("  python main_pipeline_scraper.py test")
        return True

def show_comparison():
    """Show comparison between API and scraping approaches"""
    print("\n📊 API vs Web Scraping Comparison:")
    print("=" * 40)
    
    print("🔑 PRAW (API) Approach:")
    print("  ✅ More stable data structure")
    print("  ✅ Official Reddit support")  
    print("  ❌ Requires API credentials")
    print("  ❌ Rate limiting (60 requests/min)")
    print("  ❌ Setup complexity")
    
    print("\n🕷️ Web Scraping Approach:")
    print("  ✅ No credentials required")
    print("  ✅ Immediate setup")
    print("  ✅ Higher rate limits")
    print("  ✅ Access to public data")
    print("  ❌ May break if Reddit changes HTML")
    print("  ❌ Potential IP blocking")
    
    print("\n💡 Recommendation:")
    print("  Start with web scraping for quick results")
    print("  Switch to API for production use")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'compare':
        show_comparison()
    else:
        success = main()
        sys.exit(0 if success else 1)