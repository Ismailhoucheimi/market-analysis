# LLM-Powered Notion Reddit Analysis with Gemini-2.5-flash

🧠 **Advanced AI analysis using Google's Gemini-2.5-flash for deep competitive intelligence beyond keyword matching.**

## ✨ New LLM Features

### 🎯 Advanced Analysis
- **Sentiment Analysis** (-1.0 to 1.0) - Emotional tone detection
- **Urgency Scoring** (1-5) - How critical the issue is
- **Business Impact** (1-5) - Potential impact on Notion's business
- **User Persona Detection** - Power user, beginner, team admin, etc.
- **Key Insights Extraction** - Strategic bullet points
- **Competitive Intelligence** - Market positioning insights

### 📊 Enhanced Categorization
- Goes beyond keyword matching
- Understands context and nuance  
- Identifies subtle competitive threats
- Detects feature gaps and opportunities

## 🚀 Quick Setup

### 1. Get Gemini API Key
```bash
# Visit: https://makersuite.google.com/app/apikey
# Create a new API key (free tier available)
```

### 2. Configure Environment
```bash
# Copy and edit .env file
cp .env.example .env

# Add your Gemini API key to .env:
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Install Dependencies
```bash
# Install with uv (includes Gemini dependencies)
uv sync --no-install-project
```

### 4. Run LLM Analysis
```bash
# Test LLM analyzer
python llm_analyzer.py

# Run full pipeline with LLM analysis
python main_pipeline_scraper.py quick
```

## 🧠 How It Works

### Intelligent Prompting
The system sends batches of posts to Gemini-2.5-flash with expert prompts that analyze:

1. **Context Understanding**: Goes beyond keywords to understand user intent
2. **Competitive Positioning**: Identifies threats and opportunities
3. **User Segmentation**: Detects different user types and their needs  
4. **Strategic Insights**: Extracts actionable business intelligence

### Batch Processing
- Processes posts in batches of 5 for optimal performance
- Rate limiting to respect API quotas (60 requests/minute)
- Fallback to rule-based classification if LLM fails
- Token counting for cost estimation

### Rich Output
Each post gets enhanced with:
```json
{
  "sentiment_score": 0.7,
  "urgency_level": 4,
  "business_impact": 5,
  "user_persona": "Power user frustrated with complexity",
  "key_insights": [
    "User wants simplified interface",
    "Complexity is driving users to competitors"
  ],
  "competitive_intelligence": "Risk of user churn to simpler tools"
}
```

## 📊 Enhanced Reports

### HTML Reports with AI Insights
- **Sentiment badges** (😊 positive, 😞 negative, 😐 neutral)
- **Urgency alerts** (🚨 high priority issues)
- **Business impact indicators** (💼 strategic importance)
- **AI Analysis sections** with persona and insights

### Strategic Summaries
- Overall sentiment trends
- High-urgency issue identification
- User persona distribution
- Competitive threat analysis

## 🎯 Sample Analysis Output

```
📝 "Notion really needs a User Mode"
   Category: Feature Requests
   Sentiment: 0.8 😊
   Urgency: 5/5 🚨
   Business Impact: 5/5 💼
   User Persona: Power user seeking simplification
   Key Insights: High-value users frustrated with complexity; 
                 Strong demand for view/edit mode separation;
                 Competitive risk from simpler alternatives
```

## 💰 Cost Estimation

### Gemini-2.5-flash Pricing
- **Free Tier**: 15 requests/minute, 1 million tokens/day
- **Paid Tier**: $0.075 per 1K input tokens, $0.30 per 1K output tokens

### Typical Usage
- **50 posts**: ~$0.05-0.10 per analysis
- **500 posts**: ~$0.50-1.00 per analysis
- Most analyses fit within free tier limits

## 🛠️ Configuration Options

### Environment Variables
```bash
# Required for LLM analysis
GEMINI_API_KEY=your_api_key_here

# Optional: Disable LLM analysis (uses rule-based fallback)
USE_LLM_ANALYSIS=false
```

### Batch Size Tuning
```python
# In llm_analyzer.py - adjust for your API limits
analyzer.analyze_all_posts(df, batch_size=3)  # Smaller batches
```

## 🔍 Troubleshooting

### API Key Issues
```bash
# Test API key
python llm_analyzer.py
```

### Rate Limiting
- System includes automatic rate limiting (60 requests/minute)
- Reduce batch size if hitting limits
- Free tier has daily token limits

### Fallback Behavior
- If LLM analysis fails, automatically falls back to rule-based classification
- Graceful degradation ensures pipeline never fails completely

## 📈 Advanced Usage

### Custom Analysis Prompts
Modify `create_analysis_prompt()` in `llm_analyzer.py` to customize:
- Industry-specific insights
- Different competitive frameworks
- Custom user personas
- Specialized scoring criteria

### Batch Summary Analysis
```python
# Access strategic summaries
summaries = analyzer.save_batch_summaries(batch_summaries)
# Contains: dominant themes, sentiment trends, competitive threats
```

### Integration with Existing Tools
- Works seamlessly with existing pipeline
- Enhanced HTML reports include all AI insights
- Streamlit dashboard shows LLM analysis
- CSV exports include all new columns

## 🎯 Best Practices

1. **Start Small**: Test with small batches first
2. **Monitor Costs**: Use token counting for budget control
3. **Review Results**: Validate LLM analysis quality
4. **Iterate Prompts**: Refine prompts for your specific needs
5. **Backup Strategy**: Always have rule-based fallback enabled

## 🚀 Next Steps

1. **Get API Key**: Visit https://makersuite.google.com/app/apikey
2. **Run Test**: `python llm_analyzer.py` 
3. **Analyze Posts**: `python main_pipeline_scraper.py quick`
4. **View Results**: Open HTML report to see AI insights
5. **Scale Up**: Run full analysis with larger datasets

The LLM integration transforms simple post categorization into strategic competitive intelligence! 🎉