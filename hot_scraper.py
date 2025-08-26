#!/usr/bin/env python3
"""
Specialized scraper for HOT posts with anti-blocking measures
"""

import requests
import time
import random
import pandas as pd
from datetime import datetime
from fake_useragent import UserAgent

class HotPostsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.posts_data = []
        
    def get_headers(self):
        """Get randomized headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def random_delay(self, min_delay=2, max_delay=6):
        """Random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        print(f"  Waiting {delay:.1f}s...")
        time.sleep(delay)
    
    def scrape_hot_posts_batch(self, after=None, limit=25):
        """Scrape a batch of hot posts"""
        url = "https://www.reddit.com/r/Notion/hot/.json"
        
        params = {
            'limit': limit,
            'raw_json': 1
        }
        
        if after:
            params['after'] = after
        
        try:
            response = self.session.get(
                url, 
                params=params, 
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 403:
                print(f"  ❌ Blocked (403) - trying with longer delay...")
                self.random_delay(10, 20)  # Longer delay if blocked
                return None, None
            
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                posts = data['data']['children']
                batch_posts = []
                
                for post in posts:
                    if post['kind'] == 't3':  # Post type
                        post_data = self.extract_post_data(post['data'])
                        if post_data:
                            batch_posts.append(post_data)
                
                # Get pagination token
                next_after = data['data'].get('after')
                
                return batch_posts, next_after
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error: {e}")
            return None, None
        
        return [], None
    
    def extract_post_data(self, post):
        """Extract relevant data from a post"""
        try:
            return {
                'id': post.get('id', ''),
                'title': post.get('title', ''),
                'selftext': post.get('selftext', ''),
                'score': post.get('score', 0),
                'upvote_ratio': post.get('upvote_ratio', 0),
                'num_comments': post.get('num_comments', 0),
                'created_utc': datetime.fromtimestamp(post.get('created_utc', 0)),
                'author': post.get('author', ''),
                'url': post.get('url', ''),
                'permalink': f"https://reddit.com{post.get('permalink', '')}",
                'flair_text': post.get('link_flair_text', ''),
                'is_self': post.get('is_self', False),
                'collected_at': datetime.now(),
                'source': 'hot'
            }
        except Exception as e:
            print(f"Error extracting post data: {e}")
            return None
    
    def scrape_hot_posts(self, target_posts=500):
        """Scrape hot posts with multiple strategies"""
        print(f"🔥 Starting HOT posts scraper - Target: {target_posts} posts")
        print("=" * 60)
        
        after = None
        batch_size = 25  # Start small
        failed_attempts = 0
        max_failed_attempts = 5
        
        while len(self.posts_data) < target_posts and failed_attempts < max_failed_attempts:
            remaining = target_posts - len(self.posts_data)
            current_batch_size = min(batch_size, remaining)
            
            print(f"📥 Fetching batch {len(self.posts_data)//batch_size + 1} - {current_batch_size} posts")
            
            batch_posts, next_after = self.scrape_hot_posts_batch(after, current_batch_size)
            
            if batch_posts is None:
                # Failed request
                failed_attempts += 1
                print(f"  ⚠️  Failed attempt {failed_attempts}/{max_failed_attempts}")
                
                # Progressively longer delays
                delay_time = failed_attempts * 15
                print(f"  ⏱️  Backing off for {delay_time}s...")
                time.sleep(delay_time)
                
                # Change user agent
                self.ua = UserAgent()
                continue
            
            if not batch_posts:
                print("  📭 No more posts available")
                break
            
            # Success! Add posts and reset failed counter
            failed_attempts = 0
            self.posts_data.extend(batch_posts)
            after = next_after
            
            print(f"  ✅ Got {len(batch_posts)} posts (Total: {len(self.posts_data)})")
            
            if not next_after:
                print("  🏁 Reached end of available posts")
                break
            
            # Random delay before next request
            self.random_delay(3, 8)
        
        print(f"\n🎯 Scraping completed!")
        print(f"📊 Total HOT posts collected: {len(self.posts_data)}")
        
        return self.posts_data
    
    def save_to_csv(self, filename=None):
        """Save scraped data to CSV"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/reddit_notion_hot_full_{timestamp}.csv'
        
        df = pd.DataFrame(self.posts_data)
        df.to_csv(filename, index=False)
        print(f"💾 Data saved to: {filename}")
        return filename

if __name__ == "__main__":
    scraper = HotPostsScraper()
    posts = scraper.scrape_hot_posts(500)
    filename = scraper.save_to_csv()
    print(f"\n✅ Successfully scraped {len(posts)} HOT posts!")
    print(f"📁 File: {filename}")