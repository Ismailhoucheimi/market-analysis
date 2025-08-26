# Notion Reddit Analysis - Web Scraping Version

🕷️ **No API credentials required!** This version uses web scraping to analyze r/Notion posts for competitive intelligence.

## Quick Start with uv

### 1. Install uv (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Setup Project
```bash
# Clone/navigate to project directory
cd flo_market_analysis

# Run setup script
./setup.sh
```

### 3. Run Analysis
```bash
# Test scraper
uv run python main_pipeline_scraper.py test

# Quick analysis (50 posts)
uv run python main_pipeline_scraper.py quick

# Full analysis (150+ posts)  
uv run python main_pipeline_scraper.py full

# Launch dashboard
uv run streamlit run dashboard.py
```

## Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment and install dependencies
uv sync

# Create directories
mkdir -p data models reports visualizations

# Test the scraper
uv run python main_pipeline_scraper.py test
```

## Available Commands

```bash
# Test scraper functionality
uv run python main_pipeline_scraper.py test

# Data collection only
uv run python main_pipeline_scraper.py collect

# Classification only
uv run python main_pipeline_scraper.py classify

# Analysis only  
uv run python main_pipeline_scraper.py analyze

# Quick run (25 posts per method)
uv run python main_pipeline_scraper.py quick

# Full comprehensive run (75+ posts per method)
uv run python main_pipeline_scraper.py full

# Minimal test run (10 posts)
uv run python main_pipeline_scraper.py minimal
```

## Web Scraping vs API Comparison

| Feature | Web Scraping | PRAW API |
|---------|-------------|----------|
| **Setup** | ✅ Immediate | ❌ Requires credentials |
| **Rate Limits** | ✅ Higher limits | ❌ 60 requests/min |
| **Reliability** | ⚠️ May break with HTML changes | ✅ Stable |
| **Data Quality** | ✅ Good for public posts | ✅ Comprehensive |
| **Maintenance** | ⚠️ May need updates | ✅ Officially supported |

## How It Works

### 1. Data Collection (`reddit_scraper.py`)
- Uses Reddit's public JSON endpoints (no auth required)
- Fallback to HTML parsing with BeautifulSoup
- Mimics browser headers to avoid blocking
- Rate limiting and random delays

### 2. Text Classification (`text_classifier.py`)  
- Rule-based classification using keyword patterns
- 14 competitive analysis categories
- Processes post titles and content

### 3. Analysis & Visualization (`data_analyzer.py`)
- Comprehensive competitive intelligence reports
- Pain point analysis
- Feature request identification  
- User satisfaction metrics
- Interactive visualizations

### 4. Dashboard (`dashboard.py`)
- Real-time Streamlit interface
- Filter by category, score, date range
- Competitive intelligence summaries
- Exportable insights

## Post Categories Detected

1. **Praise/Positive Feedback** - User satisfaction
2. **Criticism/Complaints** - Pain points
3. **Feature Requests** - Missing capabilities
4. **Help/Support** - User confusion areas
5. **Template Sharing** - Community resources
6. **Integration Requests** - Third-party needs
7. **Bug Reports** - Technical issues
8. **Workflow Showcase** - User creativity
9. **Comparison/Alternatives** - Competitor analysis
10. **Migration Stories** - Switching patterns
11. **Performance Issues** - Speed/reliability
12. **Mobile App Feedback** - Mobile experience
13. **Pricing/Plan Discussion** - Cost sensitivity
14. **Community/Meta** - Community discussions

## Working with uv

```bash
# Activate virtual environment
uv shell

# Run commands in venv
uv run <command>

# Add new dependency
uv add <package-name>

# Add development dependency  
uv add --dev <package-name>

# Update dependencies
uv sync

# Show installed packages
uv pip list
```

## Troubleshooting

### Scraper Issues
```bash
# Test basic connectivity
uv run python -c "import requests; print(requests.get('https://reddit.com/r/test.json').status_code)"

# Test with minimal data
uv run python main_pipeline_scraper.py minimal

# Check for blocking
uv run python reddit_scraper.py
```

### Common Problems

**❌ No posts collected**
- Check internet connection
- Reddit might be temporarily blocking
- Try again later or reduce request frequency

**❌ Import errors**  
- Ensure virtual environment is activated: `uv shell`
- Reinstall dependencies: `uv sync --reinstall`

**❌ Permission denied on setup.sh**
- Make executable: `chmod +x setup.sh`

## Output Files

- `data/raw_posts.csv` - Scraped Reddit data
- `data/processed_posts.csv` - Classified posts  
- `reports/notion_analysis_report_[timestamp].txt` - Text report
- `visualizations/comprehensive_analysis.png` - Charts

## Advantages of This Approach

✅ **No credentials needed** - Works immediately  
✅ **Higher rate limits** - Can collect more data  
✅ **Simple setup** - Just run the script  
✅ **Real-time data** - Always current  
✅ **Transparent** - See exactly what's being collected  

## Ethical Usage

- Respects Reddit's robots.txt
- Uses public endpoints only
- Implements rate limiting
- No authentication bypass
- For research/analysis purposes

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Make changes and test: `uv run python -m pytest`
4. Submit pull request

## License

Educational and competitive analysis use. Respect Reddit's terms of service.