import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from wordcloud import WordCloud
import numpy as np
from collections import Counter
import config
import os

class NotionDataAnalyzer:
    def __init__(self, data_file: str = None):
        self.data_file = data_file or config.PROCESSED_DATA_FILE
        self.df = None
        
        # Create output directories
        os.makedirs('reports', exist_ok=True)
        os.makedirs('visualizations', exist_ok=True)
    
    def load_data(self) -> pd.DataFrame:
        """Load processed data"""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
        
        self.df = pd.read_csv(self.data_file)
        self.df['created_utc'] = pd.to_datetime(self.df['created_utc'])
        self.df['collected_at'] = pd.to_datetime(self.df['collected_at'])
        
        print(f"Loaded {len(self.df)} posts from {self.data_file}")
        return self.df
    
    def generate_summary_report(self) -> dict:
        """Generate comprehensive summary report"""
        if self.df is None:
            self.load_data()
        
        # Basic statistics
        total_posts = len(self.df)
        date_range = (self.df['created_utc'].min(), self.df['created_utc'].max())
        avg_score = self.df['score'].mean()
        avg_comments = self.df['num_comments'].mean()
        
        # Category distribution
        category_dist = self.df['predicted_category'].value_counts()
        category_percentages = (category_dist / total_posts * 100).round(1)
        
        # Top categories by engagement
        engagement_by_category = self.df.groupby('predicted_category').agg({
            'score': 'mean',
            'num_comments': 'mean',
            'upvote_ratio': 'mean'
        }).round(2)
        
        # Temporal analysis
        weekly_posts = self.df.set_index('created_utc').resample('W').size()
        
        # Sentiment analysis by category (if sentiment data exists)
        sentiment_by_category = {}
        if 'sentiment_score' in self.df.columns:
            sentiment_by_category = self.df.groupby('predicted_category')['sentiment_score'].mean().round(3)
        
        report = {
            'summary': {
                'total_posts': total_posts,
                'date_range': date_range,
                'avg_score': round(avg_score, 1),
                'avg_comments': round(avg_comments, 1),
                'collection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'category_distribution': category_dist.to_dict(),
            'category_percentages': category_percentages.to_dict(),
            'engagement_by_category': engagement_by_category.to_dict(),
            'weekly_trends': weekly_posts.to_dict(),
            'sentiment_by_category': sentiment_by_category
        }
        
        return report
    
    def create_visualizations(self):
        """Create comprehensive visualizations"""
        if self.df is None:
            self.load_data()
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Category Distribution (Pie Chart)
        ax1 = plt.subplot(3, 3, 1)
        category_counts = self.df['predicted_category'].value_counts()
        category_labels = [config.POST_CATEGORIES.get(cat, cat) for cat in category_counts.index]
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
        
        wedges, texts, autotexts = ax1.pie(category_counts.values, labels=category_labels, 
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('Post Category Distribution', fontsize=14, fontweight='bold')
        
        # Make labels smaller for readability
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # 2. Posts Over Time
        ax2 = plt.subplot(3, 3, 2)
        daily_posts = self.df.set_index('created_utc').resample('D').size()
        daily_posts.plot(ax=ax2, color='steelblue', linewidth=2)
        ax2.set_title('Posts Over Time', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Number of Posts')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Score Distribution by Category
        ax3 = plt.subplot(3, 3, 3)
        top_categories = self.df['predicted_category'].value_counts().head(6)
        df_top = self.df[self.df['predicted_category'].isin(top_categories.index)]
        
        sns.boxplot(data=df_top, y='predicted_category', x='score', ax=ax3)
        ax3.set_title('Score Distribution by Category', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Score')
        ax3.set_ylabel('Category')
        
        # 4. Comment Count vs Score
        ax4 = plt.subplot(3, 3, 4)
        scatter = ax4.scatter(self.df['score'], self.df['num_comments'], 
                             c=self.df['upvote_ratio'], cmap='viridis', alpha=0.6)
        ax4.set_title('Comments vs Score (colored by upvote ratio)', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Score')
        ax4.set_ylabel('Number of Comments')
        plt.colorbar(scatter, ax=ax4, label='Upvote Ratio')
        
        # 5. Top Authors by Post Count
        ax5 = plt.subplot(3, 3, 5)
        top_authors = self.df['author'].value_counts().head(10)
        top_authors = top_authors[top_authors.index != '[deleted]'][:8]  # Exclude deleted users
        
        bars = ax5.barh(range(len(top_authors)), top_authors.values)
        ax5.set_yticks(range(len(top_authors)))
        ax5.set_yticklabels(top_authors.index)
        ax5.set_title('Top Authors by Post Count', fontsize=14, fontweight='bold')
        ax5.set_xlabel('Number of Posts')
        
        # Color bars
        for i, bar in enumerate(bars):
            bar.set_color(plt.cm.tab10(i))
        
        # 6. Engagement Rate by Category
        ax6 = plt.subplot(3, 3, 6)
        engagement_data = self.df.groupby('predicted_category').agg({
            'score': 'mean',
            'num_comments': 'mean'
        }).reset_index()
        
        x = np.arange(len(engagement_data))
        width = 0.35
        
        bars1 = ax6.bar(x - width/2, engagement_data['score'], width, 
                       label='Avg Score', color='skyblue')
        bars2 = ax6.bar(x + width/2, engagement_data['num_comments'], width,
                       label='Avg Comments', color='lightcoral')
        
        ax6.set_title('Average Engagement by Category', fontsize=14, fontweight='bold')
        ax6.set_xlabel('Category')
        ax6.set_ylabel('Count')
        ax6.set_xticks(x)
        ax6.set_xticklabels([cat[:10] + '...' if len(cat) > 10 else cat 
                            for cat in engagement_data['predicted_category']], rotation=45)
        ax6.legend()
        
        # 7. Upvote Ratio Distribution
        ax7 = plt.subplot(3, 3, 7)
        self.df['upvote_ratio'].hist(bins=20, ax=ax7, color='green', alpha=0.7, edgecolor='black')
        ax7.set_title('Upvote Ratio Distribution', fontsize=14, fontweight='bold')
        ax7.set_xlabel('Upvote Ratio')
        ax7.set_ylabel('Frequency')
        ax7.axvline(self.df['upvote_ratio'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {self.df["upvote_ratio"].mean():.2f}')
        ax7.legend()
        
        # 8. Word Cloud for Most Common Terms
        ax8 = plt.subplot(3, 3, 8)
        
        # Combine all text
        all_text = ' '.join(self.df['title'].fillna('') + ' ' + self.df['selftext'].fillna(''))
        
        # Create word cloud
        wordcloud = WordCloud(width=400, height=300, 
                             background_color='white',
                             max_words=100,
                             colormap='viridis').generate(all_text)
        
        ax8.imshow(wordcloud, interpolation='bilinear')
        ax8.axis('off')
        ax8.set_title('Most Common Terms', fontsize=14, fontweight='bold')
        
        # 9. Category Trends Over Time
        ax9 = plt.subplot(3, 3, 9)
        
        # Get top 4 categories
        top_4_categories = self.df['predicted_category'].value_counts().head(4).index
        
        for category in top_4_categories:
            category_posts = self.df[self.df['predicted_category'] == category]
            daily_category = category_posts.set_index('created_utc').resample('D').size()
            daily_category.rolling(window=3).mean().plot(ax=ax9, 
                                                        label=config.POST_CATEGORIES.get(category, category))
        
        ax9.set_title('Category Trends Over Time (3-day average)', fontsize=14, fontweight='bold')
        ax9.set_xlabel('Date')
        ax9.set_ylabel('Posts per Day')
        ax9.legend()
        ax9.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('visualizations/comprehensive_analysis.png', dpi=300, bbox_inches='tight')
        print("Comprehensive visualization saved to visualizations/comprehensive_analysis.png")
        plt.show()
    
    def generate_competitive_insights(self) -> dict:
        """Generate competitive analysis insights"""
        if self.df is None:
            self.load_data()
        
        # Key insights for competitive analysis
        insights = {}
        
        # 1. Pain Points Analysis (Criticism + Bug Reports)
        pain_points = self.df[self.df['predicted_category'].isin(['criticism', 'bug_report', 'performance'])]
        insights['pain_points'] = {
            'count': len(pain_points),
            'percentage': round(len(pain_points) / len(self.df) * 100, 1),
            'top_issues': pain_points.nlargest(10, 'score')[['title', 'score', 'num_comments']].to_dict('records')
        }
        
        # 2. Feature Requests Analysis
        feature_requests = self.df[self.df['predicted_category'] == 'feature_request']
        insights['feature_requests'] = {
            'count': len(feature_requests),
            'percentage': round(len(feature_requests) / len(self.df) * 100, 1),
            'top_requests': feature_requests.nlargest(10, 'score')[['title', 'score', 'num_comments']].to_dict('records')
        }
        
        # 3. Competitor Mentions
        competitor_posts = self.df[self.df['predicted_category'] == 'comparison']
        insights['competitor_mentions'] = {
            'count': len(competitor_posts),
            'percentage': round(len(competitor_posts) / len(self.df) * 100, 1),
            'top_comparisons': competitor_posts.nlargest(10, 'score')[['title', 'score', 'num_comments']].to_dict('records')
        }
        
        # 4. User Satisfaction (Praise vs Criticism ratio)
        praise_count = len(self.df[self.df['predicted_category'] == 'praise'])
        criticism_count = len(self.df[self.df['predicted_category'] == 'criticism'])
        
        insights['satisfaction_ratio'] = {
            'praise_count': praise_count,
            'criticism_count': criticism_count,
            'ratio': round(praise_count / max(criticism_count, 1), 2),
            'interpretation': 'positive' if praise_count > criticism_count else 'negative'
        }
        
        # 5. Most Engaging Content Types
        engagement_by_category = self.df.groupby('predicted_category').agg({
            'score': 'mean',
            'num_comments': 'mean',
            'upvote_ratio': 'mean'
        }).round(2)
        
        insights['engagement_leaders'] = engagement_by_category.nlargest(5, 'score').to_dict()
        
        return insights
    
    def export_report(self, filename: str = None, generate_html: bool = True):
        """Export comprehensive analysis report"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reports/notion_analysis_report_{timestamp}.txt'
        
        report_data = self.generate_summary_report()
        competitive_insights = self.generate_competitive_insights()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("NOTION REDDIT ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Posts Analyzed: {report_data['summary']['total_posts']}\n")
            f.write(f"Date Range: {report_data['summary']['date_range'][0]} to {report_data['summary']['date_range'][1]}\n")
            f.write(f"Average Score: {report_data['summary']['avg_score']}\n")
            f.write(f"Average Comments: {report_data['summary']['avg_comments']}\n\n")
            
            # Category Distribution
            f.write("CATEGORY DISTRIBUTION\n")
            f.write("-" * 30 + "\n")
            for category, percentage in report_data['category_percentages'].items():
                category_name = config.POST_CATEGORIES.get(category, category)
                count = report_data['category_distribution'][category]
                f.write(f"{category_name}: {count} posts ({percentage}%)\n")
            f.write("\n")
            
            # Competitive Insights
            f.write("COMPETITIVE INSIGHTS\n")
            f.write("-" * 30 + "\n")
            
            # Pain Points
            f.write(f"Pain Points: {competitive_insights['pain_points']['count']} posts ({competitive_insights['pain_points']['percentage']}%)\n")
            f.write("Top Pain Points:\n")
            for issue in competitive_insights['pain_points']['top_issues'][:5]:
                f.write(f"  • {issue['title'][:80]}... (Score: {issue['score']})\n")
            f.write("\n")
            
            # Feature Requests
            f.write(f"Feature Requests: {competitive_insights['feature_requests']['count']} posts ({competitive_insights['feature_requests']['percentage']}%)\n")
            f.write("Top Feature Requests:\n")
            for request in competitive_insights['feature_requests']['top_requests'][:5]:
                f.write(f"  • {request['title'][:80]}... (Score: {request['score']})\n")
            f.write("\n")
            
            # Satisfaction
            f.write("USER SATISFACTION\n")
            f.write("-" * 20 + "\n")
            satisfaction = competitive_insights['satisfaction_ratio']
            f.write(f"Praise Posts: {satisfaction['praise_count']}\n")
            f.write(f"Criticism Posts: {satisfaction['criticism_count']}\n")
            f.write(f"Satisfaction Ratio: {satisfaction['ratio']} ({satisfaction['interpretation']})\n")
            
        print(f"Report exported to: {filename}")
        
        # Generate HTML report if requested
        if generate_html:
            try:
                from html_report_generator import HTMLReportGenerator
                html_generator = HTMLReportGenerator(self.data_file)
                html_file = html_generator.generate_html_report()
                print(f"HTML report generated: {html_file}")
            except Exception as e:
                print(f"Warning: Could not generate HTML report: {e}")

if __name__ == "__main__":
    analyzer = NotionDataAnalyzer()
    
    try:
        analyzer.load_data()
        
        # Generate visualizations
        analyzer.create_visualizations()
        
        # Export report
        analyzer.export_report()
        
        # Print summary
        report = analyzer.generate_summary_report()
        print(f"\nAnalysis Complete!")
        print(f"Total posts analyzed: {report['summary']['total_posts']}")
        print(f"Most common category: {max(report['category_distribution'], key=report['category_distribution'].get)}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run the data collection first using reddit_collector.py")