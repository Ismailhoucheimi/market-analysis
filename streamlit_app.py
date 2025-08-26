#!/usr/bin/env python3
"""
Interactive Streamlit Dashboard for Notion Reddit Analysis
Replaces static HTML reports with real-time interactive analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
import numpy as np
from collections import Counter
import config

# Page configuration
st.set_page_config(
    page_title="Notion Reddit Analysis Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the processed Reddit data"""
    try:
        # Check if we have processed data with LLM analysis
        processed_file = 'data/processed_posts_838.csv'
        if os.path.exists(processed_file):
            df = pd.read_csv(processed_file)
            st.success(f"✅ Loaded {len(df)} posts with LLM analysis")
        else:
            # Fall back to combined raw data
            raw_file = 'data/combined_new_hot_full.csv'
            if os.path.exists(raw_file):
                df = pd.read_csv(raw_file)
                st.warning(f"📊 Loaded {len(df)} posts (no LLM analysis yet)")
            else:
                st.error("❌ No data files found. Please run the scrapers first.")
                return None
        
        # Convert datetime columns
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        if 'collected_at' in df.columns:
            df['collected_at'] = pd.to_datetime(df['collected_at'])
        
        # Clean and prepare data
        df['word_count'] = df['selftext'].fillna('').str.split().str.len()
        df['has_content'] = df['selftext'].notna() & (df['selftext'] != '')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def load_comprehensive_report():
    """Load the comprehensive analysis report"""
    report_path = 'reports/comprehensive_notion_analysis.md'
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

