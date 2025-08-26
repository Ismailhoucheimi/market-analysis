#!/bin/bash

# Setup script for Notion Reddit Analysis using uv
set -e

echo "🚀 Setting up Notion Reddit Analysis Tool with uv"
echo "=================================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo "📥 Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "🔗 Or visit: https://github.com/astral-sh/uv"
    exit 1
fi

echo "✅ uv found: $(uv --version)"

# Create virtual environment and install dependencies
echo ""
echo "🏗️ Creating virtual environment and installing dependencies..."
uv sync

echo ""
echo "📁 Creating project directories..."
mkdir -p data models reports visualizations

echo ""
echo "🧪 Testing setup..."

# Test basic imports in the virtual environment
uv run python -c "
import sys
print(f'✅ Python {sys.version.split()[0]}')

try:
    import requests, bs4, pandas, sklearn, matplotlib, seaborn
    print('✅ Core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)

try:
    import fake_useragent, wordcloud, textblob
    print('✅ Scraping dependencies imported successfully') 
except ImportError as e:
    print(f'❌ Scraping dependency error: {e}')
    sys.exit(1)

print('✅ All dependencies working!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "🚀 Quick start commands:"
    echo "  uv run python main_pipeline_scraper.py test     # Test scraper"
    echo "  uv run python main_pipeline_scraper.py quick    # Quick analysis"  
    echo "  uv run python main_pipeline_scraper.py full     # Full analysis"
    echo "  uv run streamlit run dashboard.py               # Launch dashboard"
    echo ""
    echo "💡 Working in virtual environment:"
    echo "  uv shell                    # Activate venv"
    echo "  uv run <command>            # Run in venv"
    echo "  uv add <package>            # Add dependency"
    echo ""
    echo "✨ No API credentials required for web scraping approach!"
else
    echo "❌ Setup failed during dependency testing"
    exit 1
fi