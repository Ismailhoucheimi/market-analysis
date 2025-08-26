# Competitive Intelligence Automation Setup Guide

## Overview

The ZenFlo Competitive Intelligence Automation System provides real-time monitoring of competitor activities, user sentiment analysis, and market opportunity identification. It runs continuously in the background and generates daily reports with actionable insights.

## Features

### 🚨 Automated Alerts
- **Sentiment Shifts**: Detects significant changes in user sentiment towards competitors
- **Feature Announcements**: Identifies new competitor feature releases using AI analysis
- **User Exodus**: Monitors for increased user complaints and switching intent
- **Market Opportunities**: Identifies pain points that ZenFlo can address

### 📊 Daily Intelligence Reports
- Competitive sentiment overview
- High-priority alerts requiring immediate attention
- Market opportunities with business impact assessment
- Recommended strategic responses

### 📧 Smart Notifications
- Email alerts for critical competitive threats
- Slack integration for team notifications
- Customizable alert thresholds and channels

## Installation & Setup

### 1. Install Dependencies

```bash
pip install praw textblob pandas google-generativeai schedule
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Reddit API (Create app at https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Gemini API (Get from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key

# Email Alerts (Optional)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
ALERT_EMAIL=team@zenflo.ai

# Slack Integration (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### 3. API Setup Instructions

#### Reddit API Setup
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App"
3. Choose "script" type
4. Copy Client ID and Secret to `.env`

#### Gemini API Setup
1. Visit Google AI Studio: https://aistudio.google.com/
2. Create API key
3. Add to `.env` file

#### Email Setup (Gmail)
1. Enable 2-factor authentication on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password (not regular password) in `.env`

### 4. Directory Structure

```
flo_market_analysis/
├── competitive_intelligence_automation.py
├── competitors_config.py
├── automation_data/
│   ├── sentiment_history.json
│   ├── alerts_history.json
│   └── daily_reports/
├── .env
└── requirements.txt
```

## Usage

### Run Once (Manual Analysis)

```bash
python competitive_intelligence_automation.py --mode once
```

### Continuous Monitoring

```bash
python competitive_intelligence_automation.py --mode schedule
```

This will run automatically every 4 hours during business hours (9 AM, 1 PM, 5 PM).

### Docker Deployment (Recommended for Production)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "competitive_intelligence_automation.py", "--mode", "schedule"]
```

Deploy with:
```bash
docker build -t zenflo-ci-automation .
docker run -d --env-file .env --name zenflo-ci zenflo-ci-automation
```

## Output Files

### Daily Reports
- `daily_report_YYYYMMDD.md` - Comprehensive daily intelligence report
- `market_opportunities_YYYYMMDD.csv` - Exportable opportunities data

### Data Storage
- `automation_data/sentiment_history.json` - Historical sentiment tracking
- `automation_data/alerts_history.json` - All generated alerts
- `automation_data/opportunities_history.json` - Identified market opportunities

## Alert Types & Severity Levels

### Alert Types
1. **sentiment_shift** - Significant change in user sentiment
2. **feature_announcement** - New competitor feature releases
3. **user_exodus** - Increased user complaints/switching intent
4. **pricing_change** - Competitor pricing strategy changes

### Severity Levels
- **critical** - Immediate action required (< 24 hours)
- **high** - Action needed within 1 week
- **medium** - Monitor and plan response (1-2 weeks)
- **low** - Track for trends (1 month)

## Customization

### Adding New Competitors

Edit `competitors_config.py`:

```python
def get_competitor_configs():
    configs = {
        # ... existing competitors
        "newcompetitor": CompetitorConfig(
            name="newcompetitor",
            display_name="New Competitor",
            subreddit="newcompetitorsubreddit",
            color_scheme={"primary": "#FF6B6B", "secondary": "#4ECDC4"},
            data_dir="competitors/newcompetitor",
            categories={
                "strengths": "What users love",
                "weaknesses": "Common complaints", 
                "opportunities": "Market gaps"
            },
            logo_emoji="🆕",
            description="Brief description"
        )
    }
    return configs
```