@st.cache_data
def load_batch_summaries():
    """Load LLM batch analysis summaries"""
    summary_path = 'reports/llm_batch_summaries.json'
    if os.path.exists(summary_path):
        with open(summary_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def create_sentiment_chart(df):
    """Create sentiment analysis visualization"""
    if 'sentiment_score' not in df.columns:
        return None
    
    fig = px.histogram(
        df.dropna(subset=['sentiment_score']), 
        x='sentiment_score',
        nbins=20,
        title="📊 Sentiment Distribution",
        labels={'sentiment_score': 'Sentiment Score', 'count': 'Number of Posts'},
        color_discrete_sequence=['#667eea']
    )
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Neutral")
    return fig

def create_category_chart(df):
    """Create category distribution chart"""
    category_col = None
    for col in ['predicted_category', 'llm_category', 'category_label']:
        if col in df.columns:
            category_col = col
            break
    
    if not category_col:
        return None
    
    category_counts = df[category_col].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="🏷️ Post Categories",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    return fig

def create_timeline_chart(df):
    """Create timeline visualization"""
    df_daily = df.groupby(df['created_utc'].dt.date).agg({
        'id': 'count',
        'score': 'mean',
        'num_comments': 'mean'
    }).reset_index()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('📈 Daily Post Volume', '⭐ Average Engagement'),
        vertical_spacing=0.1
    )
    
    # Post volume
    fig.add_trace(
        go.Scatter(
            x=df_daily['created_utc'],
            y=df_daily['id'],
            mode='lines+markers',
            name='Posts per Day',
            line=dict(color='#667eea')
        ),
        row=1, col=1
    )
    
    # Average score
    fig.add_trace(
        go.Scatter(
            x=df_daily['created_utc'],
            y=df_daily['score'],
            mode='lines+markers',
            name='Avg Score',
            line=dict(color='#764ba2')
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=500, title_text="📊 Post Activity Over Time")
    return fig

def render_post_card(post):
    """Render individual post information"""
    with st.expander(f"📝 {post['title'][:100]}{'...' if len(post['title']) > 100 else ''}", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if post.get('selftext') and str(post['selftext']) != 'nan':
                st.write("**Content:**")
                content = str(post['selftext'])[:500]
                if len(str(post['selftext'])) > 500:
                    content += "..."
                st.write(content)
            
            # LLM Insights
            if post.get('key_insights'):
                st.markdown("**🤖 AI Insights:**")
                st.info(post['key_insights'])
        
        with col2:
            st.metric("Score", post.get('score', 0))
            st.metric("Comments", post.get('num_comments', 0))
            if post.get('sentiment_score'):
                sentiment_emoji = "😊" if post['sentiment_score'] > 0.1 else "😞" if post['sentiment_score'] < -0.1 else "😐"
                st.metric("Sentiment", f"{sentiment_emoji} {post['sentiment_score']:.2f}")
        
        with col3:
            st.write(f"**Author:** {post.get('author', 'Unknown')}")
            st.write(f"**Date:** {post['created_utc'].strftime('%Y-%m-%d')}")
            if post.get('flair_text'):
                st.write(f"**Flair:** {post['flair_text']}")
            if post.get('permalink'):
                st.link_button("🔗 View on Reddit", post['permalink'])

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="insight-box">
        <h1>🎯 Notion Reddit Analysis Dashboard</h1>
        <p>Interactive Competitive Intelligence & User Research Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Summary metrics (always show full dataset)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Posts", f"{len(df):,}")
    
    with col2:
        avg_score = df['score'].mean()
        st.metric("⭐ Avg Score", f"{avg_score:.1f}")
    
    with col3:
        avg_comments = df['num_comments'].mean()
        st.metric("💬 Avg Comments", f"{avg_comments:.1f}")
    
    with col4:
        if 'sentiment_score' in df.columns:
            avg_sentiment = df['sentiment_score'].mean()
            sentiment_emoji = "😊" if avg_sentiment > 0.1 else "😞" if avg_sentiment < -0.1 else "😐"
            st.metric("🎭 Avg Sentiment", f"{sentiment_emoji} {avg_sentiment:.2f}")
        else:
            st.metric("🤖 LLM Analysis", "Not Available")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "💬 Posts Explorer", "📋 Strategic Report", "🤖 AI Insights"])
    
    with tab1:
        st.header("📊 Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment chart
            sentiment_chart = create_sentiment_chart(df)
            if sentiment_chart:
                st.plotly_chart(sentiment_chart, use_container_width=True)
            else:
                st.info("💡 Run LLM analysis to see sentiment distribution")
        
        with col2:
            # Category chart
            category_chart = create_category_chart(df)
            if category_chart:
                st.plotly_chart(category_chart, use_container_width=True)
            else:
                st.info("💡 Run LLM analysis to see category breakdown")
        
        # Timeline chart
        timeline_chart = create_timeline_chart(df)
        st.plotly_chart(timeline_chart, use_container_width=True)
        
        # Top posts table
        st.subheader("🔥 Top Posts by Score")
        top_posts = df.nlargest(10, 'score')[['title', 'score', 'num_comments', 'author', 'created_utc']]
        st.dataframe(top_posts, use_container_width=True)
    
    with tab2:
        st.header("💬 Posts Explorer")
        
        # Filters in main content area (not sidebar)
        st.subheader("🎛️ Filters & Controls")
        
        # Create filter columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date range filter
            date_range = st.date_input(
                "📅 Date Range",
                value=(df['created_utc'].dt.date.min(), df['created_utc'].dt.date.max()),
                min_value=df['created_utc'].dt.date.min(),
                max_value=df['created_utc'].dt.date.max()
            )
        
        with col2:
            # Category filter
            category_col = None
            for col in ['predicted_category', 'llm_category', 'category_label']:
                if col in df.columns:
                    category_col = col
                    break
            
            categories = ['All']
            selected_category = 'All'
            
            if category_col:
                categories = ['All'] + sorted(df[category_col].dropna().unique().tolist())
                selected_category = st.selectbox("🏷️ Category", categories)
            else:
                st.info("Categories not available")
        
        with col3:
            # Score filter
            score_range = st.slider(
                "⭐ Score Range",
                min_value=int(df['score'].min()),
                max_value=int(df['score'].max()),
                value=(int(df['score'].min()), int(df['score'].max()))
            )
        
        # Search filter (full width)
        search_term = st.text_input("🔍 Search in titles and content", "")
        
        # Apply filters
        filtered_df = df.copy()
        
        # Date filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['created_utc'].dt.date >= start_date) & 
                (filtered_df['created_utc'].dt.date <= end_date)
            ]
        
        # Category filter
        if selected_category != 'All' and category_col:
            filtered_df = filtered_df[filtered_df[category_col] == selected_category]
        
        # Score filter
        filtered_df = filtered_df[
            (filtered_df['score'] >= score_range[0]) & 
            (filtered_df['score'] <= score_range[1])
        ]
        
        # Search filter
        if search_term:
            mask = (
                filtered_df['title'].str.contains(search_term, case=False, na=False) |
                filtered_df['selftext'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Show filtered results summary
        if len(filtered_df) != len(df):
            st.info(f"🔍 Showing {len(filtered_df)} posts (filtered from {len(df)} total)")
        
        # Sort options
        col1, col2 = st.columns([2, 1])
        with col1:
            sort_option = st.selectbox(
                "📊 Sort by",
                ["Score (High to Low)", "Score (Low to High)", "Comments (High to Low)", 
                 "Date (Newest First)", "Date (Oldest First)"]
            )
        with col2:
            posts_per_page = st.selectbox("Posts per page", [10, 25, 50, 100], index=1)
        
        # Apply sorting
        if sort_option == "Score (High to Low)":
            display_df = filtered_df.sort_values('score', ascending=False)
        elif sort_option == "Score (Low to High)":
            display_df = filtered_df.sort_values('score', ascending=True)
        elif sort_option == "Comments (High to Low)":
            display_df = filtered_df.sort_values('num_comments', ascending=False)
        elif sort_option == "Date (Newest First)":
            display_df = filtered_df.sort_values('created_utc', ascending=False)
        else:  # Date (Oldest First)
            display_df = filtered_df.sort_values('created_utc', ascending=True)
        
        # Pagination
        total_pages = (len(display_df) - 1) // posts_per_page + 1 if len(display_df) > 0 else 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        
        # Display posts
        if len(display_df) == 0:
            st.warning("🔍 No posts found matching your filters. Try adjusting your search criteria.")
        else:
            st.write(f"📝 Showing page {page} of {total_pages} ({len(display_df)} posts total)")
            
            start_idx = (page - 1) * posts_per_page
            end_idx = start_idx + posts_per_page
            
            for _, post in display_df.iloc[start_idx:end_idx].iterrows():
                render_post_card(post)
    
    with tab3:
        st.header("📋 Comprehensive Strategic Report")
        
        report = load_comprehensive_report()
        if report:
            st.markdown(report)
        else:
            st.warning("📄 Comprehensive report not available. Run the summary report generator first.")
    
    with tab4:
        st.header("🤖 AI Insights Summary")
        
        batch_summaries = load_batch_summaries()
        if batch_summaries:
            st.subheader("🎯 Key Themes Across All Batches")
            
            # Aggregate themes
            all_themes = []
            for summary in batch_summaries:
                if 'dominant_themes' in summary:
                    all_themes.extend(summary['dominant_themes'])
            
            if all_themes:
                theme_counts = Counter(all_themes)
                theme_df = pd.DataFrame(list(theme_counts.items()), columns=['Theme', 'Frequency'])
                
                fig = px.bar(
                    theme_df.head(15),
                    x='Frequency',
                    y='Theme',
                    orientation='h',
                    title="🎯 Most Common Themes",
                    color='Frequency',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Display individual batch insights
            st.subheader("📝 Batch Analysis Details")
            
            for i, summary in enumerate(batch_summaries[:10]):  # Show first 10 batches
                with st.expander(f"Batch {i+1} Analysis", expanded=False):
                    if 'dominant_themes' in summary:
                        st.write("**Dominant Themes:**")
                        for theme in summary['dominant_themes']:
                            st.write(f"• {theme}")
                    
                    if 'sentiment_trend' in summary:
                        st.write(f"**Sentiment Trend:** {summary['sentiment_trend']}")
                    
                    if 'key_competitive_threats' in summary:
                        st.write("**Key Competitive Threats:**")
                        for threat in summary['key_competitive_threats']:
                            st.write(f"• {threat}")
                    
                    if 'strategic_recommendations' in summary:
                        st.write("**Strategic Recommendations:**")
                        for rec in summary['strategic_recommendations']:
                            st.write(f"• {rec}")
        else:
            st.warning("🤖 AI batch summaries not available. Run LLM analysis first.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Data Sources:** Reddit r/Notion (NEW & HOT posts)")

if __name__ == "__main__":
    main()