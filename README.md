# Notion Reddit Analysis - Competitive Intelligence Tool

🎯 **Automated system for analyzing r/Notion posts to extract competitive intelligence and user research insights**

## Features

- **Automated Data Collection**: Scrapes r/Notion using Reddit API (PRAW)
- **Smart Categorization**: Classifies posts into 14 competitive analysis categories
- **Comprehensive Analytics**: Generates insights on user sentiment, pain points, and feature requests
- **Interactive Dashboard**: Real-time visualization of trends and competitive intelligence
- **Detailed Reports**: Exportable analysis reports with actionable insights

## Post Categories

The system automatically categorizes posts into:

1. **Praise/Positive Feedback** - Users celebrating features
2. **Criticism/Complaints** - Issues and dissatisfaction 
3. **Feature Requests** - Requests for new capabilities
4. **Help/Support** - Users seeking assistance
5. **Template Sharing** - Template exchanges
6. **Integration Requests** - Third-party app integration needs
7. **Bug Reports** - Technical issues
8. **Workflow Showcase** - User setup demonstrations
9. **Comparison/Alternatives** - Competitor comparisons
10. **Migration Stories** - Platform switching experiences
11. **Performance Issues** - Speed and reliability concerns
12. **Mobile App Feedback** - Mobile-specific feedback
13. **Pricing/Plan Discussion** - Subscription-related discussions
14. **Community/Meta** - Subreddit community content

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Reddit API Configuration
1. Create a Reddit app at https://www.reddit.com/prefs/apps
2. Choose "script" as application type
3. Copy `.env.example` to `.env`
4. Fill in your credentials:
```bash
cp .env.example .env
# Edit .env with your Reddit API credentials
```

### 3. Project Structure
```
flo_market_analysis/
├── config.py              # Configuration settings
├── reddit_collector.py    # Data collection from Reddit
├── text_classifier.py     # Post categorization
├── data_analyzer.py       # Analysis and visualization
├── main_pipeline.py       # Main orchestration script
├── dashboard.py           # Interactive Streamlit dashboard
├── data/                  # Generated data files
├── reports/               # Analysis reports
├── visualizations/        # Generated charts
└── models/                # Saved models
```

## Usage

### Quick Start
```bash
# Run complete analysis pipeline
python main_pipeline.py

# Quick analysis with fewer posts
python main_pipeline.py quick

# Comprehensive analysis
python main_pipeline.py full
```

### Individual Components
```bash
# Collect data only
python main_pipeline.py collect

# Classify existing data
python main_pipeline.py classify

# Analyze processed data
python main_pipeline.py analyze
```

### Interactive Dashboard
```bash
# Launch Streamlit dashboard
streamlit run dashboard.py
```

### Advanced Usage
```python
from main_pipeline import NotionAnalysisPipeline

# Initialize pipeline
pipeline = NotionAnalysisPipeline()

# Custom data collection
df = pipeline.collect_data(['hot', 'top'], limit_per_method=100)

# Classification and analysis
pipeline.classify_data(df)
pipeline.analyze_data()
```

## Output Files

### Data Files
- `data/raw_posts.csv` - Raw collected Reddit posts
- `data/processed_posts.csv` - Classified and processed data

### Reports
- `reports/notion_analysis_report_[timestamp].txt` - Comprehensive text report
- `visualizations/comprehensive_analysis.png` - Multi-chart visualization

### Dashboard
- Interactive web interface with real-time filtering and analysis

## Key Insights Generated

### Competitive Intelligence
- **Pain Points Analysis**: Most common user complaints and issues
- **Feature Gap Identification**: Highly requested missing features  
- **User Satisfaction Metrics**: Praise vs criticism ratios
- **Competitor Mentions**: Comparison discussions and alternatives
- **Migration Patterns**: Users switching to/from Notion

### User Research
- **Engagement Patterns**: Most engaging content types
- **Community Trends**: Popular topics and discussion patterns
- **User Behavior**: How users utilize and discuss Notion
- **Support Needs**: Common help requests and confusion points

### Market Analysis
- **Feature Request Priorities**: What users want most
- **Pricing Sensitivity**: Cost-related discussions
- **Platform Comparisons**: How Notion stacks against competitors
- **Mobile Experience**: Mobile app specific feedback

## Customization

### Adding New Categories
Edit `config.py`:
```python
POST_CATEGORIES = {
    'your_category': 'Your Category Name',
    # ... existing categories
}
```

Update keyword patterns in `text_classifier.py`:
```python
self.keyword_patterns = {
    'your_category': [
        r'\b(keyword1|keyword2)\b',
        r'\b(pattern)\b'
    ]
}
```

### Adjusting Collection Parameters
Modify settings in `config.py`:
```python
SUBREDDIT_NAME = 'Notion'  # Change target subreddit
MAX_POSTS_PER_BATCH = 100  # Adjust batch size
```

## Troubleshooting

### Common Issues

**❌ Reddit API credentials not found**
- Ensure `.env` file exists with correct credentials
- Verify Reddit app is configured as "script" type

**❌ No processed data found**
- Run data collection first: `python main_pipeline.py collect`
- Check that `data/raw_posts.csv` exists

**❌ Rate limiting errors**
- Reddit API allows 60 requests/minute
- Reduce `limit_per_method` in collection parameters
- Add delays between requests if needed

### Data Quality
- Posts are automatically deduplicated by ID
- Deleted posts/comments are handled gracefully
- Text preprocessing removes URLs and special characters

## Dependencies

- `praw>=7.7.1` - Reddit API wrapper
- `pandas>=2.0.0` - Data manipulation
- `scikit-learn>=1.3.0` - Text classification
- `matplotlib>=3.7.0` - Visualization
- `seaborn>=0.12.0` - Statistical visualization
- `wordcloud>=1.9.0` - Word cloud generation
- `textblob>=0.17.0` - Sentiment analysis
- `streamlit` - Dashboard framework
- `plotly` - Interactive visualizations

## License

This project is for educational and competitive analysis purposes. Please respect Reddit's API terms of service and rate limits.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Reddit API documentation
3. Open an issue with detailed error information