#!/usr/bin/env python3
"""
Interactive Dashboard for Notion Reddit Analysis
Provides real-time insights and competitive intelligence
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
import config
import os
from data_analyzer import NotionDataAnalyzer

class NotionDashboard:
    def __init__(self):
        self.analyzer = NotionDataAnalyzer()
        self.df = None
        
    def load_data(self):
        """Load the processed data"""
        try:
            self.df = self.analyzer.load_data()
            return True
        except FileNotFoundError:
            return False
    
    def create_category_distribution_chart(self):
        """Create interactive category distribution chart"""
        if self.df is None:
            return None
            
        category_counts = self.df['predicted_category'].value_counts()
        category_labels = [config.POST_CATEGORIES.get(cat, cat) for cat in category_counts.index]
        
        fig = go.Figure(data=[go.Pie(
            labels=category_labels,
            values=category_counts.values,
            hole=0.4,
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Post Category Distribution",
            font=dict(size=12),
            showlegend=True,
            height=500
        )
        
        return fig
    
    def create_timeline_chart(self):
        """Create timeline of posts by category"""
        if self.df is None:
            return None
            
        # Resample by day and category
        df_timeline = self.df.copy()
        df_timeline['created_utc'] = pd.to_datetime(df_timeline['created_utc'])
        
        # Get top 6 categories for readability
        top_categories = self.df['predicted_category'].value_counts().head(6).index
        df_filtered = df_timeline[df_timeline['predicted_category'].isin(top_categories)]
        
        fig = px.histogram(
            df_filtered,
            x='created_utc',
            color='predicted_category',
            title='Post Timeline by Category',
            labels={'created_utc': 'Date', 'count': 'Number of Posts'},
            category_orders={'predicted_category': top_categories.tolist()}
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Posts",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_engagement_metrics(self):
        """Create engagement metrics visualization"""
        if self.df is None:
            return None
            
        # Calculate engagement metrics by category
        engagement_data = self.df.groupby('predicted_category').agg({
            'score': ['mean', 'sum'],
            'num_comments': ['mean', 'sum'],
            'upvote_ratio': 'mean'
        }).round(2)
        
        # Flatten column names
        engagement_data.columns = ['avg_score', 'total_score', 'avg_comments', 'total_comments', 'avg_upvote_ratio']
        engagement_data = engagement_data.reset_index()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Average Score by Category', 'Average Comments by Category',
                          'Total Engagement Score', 'Average Upvote Ratio'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        categories = [config.POST_CATEGORIES.get(cat, cat) for cat in engagement_data['predicted_category']]
        
        # Average Score
        fig.add_trace(
            go.Bar(x=categories, y=engagement_data['avg_score'], name='Avg Score',
                  marker_color='lightblue'),
            row=1, col=1
        )
        
        # Average Comments
        fig.add_trace(
            go.Bar(x=categories, y=engagement_data['avg_comments'], name='Avg Comments',
                  marker_color='lightcoral'),
            row=1, col=2
        )
        
        # Total Score
        fig.add_trace(
            go.Bar(x=categories, y=engagement_data['total_score'], name='Total Score',
                  marker_color='lightgreen'),
            row=2, col=1
        )
        
        # Upvote Ratio
        fig.add_trace(
            go.Bar(x=categories, y=engagement_data['avg_upvote_ratio'], name='Upvote Ratio',
                  marker_color='gold'),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False, title_text="Engagement Metrics by Category")
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_competitive_intelligence_summary(self):
        """Create competitive intelligence summary"""
        if self.df is None:
            return {}
            
        competitive_insights = self.analyzer.generate_competitive_insights()
        
        # Calculate additional metrics
        total_posts = len(self.df)
        
        # Recent trends (last 7 days)
        recent_date = self.df['created_utc'].max() - timedelta(days=7)
        recent_posts = self.df[pd.to_datetime(self.df['created_utc']) >= recent_date]
        
        summary = {
            'total_posts': total_posts,
            'recent_posts_7d': len(recent_posts),
            'pain_points_pct': competitive_insights['pain_points']['percentage'],
            'feature_requests_pct': competitive_insights['feature_requests']['percentage'],
            'satisfaction_ratio': competitive_insights['satisfaction_ratio']['ratio'],
            'satisfaction_interpretation': competitive_insights['satisfaction_ratio']['interpretation'],
            'top_pain_points': competitive_insights['pain_points']['top_issues'][:3],
            'top_feature_requests': competitive_insights['feature_requests']['top_requests'][:3],
            'competitor_mentions_pct': competitive_insights['competitor_mentions']['percentage']
        }
        
        return summary

def create_streamlit_dashboard():
    """Create Streamlit dashboard"""
    st.set_page_config(
        page_title="Notion Reddit Analysis Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Notion Reddit Analysis Dashboard")
    st.markdown("### Competitive Intelligence from r/Notion")
    
    dashboard = NotionDashboard()
    
    # Load data
    if not dashboard.load_data():
        st.error("❌ No processed data found. Please run the analysis pipeline first.")
        st.info("Run: `python main_pipeline.py` to collect and process data")
        return
    
    # Sidebar with controls
    st.sidebar.header("Dashboard Controls")
    
    # Data info
    st.sidebar.metric("Total Posts", len(dashboard.df))
    st.sidebar.metric("Date Range", f"{dashboard.df['created_utc'].min().split(' ')[0]} to {dashboard.df['created_utc'].max().split(' ')[0]}")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        dashboard.load_data()
        st.experimental_rerun()
    
    # Main dashboard layout
    col1, col2, col3, col4 = st.columns(4)
    
    # Key metrics
    summary = dashboard.create_competitive_intelligence_summary()
    
    with col1:
        st.metric("Total Posts", summary['total_posts'])
    
    with col2:
        st.metric("Recent Posts (7d)", summary['recent_posts_7d'])
    
    with col3:
        st.metric("Pain Points", f"{summary['pain_points_pct']}%")
    
    with col4:
        st.metric("Feature Requests", f"{summary['feature_requests_pct']}%")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(dashboard.create_category_distribution_chart(), use_container_width=True)
    
    with col2:
        st.plotly_chart(dashboard.create_timeline_chart(), use_container_width=True)
    
    # Engagement metrics
    st.plotly_chart(dashboard.create_engagement_metrics(), use_container_width=True)
    
    # Competitive Intelligence Section
    st.header("🎯 Competitive Intelligence")
    
    # Satisfaction metrics
    col1, col2 = st.columns(2)
    
    with col1:
        satisfaction_color = "green" if summary['satisfaction_interpretation'] == 'positive' else "red"
        st.metric(
            "Satisfaction Ratio",
            f"{summary['satisfaction_ratio']:.2f}",
            delta=f"{summary['satisfaction_interpretation'].upper()}",
            delta_color=satisfaction_color
        )
    
    with col2:
        st.metric("Competitor Mentions", f"{summary['competitor_mentions_pct']}%")
    
    # Top issues and requests
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Top Pain Points")
        for i, issue in enumerate(summary['top_pain_points'], 1):
            with st.expander(f"{i}. {issue['title'][:60]}..."):
                st.write(f"**Score:** {issue['score']}")
                st.write(f"**Comments:** {issue['num_comments']}")
    
    with col2:
        st.subheader("💡 Top Feature Requests")
        for i, request in enumerate(summary['top_feature_requests'], 1):
            with st.expander(f"{i}. {request['title'][:60]}..."):
                st.write(f"**Score:** {request['score']}")
                st.write(f"**Comments:** {request['num_comments']}")
    
    # Data table
    st.header("📋 Recent Posts Data")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_categories = st.multiselect(
            "Filter by Category",
            options=list(config.POST_CATEGORIES.keys()),
            default=list(config.POST_CATEGORIES.keys())[:3]
        )
    
    with col2:
        min_score = st.number_input("Minimum Score", value=0)
    
    with col3:
        days_back = st.selectbox("Days Back", [7, 14, 30, 60, 90])
    
    # Filter data
    filtered_df = dashboard.df.copy()
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['predicted_category'].isin(selected_categories)]
    
    filtered_df = filtered_df[filtered_df['score'] >= min_score]
    
    # Date filter
    cutoff_date = pd.to_datetime(filtered_df['created_utc']).max() - timedelta(days=days_back)
    filtered_df = filtered_df[pd.to_datetime(filtered_df['created_utc']) >= cutoff_date]
    
    # Display table
    display_df = filtered_df[['title', 'predicted_category', 'score', 'num_comments', 'created_utc']].copy()
    display_df['category_label'] = display_df['predicted_category'].map(config.POST_CATEGORIES)
    display_df = display_df.drop('predicted_category', axis=1)
    display_df = display_df.sort_values('score', ascending=False)
    
    st.dataframe(
        display_df,
        column_config={
            "title": "Post Title",
            "category_label": "Category",
            "score": st.column_config.NumberColumn("Score", format="%d"),
            "num_comments": st.column_config.NumberColumn("Comments", format="%d"),
            "created_utc": st.column_config.DatetimeColumn("Created")
        },
        hide_index=True
    )
    
    # Footer
    st.markdown("---")
    st.markdown("📈 Generated by Notion Reddit Analysis Pipeline | Data updated: " + 
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    create_streamlit_dashboard()