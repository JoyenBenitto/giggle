import os
import json
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class PagePath:
    """Represents a page with its absolute and relative paths."""
    title: str
    abs_path: str
    rel_path: str
    rel_dir: str
    html_name: str
    
    def html_path(self) -> str:
        """Get the HTML path relative to build root."""
        if self.rel_dir:
            return os.path.join(self.rel_dir, self.html_name)
        return self.html_name
    
    def relative_link_to(self, target: 'PagePath') -> str:
        """Compute relative path from this page to target page."""
        if self.rel_dir == target.rel_dir:
            return target.html_name
        
        from_parts: list[str] = self.rel_dir.split(os.sep) if self.rel_dir else []
        to_parts: list[str] = target.rel_dir.split(os.sep) if target.rel_dir else []
        
        common: int = 0
        for f, t in zip(from_parts, to_parts):
            if f == t:
                common += 1
            else:
                break
        
        ups: int = len(from_parts) - common
        downs: list[str] = to_parts[common:] + [target.html_name]
        
        rel_parts: list[str] = ['..'] * ups + downs
        return os.path.join(*rel_parts) if rel_parts else target.html_name


class PathResolver:
    """Resolves paths using vault workspace context."""
    
    def __init__(self, vault_root: str) -> None:
        self.vault_root: str = vault_root
        self.workspace_path: str = os.path.join(vault_root, '.obsidian', 'workspace.json')
        self.pages: Dict[str, PagePath] = {}
        self.title_to_page: Dict[str, PagePath] = {}
        self.title_counts: Dict[str, int] = {}
    
    def load_workspace(self) -> None:
        """Load workspace configuration from vault."""
        if os.path.exists(self.workspace_path):
            with open(self.workspace_path, 'r', encoding='utf-8') as f:
                self.workspace = json.load(f)
    
    def register_page(self, abs_path: str, title: str, html_name: str, src_dir: str) -> PagePath:
        """Register a page and compute its relative paths."""
        rel_path: str = os.path.relpath(abs_path, src_dir)
        rel_dir: str = os.path.dirname(rel_path)
        
        if rel_dir and rel_dir != '.':
            rel_dir = rel_dir.replace(os.sep, '/')
        else:
            rel_dir = ''
        
        is_index: bool = title.lower() == 'index'
        if is_index and rel_dir:
            final_html_name: str = 'index.html'
        else:
            final_html_name: str = html_name
        
        page: PagePath = PagePath(
            title=title,
            abs_path=abs_path,
            rel_path=rel_path,
            rel_dir=rel_dir,
            html_name=final_html_name
        )
        
        self.pages[abs_path] = page
        
        unique_key: str = f"{rel_dir}/{title}" if rel_dir else title
        self.title_to_page[unique_key] = page
        
        self.title_counts[title] = self.title_counts.get(title, 0) + 1
        
        return page
    
    def find_page_by_title(self, title: str, rel_dir: Optional[str] = None) -> Optional[PagePath]:
        """Find a page by its title, optionally scoped to a directory."""
        if rel_dir:
            unique_key: str = f"{rel_dir}/{title}"
            return self.title_to_page.get(unique_key)
        
        return self.title_to_page.get(title)
    
    def compute_link(self, from_page: PagePath, to_title: str) -> Optional[str]:
        """Compute relative link from one page to another by title."""
        to_page: Optional[PagePath] = self.find_page_by_title(to_title)
        
        if not to_page:
            for unique_key, page in self.title_to_page.items():
                if page.title == to_title:
                    to_page = page
                    break
        
        if not to_page:
            return None
        
        return from_page.relative_link_to(to_page)
