import os
import yaml
from typing import Dict, List, Optional

class SiteConfig:
    """Manages site configuration from YAML file."""
    
    def __init__(self, config_file: str = None) -> None:
        self.config_file: str = config_file
        self.title: str = "Archive"
        self.navbar_pages: List[Dict] = []
        self.intro_content: str = ""
        self.intro_html: str = ""
        
        if config_file and os.path.exists(config_file):
            self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            self.title = config.get('title', 'Archive')
            self.navbar_pages = config.get('navbar', [])
            self.intro_content = config.get('intro', '')
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    def get_navbar_links(self) -> List[Dict]:
        """Get navbar links with proper paths."""
        links = []
        for page in self.navbar_pages:
            links.append({
                'title': page.get('title', ''),
                'path': page.get('path', ''),
                'url': page.get('url', ''),
                'markdown': page.get('markdown', '')
            })
        return links
    
    def get_external_pages(self) -> List[Dict]:
        """Get external markdown pages to render, resolving paths relative to config file."""
        config_dir = os.path.dirname(os.path.abspath(self.config_file)) if self.config_file else ''
        pages = []
        for page in self.navbar_pages:
            if page.get('markdown'):
                md_path = page.get('markdown', '')
                if config_dir and not os.path.isabs(md_path):
                    md_path = os.path.join(config_dir, md_path)
                pages.append({
                    'title': page.get('title', ''),
                    'path': page.get('path', ''),
                    'markdown': md_path,
                })
        return pages
