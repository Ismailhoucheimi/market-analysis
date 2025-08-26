# 🚀 Streamlit Dashboard Deployment Guide

## Local Development
```bash
# Install dependencies
uv pip install -r requirements.txt

# Run the dashboard
streamlit run streamlit_app.py
```

## Streamlit Cloud Deployment
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `streamlit_app.py` as your main file
5. Add your environment variables (GEMINI_API_KEY) in secrets

## Features
- 📊 **Interactive Analytics**: Real-time charts and metrics
- 🔍 **Advanced Filtering**: Date range, category, score, and text search
- 💬 **Posts Explorer**: Paginated browsing with detailed post cards
- 📋 **Strategic Report**: Comprehensive analysis insights
- 🤖 **AI Insights**: LLM-powered theme analysis and recommendations

## Advantages over Static HTML
- ✅ **Real-time filtering** without page reloads
- ✅ **Interactive charts** with zoom, pan, hover details
- ✅ **Dynamic search** across titles and content
- ✅ **Responsive pagination** for large datasets
- ✅ **Easy sharing** via Streamlit Cloud URL
- ✅ **70% less code** compared to custom HTML/JS
