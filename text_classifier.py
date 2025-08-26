import pandas as pd
import re
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import config

class NotionPostClassifier:
    def __init__(self):
        self.pipeline = None
        self.categories = list(config.POST_CATEGORIES.keys())
        
        # Define keyword patterns for rule-based classification
        self.keyword_patterns = {
            'praise': [
                r'\b(love|amazing|great|awesome|perfect|excellent|fantastic|wonderful)\b',
                r'\b(thank you|thanks|grateful|impressed|blown away)\b',
                r'\b(game changer|life saver|best.*ever)\b'
            ],
            'criticism': [
                r'\b(hate|terrible|awful|worst|horrible|disappointed|frustrated)\b',
                r'\b(broken|doesn\'t work|not working|failed|crash|bug)\b',
                r'\b(slow|laggy|freezes|unresponsive)\b'
            ],
            'feature_request': [
                r'\b(request|need|want|wish|hope|please add|would be great)\b',
                r'\b(feature request|enhancement|suggestion|idea)\b',
                r'\b(missing|lack|should have|could use)\b'
            ],
            'help_support': [
                r'\b(help|how to|how do|can someone|anyone know|stuck)\b',
                r'\b(question|problem|issue|trouble|confused)\b',
                r'\b(tutorial|guide|walkthrough)\b'
            ],
            'template_sharing': [
                r'\b(template|share|sharing|created|made)\b',
                r'\b(dashboard|system|setup|workflow)\b',
                r'\b(free template|template for)\b'
            ],
            'integration_request': [
                r'\b(integration|integrate|connect|sync|api)\b',
                r'\b(google|slack|trello|asana|zapier|calendly)\b',
                r'\b(third party|external)\b'
            ],
            'bug_report': [
                r'\b(bug|error|glitch|crash|freeze|broken)\b',
                r'\b(not working|doesn\'t work|stopped working)\b',
                r'\b(sync.*issue|lost.*data)\b'
            ],
            'workflow_showcase': [
                r'\b(setup|workflow|system|organization)\b',
                r'\b(how I|my setup|my system|my workflow)\b',
                r'\b(productivity|organized|managing)\b'
            ],
            'comparison': [
                r'\b(vs|versus|compared to|alternative|instead of)\b',
                r'\b(obsidian|roam|onenote|evernote|airtable|coda)\b',
                r'\b(better than|worse than|similar to)\b'
            ],
            'migration': [
                r'\b(migrate|migration|switch|switching|move|moving)\b',
                r'\b(from.*to|import|export|transfer)\b',
                r'\b(leaving|goodbye|hello)\b'
            ],
            'performance': [
                r'\b(slow|fast|speed|performance|lag|loading)\b',
                r'\b(takes forever|too slow|quick|responsive)\b'
            ],
            'mobile_feedback': [
                r'\b(mobile|phone|ios|android|app)\b',
                r'\b(mobile.*app|phone.*app)\b'
            ],
            'pricing': [
                r'\b(price|pricing|cost|expensive|cheap|free|paid|subscription)\b',
                r'\b(plan|tier|upgrade|downgrade)\b',
                r'\b(worth it|too expensive|affordable)\b'
            ],
            'community_meta': [
                r'\b(subreddit|community|meta|poll|discussion)\b',
                r'\b(weekly|daily|thread|announcement)\b'
            ]
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for classification"""
        if pd.isna(text):
            return ""
        
        text = str(text).lower()
        text = re.sub(r'http\S+|www.\S+', '', text)  # Remove URLs
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove special characters
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        return text.strip()
    
    def rule_based_classify(self, text: str) -> str:
        """Classify text using keyword patterns"""
        text = self.preprocess_text(text)
        scores = {}
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            scores[category] = score
        
        # Return category with highest score, or 'help_support' as default
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return 'help_support'  # Default category
    
    def classify_posts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify posts using LLM analysis if available, fallback to rule-based"""
        df_classified = df.copy()
        
        # Combine title and text for classification
        df_classified['combined_text'] = df_classified['title'].fillna('') + ' ' + df_classified['selftext'].fillna('')
        
        # Try LLM analysis first if enabled and API key available
        if config.USE_LLM_ANALYSIS and config.GEMINI_API_KEY:
            try:
                print("🧠 Using LLM-powered classification with Gemini-2.5-flash...")
                from llm_analyzer import GeminiPostAnalyzer
                
                analyzer = GeminiPostAnalyzer()
                df_classified = analyzer.analyze_all_posts(df_classified)
                
                print(f"✅ LLM analysis completed for {len(df_classified)} posts")
                return df_classified
                
            except Exception as e:
                print(f"⚠️ LLM analysis failed: {e}")
                print("Falling back to rule-based classification...")
        
        # Fallback to rule-based classification
        print("🔍 Using rule-based classification...")
        df_classified['predicted_category'] = df_classified['combined_text'].apply(self.rule_based_classify)
        df_classified['category_label'] = df_classified['predicted_category'].map(config.POST_CATEGORIES)
        
        return df_classified
    
    def get_classification_stats(self, df: pd.DataFrame) -> Dict:
        """Get statistics about classification results"""
        stats = {
            'total_posts': len(df),
            'category_distribution': df['predicted_category'].value_counts().to_dict(),
            'category_percentages': (df['predicted_category'].value_counts() / len(df) * 100).to_dict()
        }
        return stats
    
    def analyze_sentiment_by_category(self, df: pd.DataFrame) -> Dict:
        """Analyze sentiment patterns by category"""
        from textblob import TextBlob
        
        sentiment_analysis = {}
        
        for category in df['predicted_category'].unique():
            category_posts = df[df['predicted_category'] == category]
            
            sentiments = []
            for text in category_posts['combined_text']:
                blob = TextBlob(text)
                sentiments.append(blob.sentiment.polarity)
            
            sentiment_analysis[category] = {
                'avg_sentiment': sum(sentiments) / len(sentiments) if sentiments else 0,
                'post_count': len(category_posts),
                'avg_score': category_posts['score'].mean(),
                'avg_comments': category_posts['num_comments'].mean()
            }
        
        return sentiment_analysis
    
    def save_model(self, filepath: str = 'models/classifier.pkl'):
        """Save the trained model"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'keyword_patterns': self.keyword_patterns,
                'categories': self.categories
            }, f)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str = 'models/classifier.pkl'):
        """Load a trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
            self.keyword_patterns = model_data['keyword_patterns']
            self.categories = model_data['categories']
        print(f"Model loaded from {filepath}")

def main():
    """Test the classifier with sample data"""
    # Create sample test cases
    test_data = [
        {"title": "Notion is amazing for project management", "selftext": "I love how organized everything is"},
        {"title": "How do I create a database?", "selftext": "I'm new to Notion and need help"},
        {"title": "Feature request: Dark mode for mobile", "selftext": "Please add dark mode to the mobile app"},
        {"title": "Notion vs Obsidian comparison", "selftext": "Which one is better for note-taking?"},
        {"title": "Bug: Pages won't sync", "selftext": "My pages are not syncing across devices"},
        {"title": "Free template for students", "selftext": "I created this dashboard for managing classes"}
    ]
    
    df = pd.DataFrame(test_data)
    
    classifier = NotionPostClassifier()
    df_classified = classifier.classify_posts(df)
    
    print("Classification Results:")
    for idx, row in df_classified.iterrows():
        print(f"Title: {row['title'][:50]}...")
        print(f"Category: {row['category_label']}")
        print("-" * 50)
    
    stats = classifier.get_classification_stats(df_classified)
    print(f"\nClassification Statistics:")
    for category, count in stats['category_distribution'].items():
        percentage = stats['category_percentages'][category]
        print(f"{config.POST_CATEGORIES[category]}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()