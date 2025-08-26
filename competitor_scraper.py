#!/usr/bin/env python3
"""
Multi-Competitor Reddit Scraper
Collects data from multiple competitor subreddits using the existing scraping infrastructure
"""

import sys
import os
import subprocess
import argparse
from competitors_config import competitor_manager

def scrape_competitor(competitor_name: str, sort_method: str = "new", limit: int = 1000):
    """Scrape data for a specific competitor"""
    
    try:
        config = competitor_manager.get_competitor_config(competitor_name)
        print(f"🚀 Starting scrape for {config.display_name} (r/{config.subreddit})")
        
        # Create directories if they don't exist
        competitor_manager.create_competitor_directories(competitor_name)
        
        # Modify the existing scraper to work with different subreddits
        output_file = f"competitors/{competitor_name}/data/raw_posts.csv"
        
        # Run the scraper with competitor-specific parameters
        command = [
            "python", "reddit_scraper.py", 
            sort_method, 
            str(limit),
            "--subreddit", config.subreddit,
            "--output", output_file
        ]
        
        print(f"🔄 Running: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully scraped {config.display_name} data")
            print(f"📁 Data saved to: {output_file}")
            return True
        else:
            print(f"❌ Scraping failed for {config.display_name}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error scraping {competitor_name}: {e}")
        return False

def analyze_competitor(competitor_name: str):
    """Run LLM analysis for a specific competitor"""
    
    try:
        config = competitor_manager.get_competitor_config(competitor_name)
        raw_file = f"competitors/{competitor_name}/data/raw_posts.csv"
        processed_file = f"competitors/{competitor_name}/data/processed_posts.csv"
        
        if not os.path.exists(raw_file):
            print(f"❌ Raw data not found for {config.display_name}. Run scraping first.")
            return False
        
        print(f"🧠 Starting LLM analysis for {config.display_name}")
        
        # Run LLM analyzer with competitor-specific configuration
        command = [
            "python", "llm_analyzer.py", 
            raw_file,
            "--output", processed_file,
            "--competitor", competitor_name
        ]
        
        print(f"🔄 Running: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully analyzed {config.display_name} data")
            print(f"📁 Analysis saved to: {processed_file}")
            return True
        else:
            print(f"❌ Analysis failed for {config.display_name}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing {competitor_name}: {e}")
        return False

def generate_competitor_report(competitor_name: str):
    """Generate comprehensive report for a specific competitor"""
    
    try:
        config = competitor_manager.get_competitor_config(competitor_name)
        processed_file = f"competitors/{competitor_name}/data/processed_posts.csv"
        report_file = f"competitors/{competitor_name}/reports/analysis.md"
        
        if not os.path.exists(processed_file):
            print(f"❌ Processed data not found for {config.display_name}. Run analysis first.")
            return False
        
        print(f"📋 Generating report for {config.display_name}")
        
        # Run report generator with competitor-specific data
        command = [
            "python", "summary_report_generator.py",
            "--input", processed_file,
            "--output", report_file,
            "--competitor", competitor_name
        ]
        
        print(f"🔄 Running: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully generated {config.display_name} report")
            print(f"📁 Report saved to: {report_file}")
            return True
        else:
            print(f"❌ Report generation failed for {config.display_name}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating report for {competitor_name}: {e}")
        return False

def run_full_pipeline(competitor_name: str, limit: int = 1000):
    """Run complete pipeline for a competitor: scrape -> analyze -> report"""
    
    config = competitor_manager.get_competitor_config(competitor_name)
    print(f"\n🎯 Running full pipeline for {config.display_name}")
    print("="*60)
    
    # Step 1: Scrape data
    if scrape_competitor(competitor_name, "new", limit):
        print(f"✅ Step 1 complete: Data collection")
    else:
        print(f"❌ Step 1 failed: Data collection")
        return False
    
    # Step 2: LLM Analysis
    if analyze_competitor(competitor_name):
        print(f"✅ Step 2 complete: LLM Analysis")
    else:
        print(f"❌ Step 2 failed: LLM Analysis")
        return False
    
    # Step 3: Report Generation
    if generate_competitor_report(competitor_name):
        print(f"✅ Step 3 complete: Report Generation")
    else:
        print(f"❌ Step 3 failed: Report Generation")
        return False
    
    print(f"\n🎉 Full pipeline completed for {config.display_name}!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Multi-Competitor Analysis Tool")
    parser.add_argument("action", choices=["scrape", "analyze", "report", "full"], 
                       help="Action to perform")
    parser.add_argument("competitor", choices=competitor_manager.get_available_competitors(),
                       help="Competitor to analyze")
    parser.add_argument("--limit", type=int, default=1000, 
                       help="Number of posts to scrape (default: 1000)")
    
    args = parser.parse_args()
    
    if args.action == "scrape":
        scrape_competitor(args.competitor, limit=args.limit)
    elif args.action == "analyze":
        analyze_competitor(args.competitor)
    elif args.action == "report":
        generate_competitor_report(args.competitor)
    elif args.action == "full":
        run_full_pipeline(args.competitor, limit=args.limit)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🎯 Multi-Competitor Analysis Tool")
        print("="*40)
        print("Available competitors:")
        for comp in competitor_manager.get_available_competitors():
            config = competitor_manager.get_competitor_config(comp)
            validation = competitor_manager.validate_data_completeness(comp)
            status = "✅" if validation["has_processed_data"] else "⏳"
            print(f"  {config.logo_emoji} {config.display_name} {status}")
        
        print("\nUsage examples:")
        print("  python competitor_scraper.py full notion")
        print("  python competitor_scraper.py scrape chatgpt --limit 500")
        print("  python competitor_scraper.py analyze obsidian")
        print("  python competitor_scraper.py report airtable")
    else:
        main()