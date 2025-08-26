import os
from dotenv import load_dotenv

load_dotenv()

# Reddit API Configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'notion_analyzer_v1.0')

# LLM Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
USE_LLM_ANALYSIS = os.getenv('USE_LLM_ANALYSIS', 'true').lower() == 'true'

# Subreddit Configuration
SUBREDDIT_NAME = 'Notion'
MAX_POSTS_PER_BATCH = 100

# Post Categories for Classification
POST_CATEGORIES = {
    'praise': 'Praise/Positive Feedback',
    'criticism': 'Criticism/Complaints',
    'feature_request': 'Feature Requests',
    'help_support': 'Help/Support',
    'template_sharing': 'Template Sharing',
    'integration_request': 'Integration Requests',
    'bug_report': 'Bug Reports',
    'workflow_showcase': 'Workflow Showcase',
    'comparison': 'Comparison/Alternatives',
    'migration': 'Migration Stories',
    'performance': 'Performance Issues',
    'mobile_feedback': 'Mobile App Feedback',
    'pricing': 'Pricing/Plan Discussion',
    'community_meta': 'Community/Meta'
}

# Data Storage Configuration
DATA_DIR = 'data'
RAW_DATA_FILE = f'{DATA_DIR}/reddit_notion_new_20250825_203710.csv'  # Updated to 838 posts
PROCESSED_DATA_FILE = f'{DATA_DIR}/processed_posts_838.csv'