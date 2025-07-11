"""Configuration handling for Giggle."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing the configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
    
    # Apply defaults for any missing configs
    default = default_config()
    merged_config = _deep_merge(default, config)
    
    return merged_config

def default_config() -> Dict[str, Any]:
    """
    Return the default configuration.
    
    Returns:
        Dict containing default configuration values
    """
    return {
        'site': {
            'title': 'My Giggle Site',
            'description': 'A site built with Giggle',
            'author': '',
            'url': '',
            'language': 'en',
            'timezone': 'UTC',
        },
        'theme': {
            'name': 'modern',
            'colors': {
                'primary': '#4285f4',
                'secondary': '#34a853',
                'accent': '#fbbc05',
                'text': '#333333',
                'background': '#ffffff',
                'link': '#1a73e8',
            },
            'fonts': {
                'heading': 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'body': 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'code': 'monospace',
            },
            'layout': {
                'container_width': '1200px',
                'sidebar': False,
                'sidebar_position': 'left',
                'toc': True,
            },
            'components': {
                'header': {
                    'sticky': True,
                    'height': '60px',
                },
                'footer': {
                    'show_social': True,
                    'show_copyright': True,
                },
                'cards': {
                    'shadow': 'medium',
                    'border_radius': '8px',
                },
            },
        },
        'navigation': {
            'main': [
                {
                    'title': 'Home',
                    'url': '/',
                },
            ],
        },
        'content': {
            'directories': {
                'posts': 'content/posts',
                'pages': 'content/pages',
                'projects': 'content/projects',
                'data': 'content/data',
            },
            'settings': {
                'posts_per_page': 10,
                'excerpt_length': 250,
                'default_layout': 'post',
                'date_format': 'YYYY-MM-DD',
            },
            'taxonomies': [
                {
                    'name': 'categories',
                    'plural': 'categories',
                    'singular': 'category',
                    'path': '/categories/',
                },
                {
                    'name': 'tags',
                    'plural': 'tags',
                    'singular': 'tag',
                    'path': '/tags/',
                },
            ],
        },
        'features': {
            'search': {
                'enabled': True,
                'type': 'client',
            },
            'dark_mode': True,
            'comments': {
                'enabled': False,
                'system': 'giscus',
                'repo': '',
            },
            'analytics': {
                'enabled': False,
                'provider': 'google',
                'id': '',
            },
            'social_sharing': True,
            'code_highlighting': True,
            'table_of_contents': True,
            'responsive_images': True,
        },
        'build': {
            'output': '_site',
            'assets': [
                'assets/images',
                'assets/fonts',
                'assets/files',
            ],
            'exclude': [
                '*.tmp',
                '*.log',
                'node_modules',
            ],
            'permalink_style': 'pretty',
            'minify': {
                'html': True,
                'css': True,
                'js': True,
            },
        },
    }

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration against schema.
    
    Args:
        config: Configuration dict to validate
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    # Basic validation - check required sections
    required_sections = ['site', 'theme', 'content', 'build']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate site section
    site = config.get('site', {})
    if not isinstance(site, dict):
        raise ValueError("'site' section must be a dictionary")
    
    required_site_fields = ['title']
    for field in required_site_fields:
        if field not in site:
            raise ValueError(f"Missing required field in 'site' section: {field}")
    
    # Validate theme section
    theme = config.get('theme', {})
    if not isinstance(theme, dict):
        raise ValueError("'theme' section must be a dictionary")
    
    # Validate content section
    content = config.get('content', {})
    if not isinstance(content, dict):
        raise ValueError("'content' section must be a dictionary")
    
    # Validate build section
    build = config.get('build', {})
    if not isinstance(build, dict):
        raise ValueError("'build' section must be a dictionary")
    
    return True

def _deep_merge(default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        default: Default dictionary
        override: Dictionary to override defaults
        
    Returns:
        Merged dictionary
    """
    result = default.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

def create_default_config(output_path: Path) -> None:
    """
    Create a default configuration file.
    
    Args:
        output_path: Path to write the configuration file
    """
    config = default_config()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
