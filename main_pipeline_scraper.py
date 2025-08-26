#!/usr/bin/env python3
"""
Main pipeline for Notion Reddit Analysis using Web Scraping
No API credentials required - uses web scraping approach
"""

import os
import sys
from datetime import datetime
import pandas as pd

from reddit_scraper import RedditWebScraper, ScraperBasedPipeline
from text_classifier import NotionPostClassifier
from data_analyzer import NotionDataAnalyzer
import config

class NotionScrapingPipeline:
    def __init__(self):
        self.collector = RedditWebScraper()
        self.classifier = NotionPostClassifier()
        self.analyzer = NotionDataAnalyzer()
        
        # Ensure directories exist
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs('models', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        os.makedirs('visualizations', exist_ok=True)
    
    def collect_data(self, sort_methods=['hot', 'new'], limit_per_method=50):
        """Step 1: Collect Reddit posts via web scraping"""
        print("\n🕷️ STEP 1: Web Scraping Reddit Posts (No API Required)")
        print("=" * 60)
        print("Using Reddit's public JSON endpoints and HTML parsing")
        
        try:
            df = self.collector.collect_and_save(
                sort_methods=sort_methods,
                limit_per_method=limit_per_method
            )
            
            if df is not None and len(df) > 0:
                print(f"✅ Successfully scraped {len(df)} unique posts")
                
                # Show sample of collected data
                print("\n📋 Sample of collected data:")
                sample_posts = df.head(3)
                for idx, row in sample_posts.iterrows():
                    print(f"  • {row['title'][:60]}... (Score: {row['score']}, Comments: {row['num_comments']})")
                
                return df
            else:
                print("❌ No posts were scraped")
                return None
                
        except Exception as e:
            print(f"❌ Error scraping data: {e}")
            print("This might be due to:")
            print("  - Network connectivity issues")
            print("  - Reddit blocking the requests")
            print("  - Changes in Reddit's HTML structure")
            return None
    
    def classify_data(self, df=None):
        """Step 2: Classify posts into categories"""
        print("\n🏷️ STEP 2: Classifying Posts")
        print("=" * 40)
        
        if df is None:
            if not os.path.exists(config.RAW_DATA_FILE):
                print("❌ No raw data found. Run data collection first.")
                return None
            df = pd.read_csv(config.RAW_DATA_FILE)
        
        try:
            # Classify posts
            df_classified = self.classifier.classify_posts(df)
            
            # Save processed data
            df_classified.to_csv(config.PROCESSED_DATA_FILE, index=False)
            
            # Show classification stats
            stats = self.classifier.get_classification_stats(df_classified)
            
            print(f"✅ Successfully classified {len(df_classified)} posts")
            print("\n📊 Category Distribution:")
            for category, count in stats['category_distribution'].items():
                percentage = stats['category_percentages'][category]
                category_name = config.POST_CATEGORIES.get(category, category)
                print(f"  {category_name}: {count} ({percentage:.1f}%)")
            
            return df_classified
            
        except Exception as e:
            print(f"❌ Error classifying data: {e}")
            return None
    
    def analyze_data(self, df=None):
        """Step 3: Analyze and generate insights"""
        print("\n📈 STEP 3: Analyzing Data & Generating Insights")
        print("=" * 55)
        
        try:
            if df is not None:
                df.to_csv(config.PROCESSED_DATA_FILE, index=False)
            
            # Generate comprehensive analysis
            self.analyzer.load_data()
            
            # Create visualizations
            print("📊 Creating visualizations...")
            self.analyzer.create_visualizations()
            
            # Generate and export report
            print("📝 Generating comprehensive reports...")
            self.analyzer.export_report(generate_html=True)
            
            # Generate competitive insights
            competitive_insights = self.analyzer.generate_competitive_insights()
            
            print("\n✅ Analysis complete!")
            
            # Print key insights
            print("\n🎯 KEY COMPETITIVE INSIGHTS:")
            print("-" * 35)
            
            pain_points = competitive_insights['pain_points']
            print(f"💢 Pain Points: {pain_points['count']} posts ({pain_points['percentage']}%)")
            
            feature_requests = competitive_insights['feature_requests']
            print(f"💡 Feature Requests: {feature_requests['count']} posts ({feature_requests['percentage']}%)")
            
            satisfaction = competitive_insights['satisfaction_ratio']
            print(f"😊 User Satisfaction: {satisfaction['ratio']} ({satisfaction['interpretation']})")
            
            competitor_mentions = competitive_insights['competitor_mentions']
            print(f"🆚 Competitor Mentions: {competitor_mentions['count']} posts ({competitor_mentions['percentage']}%)")
            
            # Show top issues
            print("\n🔥 TOP PAIN POINTS:")
            for i, issue in enumerate(pain_points['top_issues'][:3], 1):
                print(f"  {i}. {issue['title'][:70]}... (Score: {issue['score']})")
            
            print("\n💡 TOP FEATURE REQUESTS:")
            for i, request in enumerate(feature_requests['top_requests'][:3], 1):
                print(f"  {i}. {request['title'][:70]}... (Score: {request['score']})")
            
            return competitive_insights
            
        except Exception as e:
            print(f"❌ Error analyzing data: {e}")
            return None
    
    def run_full_pipeline(self, sort_methods=['hot', 'new'], limit_per_method=50):
        """Run the complete web scraping analysis pipeline"""
        print("🚀 STARTING NOTION REDDIT WEB SCRAPING PIPELINE")
        print("=" * 65)
        print("✨ No API credentials required!")
        print(f"🎯 Target: r/{config.SUBREDDIT_NAME}")
        print(f"📋 Sort Methods: {sort_methods}")
        print(f"📊 Posts per method: {limit_per_method}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Collect data via scraping
        df = self.collect_data(sort_methods, limit_per_method)
        if df is None or len(df) == 0:
            print("❌ Pipeline failed: No data collected")
            print("\n🔧 Troubleshooting tips:")
            print("  • Check internet connection")
            print("  • Try with fewer posts: --limit 25")
            print("  • Reddit might be blocking requests - try again later")
            return False
        
        # Step 2: Classify data
        df_classified = self.classify_data(df)
        if df_classified is None:
            print("❌ Pipeline failed at classification step")
            return False
        
        # Step 3: Analyze data
        insights = self.analyze_data(df_classified)
        if insights is None:
            print("❌ Pipeline failed at analysis step")
            return False
        
        print("\n🎉 WEB SCRAPING PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("📁 Generated files:")
        print(f"  📊 Raw data: {config.RAW_DATA_FILE}")
        print(f"  🏷️ Processed data: {config.PROCESSED_DATA_FILE}")
        print(f"  📈 Visualizations: visualizations/comprehensive_analysis.png")
        print(f"  📝 Text reports: reports/ (timestamped)")
        print(f"  🌐 HTML reports: reports/html/ (opens in browser)")
        
        print("\n🚀 Next steps:")
        print("  📊 View dashboard: streamlit run dashboard.py")
        print("  🌐 Open HTML report in browser (auto-opens)")
        print(f"  📋 Review data: {config.PROCESSED_DATA_FILE}")
        
        return True
    
    def test_scraper(self):
        """Test the web scraper functionality"""
        print("🧪 Testing Web Scraper...")
        print("=" * 30)
        
        try:
            # Test with a small sample
            posts = self.collector.collect_posts('hot', limit=5)
            
            if posts and len(posts) > 0:
                print(f"✅ Scraper working! Collected {len(posts)} test posts")
                
                print("\n📋 Sample post:")
                sample = posts[0]
                print(f"  Title: {sample.get('title', 'N/A')[:60]}...")
                print(f"  Score: {sample.get('score', 0)}")
                print(f"  Comments: {sample.get('num_comments', 0)}")
                print(f"  Author: {sample.get('author', 'N/A')}")
                
                return True
            else:
                print("❌ Scraper test failed - no posts collected")
                return False
                
        except Exception as e:
            print(f"❌ Scraper test failed: {e}")
            return False

def main():
    """Main entry point for web scraping pipeline"""
    pipeline = NotionScrapingPipeline()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            # Test scraper functionality
            pipeline.test_scraper()
            
        elif command == 'collect':
            # Just collect data
            pipeline.collect_data()
            
        elif command == 'classify':
            # Just classify existing data
            pipeline.classify_data()
            
        elif command == 'analyze':
            # Just analyze existing data
            pipeline.analyze_data()
            
        elif command == 'quick':
            # Quick run with fewer posts
            pipeline.run_full_pipeline(['hot', 'new'], 25)
            
        elif command == 'full':
            # Comprehensive run with more posts and methods
            pipeline.run_full_pipeline(['hot', 'new', 'top'], 75)
            
        elif command == 'minimal':
            # Minimal run for testing
            pipeline.run_full_pipeline(['hot'], 10)
            
        else:
            print("Available commands:")
            print("  test     - Test scraper functionality")
            print("  collect  - Collect data only")  
            print("  classify - Classify existing data")
            print("  analyze  - Analyze processed data")
            print("  minimal  - Minimal run (10 posts)")
            print("  quick    - Quick run (50 posts)")
            print("  full     - Full comprehensive run (150+ posts)")
            
    else:
        # Default: run moderate pipeline
        success = pipeline.run_full_pipeline(['hot', 'new'], 50)
        
        if not success:
            print("\n🔧 Try running with fewer posts:")
            print("  python main_pipeline_scraper.py quick")
            print("  python main_pipeline_scraper.py minimal")

if __name__ == "__main__":
    main()