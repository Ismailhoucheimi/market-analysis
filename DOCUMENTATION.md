# Notion Reddit Analysis - Complete Documentation

🎯 **Automated competitive intelligence system for analyzing r/Notion subreddit using web scraping and AI-powered analysis.**

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [System Architecture](#system-architecture)
5. [LLM Integration](#llm-integration)
6. [Web Scraping vs API](#web-scraping-vs-api)
7. [Output Formats](#output-formats)
8. [Configuration](#configuration)
9. [Advanced Usage](#advanced-usage)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)

---

## Overview

This system automatically collects posts from r/Notion, categorizes them into competitive intelligence categories, and generates comprehensive reports with actionable insights. It uses web scraping (no API credentials required) and optional LLM analysis for advanced insights.

### 🎯 **Primary Use Cases:**
- **Competitive Intelligence**: Understand user sentiment and pain points
- **Feature Gap Analysis**: Identify most requested features
- **Market Research**: Track user migration patterns and comparisons
- **Product Strategy**: Data-driven insights for roadmap planning

---

## Features

### 🕷️ **Web Scraping Engine**
- **No API Required**: Uses Reddit's public JSON endpoints
- **Rate Limiting**: Built-in delays to avoid blocking
- **Fault Tolerance**: Multiple scraping strategies with fallbacks
- **Real-time Data**: Always current posts and discussions

### 🧠 **AI-Powered Analysis (Optional)**
- **Gemini-2.5-flash Integration**: Advanced sentiment and context analysis  
- **Smart Categorization**: Goes beyond keyword matching
- **User Persona Detection**: Automatically identifies user types
- **Strategic Insights**: Actionable competitive intelligence
- **Business Impact Scoring**: Prioritizes issues by strategic importance

### 📊 **Comprehensive Reporting**
- **Interactive HTML Reports**: Browse posts by category in your browser
- **Traditional Text Reports**: Exportable analysis summaries
- **Visual Charts**: Category distribution, sentiment trends, engagement metrics
- **Live Dashboard**: Streamlit-powered interactive analysis
- **CSV Export**: Raw data for further analysis

### 🏷️ **14 Intelligence Categories**
1. **Praise/Positive Feedback** - User satisfaction indicators
2. **Criticism/Complaints** - Pain points and frustrations
3. **Feature Requests** - Missing capabilities and enhancements
4. **Help/Support** - User confusion and support needs
5. **Template Sharing** - Community resource exchange
6. **Integration Requests** - Third-party connection needs
7. **Bug Reports** - Technical issues and errors
8. **Workflow Showcase** - User creativity and use cases
9. **Comparison/Alternatives** - Competitive landscape insights
10. **Migration Stories** - Platform switching patterns
11. **Performance Issues** - Speed and reliability concerns
12. **Mobile App Feedback** - Mobile experience insights
13. **Pricing/Plan Discussion** - Cost sensitivity analysis
14. **Community/Meta** - Subreddit community dynamics

---

## Quick Start

### 1. **Setup with uv (Recommended)**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone/navigate to project
cd flo_market_analysis

# Setup environment and dependencies
./setup.sh

# Or manual setup:
uv sync --no-install-project
mkdir -p data models reports visualizations
```

### 2. **Basic Usage (No LLM)**
```bash
# Test web scraper
source .venv/bin/activate && python main_pipeline_scraper.py test

# Quick analysis (50 posts)
source .venv/bin/activate && python main_pipeline_scraper.py quick

# Full analysis (150+ posts)
source .venv/bin/activate && python main_pipeline_scraper.py full
```

### 3. **With LLM Analysis (Recommended)**
```bash
# Get Gemini API key from: https://makersuite.google.com/app/apikey
# Add to .env file:
cp .env.example .env
echo "GEMINI_API_KEY=your_api_key_here" >> .env

# Run with AI analysis
source .venv/bin/activate && python main_pipeline_scraper.py quick
```

### 4. **View Results**
```bash
# Launch interactive dashboard
source .venv/bin/activate && streamlit run dashboard.py

# HTML report opens automatically in browser
# Or manually: open reports/html/notion_analysis_[timestamp].html
```

---

## System Architecture

### 📁 **Core Components**

```
flo_market_analysis/
├── main_pipeline_scraper.py    # Main orchestration script
├── reddit_scraper.py          # Web scraping engine  
├── text_classifier.py         # Classification (rule-based + LLM)
├── llm_analyzer.py            # Gemini-2.5-flash integration
├── data_analyzer.py           # Analysis and visualization
├── html_report_generator.py   # Interactive HTML reports
├── dashboard.py               # Streamlit dashboard
├── config.py                  # Configuration settings
├── data/                      # Generated data files
├── reports/                   # Analysis reports
│   ├── html/                  # Interactive HTML reports
│   └── *.txt                  # Text summaries
├── visualizations/            # Charts and graphs
└── models/                    # Saved models (if any)
```

### 🔄 **Data Flow**

```
Reddit r/Notion → Web Scraper → Raw Posts CSV
                                      ↓
Classification Engine ← Rule-Based + LLM Analysis
                                      ↓
Enhanced Posts CSV → Analysis Engine → Reports + Visualizations
                                      ↓
HTML Browser Report + Streamlit Dashboard + Text Summaries
```

### 🕷️ **Web Scraping Strategy**

1. **Primary**: Reddit JSON API (`/r/subreddit/hot/.json`)
   - No authentication required
   - Higher rate limits than official API
   - Real-time public data access

2. **Fallback**: HTML parsing with BeautifulSoup
   - Parses old.reddit.com for stable structure
   - Handles edge cases and blocked requests
   - Multiple selector strategies

3. **Rate Limiting**: 1-3 second delays between requests
4. **User Agent Rotation**: Mimics real browser headers
5. **Error Recovery**: Graceful handling of failed requests

---

## LLM Integration

### 🧠 **Gemini-2.5-flash Analysis**

The system optionally uses Google's Gemini-2.5-flash for advanced analysis that goes far beyond keyword matching.

#### **Enhanced Insights:**
- **Sentiment Score** (-1.0 to 1.0): Emotional tone detection
- **Urgency Level** (1-5): How critical the issue is  
- **Business Impact** (1-5): Potential impact on Notion's business
- **User Persona**: Power user, beginner, team admin, etc.
- **Key Insights**: Strategic bullet points for each post
- **Competitive Intelligence**: Market positioning insights

#### **Expert Prompting:**
The system uses sophisticated prompts that instruct Gemini to analyze posts as a competitive intelligence expert, focusing on:
- User intent beyond surface keywords
- Competitive threats and opportunities  
- Strategic business implications
- User segmentation and personas

#### **Sample LLM Output:**
```json
{
  "post_id": "1mz2z1n",
  "category": "feature_request",
  "sentiment_score": 0.7,
  "urgency_level": 5,
  "business_impact": 5,
  "user_persona": "Power user frustrated with complexity",
  "key_insights": [
    "High-value users want simplified interface modes",
    "Strong demand for view/edit separation",
    "Competitive risk from simpler alternatives"
  ],
  "competitive_intelligence": "Critical retention risk - power users considering migration due to interface complexity"
}
```

#### **Cost & Performance:**
- **Free Tier**: 15 requests/minute, 1M tokens/day
- **Typical Cost**: $0.05-0.10 per 50 posts analyzed
- **Batch Processing**: 5 posts per request for efficiency
- **Rate Limiting**: Respects API quotas automatically
- **Fallback Strategy**: Graceful degradation to rule-based classification

---

## Web Scraping vs API

| Feature | Web Scraping (Default) | PRAW API (Optional) |
|---------|----------------------|-------------------|
| **Setup** | ✅ No credentials needed | ❌ Requires Reddit app registration |
| **Rate Limits** | ✅ Higher limits (~100+ requests/min) | ❌ 60 requests/minute |
| **Data Access** | ✅ Public posts immediately | ✅ Full Reddit data access |
| **Reliability** | ⚠️ May break with Reddit changes | ✅ Officially supported |
| **Maintenance** | ⚠️ Occasional updates needed | ✅ Automatically maintained |
| **Authentication** | ✅ None required | ❌ OAuth setup required |

**Recommendation**: Start with web scraping for immediate results, consider API for production scale.

---

## Output Formats

### 🌐 **Interactive HTML Reports** (Primary)
- **Auto-opens in browser** after analysis
- **Live filtering** by category, sentiment, score
- **Expandable post content** with "Show more" functionality
- **AI insights display** when LLM analysis enabled
- **Mobile responsive** design
- **Direct Reddit links** for source verification

**Features:**
- Real-time search across titles and content
- Sort by score, comments, date, or title
- Category-specific browsing
- Sentiment badges (😊😞😐) when LLM enabled
- Urgency alerts (🚨) for high-priority issues
- Business impact indicators (💼)

### 📊 **Streamlit Dashboard** (Interactive)
```bash
streamlit run dashboard.py
```
- Live data filtering and analysis
- Interactive charts and visualizations  
- Real-time category distribution
- Engagement metrics by category
- Competitive intelligence summaries

### 📈 **Visual Charts** (PNG)
- Category distribution pie charts
- Sentiment trends over time
- Engagement patterns by category
- Word clouds of common terms
- Score vs. comment correlation plots

### 📝 **Text Reports** (TXT)
- Executive summary with key metrics
- Category breakdown with percentages
- Top pain points and feature requests
- User satisfaction analysis
- Competitive threat assessment

### 📊 **CSV Data Export**
- **Raw Posts**: `data/raw_posts.csv`
- **Enhanced Posts**: `data/processed_posts.csv` (includes LLM analysis)
- **Batch Summaries**: `reports/llm_batch_summaries.json` (strategic insights)

---

## Configuration

### 🔧 **Environment Variables (.env)**
```bash
# Optional: Reddit API (only for PRAW approach)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=notion_analyzer_v1.0

# Required for LLM Analysis
GEMINI_API_KEY=your_gemini_api_key

# Optional: Disable LLM analysis
USE_LLM_ANALYSIS=false
```

### ⚙️ **System Settings (config.py)**
```python
# Target subreddit
SUBREDDIT_NAME = 'Notion'

# Collection limits
MAX_POSTS_PER_BATCH = 100

# LLM settings
USE_LLM_ANALYSIS = True  # Enable/disable AI analysis

# Categories mapping
POST_CATEGORIES = {
    'praise': 'Praise/Positive Feedback',
    'criticism': 'Criticism/Complaints',
    # ... 12 more categories
}
```

### 🎛️ **Runtime Parameters**
```bash
# Collection methods and limits
python main_pipeline_scraper.py full    # ['hot', 'new', 'top'] × 75 posts each
python main_pipeline_scraper.py quick   # ['hot', 'new'] × 25 posts each  
python main_pipeline_scraper.py minimal # ['hot'] × 10 posts

# Individual components
python main_pipeline_scraper.py collect   # Data collection only
python main_pipeline_scraper.py classify  # Classification only
python main_pipeline_scraper.py analyze   # Analysis only
```

---

## Advanced Usage

### 🔧 **Custom Analysis**
```python
from llm_analyzer import GeminiPostAnalyzer
import pandas as pd

# Load your data
df = pd.read_csv('your_reddit_data.csv')

# Initialize analyzer
analyzer = GeminiPostAnalyzer()

# Run analysis with custom batch size
enhanced_df = analyzer.analyze_all_posts(df, batch_size=3)

# Generate strategic summary
summary = analyzer.generate_strategic_summary(enhanced_df)
```

### 📊 **Custom Visualizations**
```python
from data_analyzer import NotionDataAnalyzer

analyzer = NotionDataAnalyzer()
analyzer.load_data()

# Create custom visualizations
analyzer.create_visualizations()

# Export custom reports
analyzer.export_report(generate_html=True)
```

### 🎯 **Category Customization**
Edit `config.py` to add/modify categories:
```python
POST_CATEGORIES = {
    'your_category': 'Your Category Name',
    # existing categories...
}
```

Update keyword patterns in `text_classifier.py`:
```python
self.keyword_patterns = {
    'your_category': [
        r'\b(keyword1|keyword2)\b',
        r'\b(your_pattern)\b'
    ]
}
```

### 🚀 **Scaling for Production**

#### **High-Volume Collection**
```python
# Collect large datasets
pipeline = NotionScrapingPipeline()
pipeline.run_full_pipeline(['hot', 'new', 'top', 'rising'], 200)
```

#### **Scheduled Analysis**
```bash
# Cron job example - daily analysis
0 9 * * * cd /path/to/project && source .venv/bin/activate && python main_pipeline_scraper.py quick
```

#### **API Cost Management**
```python
# Monitor LLM costs
analyzer = GeminiPostAnalyzer()
estimated_tokens = analyzer.count_tokens(prompt)
estimated_cost = (estimated_tokens / 1000) * 0.075  # Input cost per 1K tokens
```

---

## Troubleshooting

### 🐛 **Common Issues**

#### **Web Scraping Failures**
```bash
# Test connectivity
python -c "import requests; print(requests.get('https://reddit.com/r/test.json').status_code)"

# Should return: 200

# If blocked, try:
python main_pipeline_scraper.py minimal  # Fewer requests
```

#### **LLM Analysis Issues**
```bash
# Test API key
python llm_analyzer.py

# Common errors:
# - Invalid API key: Check .env file
# - Rate limiting: Reduce batch_size in llm_analyzer.py
# - Token limits: Monitor daily usage on Google AI Studio
```

#### **Empty Results**
```bash
# Debug collection
python reddit_scraper.py  # Test scraper directly

# Check:
# - Internet connection
# - Reddit accessibility
# - Rate limiting (try again later)
```

#### **HTML Report Issues**
```bash
# Test HTML generation
python html_report_generator.py

# Common issues:
# - Missing processed data: Run pipeline first
# - Browser doesn't open: Check file permissions
# - Styling issues: Clear browser cache
```

### 🔧 **Performance Optimization**

#### **Speed Up Collection**
- Reduce `limit_per_method` in pipeline calls
- Use `minimal` or `quick` commands for testing
- Run `collect` → `classify` → `analyze` separately for debugging

#### **Reduce LLM Costs**
- Set `USE_LLM_ANALYSIS=false` in .env for rule-based only
- Reduce `batch_size` in `llm_analyzer.py` 
- Filter posts by score/comments before LLM analysis

#### **Memory Optimization**
- Process data in chunks for large datasets
- Clear intermediate data files between runs
- Use `batch_size=1` for memory-constrained environments

### 🆘 **Error Recovery**

#### **Partial Failures**
The system is designed for graceful degradation:
- LLM analysis fails → Falls back to rule-based classification
- Web scraping fails → Retries with different methods  
- HTML generation fails → Text reports still generated
- Visualization fails → Analysis continues without charts

#### **Data Corruption**
```bash
# Reset and restart
rm -rf data/processed_posts.csv
python main_pipeline_scraper.py collect  # Re-collect
python main_pipeline_scraper.py classify # Re-classify
```

---

## Contributing

### 🤝 **Development Setup**
```bash
git clone https://github.com/your-repo/notion-reddit-analysis
cd notion-reddit-analysis
uv sync --dev  # Install dev dependencies
```

### 📋 **Code Style**
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings for public functions
- Keep functions under 50 lines when possible

### 🧪 **Testing**
```bash
# Test individual components
python reddit_scraper.py      # Test scraping
python text_classifier.py     # Test classification
python llm_analyzer.py        # Test LLM integration
python html_report_generator.py # Test HTML generation
```

### 📝 **Documentation**
- Update this file for new features
- Add docstrings for new functions
- Include usage examples for new capabilities
- Update README files for user-facing changes

### 🔀 **Pull Request Process**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Update documentation
5. Submit pull request with clear description

---

## 📄 License

This project is for educational and competitive analysis purposes. Please respect Reddit's terms of service and rate limits.

## 🙏 Acknowledgments

- **Google Gemini** for advanced AI analysis capabilities
- **Reddit** for providing public data access
- **uv** for fast Python package management
- **Streamlit** for interactive dashboards
- **BeautifulSoup** for reliable HTML parsing

---

## 📞 Support

For issues and questions:
1. Check this documentation
2. Review the troubleshooting section  
3. Test individual components
4. Open an issue with detailed error information

**Happy analyzing!** 🎯