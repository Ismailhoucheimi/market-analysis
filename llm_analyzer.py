#!/usr/bin/env python3
"""
LLM-Powered Post Analyzer using Google Gemini-2.5-flash
Advanced competitive intelligence analysis beyond keyword matching
"""

import google.generativeai as genai
import pandas as pd
import json
import time
import os
from typing import Dict, List, Any, Optional, Tuple
import tiktoken
import config

class GeminiPostAnalyzer:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Rate limiting
        self.requests_per_minute = 60
        self.last_request_time = 0
        
        # Token counter for cost estimation
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except:
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for cost tracking"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimate: ~4 characters per token
            return len(text) // 4
    
    def rate_limit(self):
        """Simple rate limiting to avoid hitting API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.requests_per_minute  # seconds between requests
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def create_analysis_prompt(self, posts_batch: List[Dict[str, Any]]) -> str:
        """Create a comprehensive analysis prompt for a batch of posts"""
        
        prompt = """You are an expert competitive intelligence analyst specializing in SaaS products and user research. Analyze the following Reddit posts from r/Notion to extract deep competitive insights.

For each post, provide:

1. **Primary Category** (choose the most fitting):
   - praise: Genuine positive feedback and satisfaction
   - criticism: Complaints, frustrations, and negative experiences  
   - feature_request: Specific requests for new capabilities
   - help_support: Users seeking assistance or confused about features
   - template_sharing: Sharing or requesting templates/setups
   - integration_request: Requests for third-party app integrations
   - bug_report: Technical issues and errors
   - workflow_showcase: Demonstrating how they use Notion
   - comparison: Comparing Notion to competitors
   - migration: Moving to/from Notion or other platforms
   - performance: Speed, reliability, or sync issues
   - mobile_feedback: Mobile app specific feedback
   - pricing: Cost, subscription, or billing discussions
   - community_meta: Subreddit or community discussions

2. **Sentiment Score** (-1.0 to 1.0): Overall emotional tone
3. **Urgency Level** (1-5): How critical/urgent is the issue raised
4. **Business Impact** (1-5): Potential impact on Notion's business
5. **Key Insights**: 2-3 bullet points of strategic insights
6. **Competitive Intelligence**: What this reveals about market position
7. **User Persona**: What type of user is this (beginner, power user, team admin, etc.)

Return your analysis as a JSON object with this structure:
```json
{
  "posts": [
    {
      "post_id": "post_id_here",
      "category": "category_name",
      "sentiment_score": 0.5,
      "urgency_level": 3,
      "business_impact": 4,
      "key_insights": [
        "insight 1",
        "insight 2"
      ],
      "competitive_intelligence": "strategic insight about market position",
      "user_persona": "user type description",
      "reasoning": "brief explanation of categorization"
    }
  ],
  "batch_summary": {
    "dominant_themes": ["theme1", "theme2"],
    "sentiment_trend": "positive/negative/neutral",
    "key_competitive_threats": ["threat1", "threat2"],
    "strategic_recommendations": ["rec1", "rec2"]
  }
}
```

Here are the posts to analyze:

"""
        
        for i, post in enumerate(posts_batch, 1):
            title = str(post.get('title', ''))
            content = str(post.get('selftext', '')) if pd.notna(post.get('selftext', '')) else ''
            score = post.get('score', 0)
            comments = post.get('num_comments', 0)
            author = str(post.get('author', ''))
            
            prompt += f"""
**Post {i}:**
- ID: {post.get('id', '')}
- Title: {title}
- Content: {content[:1000] + '...' if len(content) > 1000 else content}
- Score: {score} | Comments: {comments} | Author: {author}
- Flair: {post.get('flair_text', 'None')}

"""
        
        prompt += """
