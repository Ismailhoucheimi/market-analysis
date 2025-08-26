#!/usr/bin/env python3
"""
Multi-Competitor Analysis Configuration System
Manages competitor configurations and data paths
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import os
import json

@dataclass
class CompetitorConfig:
    """Configuration for a competitor analysis"""
    name: str                    # Internal identifier: "notion", "chatgpt", "obsidian", "airtable"
    display_name: str           # Display name: "Notion", "ChatGPT", "Obsidian", "Airtable"
    subreddit: str              # Subreddit name without 'r/': "Notion", "ChatGPT", "ObsidianMD", "Airtable"
    color_scheme: Dict[str, str] # Brand colors for charts
    data_dir: str               # Data directory path
    categories: Dict[str, str]  # Product-specific categories
    logo_emoji: str             # Emoji for branding
    description: str            # Short description

class CompetitorDataManager:
    """Manages competitor data loading and configuration"""
    
    def __init__(self):
        self.competitors = self._initialize_competitors()
    
    def _initialize_competitors(self) -> Dict[str, CompetitorConfig]:
        """Initialize competitor configurations"""
        return {
            "notion": CompetitorConfig(
                name="notion",
                display_name="Notion", 
                subreddit="Notion",
                color_scheme={
                    "primary": "#000000",
                    "secondary": "#37352f",
                    "accent": "#0f62fe"
                },
                data_dir="competitors/notion",
                categories={
                    'help_support': 'Help/Support',
                    'feature_request': 'Feature Requests', 
                    'bug_report': 'Bug Reports',
                    'template_sharing': 'Template Sharing',
                    'workflow_showcase': 'Workflow Showcase',
                    'integration_request': 'Integration Requests',
                    'praise': 'Praise/Positive Feedback',
                    'criticism': 'Criticism/Complaints',
                    'comparison': 'Comparison/Alternatives',
                    'pricing': 'Pricing/Plan Discussion',
                    'mobile_feedback': 'Mobile App Feedback',
                    'performance': 'Performance Issues'
                },
                logo_emoji="📝",
                description="All-in-one workspace for notes, docs, and collaboration"
            ),
            
            "chatgpt": CompetitorConfig(
                name="chatgpt", 
                display_name="ChatGPT",
                subreddit="ChatGPT",
                color_scheme={
                    "primary": "#00D084",
                    "secondary": "#19C37D", 
                    "accent": "#00A06A"
                },
                data_dir="competitors/chatgpt",
                categories={
                    'help_support': 'Help/Support',
                    'feature_request': 'Feature Requests',
                    'bug_report': 'Bug Reports', 
                    'use_case': 'Use Cases/Applications',
                    'prompt_sharing': 'Prompt Sharing',
                    'api_discussion': 'API Discussion',
                    'praise': 'Praise/Positive Feedback',
                    'criticism': 'Criticism/Complaints',
                    'comparison': 'AI Model Comparisons',
                    'pricing': 'Pricing/Subscription Discussion',
                    'ethics_safety': 'Ethics/Safety Concerns',
                    'performance': 'Performance Issues'
                },
                logo_emoji="🤖",
                description="AI-powered conversational assistant and productivity tool"
            ),
            
            "obsidian": CompetitorConfig(
                name="obsidian",
                display_name="Obsidian", 
                subreddit="ObsidianMD",
                color_scheme={
                    "primary": "#483699",
                    "secondary": "#7C3AED",
                    "accent": "#8B5CF6"
                },
                data_dir="competitors/obsidian", 
                categories={
                    'help_support': 'Help/Support',
                    'feature_request': 'Feature Requests',
                    'plugin_discussion': 'Plugin Discussion',
                    'template_sharing': 'Template/Vault Sharing',
                    'workflow_showcase': 'Workflow Showcase',
                    'theme_sharing': 'Theme Sharing',
                    'praise': 'Praise/Positive Feedback', 
                    'criticism': 'Criticism/Complaints',
                    'comparison': 'Comparison/Alternatives',
                    'mobile_feedback': 'Mobile App Feedback',
                    'performance': 'Performance Issues',
                    'sync_issues': 'Sync Issues'
                },
                logo_emoji="🔗", 
                description="Knowledge management app with linked note-taking"
            ),
            
            "airtable": CompetitorConfig(
                name="airtable",
                display_name="Airtable",
                subreddit="Airtable", 
                color_scheme={
                    "primary": "#FCBF00",
                    "secondary": "#F82B60",
                    "accent": "#18BFFF"
                },
                data_dir="competitors/airtable",
                categories={
                    'help_support': 'Help/Support',
                    'feature_request': 'Feature Requests',
                    'bug_report': 'Bug Reports',
                    'template_sharing': 'Base/Template Sharing',
                    'automation_discussion': 'Automation Discussion',
                    'integration_request': 'Integration Requests', 
                    'praise': 'Praise/Positive Feedback',
                    'criticism': 'Criticism/Complaints',
                    'comparison': 'Comparison/Alternatives',
                    'pricing': 'Pricing/Plan Discussion',
                    'api_discussion': 'API Discussion',
                    'performance': 'Performance Issues'
                },
                logo_emoji="📊",
                description="Cloud-based database and collaboration platform"
            ),
            
            "jira": CompetitorConfig(
                name="jira",
                display_name="Jira",
                subreddit="jira", 
                color_scheme={
                    "primary": "#0052CC",
                    "secondary": "#2684FF",
                    "accent": "#0065FF"
                },
                data_dir="competitors/jira",
                categories={
                    'help_support': 'Help/Support',
                    'feature_request': 'Feature Requests',
                    'bug_report': 'Bug Reports',
                    'workflow_discussion': 'Workflow Discussion',
                    'automation_discussion': 'Automation Discussion',
                    'integration_request': 'Integration Requests',
                    'praise': 'Praise/Positive Feedback',
                    'criticism': 'Criticism/Complaints',
                    'comparison': 'Comparison/Alternatives',
                    'pricing': 'Pricing/Plan Discussion',
                    'admin_discussion': 'Admin/Configuration',
                    'performance': 'Performance Issues'
                },
                logo_emoji="🔵",
                description="Issue tracking and project management tool"
            ),
            
            "gemini": CompetitorConfig(
                name="gemini",
                display_name="Google Gemini",
                subreddit="Bard", 
                color_scheme={
                    "primary": "#4285F4",
                    "secondary": "#34A853",
                    "accent": "#FBBC04"
                },
                data_dir="competitors/gemini",
                categories={
                    'help_support': 'Help/Support',
                    'feature_request': 'Feature Requests',
                    'bug_report': 'Bug Reports',
                    'use_case': 'Use Cases/Applications',
                    'prompt_sharing': 'Prompt Sharing',
                    'api_discussion': 'API Discussion',
                    'praise': 'Praise/Positive Feedback',
                    'criticism': 'Criticism/Complaints',
                    'comparison': 'AI Model Comparisons',
                    'pricing': 'Pricing/Subscription Discussion',
                    'ethics_safety': 'Ethics/Safety Concerns',
                    'performance': 'Performance Issues'
                },
                logo_emoji="💎",
                description="Google's AI-powered conversational assistant"
            )
        }
    
    def get_available_competitors(self) -> List[str]:
        """Get list of available competitor names"""
        return list(self.competitors.keys())
    
    def get_competitor_config(self, competitor: str) -> CompetitorConfig:
        """Get configuration for a specific competitor"""
        if competitor not in self.competitors:
            raise ValueError(f"Unknown competitor: {competitor}")
        return self.competitors[competitor]
    
    def get_competitor_display_names(self) -> Dict[str, str]:
        """Get mapping of competitor names to display names"""
        return {name: config.display_name for name, config in self.competitors.items()}
    
    def load_competitor_data(self, competitor: str, data_type: str = "processed") -> Optional[str]:
        """Get file path for competitor data"""
        config = self.get_competitor_config(competitor)
        
        if data_type == "processed":
            # Check multiple possible file locations
            possible_files = [
                f"{config.data_dir}/data/processed_posts.csv",
                f"data/processed_posts_{competitor}.csv", 
                f"data/{competitor}_processed.csv"
            ]
        elif data_type == "raw":
            possible_files = [
                f"{config.data_dir}/data/raw_posts.csv",
                f"data/raw_posts_{competitor}.csv",
                f"data/{competitor}_raw.csv"
            ]
        else:
            return None
        
        # Return first existing file
        for file_path in possible_files:
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def validate_data_completeness(self, competitor: str) -> Dict[str, bool]:
        """Check data availability for a competitor"""
        config = self.get_competitor_config(competitor)
        
        return {
            "has_processed_data": self.load_competitor_data(competitor, "processed") is not None,
            "has_raw_data": self.load_competitor_data(competitor, "raw") is not None,
            "has_reports": os.path.exists(f"{config.data_dir}/reports/"),
            "config_valid": True
        }
    
    def create_competitor_directories(self, competitor: str):
        """Create directory structure for a competitor"""
        config = self.get_competitor_config(competitor)
        
        directories = [
            config.data_dir,
            f"{config.data_dir}/data",
            f"{config.data_dir}/reports"
        ]
        
        for dir_path in directories:
            os.makedirs(dir_path, exist_ok=True)
            
        # Create config file
        config_file = f"{config.data_dir}/config.json"
        if not os.path.exists(config_file):
            with open(config_file, 'w') as f:
                json.dump({
                    "name": config.name,
                    "display_name": config.display_name,
                    "subreddit": config.subreddit,
                    "color_scheme": config.color_scheme,
                    "categories": config.categories,
                    "logo_emoji": config.logo_emoji,
                    "description": config.description
                }, f, indent=2)

# Global instance
competitor_manager = CompetitorDataManager()