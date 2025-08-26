#!/usr/bin/env python3
"""
Reddit Web Scraper for Notion Analysis
Alternative to PRAW that doesn't require API credentials
Based on web scraping techniques from ScrapFly
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import time
import random
from fake_useragent import UserAgent
import config
import os

class RedditWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Set up headers to mimic a real browser
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.min_delay = 1  # Minimum delay between requests
        self.max_delay = 3  # Maximum delay between requests
        
        # Ensure data directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)
    
    def _random_delay(self):
        """Add random delay to avoid being blocked"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def _extract_post_data_from_listing(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract post data from Reddit listing page"""
        posts_data = []
        
        # Find post containers - Reddit uses different selectors
        # Try multiple selectors for robustness
        post_selectors = [
            'div[data-testid="post-container"]',  # New Reddit
            'div.Post',  # New Reddit alternative
            'div.thing',  # Old Reddit
            'div[id^="thing_"]'  # Old Reddit alternative
        ]
        
        posts = None
        for selector in post_selectors:
            posts = soup.select(selector)
            if posts:
                break
        
        if not posts:
            # Try to find posts by looking for common patterns
            posts = soup.find_all('div', {'class': re.compile(r'.*[Pp]ost.*')})
        
        print(f"Found {len(posts)} post containers")
        
        for post in posts:
            try:
                post_data = self._extract_single_post_data(post)
                if post_data:
                    posts_data.append(post_data)
            except Exception as e:
                print(f"Error extracting post: {e}")
                continue
        
        return posts_data
    
    def _extract_single_post_data(self, post_element) -> Optional[Dict[str, Any]]:
        """Extract data from a single post element"""
        try:
            # Initialize post data
            post_data = {
                'title': '',
                'selftext': '',
                'score': 0,
                'num_comments': 0,
                'author': '',
                'created_utc': None,
                'url': '',
                'permalink': '',
                'flair_text': '',
                'upvote_ratio': None,
                'is_self': True,
                'id': '',
                'collected_at': datetime.now(timezone.utc)
            }
            
            # Extract title
            title_selectors = [
                'h3[data-testid="post-title"]',
                'h3 a',
                'a.title',
                '.title a',
                'h1',
                'h2',
                'h3'
            ]
            
            title_element = None
            for selector in title_selectors:
                title_element = post_element.select_one(selector)
                if title_element:
                    break
            
            if title_element:
                post_data['title'] = title_element.get_text(strip=True)
            
            # Extract post URL/ID from various possible locations
            link_element = post_element.find('a', href=re.compile(r'/r/\w+/comments/'))
            if link_element:
                href = link_element.get('href')
                if href:
                    if href.startswith('/'):
                        post_data['permalink'] = f"https://reddit.com{href}"
                    else:
                        post_data['permalink'] = href
                    
                    # Extract ID from URL
                    id_match = re.search(r'/comments/([a-z0-9]+)/', href)
                    if id_match:
                        post_data['id'] = id_match.group(1)
            
            # Extract author
            author_selectors = [
                'span[data-testid="post_author_link"]',
                'a[data-testid="post_author_link"]',
                '.author',
                'a.author'
            ]
            
            author_element = None
            for selector in author_selectors:
                author_element = post_element.select_one(selector)
                if author_element:
                    break
            
            if author_element:
                post_data['author'] = author_element.get_text(strip=True).replace('u/', '')
            
            # Extract score/upvotes
            score_selectors = [
                'div[data-testid="vote-arrows"] div:first-child',
                '.score',
                '.likes',
                '.upvotes'
            ]
            
            score_element = None
            for selector in score_selectors:
                score_element = post_element.select_one(selector)
                if score_element:
                    score_text = score_element.get_text(strip=True)
                    # Handle different score formats
                    score_match = re.search(r'(\d+(?:\.\d+)?)[kK]?', score_text)
                    if score_match:
                        score = float(score_match.group(1))
                        if 'k' in score_text.lower():
                            score *= 1000
                        post_data['score'] = int(score)
                    break
            
            # Extract comment count
            comments_selectors = [
                'span[data-testid="comment-count"]',
                '.comments',
                'a[data-click-id="comments"]'
            ]
            
            comments_element = None
            for selector in comments_selectors:
                comments_element = post_element.select_one(selector)
                if comments_element:
                    comments_text = comments_element.get_text(strip=True)
                    comments_match = re.search(r'(\d+)', comments_text)
                    if comments_match:
                        post_data['num_comments'] = int(comments_match.group(1))
                    break
            
            # Extract flair
            flair_selectors = [
                'span[data-testid="post-flair-text"]',
                '.linkflairlabel',
                '.flair'
            ]
            
            flair_element = None
            for selector in flair_selectors:
                flair_element = post_element.select_one(selector)
                if flair_element:
                    post_data['flair_text'] = flair_element.get_text(strip=True)
                    break
            
            # Only return posts with at least a title and ID
            if post_data['title'] and post_data['id']:
                return post_data
            
            return None
            
        except Exception as e:
            print(f"Error parsing post element: {e}")
            return None
    
    def scrape_subreddit_json(self, subreddit: str, sort_method: str = 'hot', limit: int = 25, time_filter: str = 'all') -> List[Dict[str, Any]]:
        """
        Scrape subreddit using Reddit's JSON API with pagination support
        This is more reliable than HTML parsing
        """
        posts_data = []
        after = None
        posts_per_request = 100  # Reddit's max per request
        
        # Build base URL with .json suffix
        base_url = f"https://www.reddit.com/r/{subreddit}/{sort_method}/.json"
        
        print(f"Fetching up to {limit} posts from: {base_url}")
        
        while len(posts_data) < limit:
            # Calculate how many posts to request this round
            remaining = limit - len(posts_data)
            current_limit = min(remaining, posts_per_request)
            
            params = {
                'limit': current_limit,
                'raw_json': 1
            }
            
            # Add pagination parameter if we have one
            if after:
                params['after'] = after
                print(f"  Fetching next page (after={after[:10]}...)")
            
            try:
                self._random_delay()
                response = self.session.get(base_url, params=params, timeout=30)
                response.raise_for_status()
            
                data = response.json()
                
                if 'data' in data and 'children' in data['data']:
                    posts = data['data']['children']
                    print(f"  Found {len(posts)} posts in this batch")
                    
                    if not posts:  # No more posts available
                        print("  No more posts available")
                        break
                    
                    for post in posts:
                        try:
                            post_info = post['data']
                            
                            # Convert Unix timestamp to datetime
                            created_utc = datetime.fromtimestamp(post_info.get('created_utc', 0), timezone.utc)
                            
                            post_data = {
                                'id': post_info.get('id', ''),
                                'title': post_info.get('title', ''),
                                'selftext': post_info.get('selftext', ''),
                                'score': post_info.get('score', 0),
                                'upvote_ratio': post_info.get('upvote_ratio'),
                                'num_comments': post_info.get('num_comments', 0),
                                'created_utc': created_utc,
                                'author': post_info.get('author', '[deleted]'),
                                'url': post_info.get('url', ''),
                                'permalink': f"https://reddit.com{post_info.get('permalink', '')}",
                                'flair_text': post_info.get('link_flair_text'),
                                'is_self': post_info.get('is_self', True),
                                'collected_at': datetime.now(timezone.utc)
                            }
                            
                            posts_data.append(post_data)
                            
                        except Exception as e:
                            print(f"Error processing post from JSON: {e}")
                            continue
                    
                    # Get the 'after' token for pagination
                    after = data['data'].get('after')
                    if not after:  # No more pages available
                        print("  No pagination token - reached end")
                        break
                        
                else:
                    print("  Invalid JSON response structure")
                    break
                    
            except Exception as e:
                print(f"Error in pagination request: {e}")
                break
        
        print(f"Total posts collected: {len(posts_data)}")
        return posts_data
    
    def scrape_subreddit_html(self, subreddit: str, sort_method: str = 'hot', limit: int = 25) -> List[Dict[str, Any]]:
        """
        Scrape subreddit using HTML parsing as fallback
        """
        posts_data = []
        
        # Use old.reddit.com for more stable HTML structure
        base_url = f"https://old.reddit.com/r/{subreddit}/{sort_method}/"
        params = {'limit': limit}
        
        try:
            print(f"Fetching HTML from: {base_url}")
            self._random_delay()
            
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            posts_data = self._extract_post_data_from_listing(soup)
            
            print(f"Extracted {len(posts_data)} posts from HTML")
            return posts_data
            
        except Exception as e:
            print(f"Error scraping HTML: {e}")
            return []
    
    def collect_posts(self, sort_method='hot', time_filter='week', limit=100) -> List[Dict[str, Any]]:
        """
        Collect posts from r/Notion using web scraping
        First tries JSON API, falls back to HTML parsing
        """
        subreddit = config.SUBREDDIT_NAME
        
        print(f"Collecting posts from r/{subreddit} using web scraping...")
        print(f"Method: {sort_method}, Limit: {limit}")
        
        # Try JSON API first (more reliable)
        posts_data = self.scrape_subreddit_json(subreddit, sort_method, limit)
        
        # If JSON fails or returns few results, try HTML parsing
        if len(posts_data) < limit // 2:
            print("JSON API returned few results, trying HTML parsing...")
            html_posts = self.scrape_subreddit_html(subreddit, sort_method, limit)
            
            # Combine results, avoiding duplicates
            existing_ids = {post['id'] for post in posts_data}
            for post in html_posts:
                if post['id'] not in existing_ids:
                    posts_data.append(post)
        
        return posts_data
    
    def save_to_csv(self, posts_data: List[Dict[str, Any]], filename: str = None):
        """Save collected posts to CSV file"""
        if not filename:
            filename = config.RAW_DATA_FILE
        
        df = pd.DataFrame(posts_data)
        
        if len(df) == 0:
            print("No data to save")
            return df
        
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
        unique_posts = {post['id']: post for post in all_posts if post.get('id')}.values()
        
        return self.save_to_csv(list(unique_posts))