Focus on actionable competitive intelligence that Notion could use to improve their product strategy, identify market gaps, and understand user pain points. Be specific and strategic in your analysis.
"""
        
        return prompt
    
    def analyze_posts_batch(self, posts_batch: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze a batch of posts using Gemini"""
        try:
            self.rate_limit()
            
            prompt = self.create_analysis_prompt(posts_batch)
            
            # Count tokens for cost estimation
            estimated_tokens = self.count_tokens(prompt)
            print(f"🤖 Analyzing {len(posts_batch)} posts (~{estimated_tokens} tokens)")
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Clean up the response (remove markdown code blocks if present)
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            try:
                analysis_data = json.loads(response_text.strip())
                return analysis_data
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw response: {response_text[:500]}...")
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing posts batch: {e}")
            return None
    
    def analyze_all_posts(self, df: pd.DataFrame, batch_size: int = 5) -> pd.DataFrame:
        """Analyze all posts in batches using Gemini"""
        
        print(f"\n🧠 Starting LLM Analysis with Gemini-2.5-flash")
        print(f"📊 Analyzing {len(df)} posts in batches of {batch_size}")
        
        # Prepare results
        llm_results = []
        batch_summaries = []
        
        # Process in batches
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size].to_dict('records')
            batch_num = (i // batch_size) + 1
            total_batches = (len(df) + batch_size - 1) // batch_size
            
            print(f"🔄 Processing batch {batch_num}/{total_batches}")
            
            analysis = self.analyze_posts_batch(batch)
            
            if analysis and 'posts' in analysis:
                llm_results.extend(analysis['posts'])
                if 'batch_summary' in analysis:
                    batch_summaries.append(analysis['batch_summary'])
                print(f"✅ Analyzed {len(analysis['posts'])} posts")
            else:
                print(f"❌ Failed to analyze batch {batch_num}")
                # Create fallback analysis
                for post in batch:
                    llm_results.append({
                        'post_id': post.get('id', ''),
                        'category': 'help_support',  # Default fallback
                        'sentiment_score': 0.0,
                        'urgency_level': 2,
                        'business_impact': 2,
                        'key_insights': ['Analysis failed'],
                        'competitive_intelligence': 'Unable to analyze',
                        'user_persona': 'Unknown',
                        'reasoning': 'LLM analysis failed'
                    })
        
        # Merge results back to dataframe
        df_enhanced = df.copy()
        
        # Create mapping for easy lookup
        llm_dict = {result['post_id']: result for result in llm_results}
        
        # Add new columns
        df_enhanced['llm_category'] = df_enhanced['id'].map(lambda x: llm_dict.get(x, {}).get('category', 'help_support'))
        df_enhanced['sentiment_score'] = df_enhanced['id'].map(lambda x: llm_dict.get(x, {}).get('sentiment_score', 0.0))
        df_enhanced['urgency_level'] = df_enhanced['id'].map(lambda x: llm_dict.get(x, {}).get('urgency_level', 2))
        df_enhanced['business_impact'] = df_enhanced['id'].map(lambda x: llm_dict.get(x, {}).get('business_impact', 2))
        df_enhanced['key_insights'] = df_enhanced['id'].map(lambda x: '; '.join(llm_dict.get(x, {}).get('key_insights', [])))
        df_enhanced['competitive_intelligence'] = df_enhanced['id'].map(lambda x: llm_dict.get(x, {}).get('competitive_intelligence', ''))
        df_enhanced['user_persona'] = df_enhanced['id'].map(lambda x: llm_dict.get(x, {}).get('user_persona', ''))
        df_enhanced['llm_reasoning'] = df_enhanced['id'].map(lambda x: llm_dict.get(x, {}).get('reasoning', ''))
        
        # Use LLM category as the primary category if available
        df_enhanced['predicted_category'] = df_enhanced['llm_category']
        df_enhanced['category_label'] = df_enhanced['predicted_category'].map(config.POST_CATEGORIES)
        
        print(f"\n✅ LLM Analysis Complete!")
        print(f"📈 Enhanced {len(df_enhanced)} posts with AI insights")
        
        # Save batch summaries
        if batch_summaries:
            self.save_batch_summaries(batch_summaries)
        
        return df_enhanced
    
    def save_batch_summaries(self, batch_summaries: List[Dict[str, Any]]):
        """Save batch summaries for strategic insights"""
        summary_file = 'reports/llm_batch_summaries.json'
        os.makedirs(os.path.dirname(summary_file), exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(batch_summaries, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved batch summaries to {summary_file}")
    
    def generate_strategic_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate high-level strategic insights from LLM analysis"""
        
        if 'sentiment_score' not in df.columns:
            return {}
        
        summary = {
            'total_posts': len(df),
            'avg_sentiment': df['sentiment_score'].mean(),
            'sentiment_distribution': {
                'positive': len(df[df['sentiment_score'] > 0.1]),
                'neutral': len(df[df['sentiment_score'].between(-0.1, 0.1)]),
                'negative': len(df[df['sentiment_score'] < -0.1])
            },
            'high_urgency_posts': len(df[df['urgency_level'] >= 4]),
            'high_business_impact': len(df[df['business_impact'] >= 4]),
            'top_user_personas': df['user_persona'].value_counts().head(5).to_dict(),
            'category_sentiment': df.groupby('predicted_category')['sentiment_score'].mean().to_dict(),
            'priority_issues': df[df['urgency_level'] >= 4].nlargest(5, 'business_impact')[
                ['title', 'sentiment_score', 'urgency_level', 'business_impact', 'key_insights']
            ].to_dict('records')
        }
        
        return summary

def main():
    """Run LLM analyzer with resume capability"""
    import sys
    
    try:
        if not config.GEMINI_API_KEY:
            print("❌ GEMINI_API_KEY not found in environment variables")
            print("Please add your Gemini API key to .env file")
            print("Get your API key from: https://makersuite.google.com/app/apikey")
            return
        
        # Parse command line arguments
        resume_mode = '--resume' in sys.argv or len(sys.argv) > 1 and sys.argv[1].endswith('.csv')
        input_file = None
        
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if arg.endswith('.csv'):
                    input_file = arg
                    break
        
        # Determine input file
        if input_file:
            if not os.path.exists(input_file):
                print(f"❌ Input file not found: {input_file}")
                return
            df = pd.read_csv(input_file)
            print(f"📊 Loaded {len(df)} posts from {input_file}")
        else:
            if not os.path.exists(config.PROCESSED_DATA_FILE):
                print("❌ No processed data found. Run the scraping pipeline first:")
                print("  python main_pipeline_scraper.py quick")
                return
            df = pd.read_csv(config.PROCESSED_DATA_FILE)
            print(f"📊 Loaded {len(df)} posts from {config.PROCESSED_DATA_FILE}")
        
        analyzer = GeminiPostAnalyzer()
        
        # Check for existing processed results to resume from
        output_file = 'data/processed_posts_838.csv' if input_file else 'data/processed_posts.csv'
        processed_ids = set()
        
        if os.path.exists(output_file) and resume_mode:
            existing_df = pd.read_csv(output_file)
            processed_ids = set(existing_df['id'].tolist())
            print(f"🔄 Resume mode: Found {len(processed_ids)} already processed posts")
            
            # Filter out already processed posts
            df_to_process = df[~df['id'].isin(processed_ids)]
            print(f"📋 Will process {len(df_to_process)} remaining posts")
        else:
            df_to_process = df
            print(f"🚀 Processing all {len(df_to_process)} posts...")
        
        if len(df_to_process) == 0:
            print("✅ All posts already processed!")
            return
        
        # Analyze remaining posts
        enhanced_df = analyzer.analyze_all_posts(df_to_process, batch_size=10)
        
        # If resuming, merge with existing data
        if processed_ids and os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            # Combine existing and new results
            final_df = pd.concat([existing_df, enhanced_df], ignore_index=True)
            print(f"🔗 Merged {len(existing_df)} existing + {len(enhanced_df)} new = {len(final_df)} total posts")
        else:
            final_df = enhanced_df
        
        # Save results
        final_df.to_csv(output_file, index=False)
        print(f"💾 Saved {len(final_df)} processed posts to {output_file}")
        
        # Update config to point to new file if processing the 838 dataset
        if input_file and '838' in output_file:
            config.PROCESSED_DATA_FILE = output_file
        
        # Generate strategic summary
        summary = analyzer.generate_strategic_summary(final_df)
        print(f"\n📈 Strategic Summary:")
        print(f"   Total Posts Analyzed: {len(final_df)}")
        print(f"   Average Sentiment: {summary.get('avg_sentiment', 0):.2f}")
        print(f"   High Priority Issues: {summary.get('high_urgency_posts', 0)}")
        print(f"   High Business Impact: {summary.get('high_business_impact', 0)}")
        
        print(f"\n✅ LLM Analysis completed! Processed {len(final_df)} posts total")
        
    except Exception as e:
        print(f"❌ Error running LLM analysis: {e}")
        print("Make sure you have a valid GEMINI_API_KEY in your .env file")

if __name__ == "__main__":
    main()