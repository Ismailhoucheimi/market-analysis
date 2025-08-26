#!/usr/bin/env python3
"""
Tailwind-based HTML Report Generator for Notion Reddit Analysis
Creates interactive HTML reports using Tailwind CSS
"""

import pandas as pd
import json
import os
import webbrowser
from datetime import datetime
from typing import Dict, Any
import config

class TailwindHTMLReportGenerator:
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
        
        print(f"Loaded {len(self.df)} posts for Tailwind HTML report")
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
                'percentage': (len(category_posts) / total_posts) * 100,
                'avg_score': category_posts['score'].mean(),
                'avg_comments': category_posts['num_comments'].mean(),
                'posts': category_posts.to_dict('records')
            }
        
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
    
    def load_tailwind_template(self) -> str:
        """Load the Tailwind HTML template"""
        template_path = 'templates/tailwind_template.html'
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Tailwind template file not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def generate_tailwind_html_report(self, output_filename: str = None) -> str:
        """Generate the Tailwind CSS HTML report"""
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f'reports/html/notion_analysis_tailwind_{timestamp}.html'
        
        # Prepare data
        data = self.prepare_data_for_html()
        
        # Load template
        template = self.load_tailwind_template()
        
        # Replace placeholders in template
        html_content = template.replace('{{data_json}}', json.dumps(data, default=str, indent=2))
        html_content = html_content.replace('{{summary.total_posts}}', str(data['summary']['total_posts']))
        html_content = html_content.replace('{{summary.date_range_start}}', data['summary']['date_range_start'])
        html_content = html_content.replace('{{summary.date_range_end}}', data['summary']['date_range_end'])
        html_content = html_content.replace('{{summary.avg_score}}', str(data['summary']['avg_score']))
        html_content = html_content.replace('{{summary.avg_comments}}', str(data['summary']['avg_comments']))
        
        # Embed the Tailwind JavaScript functionality
        html_content = self.embed_tailwind_js(html_content)
        
        # Write HTML file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Tailwind HTML report generated: {output_filename}")
        
        # Open in browser
        file_path = os.path.abspath(output_filename)
        file_url = f"file:///{file_path.replace(os.sep, '/')}"
        print(f"🌐 Opening in browser: {file_url}")
        
        try:
            webbrowser.open(file_url)
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print(f"Please open this file manually: {file_path}")
        
        return output_filename
    
    def embed_tailwind_js(self, html_content: str) -> str:
        """Embed Tailwind-specific JavaScript directly into HTML"""
        
        # Load and embed JavaScript
        js_path = 'scripts/tailwind_report_functionality.js'
        if os.path.exists(js_path):
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            html_content = html_content.replace(
                '<script src="../scripts/tailwind_report_functionality.js"></script>',
                f'<script>{js_content}</script>'
            )
        
        return html_content

def main():
    """Generate the Tailwind HTML report"""
    try:
        generator = TailwindHTMLReportGenerator()
        output_file = generator.generate_tailwind_html_report()
        print(f"\n🎯 Tailwind HTML Report Generated Successfully!")
        print(f"📁 Location: {output_file}")
        
    except Exception as e:
        print(f"❌ Error generating Tailwind HTML report: {e}")

if __name__ == "__main__":
    main()