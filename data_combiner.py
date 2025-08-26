#!/usr/bin/env python3
"""
Combine multiple Reddit datasets into one comprehensive dataset
"""

import pandas as pd
import os
from datetime import datetime

def combine_datasets():
    """Combine all available Reddit data files"""
    
    data_files = []
    base_path = 'data/'
    
    # Find all CSV files in the data directory
    for filename in os.listdir(base_path):
        if filename.endswith('.csv') and 'reddit_notion' in filename:
            data_files.append(os.path.join(base_path, filename))
    
    # Also check for existing processed data
    if os.path.exists('data/raw_posts.csv'):
        data_files.append('data/raw_posts.csv')
    
    print(f"Found {len(data_files)} data files to combine:")
    for file in data_files:
        print(f"  - {file}")
    
    if not data_files:
        print("No data files found!")
        return None
    
    # Load and combine all datasets
    all_dataframes = []
    total_posts = 0
    
    for file_path in data_files:
        try:
            df = pd.read_csv(file_path)
            print(f"Loaded {len(df)} posts from {os.path.basename(file_path)}")
            
            # Add source information
            source_name = os.path.basename(file_path).replace('.csv', '')
            if 'hot' in source_name:
                df['source'] = 'hot'
            elif 'top' in source_name:
                df['source'] = 'top'  
            elif 'raw_posts' in source_name:
                df['source'] = 'new'  # Our original data was from /new
            else:
                df['source'] = 'unknown'
            
            all_dataframes.append(df)
            total_posts += len(df)
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if not all_dataframes:
        print("No valid data files found!")
        return None
    
    # Combine all dataframes
    print(f"\nCombining {len(all_dataframes)} datasets...")
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Remove duplicates based on post ID
    print(f"Before deduplication: {len(combined_df)} posts")
    combined_df = combined_df.drop_duplicates(subset=['id'], keep='first')
    print(f"After deduplication: {len(combined_df)} posts")
    
    # Sort by creation date
    if 'created_utc' in combined_df.columns:
        combined_df['created_utc'] = pd.to_datetime(combined_df['created_utc'])
        combined_df = combined_df.sort_values('created_utc', ascending=False)
    
    # Save combined dataset
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/combined_reddit_data_{timestamp}.csv'
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Combined dataset saved: {output_file}")
    print(f"📊 Total unique posts: {len(combined_df)}")
    
    # Show breakdown by source
    if 'source' in combined_df.columns:
        print("\nBreakdown by source:")
        source_counts = combined_df['source'].value_counts()
        for source, count in source_counts.items():
            print(f"  {source}: {count} posts")
    
    return output_file

if __name__ == "__main__":
    combine_datasets()