"""Template rendering for Giggle."""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown
from datetime import datetime

def setup_jinja_env(template_dirs: List[str], md_instance=None) -> Environment:
    """
    Set up Jinja2 template environment.
    
    Args:
        template_dirs: List of template directories
        md_instance: Markdown instance for markdown filter
        
    Returns:
        Jinja2 Environment
    """
    # Create environment
    env = Environment(
        loader=FileSystemLoader(template_dirs),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Add custom filters
    env.filters['markdown'] = markdown_filter(md_instance)
    env.filters['date_format'] = date_format_filter
    env.filters['slugify'] = slugify_filter
    env.filters['limit'] = limit_filter
    env.filters['sort_by'] = sort_by_filter
    env.filters['where'] = where_filter
    
    # Add global functions
    env.globals['now'] = datetime.now
    
    return env

def markdown_filter(md_instance=None):
    """
    Create a markdown filter function.
    
    Args:
        md_instance: Markdown instance to use
        
    Returns:
        Filter function
    """
    def _markdown_filter(text):
        """Convert markdown to HTML."""
        if not text:
            return ''
        
        if md_instance:
            return md_instance.convert(text)
        else:
            return markdown.markdown(
                text,
                extensions=[
                    'markdown.extensions.meta',
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.toc',
                ]
            )
    
    return _markdown_filter

def date_format_filter(value, format='%B %d, %Y'):
    """
    Format a date.
    
    Args:
        value: Date to format
        format: Format string
        
    Returns:
        Formatted date string
    """
    if not value:
        return ''
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
    
    if isinstance(value, datetime):
        return value.strftime(format)
    
    return value

def slugify_filter(value):
    """
    Convert a string to a slug.
    
    Args:
        value: String to convert
        
    Returns:
        Slug string
    """
    if not value:
        return ''
    
    # Convert to lowercase
    value = str(value).lower()
    
    # Replace spaces with hyphens
    value = re.sub(r'\s+', '-', value)
    
    # Remove non-alphanumeric characters
    value = re.sub(r'[^a-z0-9\-]', '', value)
    
    # Remove duplicate hyphens
    value = re.sub(r'-+', '-', value)
    
    # Remove leading/trailing hyphens
    value = value.strip('-')
    
    return value

def limit_filter(value, limit=10):
    """
    Limit a list to a certain number of items.
    
    Args:
        value: List to limit
        limit: Maximum number of items
        
    Returns:
        Limited list
    """
    if not value or not isinstance(value, list):
        return []
    
    return value[:limit]

def sort_by_filter(value, key, reverse=False):
    """
    Sort a list by a key.
    
    Args:
        value: List to sort
        key: Key to sort by
        reverse: Whether to reverse the sort
        
    Returns:
        Sorted list
    """
    if not value or not isinstance(value, list):
        return []
    
    return sorted(value, key=lambda x: x.get(key, ''), reverse=reverse)

def where_filter(value, key, val=None):
    """
    Filter a list by a key/value pair.
    
    Args:
        value: List to filter
        key: Key to filter by
        val: Value to filter by
        
    Returns:
        Filtered list
    """
    if not value or not isinstance(value, list):
        return []
    
    if val is None:
        # Filter by truthy value
        return [item for item in value if item.get(key)]
    else:
        # Filter by specific value
        return [item for item in value if item.get(key) == val]