### Custom Alert Thresholds

Modify thresholds in `competitive_intelligence_automation.py`:

```python
# Sentiment shift threshold (default: 0.2)
if abs(sentiment_data.get('sentiment_change', 0)) > 0.3:  # More sensitive

# Feature announcement confidence (default: 0.7)
if announcement.get('confidence', 0.7) > 0.8:  # Higher confidence required
```

### Notification Channels

Add Slack integration:

```python
import requests

def send_slack_alert(alert, webhook_url):
    message = {
        "text": f"🚨 *{alert.title}*",
        "attachments": [{
            "color": "danger" if alert.severity == "critical" else "warning",
            "fields": [
                {"title": "Competitor", "value": alert.competitor, "short": True},
                {"title": "Severity", "value": alert.severity, "short": True},
                {"title": "Description", "value": alert.description},
                {"title": "Action", "value": alert.recommended_action}
            ]
        }]
    }
    requests.post(webhook_url, json=message)
```

## Monitoring & Maintenance

### Health Checks
The system logs all activities. Monitor logs for:
- API rate limit issues
- Failed sentiment analysis
- Missing competitor data
- Email delivery failures

### Data Retention
- Sentiment data: Kept indefinitely for trend analysis
- Alerts: Archived after 90 days
- Opportunities: Kept until resolved/dismissed

### Performance Optimization
- **Rate Limiting**: Automatically handles Reddit API limits
- **Caching**: Sentiment analysis results cached for 1 hour
- **Batching**: AI analysis runs in batches for efficiency

## Integration with ZenFlo Dashboard

Add automation insights to your Streamlit dashboard:

```python
import json
from datetime import datetime

def render_automation_insights():
    st.header("🤖 Automated Intelligence")
    
    # Load recent alerts
    with open('automation_data/alerts_history.json', 'r') as f:
        alerts = json.load(f)
    
    recent_alerts = [a for a in alerts 
                    if datetime.fromisoformat(a['timestamp']).date() == datetime.now().date()]
    
    if recent_alerts:
        st.subheader(f"Today's Alerts ({len(recent_alerts)})")
        for alert in recent_alerts[-5:]:  # Show latest 5
            severity_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟢", "low": "⚪"}
            st.write(f"{severity_emoji[alert['severity']]} **{alert['title']}**")
            st.write(f"_{alert['description']}_")
            st.write(f"**Action**: {alert['recommended_action']}")
            st.divider()
```

## Troubleshooting

### Common Issues

1. **Reddit API 403 Errors**
   - Check API credentials in `.env`
   - Verify rate limiting delays
   - Ensure User-Agent is set correctly

2. **Gemini API Quota Exceeded**
   - Monitor usage at Google AI Studio
   - Implement exponential backoff
   - Consider upgrading to paid tier

3. **Email Alerts Not Sending**
   - Verify Gmail App Password (not regular password)
   - Check firewall/network restrictions
   - Test SMTP connection manually

4. **Missing Historical Data**
   - Ensure `automation_data/` directory exists
   - Check file permissions
   - Initialize with empty JSON if needed

### Performance Tuning

For high-volume monitoring:

```python
# Reduce AI analysis frequency
ANALYSIS_INTERVAL_HOURS = 8  # Instead of 4

# Batch process posts
BATCH_SIZE = 20  # Process 20 posts at once

# Cache sentiment analysis
SENTIMENT_CACHE_HOURS = 2
```

## Best Practices

1. **Start Small**: Begin with 2-3 competitors, expand gradually
2. **Monitor Costs**: Track AI API usage to manage expenses
3. **Regular Reviews**: Weekly review of alert accuracy and relevance
4. **Team Training**: Ensure team knows how to interpret and act on alerts
5. **Data Backup**: Regular backups of automation_data/ directory

The system is designed to run autonomously but benefits from periodic human oversight to ensure accuracy and relevance of insights generated.