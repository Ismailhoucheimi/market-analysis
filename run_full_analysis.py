#!/usr/bin/env python3
"""
Complete analysis pipeline for 838 posts
Runs LLM analysis and generates comprehensive report
"""

import subprocess
import os
import sys

def run_command(command, description):
    """Run a command and show progress"""
    print(f"🚀 {description}")
    print(f"Running: {command}")
    print("=" * 60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print("Output:", result.stdout[-500:])  # Last 500 chars
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e}")
        if e.stdout:
            print("Output:", e.stdout)
        if e.stderr:
            print("Error output:", e.stderr)
        return False

def main():
    """Run the complete analysis pipeline"""
    
    # Check if LLM analysis is already done
    if os.path.exists('data/processed_posts_838.csv'):
        print("✅ LLM analysis already completed!")
        llm_done = True
    else:
        print("🤖 Running LLM analysis on 838 posts...")
        llm_done = run_command(
            "python llm_analyzer.py data/reddit_notion_new_20250825_203710.csv",
            "LLM Analysis"
        )
    
    if not llm_done:
        print("❌ Cannot proceed without LLM analysis")
        sys.exit(1)
    
    # Run comprehensive report generation
    print("📋 Generating comprehensive strategic report...")
    report_done = run_command(
        "python summary_report_generator.py",
        "Comprehensive Report Generation"
    )
    
    if report_done:
        print("\n🎯 Analysis Pipeline Complete!")
        print("📊 838 posts analyzed with LLM insights")
        print("📋 Comprehensive strategic report generated") 
        print("🌐 Streamlit dashboard ready with new data")
        print("\nTo view results:")
        print("- Run: streamlit run streamlit_app.py")
        print("- Or check: reports/comprehensive_notion_analysis.md")
    else:
        print("⚠️  Analysis completed but report generation failed")

if __name__ == "__main__":
    main()