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
from competitors_config import competitor_manager, CompetitorConfig

# Page configuration
st.set_page_config(
    page_title="ZenFlo Strategic Analysis Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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


@st.cache_data(ttl=60)  # Cache for 60 seconds to allow fresh data loading
def load_competitor_data(competitor: str):
    """Load and cache competitor data"""
    try:
        config = competitor_manager.get_competitor_config(competitor)
        data_file = competitor_manager.load_competitor_data(
            competitor, "processed")

        if data_file and os.path.exists(data_file):
            df = pd.read_csv(data_file)
            st.success(
                f"Loaded {len(df)} {config.display_name} posts with analysis")
        else:
            st.warning(f"No processed data found for {config.display_name}")
            return None

        # Convert datetime columns
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        if 'collected_at' in df.columns:
            df['collected_at'] = pd.to_datetime(df['collected_at'])

        # Clean and prepare data
        df['word_count'] = df['selftext'].fillna('').str.split().str.len()
        df['has_content'] = df['selftext'].notna() & (df['selftext'] != '')

        return df, config
    except Exception as e:
        st.error(f"Error loading {competitor} data: {e}")
        return None, None


@st.cache_data(ttl=60)  # Cache for 60 seconds to allow fresh data loading
def load_comprehensive_report(competitor: str):
    """Load the comprehensive analysis report for a competitor"""
    config = competitor_manager.get_competitor_config(competitor)

    # Try competitor-specific report first
    competitor_report_path = f'competitors/{competitor}/reports/analysis.md'
    if os.path.exists(competitor_report_path):
        with open(competitor_report_path, 'r', encoding='utf-8') as f:
            return f.read()

    # Fall back to legacy report for Notion
    if competitor == 'notion':
        legacy_path = 'reports/comprehensive_notion_analysis.md'
        if os.path.exists(legacy_path):
            with open(legacy_path, 'r', encoding='utf-8') as f:
                return f.read()

    return None


@st.cache_data(ttl=60)  # Cache for 60 seconds to allow fresh data loading
def load_batch_summaries(competitor: str):
    """Load LLM batch analysis summaries for a competitor"""
    config = competitor_manager.get_competitor_config(competitor)

    # Try competitor-specific summaries first
    competitor_summary_path = f'competitors/{competitor}/reports/batch_summaries.json'
    if os.path.exists(competitor_summary_path):
        with open(competitor_summary_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Fall back to legacy summaries for any competitor (they're generic)
    legacy_path = 'reports/llm_batch_summaries.json'
    if os.path.exists(legacy_path):
        with open(legacy_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    return None


def create_sentiment_chart(df, competitor_config):
    """Create sentiment analysis visualization"""
    if 'sentiment_score' not in df.columns:
        return None

    fig = px.histogram(
        df.dropna(subset=['sentiment_score']),
        x='sentiment_score',
        nbins=20,
        title="Sentiment Distribution",
        labels={'sentiment_score': 'Sentiment Score',
                'count': 'Number of Posts'},
        color_discrete_sequence=[competitor_config.color_scheme['primary']]
    )
    fig.add_vline(x=0, line_dash="dash", line_color="red",
                  annotation_text="Neutral")
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
        title="Post Categories",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    return fig


def create_timeline_chart(df, competitor_config):
    """Create timeline visualization"""
    df_daily = df.groupby(df['created_utc'].dt.date).agg({
        'id': 'count',
        'score': 'mean',
        'num_comments': 'mean'
    }).reset_index()

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Post Volume', 'Average Engagement'),
        vertical_spacing=0.1
    )

    # Post volume
    fig.add_trace(
        go.Scatter(
            x=df_daily['created_utc'],
            y=df_daily['id'],
            mode='lines+markers',
            name='Posts per Day',
            line=dict(color=competitor_config.color_scheme['primary'])
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
            line=dict(color=competitor_config.color_scheme['secondary'])
        ),
        row=2, col=1
    )

    fig.update_layout(height=500, title_text="Post Activity Over Time")
    return fig


def render_post_card(post):
    """Render individual post information"""
    with st.expander(f"{post['title'][:100]}{'...' if len(post['title']) > 100 else ''}", expanded=False):
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
                st.markdown("**AI Insights:**")
                st.info(post['key_insights'])

        with col2:
            st.metric("Score", post.get('score', 0))
            st.metric("Comments", post.get('num_comments', 0))
            if post.get('sentiment_score'):
                sentiment_text = "Positive" if post['sentiment_score'] > 0.1 else "Negative" if post[
                    'sentiment_score'] < -0.1 else "Neutral"
                st.metric(
                    "Sentiment", f"{sentiment_text} ({post['sentiment_score']:.2f})")

        with col3:
            st.write(f"**Author:** {post.get('author', 'Unknown')}")
            st.write(f"**Date:** {post['created_utc'].strftime('%Y-%m-%d')}")
            if post.get('flair_text'):
                st.write(f"**Flair:** {post['flair_text']}")
            if post.get('permalink'):
                st.link_button("View on Reddit", post['permalink'])


def render_navigation_sidebar():
    """Render main navigation sidebar"""
    st.sidebar.markdown("# Navigation")

    # Main navigation
    page = st.sidebar.radio(
        "Select Section:",
        ["Competitive Analysis", "Strategic Reports", "User Research", "Automation Intelligence"],
        key="main_navigation"
    )

    return page


def render_competitor_sidebar():
    """Render competitor selection sidebar"""
    st.sidebar.markdown("## Select Competitor")

    # Get available competitors
    competitors = competitor_manager.get_available_competitors()
    display_names = competitor_manager.get_competitor_display_names()

    # Show competitor options with emojis and validation
    competitor_options = []
    for comp in competitors:
        config = competitor_manager.get_competitor_config(comp)
        validation = competitor_manager.validate_data_completeness(comp)

        # Add status indicator
        status = "Ready" if validation["has_processed_data"] else "Loading"
        option_text = f"{config.display_name} ({status})"
        competitor_options.append((comp, option_text))

    # Create radio buttons
    selected_comp = st.sidebar.radio(
        "Choose competitor to analyze:",
        options=[comp[0] for comp in competitor_options],
        format_func=lambda x: next(
            opt[1] for opt in competitor_options if opt[0] == x),
        key="competitor_selection"
    )

    # Show competitor info
    config = competitor_manager.get_competitor_config(selected_comp)
    st.sidebar.markdown(f"**{config.description}**")
    st.sidebar.markdown(f"**Subreddit:** r/{config.subreddit}")

    return selected_comp


def get_available_reports():
    """Get all available markdown reports from the reports directory"""
    reports_dir = 'reports'
    report_files = []

    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith('.md'):
                report_files.append(file)

    # Sort alphabetically for consistent ordering
    report_files.sort()
    return report_files


def format_report_display_name(filename):
    """Convert filename to user-friendly display name"""
    # Remove .md extension and replace underscores with spaces
    name = filename.replace('.md', '').replace('_', ' ')
    # Capitalize each word
    return ' '.join(word.capitalize() for word in name.split())


def render_strategic_reports_page():
    """Render strategic reports section"""
    st.markdown("""
    <div class="insight-box">
        <h1>Strategic Reports</h1>
        <p>Comprehensive strategic analysis based on competitive intelligence and user research</p>
    </div>
    """, unsafe_allow_html=True)

    # Get available reports
    available_reports = get_available_reports()

    if not available_reports:
        st.error("No reports found in the reports directory.")
        return

    # Create display names for reports
    report_display_names = [format_report_display_name(
        filename) for filename in available_reports]

    # Add legacy reports from root directory if they exist
    legacy_reports = []
    legacy_files = []

    if os.path.exists('strategic_synthesis_report.md'):
        legacy_reports.append("Strategic Synthesis (Root)")
        legacy_files.append('strategic_synthesis_report.md')

    if os.path.exists('competitive_counter_strategies.md'):
        legacy_reports.append("Competitive Counter-Strategies (Root)")
        legacy_files.append('competitive_counter_strategies.md')

    if os.path.exists('detailed_feature_roadmap.md'):
        legacy_reports.append("Feature Roadmap (Root)")
        legacy_files.append('detailed_feature_roadmap.md')

    # Combine all options
    all_display_names = report_display_names + legacy_reports
    all_files = [f"reports/{f}" for f in available_reports] + legacy_files

    # Strategic reports selection
    st.sidebar.markdown("## Strategic Reports")
    st.sidebar.markdown(f"**Available Reports:** {len(all_display_names)}")

    selected_display_name = st.sidebar.radio(
        "Select Report:",
        all_display_names,
        key="strategic_report_selection"
    )

    # Get the corresponding file path
    selected_index = all_display_names.index(selected_display_name)
    selected_file = all_files[selected_index]

    # Display the selected report
    st.header(selected_display_name)

    try:
        with open(selected_file, 'r', encoding='utf-8') as f:
            content = f.read()
        st.markdown(content)
    except FileNotFoundError:
        st.error(f"Report file not found: {selected_file}")
    except Exception as e:
        st.error(f"Error loading report: {str(e)}")


def render_user_research_page():
    """Render user research section"""
    st.markdown("""
    <div class="insight-box">
        <h1>User Research</h1>
        <p>Comprehensive findings from user interviews and research</p>
    </div>
    """, unsafe_allow_html=True)

    st.header("User Research Final Report")
    try:
        with open('user_research_final_report.md', 'r', encoding='utf-8') as f:
            content = f.read()
        st.markdown(content)
    except FileNotFoundError:
        st.error(
            "User research report not found. Please ensure the report file is available.")


def render_automation_intelligence_page():
    """Render automation intelligence section"""
    st.markdown("""
    <div class="insight-box">
        <h1>🤖 Automation Intelligence</h1>
        <p>Real-time competitive intelligence monitoring and market opportunity detection</p>
    </div>
    """, unsafe_allow_html=True)

    # Status overview
    st.header("System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Check if automation system is running
        automation_status = "🟢 Active" if os.path.exists('automation_data') else "🔴 Inactive"
        st.metric("Automation Status", automation_status)
    
    with col2:
        # Count of alerts today
        today_alerts_count = 0
        if os.path.exists('automation_data/alerts_history.json'):
            try:
                with open('automation_data/alerts_history.json', 'r') as f:
                    alerts = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                today_alerts_count = len([a for a in alerts if a.get('timestamp', '')[:10] == today])
            except:
                pass
        st.metric("Alerts Today", today_alerts_count)
    
    with col3:
        # Opportunities identified
        opportunities_count = 0
        if os.path.exists('automation_data/opportunities_history.json'):
            try:
                with open('automation_data/opportunities_history.json', 'r') as f:
                    opportunities = json.load(f)
                opportunities_count = len(opportunities)
            except:
                pass
        st.metric("Opportunities Identified", opportunities_count)
    
    with col4:
        # Competitors monitored
        monitored_count = len(competitor_manager.get_available_competitors())
        st.metric("Competitors Monitored", monitored_count)

    # Recent Alerts Section
    st.header("🚨 Recent Alerts")
    
    if os.path.exists('automation_data/alerts_history.json'):
        try:
            with open('automation_data/alerts_history.json', 'r') as f:
                alerts = json.load(f)
            
            if alerts:
                # Sort by timestamp, most recent first
                alerts_sorted = sorted(alerts, key=lambda x: x.get('timestamp', ''), reverse=True)
                recent_alerts = alerts_sorted[:10]  # Show latest 10
                
                for alert in recent_alerts:
                    severity_color = {
                        'critical': 'red',
                        'high': 'orange', 
                        'medium': 'blue',
                        'low': 'green'
                    }.get(alert.get('severity', 'medium'), 'blue')
                    
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟡',
                        'medium': '🔵',
                        'low': '🟢'
                    }.get(alert.get('severity', 'medium'), '🔵')
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="border-left: 4px solid {severity_color}; padding-left: 1rem; margin: 1rem 0; background-color: #f8f9fa; padding: 1rem;">
                            <h4>{severity_emoji} {alert.get('title', 'Alert')}</h4>
                            <p><strong>Competitor:</strong> {alert.get('competitor', 'Unknown')}</p>
                            <p><strong>Type:</strong> {alert.get('alert_type', 'Unknown')}</p>
                            <p>{alert.get('description', 'No description available')}</p>
                            <p><strong>Recommended Action:</strong> {alert.get('recommended_action', 'Monitor situation')}</p>
                            <small>🕒 {alert.get('timestamp', 'Unknown time')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No alerts generated yet. The automation system may still be collecting initial data.")
        
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
    else:
        st.info("Automation system not yet initialized. Run the competitive intelligence automation to start monitoring.")

    # Market Opportunities Section
    st.header("📈 Market Opportunities")
    
    if os.path.exists('automation_data/opportunities_history.json'):
        try:
            with open('automation_data/opportunities_history.json', 'r') as f:
                opportunities = json.load(f)
            
            if opportunities:
                # Filter for high-value opportunities
                high_value_ops = [op for op in opportunities 
                                if op.get('urgency') in ['high', 'critical'] or 
                                   op.get('market_size_indicator') in ['large', 'massive']]
                
                if high_value_ops:
                    st.subheader("High-Value Opportunities")
                    for opp in high_value_ops[:5]:  # Show top 5
                        urgency_emoji = {
                            'critical': '🔥',
                            'high': '⚡',
                            'medium': '📋',
                            'low': '💡'
                        }.get(opp.get('urgency', 'medium'), '📋')
                        
                        market_size_emoji = {
                            'massive': '🌍',
                            'large': '🏢',
                            'medium': '🏪',
                            'small': '🏠'
                        }.get(opp.get('market_size_indicator', 'medium'), '🏪')
                        
                        with st.expander(f"{urgency_emoji} {market_size_emoji} {opp.get('title', 'Opportunity')}"):
                            st.markdown(f"**Type:** {opp.get('opportunity_type', 'Unknown')}")
                            st.markdown(f"**Market Size:** {opp.get('market_size_indicator', 'Medium')}")
                            st.markdown(f"**Urgency:** {opp.get('urgency', 'Medium')}")
                            st.markdown(f"**Confidence:** {opp.get('confidence', 0.5):.1%}")
                            st.markdown(f"**Description:** {opp.get('description', 'No description available')}")
                            st.markdown(f"**Recommended Response:** {opp.get('recommended_response', 'Monitor and assess')}")
                            
                            if opp.get('supporting_evidence'):
                                st.markdown("**Supporting Evidence:**")
                                for evidence in opp['supporting_evidence'][:3]:  # Show top 3
                                    st.markdown(f"- {evidence}")
                
                # Show all opportunities in table format
                st.subheader("All Opportunities")
                opp_df = pd.DataFrame(opportunities)
                if not opp_df.empty:
                    display_df = opp_df[['title', 'opportunity_type', 'market_size_indicator', 'urgency', 'confidence']].copy()
                    display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.1%}")
                    st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No market opportunities identified yet.")
        
        except Exception as e:
            st.error(f"Error loading opportunities: {e}")
    else:
        st.info("Market opportunity tracking not yet available.")

    # Sentiment Monitoring Section
    st.header("📊 Sentiment Monitoring")
    
    if os.path.exists('automation_data/sentiment_history.json'):
        try:
            with open('automation_data/sentiment_history.json', 'r') as f:
                sentiment_history = json.load(f)
            
            if sentiment_history:
                # Process sentiment data for visualization
                sentiment_data = []
                for key, score in sentiment_history.items():
                    if '_' in key:
                        competitor, date = key.rsplit('_', 1)
                        sentiment_data.append({
                            'competitor': competitor,
                            'date': date,
                            'sentiment': score
                        })
                
                if sentiment_data:
                    sentiment_df = pd.DataFrame(sentiment_data)
                    
                    # Create sentiment trend chart
                    fig = px.line(sentiment_df, 
                                x='date', 
                                y='sentiment', 
                                color='competitor',
                                title='Competitor Sentiment Trends',
                                labels={'sentiment': 'Sentiment Score', 'date': 'Date'})
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Current sentiment overview
                    st.subheader("Current Sentiment Scores")
                    latest_sentiment = sentiment_df.groupby('competitor')['sentiment'].last().sort_values(ascending=False)
                    
                    cols = st.columns(min(len(latest_sentiment), 4))
                    for i, (competitor, score) in enumerate(latest_sentiment.items()):
                        col_idx = i % 4
                        with cols[col_idx]:
                            sentiment_emoji = "😊" if score > 0.1 else "😐" if score > -0.1 else "😞"
                            color = "green" if score > 0.1 else "gray" if score > -0.1 else "red"
                            st.markdown(f"""
                            <div style="text-align: center; padding: 1rem; border: 1px solid {color}; border-radius: 0.5rem;">
                                <h4>{competitor.title()}</h4>
                                <h2 style="color: {color};">{sentiment_emoji}</h2>
                                <p>{score:.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No sentiment data collected yet.")
        
        except Exception as e:
            st.error(f"Error loading sentiment data: {e}")
    else:
        st.info("Sentiment monitoring not yet initialized.")

    # Automation Controls
    st.header("⚙️ Automation Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Run Analysis Now"):
            st.info("Manual analysis trigger would run the automation system once. Implementation requires API keys and background processing.")
    
    with col2:
        if st.button("📊 Export Data"):
            st.info("Data export functionality would generate CSV/JSON files of all collected intelligence. Implementation requires file generation system.")
    
    with col3:
        if st.button("⚡ Setup Automation"):
            st.info("This would guide you through setting up automated monitoring. See automation_setup.md for detailed instructions.")
    
    # Setup Instructions
    st.header("🛠️ Setup Instructions")
    
    with st.expander("How to Enable Automation Intelligence"):
        st.markdown("""
        To enable the full automation intelligence system:
        
        1. **Install Dependencies:**
           ```bash
           pip install -r requirements_automation.txt
           ```
        
        2. **Configure APIs:**
           - Create `.env` file with Reddit and Gemini API keys
           - See `automation_setup.md` for detailed instructions
        
        3. **Start Monitoring:**
           ```bash
           python competitive_intelligence_automation.py --mode schedule
           ```
        
        4. **View Results:**
           - Real-time alerts will appear in this dashboard
           - Daily reports generated automatically
           - Email notifications for critical alerts
        
        📖 **Full Setup Guide:** Check `automation_setup.md` for complete instructions
        """)


def render_competitive_analysis_page():
    """Render competitive analysis section"""
    # Render competitor selection sidebar
    selected_competitor = render_competitor_sidebar()

    # Load competitor data
    result = load_competitor_data(selected_competitor)
    if result is None or result[0] is None:
        st.error(f"Could not load data for {selected_competitor}")
        st.info(
            "This competitor analysis is not yet available. Data collection needed.")
        st.stop()

    df, competitor_config = result

    # Dynamic header based on selected competitor
    st.markdown(f"""
    <div class="insight-box">
        <h1>{competitor_config.display_name} Analysis Dashboard</h1>
        <p>Interactive Competitive Intelligence & User Research Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Summary metrics (always show full dataset)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Posts", f"{len(df):,}")

    with col2:
        avg_score = df['score'].mean()
        st.metric("Avg Score", f"{avg_score:.1f}")

    with col3:
        avg_comments = df['num_comments'].mean()
        st.metric("Avg Comments", f"{avg_comments:.1f}")

    with col4:
        if 'sentiment_score' in df.columns:
            avg_sentiment = df['sentiment_score'].mean()
            sentiment_text = "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
            st.metric("Avg Sentiment",
                      f"{sentiment_text} ({avg_sentiment:.2f})")
        else:
            st.metric("LLM Analysis", "Not Available")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Analytics", "Posts Explorer", "Strategic Report", "AI Insights"])

    with tab1:
        st.header("Analytics Dashboard")

        col1, col2 = st.columns(2)

        with col1:
            # Sentiment chart
            sentiment_chart = create_sentiment_chart(df, competitor_config)
            if sentiment_chart:
                st.plotly_chart(sentiment_chart, use_container_width=True)
            else:
                st.info("Run LLM analysis to see sentiment distribution")

        with col2:
            # Category chart
            category_chart = create_category_chart(df)
            if category_chart:
                st.plotly_chart(category_chart, use_container_width=True)
            else:
                st.info("Run LLM analysis to see category breakdown")

        # Timeline chart
        timeline_chart = create_timeline_chart(df, competitor_config)
        st.plotly_chart(timeline_chart, use_container_width=True)

        # Top posts table
        st.subheader("Top Posts by Score")
        top_posts = df.nlargest(10, 'score')[
            ['title', 'score', 'num_comments', 'author', 'created_utc']]
        st.dataframe(top_posts, use_container_width=True)

    with tab2:
        st.header("Posts Explorer")

        # Filters in main content area (not sidebar)
        st.subheader("Filters & Controls")

        # Create filter columns
        col1, col2, col3 = st.columns(3)

        with col1:
            # Date range filter
            date_range = st.date_input(
                "Date Range",
                value=(df['created_utc'].dt.date.min(),
                       df['created_utc'].dt.date.max()),
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
                categories = ['All'] + \
                    sorted(df[category_col].dropna().unique().tolist())
                selected_category = st.selectbox("Category", categories)
            else:
                st.info("Categories not available")

        with col3:
            # Score filter
            score_range = st.slider(
                "Score Range",
                min_value=int(df['score'].min()),
                max_value=int(df['score'].max()),
                value=(int(df['score'].min()), int(df['score'].max()))
            )

        # Search filter (full width)
        search_term = st.text_input("Search in titles and content", "")

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
            filtered_df = filtered_df[filtered_df[category_col]
                                      == selected_category]

        # Score filter
        filtered_df = filtered_df[
            (filtered_df['score'] >= score_range[0]) &
            (filtered_df['score'] <= score_range[1])
        ]

        # Search filter
        if search_term:
            mask = (
                filtered_df['title'].str.contains(search_term, case=False, na=False) |
                filtered_df['selftext'].str.contains(
                    search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]

        # Show filtered results summary
        if len(filtered_df) != len(df):
            st.info(
                f"Showing {len(filtered_df)} posts (filtered from {len(df)} total)")

        # Sort options
        col1, col2 = st.columns([2, 1])
        with col1:
            sort_option = st.selectbox(
                "Sort by",
                ["Score (High to Low)", "Score (Low to High)", "Comments (High to Low)",
                 "Date (Newest First)", "Date (Oldest First)"]
            )
        with col2:
            posts_per_page = st.selectbox(
                "Posts per page", [10, 25, 50, 100], index=1)

        # Apply sorting
        if sort_option == "Score (High to Low)":
            display_df = filtered_df.sort_values('score', ascending=False)
        elif sort_option == "Score (Low to High)":
            display_df = filtered_df.sort_values('score', ascending=True)
        elif sort_option == "Comments (High to Low)":
            display_df = filtered_df.sort_values(
                'num_comments', ascending=False)
        elif sort_option == "Date (Newest First)":
            display_df = filtered_df.sort_values(
                'created_utc', ascending=False)
        else:  # Date (Oldest First)
            display_df = filtered_df.sort_values('created_utc', ascending=True)

        # Pagination
        total_pages = (len(display_df) - 1) // posts_per_page + \
            1 if len(display_df) > 0 else 1
        page = st.number_input("Page", min_value=1,
                               max_value=total_pages, value=1)

        # Display posts
        if len(display_df) == 0:
            st.warning(
                "No posts found matching your filters. Try adjusting your search criteria.")
        else:
            st.write(
                f"Showing page {page} of {total_pages} ({len(display_df)} posts total)")

            start_idx = (page - 1) * posts_per_page
            end_idx = start_idx + posts_per_page

            for _, post in display_df.iloc[start_idx:end_idx].iterrows():
                render_post_card(post)

    with tab3:
        st.header("Comprehensive Strategic Report")

        report = load_comprehensive_report(selected_competitor)
        if report:
            st.markdown(report)
        else:
            st.warning(
                f"Comprehensive report not available for {competitor_config.display_name}. Run the summary report generator first.")

    with tab4:
        st.header("AI Insights Summary")

        batch_summaries = load_batch_summaries(selected_competitor)
        if batch_summaries:
            st.subheader("Key Themes Across All Batches")

            # Aggregate themes
            all_themes = []
            for summary in batch_summaries:
                if 'dominant_themes' in summary:
                    all_themes.extend(summary['dominant_themes'])

            if all_themes:
                theme_counts = Counter(all_themes)
                theme_df = pd.DataFrame(list(theme_counts.items()), columns=[
                                        'Theme', 'Frequency'])

                fig = px.bar(
                    theme_df.head(15),
                    x='Frequency',
                    y='Theme',
                    orientation='h',
                    title="Most Common Themes",
                    color='Frequency',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

            # Display individual batch insights
            st.subheader("Batch Analysis Details")

            # Show first 10 batches
            for i, summary in enumerate(batch_summaries[:10]):
                with st.expander(f"Batch {i+1} Analysis", expanded=False):
                    if 'dominant_themes' in summary:
                        st.write("**Dominant Themes:**")
                        for theme in summary['dominant_themes']:
                            st.write(f"• {theme}")

                    if 'sentiment_trend' in summary:
                        st.write(
                            f"**Sentiment Trend:** {summary['sentiment_trend']}")

                    if 'key_competitive_threats' in summary:
                        st.write("**Key Competitive Threats:**")
                        for threat in summary['key_competitive_threats']:
                            st.write(f"• {threat}")

                    if 'strategic_recommendations' in summary:
                        st.write("**Strategic Recommendations:**")
                        for rec in summary['strategic_recommendations']:
                            st.write(f"• {rec}")
        else:
            st.warning(
                "AI batch summaries not available. Run LLM analysis first.")

    # Footer
    st.markdown("---")
    st.markdown(
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Data Sources:** Reddit r/{competitor_config.subreddit} (NEW & HOT posts)")


def main():
    """Main Streamlit application"""

    # Render main navigation
    selected_page = render_navigation_sidebar()

    # Route to appropriate page
    if selected_page == "Competitive Analysis":
        render_competitive_analysis_page()
    elif selected_page == "Strategic Reports":
        render_strategic_reports_page()
    elif selected_page == "User Research":
        render_user_research_page()
    elif selected_page == "Automation Intelligence":
        render_automation_intelligence_page()


if __name__ == "__main__":
    main()
