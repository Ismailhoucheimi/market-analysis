#!/usr/bin/env python3
"""
Main pipeline for Notion Reddit Analysis
Orchestrates data collection, classification, and analysis
"""

import os
import sys
from datetime import datetime
import pandas as pd

from reddit_collector import RedditCollector
from text_classifier import NotionPostClassifier
from data_analyzer import NotionDataAnalyzer
import config

class NotionAnalysisPipeline:
    def __init__(self):
        self.collector = RedditCollector()
        self.classifier = NotionPostClassifier()
        self.analyzer = NotionDataAnalyzer()
        
        # Ensure directories exist
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs('models', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        os.makedirs('visualizations', exist_ok=True)
    
    def check_credentials(self) -> bool:
        """Check if Reddit API credentials are configured"""
        if not config.REDDIT_CLIENT_ID or not config.REDDIT_CLIENT_SECRET:
            print("❌ Reddit API credentials not found!")
            print("Please:")
            print("1. Copy .env.example to .env")
            print("2. Get Reddit API credentials from https://www.reddit.com/prefs/apps")
            print("3. Fill in your credentials in the .env file")
            return False
        return True
    
    def collect_data(self, sort_methods=['hot', 'new', 'top'], limit_per_method=50):
        """Step 1: Collect Reddit posts"""
        print("\n🔄 STEP 1: Collecting Reddit Posts")
        print("=" * 50)
        
        if not self.check_credentials():
            return None
        
        try:
            df = self.collector.collect_and_save(
                sort_methods=sort_methods,
                limit_per_method=limit_per_method
            )
            
            print(f"✅ Successfully collected {len(df)} unique posts")
            return df
            
        except Exception as e:
            print(f"❌ Error collecting data: {e}")
            return None
    
    def classify_data(self, df=None):
        """Step 2: Classify posts into categories"""
        print("\n🔄 STEP 2: Classifying Posts")
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
            print("\nCategory Distribution:")
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
        print("\n🔄 STEP 3: Analyzing Data & Generating Insights")
        print("=" * 55)
        
        try:
            if df is not None:
                # Save the dataframe for analyzer to use
                df.to_csv(config.PROCESSED_DATA_FILE, index=False)
            
            # Generate comprehensive analysis
            self.analyzer.load_data()
            
            # Create visualizations
            print("📊 Creating visualizations...")
            self.analyzer.create_visualizations()
            
            # Generate and export report
            print("📝 Generating report...")
            self.analyzer.export_report()
            
            # Generate competitive insights
            competitive_insights = self.analyzer.generate_competitive_insights()
            
            print("\n✅ Analysis complete!")
            
            # Print key insights
            print("\n🎯 KEY COMPETITIVE INSIGHTS:")
            print("-" * 30)
            
            pain_points = competitive_insights['pain_points']
            print(f"💢 Pain Points: {pain_points['count']} posts ({pain_points['percentage']}%)")
            
            feature_requests = competitive_insights['feature_requests']
            print(f"💡 Feature Requests: {feature_requests['count']} posts ({feature_requests['percentage']}%)")
            
            satisfaction = competitive_insights['satisfaction_ratio']
            print(f"😊 Satisfaction Ratio: {satisfaction['ratio']} ({satisfaction['interpretation']})")
            
            competitor_mentions = competitive_insights['competitor_mentions']
            print(f"🆚 Competitor Comparisons: {competitor_mentions['count']} posts ({competitor_mentions['percentage']}%)")
            
            return competitive_insights
            
        except Exception as e:
            print(f"❌ Error analyzing data: {e}")
            return None
    
    def run_full_pipeline(self, sort_methods=['hot', 'new', 'top'], limit_per_method=50):
        """Run the complete analysis pipeline"""
        print("🚀 STARTING NOTION REDDIT ANALYSIS PIPELINE")
        print("=" * 60)
        print(f"Target Subreddit: r/{config.SUBREDDIT_NAME}")
        print(f"Sort Methods: {sort_methods}")
        print(f"Posts per method: {limit_per_method}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Collect data
        df = self.collect_data(sort_methods, limit_per_method)
        if df is None:
            print("❌ Pipeline failed at data collection step")
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
        
        print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 40)
        print("Generated files:")
        print(f"  📊 Raw data: {config.RAW_DATA_FILE}")
        print(f"  🏷️  Processed data: {config.PROCESSED_DATA_FILE}")
        print(f"  📈 Visualizations: visualizations/comprehensive_analysis.png")
        print(f"  📝 Reports: reports/ (timestamped)")
        
        return True
    
    def run_analysis_only(self):
        """Run only analysis on existing processed data"""
        print("🔄 Running analysis on existing data...")
        
        if not os.path.exists(config.PROCESSED_DATA_FILE):
            print("❌ No processed data found. Run full pipeline first.")
            return False
        
        return self.analyze_data() is not None

def main():
    """Main entry point with command line interface"""
    pipeline = NotionAnalysisPipeline()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'collect':
            # Just collect data
            pipeline.collect_data()
            
        elif command == 'classify':
            # Just classify existing data
            pipeline.classify_data()
            
        elif command == 'analyze':
            # Just analyze existing data
            pipeline.run_analysis_only()
            
        elif command == 'quick':
            # Quick run with fewer posts
            pipeline.run_full_pipeline(['hot', 'new'], 25)
            
        elif command == 'full':
            # Full comprehensive run
            pipeline.run_full_pipeline(['hot', 'new', 'top', 'rising'], 100)
            
        else:
            print("Unknown command. Use: collect, classify, analyze, quick, or full")
            
    else:
        # Default: run full pipeline with moderate settings
        pipeline.run_full_pipeline()

if __name__ == "__main__":
    main()