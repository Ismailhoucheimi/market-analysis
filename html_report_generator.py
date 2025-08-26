#!/usr/bin/env python3
"""
HTML Report Generator for Notion Reddit Analysis
Creates interactive HTML reports that open in browser
"""

import pandas as pd
import json
import os
import webbrowser
from datetime import datetime
from typing import Dict, List, Any
import config

class HTMLReportGenerator:
    def __init__(self, data_file: str = None):
        self.data_file = data_file or config.PROCESSED_DATA_FILE
        self.df = None
        
        # Ensure output directory exists
        os.makedirs('reports/html', exist_ok=True)
    
    def load_data(self) -> pd.DataFrame:
        """Load processed data"""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
        
        self.df = pd.read_csv(self.data_file)
        self.df['created_utc'] = pd.to_datetime(self.df['created_utc'])
        
        print(f"Loaded {len(self.df)} posts for HTML report")
        return self.df
    
    def load_comprehensive_report(self) -> str:
        """Load the comprehensive summary report if available"""
        report_path = 'reports/comprehensive_notion_analysis.md'
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def prepare_data_for_html(self) -> Dict[str, Any]:
        """Prepare data structure for HTML template"""
        if self.df is None:
            self.load_data()
        
        # Summary statistics
        total_posts = len(self.df)
        date_range = (self.df['created_utc'].min(), self.df['created_utc'].max())
        avg_score = self.df['score'].mean()
        avg_comments = self.df['num_comments'].mean()
        
        # Load comprehensive summary report if available
        comprehensive_report = self.load_comprehensive_report()
        
        # Category distribution
        category_stats = {}
        for category in self.df['predicted_category'].unique():
            category_posts = self.df[self.df['predicted_category'] == category]
            category_stats[category] = {
                'name': config.POST_CATEGORIES.get(category, category),
                'count': len(category_posts),
                'percentage': (len(category_posts) / total_posts * 100),
                'avg_score': category_posts['score'].mean(),
                'avg_comments': category_posts['num_comments'].mean(),
                'posts': []
            }
            
            # Add posts for this category
            for _, post in category_posts.iterrows():
                post_data = {
                    'title': post['title'],
                    'selftext': post['selftext'] if pd.notna(post['selftext']) else '',
                    'score': int(post['score']) if pd.notna(post['score']) else 0,
                    'num_comments': int(post['num_comments']) if pd.notna(post['num_comments']) else 0,
                    'author': post['author'] if pd.notna(post['author']) else '[deleted]',
                    'created_utc': post['created_utc'].strftime('%Y-%m-%d %H:%M'),
                    'permalink': post['permalink'] if pd.notna(post['permalink']) else '',
                    'flair_text': post['flair_text'] if pd.notna(post['flair_text']) else '',
                    'upvote_ratio': post['upvote_ratio'] if pd.notna(post['upvote_ratio']) else None,
                    # LLM analysis fields
                    'sentiment_score': post.get('sentiment_score', 0.0) if pd.notna(post.get('sentiment_score', 0.0)) else 0.0,
                    'urgency_level': int(post.get('urgency_level', 2)) if pd.notna(post.get('urgency_level', 2)) else 2,
                    'business_impact': int(post.get('business_impact', 2)) if pd.notna(post.get('business_impact', 2)) else 2,
                    'key_insights': post.get('key_insights', '') if pd.notna(post.get('key_insights', '')) else '',
                    'user_persona': post.get('user_persona', '') if pd.notna(post.get('user_persona', '')) else '',
                    'competitive_intelligence': post.get('competitive_intelligence', '') if pd.notna(post.get('competitive_intelligence', '')) else ''
                }
                category_stats[category]['posts'].append(post_data)
            
            # Sort posts by score descending
            category_stats[category]['posts'].sort(key=lambda x: x['score'], reverse=True)
        
        # Sort categories by post count
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        
        return {
            'summary': {
                'total_posts': total_posts,
                'date_range_start': date_range[0].strftime('%Y-%m-%d'),
                'date_range_end': date_range[1].strftime('%Y-%m-%d'),
                'avg_score': round(avg_score, 1),
                'avg_comments': round(avg_comments, 1),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'categories': dict(sorted_categories),
            'comprehensive_report': comprehensive_report
        }
    
    def generate_html_template(self) -> str:
        """Generate the HTML template with embedded JavaScript"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notion Reddit Analysis Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .comprehensive-report {
            background: white;
            border-radius: 10px;
            margin: 30px 0;
            padding: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        
        .toggle-btn, .show-report-btn {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .toggle-btn:hover, .show-report-btn:hover {
            background: #5a6fd8;
        }
        
        .report-content {
            line-height: 1.6;
            max-height: 600px;
            overflow-y: auto;
            padding-right: 10px;
        }
        
        .report-content h1, .report-content h2, .report-content h3 {
            color: #333;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        
        .report-content h1 { font-size: 1.8em; }
        .report-content h2 { font-size: 1.5em; color: #667eea; }
        .report-content h3 { font-size: 1.3em; }
        
        .report-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .report-content th, .report-content td {
            border: 1px solid #e0e0e0;
            padding: 12px 15px;
            text-align: left;
            vertical-align: top;
        }
        
        .report-content th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }
        
        .report-content tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .report-content tr:hover {
            background-color: #e3f2fd;
        }
        
        .report-content td {
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .report-content ul, .report-content ol {
            margin: 10px 0;
            padding-left: 25px;
        }
        
        .report-content li {
            margin: 5px 0;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .summary-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .summary-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }
        
        .controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .filter-controls {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .filter-group label {
            font-weight: 500;
            color: #555;
        }
        
        select, input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .category-section {
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .category-header {
            background: #667eea;
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s;
        }
        
        .category-header:hover {
            background: #5a67d8;
        }
        
        .category-title {
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .category-stats {
            display: flex;
            gap: 20px;
            align-items: center;
            font-size: 0.9rem;
        }
        
        .toggle-icon {
            transition: transform 0.3s;
        }
        
        .toggle-icon.rotated {
            transform: rotate(180deg);
        }
        
        .category-content {
            display: none;
            padding: 0;
        }
        
        .category-content.active {
            display: block;
        }
        
        .post {
            border-bottom: 1px solid #eee;
            padding: 20px;
            transition: background-color 0.3s;
        }
        
        .post:last-child {
            border-bottom: none;
        }
        
        .post:hover {
            background-color: #f8f9ff;
        }
        
        .post-header {
            display: flex;
            justify-content: between;
            align-items: flex-start;
            margin-bottom: 10px;
            gap: 15px;
        }
        
        .post-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            flex: 1;
            line-height: 1.4;
        }
        
        .post-meta {
            display: flex;
            gap: 15px;
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }
        
        .post-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .post-content {
            margin-bottom: 15px;
            line-height: 1.6;
            color: #555;
        }
        
        .post-content.collapsed {
            max-height: 100px;
            overflow: hidden;
            position: relative;
        }
        
        .post-content.collapsed::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30px;
            background: linear-gradient(transparent, white);
        }
        
        .expand-btn {
            color: #667eea;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        .expand-btn:hover {
            text-decoration: underline;
        }
        
        .post-actions {
            display: flex;
            gap: 10px;
        }
        
        .action-btn {
            padding: 5px 10px;
            background: #f1f3f4;
            border: none;
            border-radius: 5px;
            color: #667eea;
            text-decoration: none;
            font-size: 0.85rem;
            transition: background-color 0.3s;
        }
        
        .action-btn:hover {
            background: #e2e6ea;
        }
        
        .score {
            background: #4CAF50;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: 500;
            font-size: 0.8rem;
        }
        
        .comments {
            background: #2196F3;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: 500;
            font-size: 0.8rem;
        }
        
        .flair {
            background: #FF9800;
            color: white;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .sentiment {
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .sentiment.positive {
            background: #4CAF50;
            color: white;
        }
        
        .sentiment.negative {
            background: #F44336;
            color: white;
        }
        
        .sentiment.neutral {
            background: #9E9E9E;
            color: white;
        }
        
        .urgency {
            background: #FF5722;
            color: white;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .business-impact {
            background: #9C27B0;
            color: white;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .llm-insights {
            background: #f8f9ff;
            border-left: 4px solid #667eea;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        
        .llm-insights h4 {
            color: #667eea;
            margin-bottom: 5px;
            font-size: 0.9rem;
        }
        
        .no-posts {
            padding: 40px;
            text-align: center;
            color: #666;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .filter-controls {
                flex-direction: column;
                align-items: stretch;
            }
            
            .post-header {
                flex-direction: column;
            }
            
            .post-meta {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Notion Reddit Analysis</h1>
            <p>Competitive Intelligence from r/Notion</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Posts</h3>
                <div class="value" id="total-posts">{{summary.total_posts}}</div>
            </div>
            <div class="summary-card">
                <h3>Date Range</h3>
                <div class="value" style="font-size: 1rem;">{{summary.date_range_start}} to {{summary.date_range_end}}</div>
            </div>
            <div class="summary-card">
                <h3>Average Score</h3>
                <div class="value">{{summary.avg_score}}</div>
            </div>
            <div class="summary-card">
                <h3>Average Comments</h3>
                <div class="value">{{summary.avg_comments}}</div>
            </div>
        </div>
        
        <div class="comprehensive-report" id="comprehensive-section" style="display: none;">
            <div class="section-header">
                <h3>📋 Comprehensive Analysis Report</h3>
                <button class="toggle-btn" onclick="toggleSection('comprehensive-section')" style="margin-left: auto;">Hide Report</button>
            </div>
            <div class="report-content" id="comprehensive-content">
                <!-- Report content will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="controls">
            <h3 style="margin-bottom: 15px;">📊 Filter & Search</h3>
            <button class="show-report-btn" onclick="toggleSection('comprehensive-section')" style="margin-bottom: 15px; padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">📋 Show Comprehensive Report</button>
            <div class="filter-controls">
                <div class="filter-group">
                    <label for="category-filter">Category:</label>
                    <select id="category-filter">
                        <option value="">All Categories</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="sort-posts">Sort by:</label>
                    <select id="sort-posts">
                        <option value="score">Score (High to Low)</option>
                        <option value="comments">Comments (High to Low)</option>
                        <option value="date">Date (Newest First)</option>
                        <option value="title">Title (A-Z)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="search-posts">Search:</label>
                    <input type="text" id="search-posts" placeholder="Search in titles and content...">
                </div>
                <div class="filter-group">
                    <label for="min-score">Min Score:</label>
                    <input type="number" id="min-score" placeholder="0" min="0">
                </div>
            </div>
        </div>
        
        <div id="categories-container">
            <!-- Categories will be populated by JavaScript -->
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: white; border-radius: 10px; color: #666;">
            <p>📈 Generated on {{summary.generated_at}} by Notion Reddit Analysis Pipeline</p>
        </div>
    </div>
    
    <script>
        // Data will be injected here
        const data = {{data_json}};
        
        let currentData = JSON.parse(JSON.stringify(data)); // Deep copy
        
        // Test function - call this from browser console to test data access
        function testReportData() {
            console.log('Testing report data access...');
            console.log('Data object exists:', typeof data !== 'undefined');
            console.log('Comprehensive report exists:', !!data.comprehensive_report);
            console.log('Report length:', data.comprehensive_report ? data.comprehensive_report.length : 'N/A');
            if (data.comprehensive_report) {
                console.log('First 200 chars:', data.comprehensive_report.substring(0, 200));
            }
            return data;
        }
        
        // Function to toggle comprehensive report section
        function toggleSection(sectionId) {
            console.log('toggleSection called with:', sectionId);
            const section = document.getElementById(sectionId);
            console.log('Section found:', section ? 'yes' : 'no');
            
            if (!section) {
                console.error('Section not found:', sectionId);
                return;
            }
            
            const isHidden = section.style.display === 'none';
            console.log('Section is hidden:', isHidden);
            
            if (isHidden) {
                section.style.display = 'block';
                console.log('Section shown, now populating content...');
                // Always populate content (force refresh)
                const contentElement = section.querySelector('#comprehensive-content');
                console.log('Current content length:', contentElement.innerHTML.length);
                console.log('Current content:', contentElement.innerHTML.substring(0, 100));
                populateComprehensiveReport();
            } else {
                section.style.display = 'none';
                console.log('Section hidden');
            }
        }
        
        // Function to populate comprehensive report with markdown content
        function populateComprehensiveReport() {
            const content = document.getElementById('comprehensive-content');
            const reportMarkdown = data.comprehensive_report;
            
            console.log('Report markdown length:', reportMarkdown ? reportMarkdown.length : 'undefined');
            console.log('First 100 chars:', reportMarkdown ? reportMarkdown.substring(0, 100) : 'undefined');
            
            if (!reportMarkdown) {
                content.innerHTML = '<p>Comprehensive report not available.</p>';
                return;
            }
            
            // Simple approach: just convert the markdown with basic replacements and preserve formatting
            let html = reportMarkdown
                // Convert headers
                .replace(/^# (.+)$/gm, '<h1>$1</h1>')
                .replace(/^## (.+)$/gm, '<h2>$1</h2>')  
                .replace(/^### (.+)$/gm, '<h3>$1</h3>')
                // Convert bold and italic (fix the escaping issue)
                .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\*(.+?)\\*/g, '<em>$1</em>')
                // Convert code
                .replace(/`(.+?)`/g, '<code>$1</code>')
                // Convert line breaks
                .replace(/\\n/g, '<br>')
                // Handle lists
                .replace(/^- (.+)$/gm, '<li>$1</li>')
                .replace(/^\\* (.+)$/gm, '<li>$1</li>');
            
            // Wrap consecutive <li> elements in <ul>
            html = html.replace(/((<li>.*?<\\/li>\\s*)+)/g, '<ul>$1</ul>');
            
            // Handle tables (simple pattern)
            html = html.replace(/\\|(.+?)\\|/g, (match, content) => {
                const cells = content.split('|').map(cell => cell.trim()).filter(cell => cell);
                return '<tr>' + cells.map(cell => `<td>${cell}</td>`).join('') + '</tr>';
            });
            html = html.replace(/((<tr>.*?<\\/tr>\\s*)+)/g, '<table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">$1</table>');
            
            console.log('Processed HTML length:', html.length);
            console.log('First 200 chars of HTML:', html.substring(0, 200));
            
            content.innerHTML = html;
        }
        
        function renderCategories(categoriesData) {
            const container = document.getElementById('categories-container');
            container.innerHTML = '';
            
            Object.entries(categoriesData).forEach(([categoryKey, category]) => {
                const section = document.createElement('div');
                section.className = 'category-section';
                
                const header = document.createElement('div');
                header.className = 'category-header';
                header.onclick = () => toggleCategory(categoryKey);
                
                header.innerHTML = `
                    <div>
                        <div class="category-title">${category.name}</div>
                        <div class="category-stats">
                            <span>${category.count} posts (${category.percentage.toFixed(1)}%)</span>
                            <span>Avg Score: ${category.avg_score.toFixed(1)}</span>
                            <span>Avg Comments: ${category.avg_comments.toFixed(1)}</span>
                        </div>
                    </div>
                    <div class="toggle-icon" id="toggle-${categoryKey}">▼</div>
                `;
                
                const content = document.createElement('div');
                content.className = 'category-content';
                content.id = `content-${categoryKey}`;
                
                if (category.posts.length === 0) {
                    content.innerHTML = '<div class="no-posts">No posts match the current filters</div>';
                } else {
                    category.posts.forEach(post => {
                        const postElement = createPostElement(post);
                        content.appendChild(postElement);
                    });
                }
                
                section.appendChild(header);
                section.appendChild(content);
                container.appendChild(section);
            });
            
            // Update category filter options
            updateCategoryFilter(categoriesData);
        }
        
        function createPostElement(post) {
            const postDiv = document.createElement('div');
            postDiv.className = 'post';
            
            const hasLongContent = post.selftext.length > 300;
            const shortContent = hasLongContent ? post.selftext.substring(0, 300) + '...' : post.selftext;
            const postId = post.title.replace(/[^a-zA-Z0-9]/g, '');
            
            // Create post header
            const headerDiv = document.createElement('div');
            headerDiv.className = 'post-header';
            headerDiv.innerHTML = `<div class="post-title">${escapeHtml(post.title)}</div>`;
            
            // Create post meta
            const metaDiv = document.createElement('div');
            metaDiv.className = 'post-meta';
            metaDiv.innerHTML = `
                <span class="score">↑ ${post.score}</span>
                <span class="comments">💬 ${post.num_comments}</span>
                <span>👤 u/${escapeHtml(post.author)}</span>
                <span>📅 ${post.created_utc}</span>
                ${post.flair_text ? `<span class="flair">${escapeHtml(post.flair_text)}</span>` : ''}
                ${post.sentiment_score !== 0 ? `<span class="sentiment ${post.sentiment_score > 0 ? 'positive' : post.sentiment_score < 0 ? 'negative' : 'neutral'}">${post.sentiment_score > 0 ? '😊' : post.sentiment_score < 0 ? '😞' : '😐'} ${post.sentiment_score.toFixed(2)}</span>` : ''}
                ${post.urgency_level > 2 ? `<span class="urgency">🚨 Urgency: ${post.urgency_level}/5</span>` : ''}
                ${post.business_impact > 2 ? `<span class="business-impact">💼 Impact: ${post.business_impact}/5</span>` : ''}
            `;
            
            postDiv.appendChild(headerDiv);
            postDiv.appendChild(metaDiv);
            
            // Create post content if exists
            if (post.selftext) {
                const contentDiv = document.createElement('div');
                contentDiv.className = `post-content ${hasLongContent ? 'collapsed' : ''}`;
                contentDiv.id = `content-${postId}`;
                contentDiv.innerHTML = escapeHtml(hasLongContent ? shortContent : post.selftext);
                postDiv.appendChild(contentDiv);
                
                // Add expand button if content is long
                if (hasLongContent) {
                    const expandBtn = document.createElement('div');
                    expandBtn.className = 'expand-btn';
                    expandBtn.textContent = 'Show more...';
                    expandBtn.onclick = () => toggleContent(postId, post.selftext);
                    postDiv.appendChild(expandBtn);
                }
            }
            
            // Add LLM insights if available
            if (post.key_insights || post.user_persona || post.competitive_intelligence) {
                const insightsDiv = document.createElement('div');
                insightsDiv.className = 'llm-insights';
                
                let insightsHTML = '<h4>🧠 AI Analysis</h4>';
                
                if (post.user_persona) {
                    insightsHTML += `<p><strong>User Persona:</strong> ${escapeHtml(post.user_persona)}</p>`;
                }
                
                if (post.key_insights) {
                    insightsHTML += `<p><strong>Key Insights:</strong> ${escapeHtml(post.key_insights)}</p>`;
                }
                
                if (post.competitive_intelligence) {
                    insightsHTML += `<p><strong>Competitive Intelligence:</strong> ${escapeHtml(post.competitive_intelligence)}</p>`;
                }
                
                insightsDiv.innerHTML = insightsHTML;
                postDiv.appendChild(insightsDiv);
            }
            
            // Create post actions
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'post-actions';
            if (post.permalink) {
                actionsDiv.innerHTML = `<a href="${post.permalink}" target="_blank" class="action-btn">View on Reddit</a>`;
            }
            postDiv.appendChild(actionsDiv);
            
            return postDiv;
        }
        
        function toggleCategory(categoryKey) {
            const content = document.getElementById(`content-${categoryKey}`);
            const toggle = document.getElementById(`toggle-${categoryKey}`);
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                toggle.classList.remove('rotated');
            } else {
                content.classList.add('active');
                toggle.classList.add('rotated');
            }
        }
        
        function toggleContent(postId, fullText) {
            const element = document.getElementById(`content-${postId}`);
            const expandBtn = element.nextElementSibling;
            
            if (element.classList.contains('collapsed')) {
                element.classList.remove('collapsed');
                element.innerHTML = escapeHtml(fullText);
                expandBtn.textContent = 'Show less...';
            } else {
                element.classList.add('collapsed');
                element.innerHTML = escapeHtml(fullText.substring(0, 300) + '...');
                expandBtn.textContent = 'Show more...';
            }
        }
        
        function updateCategoryFilter(categoriesData) {
            const select = document.getElementById('category-filter');
            const currentValue = select.value;
            
            // Clear existing options except "All Categories"
            select.innerHTML = '<option value="">All Categories</option>';
            
            Object.entries(categoriesData).forEach(([key, category]) => {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = `${category.name} (${category.count})`;
                select.appendChild(option);
            });
            
            select.value = currentValue;
        }
        
        function applyFilters() {
            const categoryFilter = document.getElementById('category-filter').value;
            const sortBy = document.getElementById('sort-posts').value;
            const searchTerm = document.getElementById('search-posts').value.toLowerCase();
            const minScore = parseInt(document.getElementById('min-score').value) || 0;
            
            // Start with original data
            const filteredData = {};
            
            Object.entries(data.categories).forEach(([categoryKey, category]) => {
                let posts = [...category.posts];
                
                // Apply search filter
                if (searchTerm) {
                    posts = posts.filter(post => 
                        post.title.toLowerCase().includes(searchTerm) ||
                        post.selftext.toLowerCase().includes(searchTerm)
                    );
                }
                
                // Apply minimum score filter
                posts = posts.filter(post => post.score >= minScore);
                
                // Apply category filter
                if (!categoryFilter || categoryKey === categoryFilter) {
                    // Sort posts
                    posts.sort((a, b) => {
                        switch (sortBy) {
                            case 'score':
                                return b.score - a.score;
                            case 'comments':
                                return b.num_comments - a.num_comments;
                            case 'date':
                                return new Date(b.created_utc) - new Date(a.created_utc);
                            case 'title':
                                return a.title.localeCompare(b.title);
                            default:
                                return b.score - a.score;
                        }
                    });
                    
                    filteredData[categoryKey] = {
                        ...category,
                        posts: posts,
                        count: posts.length,
                        percentage: posts.length / data.summary.total_posts * 100
                    };
                }
            });
            
            currentData = { ...data, categories: filteredData };
            renderCategories(currentData.categories);
        }
        
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
        
        // Event listeners
        document.getElementById('category-filter').addEventListener('change', applyFilters);
        document.getElementById('sort-posts').addEventListener('change', applyFilters);
        document.getElementById('search-posts').addEventListener('input', applyFilters);
        document.getElementById('min-score').addEventListener('input', applyFilters);
        
        // Initialize
        renderCategories(data.categories);
        
        // Expand all categories by default
        Object.keys(data.categories).forEach(categoryKey => {
            toggleCategory(categoryKey);
        });
    </script>
</body>
</html>'''
    
    def generate_html_report(self, filename: str = None, open_browser: bool = True) -> str:
        """Generate HTML report and optionally open in browser"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reports/html/notion_analysis_{timestamp}.html'
        
        # Prepare data
        report_data = self.prepare_data_for_html()
        
        # Generate HTML
        template = self.generate_html_template()
        
        # Replace template variables
        html_content = template.replace('{{summary.total_posts}}', str(report_data['summary']['total_posts']))
        html_content = html_content.replace('{{summary.date_range_start}}', report_data['summary']['date_range_start'])
        html_content = html_content.replace('{{summary.date_range_end}}', report_data['summary']['date_range_end'])
        html_content = html_content.replace('{{summary.avg_score}}', str(report_data['summary']['avg_score']))
        html_content = html_content.replace('{{summary.avg_comments}}', str(report_data['summary']['avg_comments']))
        html_content = html_content.replace('{{summary.generated_at}}', report_data['summary']['generated_at'])
        
        # Inject data as JSON
        data_json = json.dumps(report_data, indent=2)
        html_content = html_content.replace('{{data_json}}', data_json)
        
        # Write HTML file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report generated: {filename}")
        
        # Open in browser
        if open_browser:
            file_url = f"file://{os.path.abspath(filename)}"
            webbrowser.open(file_url)
            print(f"🌐 Opening in browser: {file_url}")
        
        return filename

def main():
    """Test the HTML report generator"""
    try:
        generator = HTMLReportGenerator()
        generator.load_data()
        
        # Generate HTML report
        html_file = generator.generate_html_report()
        
        print(f"\n🎉 HTML Report Generated Successfully!")
        print(f"📁 File: {html_file}")
        print(f"🌐 Should open automatically in your default browser")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please run the analysis pipeline first:")
        print("  python main_pipeline_scraper.py quick")

if __name__ == "__main__":
    main()