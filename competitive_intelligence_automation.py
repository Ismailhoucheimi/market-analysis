#!/usr/bin/env python3
"""
ZenFlo Competitive Intelligence Automation System
Automated monitoring and analysis of competitor activities, user sentiment, and market opportunities.
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import asyncio
from pathlib import Path
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
import praw
import pandas as pd
from textblob import TextBlob
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CompetitorAlert:
    """Data class for competitor alerts"""
    competitor: str
    alert_type: str  # 'sentiment_shift', 'feature_announcement', 'pricing_change', 'user_exodus'
    severity: str   # 'low', 'medium', 'high', 'critical'
    title: str
    description: str
    confidence: float
    timestamp: datetime
    data_source: str
    recommended_action: str

@dataclass
class MarketOpportunity:
    """Data class for identified market opportunities"""
    opportunity_type: str  # 'user_pain_point', 'competitor_weakness', 'feature_gap', 'pricing_opportunity'
    title: str
    description: str
    market_size_indicator: str  # 'small', 'medium', 'large', 'massive'
    urgency: str  # 'low', 'medium', 'high', 'critical'
    confidence: float
    supporting_evidence: List[str]
    recommended_response: str
    timestamp: datetime

class CompetitiveIntelligenceEngine:
    """Main engine for automated competitive intelligence"""
    
    def __init__(self, config_path: str = "competitors_config.py"):
        self.config_path = config_path
        self.competitors = {}
        self.reddit_client = None
        self.gemini_client = None
        self.alerts: List[CompetitorAlert] = []
        self.opportunities: List[MarketOpportunity] = []
        self.sentiment_history = {}
        self.data_dir = Path("automation_data")
        self.data_dir.mkdir(exist_ok=True)
        
        self._setup_apis()
        self._load_competitors()
        self._load_historical_data()
        
    def _setup_apis(self):
        """Initialize API clients"""
        try:
            # Reddit API
            self.reddit_client = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent='ZenFlo-CompetitiveIntel/1.0'
            )
            
            # Gemini API
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.gemini_client = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            logger.info("APIs initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize APIs: {e}")
    
    def _load_competitors(self):
        """Load competitor configurations"""
        try:
            # Import the competitors config
            import sys
            sys.path.append('.')
            from competitors_config import get_competitor_configs
            self.competitors = get_competitor_configs()
            logger.info(f"Loaded {len(self.competitors)} competitors")
        except Exception as e:
            logger.error(f"Failed to load competitors: {e}")
    
    def _load_historical_data(self):
        """Load historical sentiment and alert data"""
        try:
            sentiment_file = self.data_dir / "sentiment_history.json"
            if sentiment_file.exists():
                with open(sentiment_file, 'r') as f:
                    self.sentiment_history = json.load(f)
            
            alerts_file = self.data_dir / "alerts_history.json"
            if alerts_file.exists():
                with open(alerts_file, 'r') as f:
                    alerts_data = json.load(f)
                    self.alerts = [CompetitorAlert(**alert) for alert in alerts_data]
                    
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
    
    def _save_data(self):
        """Save current state to disk"""
        try:
            # Save sentiment history
            sentiment_file = self.data_dir / "sentiment_history.json"
            with open(sentiment_file, 'w') as f:
                json.dump(self.sentiment_history, f, indent=2, default=str)
            
            # Save alerts history
            alerts_file = self.data_dir / "alerts_history.json"
            alerts_data = [asdict(alert) for alert in self.alerts]
            with open(alerts_file, 'w') as f:
                json.dump(alerts_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save data: {e}")

    async def monitor_competitor_sentiment(self, competitor: str, subreddit: str) -> Dict[str, Any]:
        """Monitor sentiment changes for a specific competitor"""
        try:
            # Get recent posts (last 24 hours)
            posts = []
            subreddit_obj = self.reddit_client.subreddit(subreddit)
            
            for post in subreddit_obj.new(limit=50):
                post_time = datetime.fromtimestamp(post.created_utc)
                if post_time > datetime.now() - timedelta(days=1):
                    posts.append({
                        'title': post.title,
                        'body': post.selftext,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'timestamp': post_time,
                        'url': post.url
                    })
            
            if not posts:
                return {'competitor': competitor, 'sentiment_score': 0, 'post_count': 0}
            
            # Analyze sentiment
            sentiment_scores = []
            for post in posts:
                text = f"{post['title']} {post['body']}"
                blob = TextBlob(text)
                sentiment_scores.append(blob.sentiment.polarity)
            
            current_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Compare with historical sentiment
            historical_key = f"{competitor}_{datetime.now().strftime('%Y-%m')}"
            historical_sentiment = self.sentiment_history.get(historical_key, 0)
            
            sentiment_change = current_sentiment - historical_sentiment
            
            # Update history
            daily_key = f"{competitor}_{datetime.now().strftime('%Y-%m-%d')}"
            self.sentiment_history[daily_key] = current_sentiment
            
            return {
                'competitor': competitor,
                'current_sentiment': current_sentiment,
                'historical_sentiment': historical_sentiment,
                'sentiment_change': sentiment_change,
                'post_count': len(posts),
                'posts': posts
            }
            
        except Exception as e:
            logger.error(f"Failed to monitor sentiment for {competitor}: {e}")
            return {'competitor': competitor, 'error': str(e)}

    async def detect_feature_announcements(self, competitor: str, posts: List[Dict]) -> List[Dict]:
        """Detect potential feature announcements using AI"""
        try:
            feature_keywords = [
                'new feature', 'announcing', 'released', 'launch', 'update', 
                'now available', 'introducing', 'beta', 'rolling out'
            ]
            
            potential_announcements = []
            for post in posts:
                text = f"{post['title']} {post['body']}".lower()
                if any(keyword in text for keyword in feature_keywords):
                    potential_announcements.append(post)
            
            if not potential_announcements:
                return []
            
            # Use AI to analyze and categorize announcements
            analysis_prompt = f"""
            Analyze these potential feature announcements for {competitor}:
            
            {json.dumps(potential_announcements[:5], indent=2)}
            
            For each post, determine:
            1. Is this actually a feature announcement? (yes/no)
            2. What type of feature is it? (AI, mobile, collaboration, etc.)
            3. How significant is this feature? (minor/major/game-changing)
            4. What threat level does this pose to ZenFlo? (low/medium/high/critical)
            5. Recommended response strategy
            
            Return as JSON array with analysis for each post.
            """
            
            response = await self._analyze_with_ai(analysis_prompt)
            return json.loads(response.text) if response else []
            
        except Exception as e:
            logger.error(f"Failed to detect feature announcements for {competitor}: {e}")
            return []

    async def identify_user_pain_points(self, competitor: str, posts: List[Dict]) -> List[MarketOpportunity]:
        """Identify user pain points that represent opportunities"""
        try:
            # Filter posts with negative sentiment or complaint indicators
            complaint_keywords = [
                'frustrating', 'annoying', 'broken', 'terrible', 'awful', 'hate',
                'worst', 'useless', 'disappointed', 'bug', 'issue', 'problem'
            ]
            
            pain_point_posts = []
            for post in posts:
                text = f"{post['title']} {post['body']}".lower()
                if any(keyword in text for keyword in complaint_keywords) or post['score'] < 0:
                    pain_point_posts.append(post)
            
            if not pain_point_posts:
                return []
            
            # Use AI to analyze pain points and identify opportunities
            analysis_prompt = f"""
            Analyze these user pain points about {competitor} to identify market opportunities for ZenFlo:
            
            {json.dumps(pain_point_posts[:10], indent=2)}
            
            For each significant pain point, determine:
            1. What specific problem are users experiencing?
            2. How widespread does this problem seem? (small/medium/large/massive)
            3. Could ZenFlo solve this better? How?
            4. What would be the business impact of solving this?
            5. How urgent is addressing this opportunity?
            
            Return as JSON array of market opportunities with:
            - opportunity_type: 'user_pain_point'
            - title: Brief description
            - description: Detailed analysis  
            - market_size_indicator: small/medium/large/massive
            - urgency: low/medium/high/critical
            - confidence: 0.0-1.0
            - supporting_evidence: Array of relevant quotes
            - recommended_response: What ZenFlo should do
            """
            
            response = await self._analyze_with_ai(analysis_prompt)
            if not response:
                return []
                
            opportunities_data = json.loads(response.text)
            opportunities = []
            
            for opp_data in opportunities_data:
                opportunity = MarketOpportunity(
                    opportunity_type=opp_data['opportunity_type'],
                    title=opp_data['title'],
                    description=opp_data['description'],
                    market_size_indicator=opp_data['market_size_indicator'],
                    urgency=opp_data['urgency'],
                    confidence=opp_data['confidence'],
                    supporting_evidence=opp_data['supporting_evidence'],
                    recommended_response=opp_data['recommended_response'],
                    timestamp=datetime.now()
                )
                opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to identify pain points for {competitor}: {e}")
            return []

    async def _analyze_with_ai(self, prompt: str) -> Optional[Any]:
        """Generic AI analysis method"""
        try:
            response = await self.gemini_client.generate_content_async(prompt)
            return response
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None

    async def generate_competitive_alerts(self) -> List[CompetitorAlert]:
        """Main method to generate all types of competitive alerts"""
        new_alerts = []
        
        for competitor_name, config in self.competitors.items():
            try:
                logger.info(f"Analyzing {competitor_name}...")
                
                # Monitor sentiment
                sentiment_data = await self.monitor_competitor_sentiment(
                    competitor_name, config.subreddit
                )
                
                # Check for significant sentiment shifts
                if abs(sentiment_data.get('sentiment_change', 0)) > 0.2:
                    severity = 'high' if abs(sentiment_data['sentiment_change']) > 0.4 else 'medium'
                    direction = 'positive' if sentiment_data['sentiment_change'] > 0 else 'negative'
                    
                    alert = CompetitorAlert(
                        competitor=competitor_name,
                        alert_type='sentiment_shift',
                        severity=severity,
                        title=f"{competitor_name} sentiment shift detected",
                        description=f"User sentiment has shifted {direction} by {sentiment_data['sentiment_change']:.2f}",
                        confidence=0.8,
                        timestamp=datetime.now(),
                        data_source=f"r/{config.subreddit}",
                        recommended_action=f"Investigate {direction} sentiment change and adapt strategy"
                    )
                    new_alerts.append(alert)
                
                # Detect feature announcements
                posts = sentiment_data.get('posts', [])
                feature_announcements = await self.detect_feature_announcements(competitor_name, posts)
                
                for announcement in feature_announcements:
                    if announcement.get('is_feature_announcement'):
                        threat_level = announcement.get('threat_level', 'medium')
                        alert = CompetitorAlert(
                            competitor=competitor_name,
                            alert_type='feature_announcement',
                            severity=threat_level,
                            title=f"{competitor_name} feature announcement: {announcement.get('feature_type', 'Unknown')}",
                            description=announcement.get('description', ''),
                            confidence=announcement.get('confidence', 0.7),
                            timestamp=datetime.now(),
                            data_source=f"r/{config.subreddit}",
                            recommended_action=announcement.get('recommended_response', 'Monitor and assess')
                        )
                        new_alerts.append(alert)
                
                # Identify market opportunities
                opportunities = await self.identify_user_pain_points(competitor_name, posts)
                self.opportunities.extend(opportunities)
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to analyze {competitor_name}: {e}")
        
        self.alerts.extend(new_alerts)
        self._save_data()
        
        return new_alerts

    def generate_daily_report(self) -> str:
        """Generate daily competitive intelligence report"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_alerts = [alert for alert in self.alerts 
                       if alert.timestamp.strftime("%Y-%m-%d") == today]
        
        today_opportunities = [opp for opp in self.opportunities 
                             if opp.timestamp.strftime("%Y-%m-%d") == today]
        
        report = f"""
# ZenFlo Competitive Intelligence Daily Report - {today}

## Summary
- **New Alerts**: {len(today_alerts)}
- **New Opportunities**: {len(today_opportunities)}
- **Competitors Monitored**: {len(self.competitors)}

## High Priority Alerts
"""
        
        high_priority_alerts = [alert for alert in today_alerts 
                              if alert.severity in ['high', 'critical']]
        
        if high_priority_alerts:
            for alert in high_priority_alerts:
                report += f"""
### {alert.title}
- **Competitor**: {alert.competitor}
- **Type**: {alert.alert_type}
- **Severity**: {alert.severity}
- **Description**: {alert.description}
- **Recommended Action**: {alert.recommended_action}
"""
        else:
            report += "\nNo high-priority alerts today.\n"
        
        report += "\n## Market Opportunities\n"
        
        high_value_opportunities = [opp for opp in today_opportunities 
                                  if opp.urgency in ['high', 'critical']]
        
        if high_value_opportunities:
            for opp in high_value_opportunities:
                report += f"""
### {opp.title}
- **Type**: {opp.opportunity_type}
- **Market Size**: {opp.market_size_indicator}
- **Urgency**: {opp.urgency}
- **Confidence**: {opp.confidence:.1%}
- **Description**: {opp.description}
- **Recommended Response**: {opp.recommended_response}
"""
        else:
            report += "\nNo high-value opportunities identified today.\n"
        
        report += f"""
## Sentiment Overview
"""
        
        for competitor in self.competitors.keys():
            daily_key = f"{competitor}_{today}"
            sentiment = self.sentiment_history.get(daily_key, 0)
            if sentiment != 0:
                sentiment_emoji = "📈" if sentiment > 0.1 else "📉" if sentiment < -0.1 else "➡️"
                report += f"- **{competitor}**: {sentiment_emoji} {sentiment:.2f}\n"
        
        return report

    def send_alert_email(self, alerts: List[CompetitorAlert], email_to: str):
        """Send email alerts for high-priority issues"""
        try:
            if not alerts:
                return
                
            high_priority = [a for a in alerts if a.severity in ['high', 'critical']]
            if not high_priority:
                return
            
            # Email configuration (you'll need to set these environment variables)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            email_user = os.getenv('EMAIL_USER')
            email_password = os.getenv('EMAIL_PASSWORD')
            
            if not all([email_user, email_password]):
                logger.warning("Email credentials not configured")
                return
            
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_to
            msg['Subject'] = f"ZenFlo Competitive Intelligence Alert - {len(high_priority)} High Priority Items"
            
            body = "High priority competitive intelligence alerts:\n\n"
            for alert in high_priority:
                body += f"""
Alert: {alert.title}
Competitor: {alert.competitor}
Severity: {alert.severity}
Description: {alert.description}
Action: {alert.recommended_action}
Time: {alert.timestamp}

---
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, email_to, text)
            server.quit()
            
            logger.info(f"Alert email sent to {email_to}")
            
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")

    def export_opportunities_csv(self, filepath: str = None):
        """Export identified opportunities to CSV"""
        if not filepath:
            filepath = f"market_opportunities_{datetime.now().strftime('%Y%m%d')}.csv"
        
        opportunities_data = []
        for opp in self.opportunities:
            opportunities_data.append({
                'timestamp': opp.timestamp,
                'opportunity_type': opp.opportunity_type,
                'title': opp.title,
                'description': opp.description,
                'market_size': opp.market_size_indicator,
                'urgency': opp.urgency,
                'confidence': opp.confidence,
                'recommended_response': opp.recommended_response
            })
        
        df = pd.DataFrame(opportunities_data)
        df.to_csv(filepath, index=False)
        logger.info(f"Opportunities exported to {filepath}")

async def main():
    """Main execution function"""
    engine = CompetitiveIntelligenceEngine()
    
    # Generate alerts
    logger.info("Starting competitive intelligence analysis...")
    alerts = await engine.generate_competitive_alerts()
    
    # Generate daily report
    report = engine.generate_daily_report()
    
    # Save report
    report_file = f"daily_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Daily report saved to {report_file}")
    logger.info(f"Generated {len(alerts)} new alerts")
    
    # Export opportunities
    engine.export_opportunities_csv()
    
    # Send email alerts if configured
    email_to = os.getenv('ALERT_EMAIL')
    if email_to:
        engine.send_alert_email(alerts, email_to)

def schedule_monitoring():
    """Set up scheduled monitoring"""
    # Run every 4 hours during business hours
    schedule.every().day.at("09:00").do(asyncio.run, main)
    schedule.every().day.at("13:00").do(asyncio.run, main)
    schedule.every().day.at("17:00").do(asyncio.run, main)
    
    logger.info("Scheduled monitoring set up. Running every 4 hours during business hours.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='ZenFlo Competitive Intelligence Automation')
    parser.add_argument('--mode', choices=['once', 'schedule'], default='once',
                      help='Run once or schedule for continuous monitoring')
    args = parser.parse_args()
    
    if args.mode == 'once':
        asyncio.run(main())
    else:
        schedule_monitoring()