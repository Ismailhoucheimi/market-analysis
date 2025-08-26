#!/usr/bin/env python3
"""
Comprehensive Summary Report Generator using Gemini 2.5 Pro
Analyzes all posts and LLM insights to generate executive summary
"""

import google.generativeai as genai
import pandas as pd
import json
import os
from typing import Dict, Any
import config

class ComprehensiveSummaryGenerator:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        # Use Gemini 2.5 Pro for comprehensive analysis
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def create_summary_prompt(self, posts_data: str, batch_summaries: str, zenflo_context: str = "") -> str:
        """Create comprehensive analysis prompt for Gemini 2.5 Pro"""
        
        zenflo_analysis_section = ""
        if zenflo_context:
            zenflo_analysis_section = f"""
## ZENFLO COMPETITIVE ANALYSIS & STRATEGIC OPPORTUNITIES

Based on the ZenFlo product analysis and Notion user insights, provide:
- How ZenFlo's positioning addresses gaps identified in Notion user feedback
- Specific opportunities where ZenFlo can capitalize on Notion's pain points
- Feature differentiation strategies based on user complaints about Notion
- Market positioning recommendations for ZenFlo vs Notion
- Target user segments that would be most likely to switch from Notion to ZenFlo

ZENFLO CONTEXT:
{zenflo_context}
"""
        
        prompt = f"""You are an expert product strategist and competitive intelligence analyst. Analyze this comprehensive dataset of 500+ Reddit posts from r/Notion to generate an executive summary report.

DATA PROVIDED:
1. Individual post analysis with sentiment scores, categories, and AI insights
2. Batch summaries with strategic recommendations and competitive threats

Your task is to synthesize all this information into a comprehensive report with the following sections:

# COMPREHENSIVE NOTION ANALYSIS REPORT

## EXECUTIVE SUMMARY
Provide a 3-4 paragraph high-level overview of the key findings and strategic implications.

## WHAT USERS LOVE ABOUT NOTION
Analyze positive sentiment and praise to identify:
- Top 5 most appreciated features/aspects
- Why users choose Notion over competitors
- Unique value propositions that drive loyalty
- Community strengths and engagement patterns

## WHAT USERS DISLIKE ABOUT NOTION
Analyze negative sentiment and criticism to identify:
- Top 5 most complained about issues/limitations  
- Common pain points across user segments
- Feature gaps compared to competitors
- Usability and performance concerns

## MOST REQUESTED FEATURES
Identify and prioritize:
- Top 10 most frequently requested features
- Categorize by theme (integrations, UI/UX, automation, etc.)
- Business impact assessment for each request
- Technical complexity vs user demand analysis

## COMPETITIVE INTELLIGENCE INSIGHTS
- Key competitive threats and how users compare Notion to alternatives
- Market positioning gaps and opportunities
- User migration patterns and retention risks
- Differentiation opportunities

## USER PERSONA & SEGMENT ANALYSIS
- Primary user types and their distinct needs
- Pain points by user segment
- Feature adoption patterns
- Churn risk factors by segment

## STRATEGIC RECOMMENDATIONS
Provide 8-10 actionable recommendations prioritized by:
- Business impact (revenue, retention, growth)
- Implementation complexity
- Competitive urgency
- User satisfaction impact

## ADDITIONAL INSIGHTS & TRENDS
Identify any other significant patterns, emerging trends, or strategic insights not covered in previous sections.

{zenflo_analysis_section}

---

ANALYSIS DATA:

INDIVIDUAL POSTS DATA:
{posts_data}

BATCH SUMMARIES:
{batch_summaries}

Please provide a comprehensive, data-driven analysis that a product team and executive leadership could use for strategic planning. Focus on actionable insights backed by the data provided."""
        
        return prompt
    
    def generate_comprehensive_report(self, processed_data_file: str = None, batch_summaries_file: str = None, include_zenflo_analysis: bool = True) -> str:
        """Generate comprehensive summary using Gemini 2.5 Pro"""
        
        # Load processed posts data
        if not processed_data_file:
            processed_data_file = 'data/processed_posts_838.csv'
        
        if not batch_summaries_file:
            batch_summaries_file = 'reports/llm_batch_summaries.json'
        
        print(f"📊 Loading processed posts from {processed_data_file}")
        df = pd.read_csv(processed_data_file)
        
        print(f"📋 Loading batch summaries from {batch_summaries_file}")
        with open(batch_summaries_file, 'r', encoding='utf-8') as f:
            batch_summaries = json.load(f)
        
        # Prepare data summaries for the prompt (to fit within token limits)
        posts_summary = []
        
        print(f"🔄 Preparing data summary for {len(df)} posts...")
        
        # Create condensed post summaries
        for _, row in df.iterrows():
            post_summary = {
                'title': str(row.get('title', ''))[:100],
                'category': row.get('llm_category', ''),
                'sentiment_score': row.get('sentiment_score', 0),
                'urgency_level': row.get('urgency_level', 0),
                'business_impact': row.get('business_impact', 0),
                'user_persona': str(row.get('user_persona', ''))[:50],
                'key_insights': str(row.get('key_insights', ''))[:200],
                'competitive_intelligence': str(row.get('competitive_intelligence', ''))[:150]
            }
            posts_summary.append(post_summary)
        
        # Convert to JSON strings for the prompt
        posts_data_json = json.dumps(posts_summary[:100], indent=2)  # First 100 for token limits
        batch_summaries_json = json.dumps(batch_summaries, indent=2)
        
        # Prepare ZenFlo context if requested
        zenflo_context = ""
        if include_zenflo_analysis:
            zenflo_context = """
ZENFLO PRODUCT ANALYSIS:

About ZenFlo:
ZenFlo is an AI-powered productivity app designed to create "a calm space where you can focus on what matters, stay organized, and finish each day with peace of mind." It targets professionals and individuals seeking mindful productivity, particularly those overwhelmed by notifications, shifting priorities, and endless to-do lists.

Core Value Propositions:
- Mindfulness-driven productivity
- AI-assisted project management  
- Minimalist, intuitive interface
- Comprehensive project tracking across personal and professional domains

Key Features:
- Flexible project views (dashboard, list, board, calendar)
- AI capabilities including natural language recommendations, automatic project breakdowns, bulk task rescheduling, and on-demand brainstorming
- Planned integrations with Google Calendar, Gmail, Outlook, and Slack
- Mobile-first design with context-aware recommendations
- Smart task scheduling and productivity insights
- AI Chat Assistant and AI Project Planner

Competitive Positioning:
ZenFlo differentiates itself from traditional productivity tools by emphasizing calm, intentional workflow, intelligent but non-intrusive AI assistance, scalability from simple checklists to complex projects, and a holistic approach to productivity that prioritizes user well-being. The platform combines minimalist design, AI intelligence, and a mindfulness-first approach to productivity management.

Market Statistics:
- 73% of productivity app users want AI-powered features
- Early adopters willing to pay 30% premium for AI integration
- Focuses on reducing cognitive load through intelligent task management
"""
        
        # Create the comprehensive analysis prompt
        prompt = self.create_summary_prompt(posts_data_json, batch_summaries_json, zenflo_context)
        
        print(f"🤖 Generating comprehensive report with Gemini 2.5 Pro...")
        print(f"📝 Prompt length: ~{len(prompt)} characters")
        
        try:
            response = self.model.generate_content(prompt)
            report_content = response.text
            
            # Save the comprehensive report
            os.makedirs('reports', exist_ok=True)
            report_filename = 'reports/comprehensive_notion_analysis.md'
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ Comprehensive report generated: {report_filename}")
            print(f"📄 Report length: {len(report_content)} characters")
            
            return report_content
            
        except Exception as e:
            print(f"❌ Error generating comprehensive report: {e}")
            return None
    
    def generate_additional_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate additional statistical insights from the data"""
        
        insights = {
            'total_posts_analyzed': len(df),
            'sentiment_distribution': {
                'positive': len(df[df['sentiment_score'] > 0.1]),
                'neutral': len(df[df['sentiment_score'].between(-0.1, 0.1)]),
                'negative': len(df[df['sentiment_score'] < -0.1])
            },
            'average_sentiment': df['sentiment_score'].mean(),
            'high_urgency_posts': len(df[df['urgency_level'] >= 4]),
            'high_business_impact': len(df[df['business_impact'] >= 4]),
            'category_distribution': df['llm_category'].value_counts().to_dict(),
            'top_user_personas': df['user_persona'].value_counts().head(10).to_dict() if 'user_persona' in df.columns else {},
            'urgency_by_category': df.groupby('llm_category')['urgency_level'].mean().sort_values(ascending=False).to_dict(),
            'business_impact_by_category': df.groupby('llm_category')['business_impact'].mean().sort_values(ascending=False).to_dict()
        }
        
        return insights

def main():
    """Generate comprehensive summary report"""
    try:
        generator = ComprehensiveSummaryGenerator()
        
        # Generate the comprehensive report
        report = generator.generate_comprehensive_report()
        
        if report:
            print(f"\n🎯 COMPREHENSIVE REPORT GENERATED!")
            print(f"📁 Location: reports/comprehensive_notion_analysis.md")
            print(f"\n📊 Additional statistical insights:")
            
            # Load data for additional insights
            df = pd.read_csv('data/processed_posts_838.csv')
            insights = generator.generate_additional_insights(df)
            
            print(f"   Total posts analyzed: {insights['total_posts_analyzed']}")
            print(f"   Average sentiment: {insights['average_sentiment']:.3f}")
            print(f"   High urgency posts: {insights['high_urgency_posts']}")
            print(f"   High business impact posts: {insights['high_business_impact']}")
            print(f"   Top category: {list(insights['category_distribution'].keys())[0]}")
            
            # Save insights as well
            with open('reports/statistical_insights.json', 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Statistical insights saved to: reports/statistical_insights.json")
            
        else:
            print("❌ Failed to generate comprehensive report")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()