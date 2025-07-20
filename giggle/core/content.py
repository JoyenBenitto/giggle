"""Content processing for Giggle."""

import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import frontmatter
import markdown
from collections import defaultdict

def discover_content(content_dir: Path, content_type: str, site_dir: Path) -> List[Dict[str, Any]]:
    """
    Discover and process content files in a directory.
    
    Args:
        content_dir: Directory to search for content
        content_type: Type of content (posts, pages, etc.)
        site_dir: Root directory of the site
        
    Returns:
        List of processed content items
    """
    items = []
    
    # Skip if directory doesn't exist
    if not content_dir.exists():
        return items
    
    # Find all markdown files
    markdown_files = list(content_dir.glob('**/*.md'))
    
    # Process each file
    for file_path in markdown_files:
        item = process_content(file_path, content_type, site_dir)
        if item:
            items.append(item)
    
    # Sort items by date if available
    items.sort(key=lambda x: x.get('date', datetime.datetime.now()), reverse=True)
    
    return items

def process_content(file_path: Path, content_type: str, site_dir: Path) -> Dict[str, Any]:
    """
    Process a content file.
    
    Args:
        file_path: Path to the content file
        content_type: Type of content (posts, pages, etc.)
        site_dir: Root directory of the site
        
    Returns:
        Dict containing processed content
    """
    try:
        # Parse frontmatter and content
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Extract metadata
        metadata = dict(post.metadata)
        
        # Set default layout based on content type
        if 'layout' not in metadata:
            if content_type == 'posts':
                metadata['layout'] = 'post'
            elif content_type == 'projects':
                metadata['layout'] = 'project'
            else:
                metadata['layout'] = 'page'
        
        # Generate URL if not specified
        if 'url' not in metadata:
            url = _generate_url(file_path, content_type, site_dir)
            metadata['url'] = url
        
        # Parse date from filename or frontmatter
        if 'date' not in metadata and content_type == 'posts':
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})-', file_path.name)
            if date_match:
                date_str = date_match.group(1)
                try:
                    metadata['date'] = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    metadata['date'] = datetime.datetime.now()
            else:
                metadata['date'] = datetime.datetime.now()
        
        # Format date as string if it's a datetime object
        if isinstance(metadata.get('date'), datetime.datetime):
            metadata['date_formatted'] = metadata['date'].strftime('%B %d, %Y')
        
        # Add file path
        metadata['file_path'] = str(file_path)
        
        # Add content type
        metadata['content_type'] = content_type
        
        # Convert content to HTML
        content_html = markdown.markdown(
            post.content,
            extensions=[
                'markdown.extensions.meta',
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.toc',
                'markdown.extensions.codehilite',
                'markdown.extensions.attr_list',
            ]
        )
        
        # Add content to metadata
        metadata['content'] = content_html
        
        # Generate excerpt if not provided
        if 'excerpt' not in metadata and content_html:
            excerpt = _generate_excerpt(content_html, 250)
            metadata['excerpt'] = excerpt
        
        return metadata
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}

def build_taxonomies(content: Dict[str, List[Dict[str, Any]]], taxonomy_config: List[Dict[str, str]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Build taxonomy collections from content.
    
    Args:
        content: Dictionary of content items by type
        taxonomy_config: List of taxonomy configurations
        
    Returns:
        Dictionary of taxonomies with terms and associated content
    """
    taxonomies = {}
    
    # Initialize taxonomies
    for taxonomy in taxonomy_config:
        taxonomy_name = taxonomy.get('name')
        if taxonomy_name:
            taxonomies[taxonomy_name] = defaultdict(list)
    
    # Process all content
    for content_type, items in content.items():
        for item in items:
            # Process each taxonomy
            for taxonomy_name in taxonomies.keys():
                # Get terms for this item
                terms = item.get(taxonomy_name, [])
                if terms:
                    # Convert single term to list
                    if not isinstance(terms, list):
                        terms = [terms]
                    
                    # Add item to each term
                    for term in terms:
                        taxonomies[taxonomy_name][term].append(item)
    
    # Convert defaultdicts to regular dicts
    return {k: dict(v) for k, v in taxonomies.items()}

def _generate_url(file_path: Path, content_type: str, site_dir: Path) -> str:
    """
    Generate URL from file path.
    
    Args:
        file_path: Path to the content file
        content_type: Type of content (posts, pages, etc.)
        site_dir: Root directory of the site
        
    Returns:
        URL string
    """
    # Get relative path from content directory
    rel_path = file_path.relative_to(site_dir)
    
    # Remove date prefix for posts
    if content_type == 'posts':
        name = file_path.stem
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)', name)
        if date_match:
            name = date_match.group(2)
        else:
            name = file_path.stem
    else:
        name = file_path.stem
    
    # Handle index files
    if name.lower() == 'index':
        try:
            parent_dir = file_path.parent.relative_to(site_dir)
            # Check if this is the root index.md file in content/pages
            if str(parent_dir) == 'content/pages':
                return "/"
            return f"/{parent_dir}/"
        except ValueError:
            # If we can't get a relative path, just use root
            return "/"
    
    # Handle content type directories
    if content_type == 'posts':
        return f"/posts/{name}/"
    elif content_type == 'projects':
        return f"/projects/{name}/"
    else:
        # For pages, use the relative path
        if 'content/pages' in str(file_path):
            # Remove content/pages prefix
            parts = list(rel_path.parts)
            if 'content' in parts:
                content_idx = parts.index('content')
                if content_idx + 1 < len(parts) and parts[content_idx + 1] == 'pages':
                    parts = parts[content_idx + 2:]
            
            # Build URL
            if parts:
                if parts[-1].endswith('.md'):
                    parts[-1] = parts[-1][:-3]
                return f"/{'/'.join(parts)}/"
            else:
                return "/"
        else:
            # For other content, use the name
            return f"/{name}/"

def _generate_excerpt(content: str, length: int = 250) -> str:
    """
    Generate an excerpt from content.
    
    Args:
        content: HTML content
        length: Maximum length of excerpt
        
    Returns:
        Excerpt string
    """
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', content)
    
    # Truncate to length
    if len(text) > length:
        text = text[:length].rsplit(' ', 1)[0] + '...'
    
    return text