# Update main_pipeline.py to use the scraper
class ScraperBasedPipeline:
    """Alternative pipeline using web scraper instead of PRAW"""
    
    def __init__(self):
        from text_classifier import NotionPostClassifier
        from data_analyzer import NotionDataAnalyzer
        
        self.collector = RedditWebScraper()
        self.classifier = NotionPostClassifier()
        self.analyzer = NotionDataAnalyzer()
    
    def run_collection(self, sort_methods=['hot', 'new', 'top'], limit_per_method=50):
        """Run collection using web scraper"""
        print("🕷️ Using Web Scraping Method (No API Required)")
        print("=" * 50)
        
        try:
            df = self.collector.collect_and_save(
                sort_methods=sort_methods,
                limit_per_method=limit_per_method
            )
            
            if len(df) > 0:
                print(f"✅ Successfully collected {len(df)} unique posts")
                return df
            else:
                print("❌ No posts collected")
                return None
                
        except Exception as e:
            print(f"❌ Error collecting data: {e}")
            return None

if __name__ == "__main__":
    import sys
    
    scraper = RedditWebScraper()
    
    # Check for command line arguments
    if len(sys.argv) >= 3:
        sort_method = sys.argv[1]  # 'hot', 'new', 'top', etc.
        limit = int(sys.argv[2])  # number of posts
        
        print(f"🚀 Starting Reddit scraping for r/Notion/{sort_method} - {limit} posts")
        print("=" * 60)
        
        # Run full scraping
        posts = scraper.scrape_subreddit_json('Notion', sort_method, limit)
        print(f"✅ Collected {len(posts)} posts from r/Notion/{sort_method}")
        
        if posts:
            # Save to timestamped file
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/reddit_notion_{sort_method}_{timestamp}.csv'
            df = scraper.save_to_csv(posts, filename)
            print(f"💾 Data saved to: {filename}")
            print(f"📊 Total posts: {len(df)}")
    else:
        # Default test mode
        print("Testing JSON API method...")
        posts = scraper.scrape_subreddit_json('Notion', 'hot', 10)
        print(f"JSON API returned {len(posts)} posts")
        
        if posts:
            print("Sample post:")
            sample = posts[0]
            print(f"  Title: {sample['title'][:80]}...")
            print(f"  Score: {sample['score']}")
            print(f"  Comments: {sample['num_comments']}")
            print(f"  Author: {sample['author']}")
        
        # Save test data
        if posts:
            df = scraper.save_to_csv(posts, 'data/test_scraper_data.csv')
            print(f"\nTest data saved: {len(df)} posts")