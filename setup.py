#!/usr/bin/env python3
"""
Setup script for Notion Reddit Analysis Tool
Creates necessary directories and validates environment
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
    """Check if requirements are installed"""
    print("\n📋 Checking requirements...")
    
    required_packages = [
        'praw',
        'pandas', 
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'wordcloud',
        'textblob',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All requirements satisfied!")
    return True

def check_env_file():
    """Check if .env file exists and is configured"""
    print("\n🔐 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("  ❌ .env file not found")
        print("  📝 Copy .env.example to .env and fill in your Reddit API credentials")
        print("  🔗 Get credentials from: https://www.reddit.com/prefs/apps")
        return False
    
    # Check if .env has the required variables
    with open('.env', 'r') as f:
        env_content = f.read()
    
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=your_" in env_content or f"{var}=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"  ⚠️  Please configure: {', '.join(missing_vars)}")
        print("  📝 Edit .env file with your Reddit API credentials")
        return False
    
    print("  ✅ Environment file configured")
    return True

def validate_reddit_connection():
    """Test Reddit API connection"""
    print("\n🌐 Testing Reddit API connection...")
    
    try:
        from reddit_collector import RedditCollector
        collector = RedditCollector()
        
        # Try to access Reddit API
        subreddit = collector.reddit.subreddit('test')
        subreddit.display_name  # This will trigger API call
        
        print("  ✅ Reddit API connection successful")
        return True
        
    except Exception as e:
        print(f"  ❌ Reddit API connection failed: {e}")
        print("  🔧 Check your Reddit API credentials in .env file")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Notion Reddit Analysis Tool")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup incomplete - please install missing requirements")
        return False
    
    # Check environment
    env_ok = check_env_file()
    
    if env_ok:
        # Test API connection
        api_ok = validate_reddit_connection()
    else:
        api_ok = False
    
    print("\n" + "=" * 50)
    
    if env_ok and api_ok:
        print("🎉 Setup complete! You're ready to analyze r/Notion")
        print("\nNext steps:")
        print("  📊 Run analysis: python main_pipeline.py")
        print("  🚀 Quick start: python main_pipeline.py quick")
        print("  📈 Dashboard: streamlit run dashboard.py")
        return True
    else:
        print("⚠️  Setup incomplete - please fix the issues above")
        if not env_ok:
            print("  1. Configure .env file with Reddit API credentials")
        if not api_ok and env_ok:
            print("  2. Verify Reddit API credentials")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)