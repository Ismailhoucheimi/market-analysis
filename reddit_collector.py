import praw
import pandas as pd
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
import config

class RedditCollector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT
        )
        
        # Ensure data directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)
    
    def collect_posts(self, sort_method='hot', time_filter='week', limit=100) -> List[Dict[str, Any]]:
        """
        Collect posts from r/Notion subreddit
        
        Args:
            sort_method: 'hot', 'new', 'top', 'rising'
            time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
            limit: Maximum number of posts to collect
        """
        subreddit = self.reddit.subreddit(config.SUBREDDIT_NAME)
        posts_data = []
        
        # Select sorting method
        if sort_method == 'hot':
            posts = subreddit.hot(limit=limit)
        elif sort_method == 'new':
            posts = subreddit.new(limit=limit)
        elif sort_method == 'top':
            posts = subreddit.top(time_filter=time_filter, limit=limit)
        elif sort_method == 'rising':
            posts = subreddit.rising(limit=limit)
        else:
            raise ValueError(f"Invalid sort method: {sort_method}")
        
        print(f"Collecting posts from r/{config.SUBREDDIT_NAME}...")
        
        for post in posts:
            try:
                # Get post creation date
                created_utc = datetime.fromtimestamp(post.created_utc, timezone.utc)
                
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'selftext': post.selftext,
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'created_utc': created_utc,
                    'author': str(post.author) if post.author else '[deleted]',
                    'url': post.url,
                    'permalink': f"https://reddit.com{post.permalink}",
                    'flair_text': post.link_flair_text,
                    'is_self': post.is_self,
                    'collected_at': datetime.now(timezone.utc)
                }
                
                posts_data.append(post_data)
                
            except Exception as e:
                print(f"Error processing post {post.id}: {e}")
                continue
        
        print(f"Collected {len(posts_data)} posts")
        return posts_data
    
    def collect_comments(self, post_id: str, max_comments: int = 50) -> List[Dict[str, Any]]:
        """Collect comments for a specific post"""
        submission = self.reddit.submission(id=post_id)
        submission.comments.replace_more(limit=0)  # Remove "more comments" objects
        
        comments_data = []
        
        for comment in submission.comments.list()[:max_comments]:
            try:
                comment_data = {
                    'post_id': post_id,
                    'comment_id': comment.id,
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': datetime.fromtimestamp(comment.created_utc, timezone.utc),
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'parent_id': comment.parent_id
                }
                comments_data.append(comment_data)
            except Exception as e:
                print(f"Error processing comment {comment.id}: {e}")
                continue
        
        return comments_data
    
    def save_to_csv(self, posts_data: List[Dict[str, Any]], filename: str = None):
        """Save collected posts to CSV file"""
        if not filename:
            filename = config.RAW_DATA_FILE
        
        df = pd.DataFrame(posts_data)
        
        # If file exists, append new data
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)
            # Remove duplicates based on post ID
            combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['id'], keep='last')
        else:
            combined_df = df
        
        combined_df.to_csv(filename, index=False)
        print(f"Saved {len(combined_df)} posts to {filename}")
        return combined_df
    
    def collect_and_save(self, sort_methods=['hot', 'new'], limit_per_method=50):
        """Collect posts using multiple sorting methods and save to CSV"""
        all_posts = []
        
        for method in sort_methods:
            print(f"\nCollecting {method} posts...")
            posts = self.collect_posts(sort_method=method, limit=limit_per_method)
            all_posts.extend(posts)
        
        # Remove duplicates
        unique_posts = {post['id']: post for post in all_posts}.values()
        
        return self.save_to_csv(list(unique_posts))

if __name__ == "__main__":
    collector = RedditCollector()
    
    # Collect posts from multiple sources
    df = collector.collect_and_save(
        sort_methods=['hot', 'new', 'top'],
        limit_per_method=50
    )
    
    print(f"\nCollection complete! Total unique posts: {len(df)}")
    print(f"Data saved to: {config.RAW_DATA_FILE}")