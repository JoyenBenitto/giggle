import os
import shutil
import re
from typing import Optional
from pathlib import Path
import frontmatter
from .path_resolver import PagePath, PathResolver

class MarkdownFile:
    """Represents a processed markdown file with metadata."""
    def __init__(self, title: str, content: str, path: str, metadata: dict, page_path: PagePath) -> None:
        self.title: str = title
        self.content: str = content
        self.path: str = path
        self.metadata: dict = metadata
        self.page_path: PagePath = page_path

def copy_markdown_files(src_dir: str, dest_dir: str) -> list[str]:
    """Copy all markdown files from src_dir to dest_dir, preserving structure."""
    os.makedirs(dest_dir, exist_ok=True)
    copied_files: list[str] = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.md'):
                src_path: str = os.path.join(root, file)
                rel_path: str = os.path.relpath(src_path, src_dir)
                dest_path: str = os.path.join(dest_dir, rel_path)
                
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)
                copied_files.append(dest_path)
    
    return copied_files

def copy_images(src_dir: str, dest_dir: str) -> None:
    """Copy all images to common assets directory."""
    assets_dir: str = os.path.join(dest_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    image_extensions: tuple = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                src_path: str = os.path.join(root, file)
                dest_path: str = os.path.join(assets_dir, file)
                shutil.copy2(src_path, dest_path)

def resolve_obsidian_links(content: str, from_page: PagePath, path_resolver: PathResolver) -> str:
    """Resolve [[link]] style Obsidian links to relative HTML paths."""
    
    def replace_link(match) -> str:
        link_text: str = match.group(1)
        parts: list[str] = link_text.split('|')
        link_name: str = parts[0].strip()
        display_text: str = parts[1].strip() if len(parts) > 1 else link_name
        
        rel_link: Optional[str] = path_resolver.compute_link(from_page, link_name)
        if rel_link:
            return f'[{display_text}]({rel_link})'
        return f'[{display_text}](#)'
    
    pattern = re.compile(r'\[\[([^\]]+)\]\]')
    return pattern.sub(replace_link, content)

def resolve_obsidian_images(content: str, rel_dir: str = '') -> str:
    """Convert Obsidian image syntax ![[filename]] to markdown with asset paths."""
    
    def replace_obsidian_img(match) -> str:
        filename: str = match.group(1)
        
        if rel_dir and rel_dir != '.':
            depth: int = rel_dir.count('/')
            assets_path: str = '/'.join(['..'] * (depth + 1)) + '/assets/' + filename
        else:
            assets_path: str = 'assets/' + filename
        
        return f'![{filename}]({assets_path})'
    
    pattern = re.compile(r'!\[\[([^\]]+)\]\]')
    return pattern.sub(replace_obsidian_img, content)

def resolve_image_paths(content: str, rel_dir: str = '') -> str:
    """Resolve image paths to common assets directory with proper relative paths."""
    
    def replace_img(match) -> str:
        img_path: str = match.group(1)
        filename: str = os.path.basename(img_path)
        
        if rel_dir and rel_dir != '.':
            depth: int = rel_dir.count('/')
            assets_path: str = '/'.join(['..'] * (depth + 1)) + '/assets/' + filename
        else:
            assets_path: str = 'assets/' + filename
        
        return f'![{match.group(2)}]({assets_path})'
    
    pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    return pattern.sub(replace_img, content)

def load_markdown(file_path: str, page_path: PagePath) -> MarkdownFile:
    """Load markdown file and extract frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    title: str = post.metadata.get('title', os.path.splitext(os.path.basename(file_path))[0])
    
    return MarkdownFile(
        title=title,
        content=post.content,
        path=file_path,
        metadata=post.metadata,
        page_path=page_path
    )

def process_markdown_file(src_path: str, dest_path: str, page_path: PagePath, path_resolver: PathResolver) -> MarkdownFile:
    """Load markdown, resolve links and images, and save to destination."""
    md_file: MarkdownFile = load_markdown(src_path, page_path)
    
    md_file.content = resolve_obsidian_links(md_file.content, page_path, path_resolver)
    md_file.content = resolve_obsidian_images(md_file.content, page_path.rel_dir)
    md_file.content = resolve_image_paths(md_file.content, page_path.rel_dir)
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(md_file.content)
    
    return md_file
