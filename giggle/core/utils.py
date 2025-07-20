"""Utility functions for Giggle."""

import os
import shutil
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

def clean_directory(directory: Path) -> None:
    """
    Clean a directory by removing all files and subdirectories.
    
    Args:
        directory: Directory to clean
    """
    if not directory.exists():
        return
    
    # Remove all files and subdirectories
    for item in directory.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

def copy_assets(source_dir: Path, target_dir: Path) -> None:
    """
    Copy assets from source to target directory.
    
    Args:
        source_dir: Source directory
        target_dir: Target directory
    """
    if not source_dir.exists():
        return
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(exist_ok=True, parents=True)
    
    # Copy all files and subdirectories
    for item in source_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, target_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)

def generate_sitemap(site_dir: Path, site_url: str) -> None:
    """
    Generate sitemap.xml for search engines.
    
    Args:
        site_dir: Site directory
        site_url: Base URL of the site
    """
    # Find all HTML files
    html_files = list(site_dir.glob('**/*.html'))
    
    # Create sitemap content
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for html_file in html_files:
        # Get relative path
        rel_path = html_file.relative_to(site_dir)
        
        # Convert to URL
        url_path = str(rel_path).replace('\\', '/')
        
        # Handle index.html files
        if url_path.endswith('index.html'):
            url_path = url_path[:-10]
        
        # Add trailing slash if needed
        if url_path and not url_path.endswith('/'):
            url_path += '/'
        
        # Get last modified time
        last_mod = datetime.datetime.fromtimestamp(html_file.stat().st_mtime)
        last_mod_str = last_mod.strftime('%Y-%m-%d')
        
        # Add URL to sitemap
        sitemap += '  <url>\n'
        sitemap += f'    <loc>{site_url}/{url_path}</loc>\n'
        sitemap += f'    <lastmod>{last_mod_str}</lastmod>\n'
        sitemap += '  </url>\n'
    
    sitemap += '</urlset>'
    
    # Write sitemap
    with open(site_dir / 'sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '-')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    return filename

def get_relative_path(path: Path, base_path: Path) -> Path:
    """
    Get relative path from base path.
    
    Args:
        path: Path to get relative path for
        base_path: Base path
        
    Returns:
        Relative path
    """
    try:
        return path.relative_to(base_path)
    except ValueError:
        return path
