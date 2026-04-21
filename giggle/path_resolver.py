import os
import posixpath
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
        """Get the HTML path relative to build root (always forward slashes)."""
        if self.rel_dir:
            return posixpath.join(self.rel_dir, self.html_name)
        return self.html_name

    def relative_link_to(self, target: 'PagePath') -> str:
        """Compute relative path from this page to target page."""
        if self.rel_dir == target.rel_dir:
            return target.html_name

        from_parts: list[str] = self.rel_dir.split('/') if self.rel_dir else []
        to_parts: list[str] = target.rel_dir.split('/') if target.rel_dir else []

        common: int = 0
        for f, t in zip(from_parts, to_parts):
            if f == t:
                common += 1
            else:
                break

        ups: int = len(from_parts) - common
        downs: list[str] = to_parts[common:] + [target.html_name]
        rel_parts: list[str] = ['..'] * ups + downs
        return '/'.join(rel_parts) if rel_parts else target.html_name


class PathResolver:
    """Tracks registered pages and resolves inter-page links."""

    def __init__(self, vault_root: str) -> None:
        self.vault_root: str = vault_root
        self.pages: Dict[str, PagePath] = {}
        self.title_to_page: Dict[str, PagePath] = {}

    def register_page(self, abs_path: str, title: str, html_name: str, src_dir: str) -> PagePath:
        """Register a page and compute its relative paths."""
        rel_path: str = os.path.relpath(abs_path, src_dir)
        rel_dir: str = os.path.dirname(rel_path)

        rel_dir = rel_dir.replace(os.sep, '/')
        if rel_dir == '.':
            rel_dir = ''

        is_index: bool = title.lower() == 'index'
        final_html_name: str = 'index.html' if (is_index and rel_dir) else html_name

        page: PagePath = PagePath(
            title=title,
            abs_path=abs_path,
            rel_path=rel_path,
            rel_dir=rel_dir,
            html_name=final_html_name,
        )

        self.pages[abs_path] = page
        unique_key: str = f"{rel_dir}/{title}" if rel_dir else title
        self.title_to_page[unique_key] = page
        return page

    def find_page_by_title(self, title: str, rel_dir: Optional[str] = None) -> Optional[PagePath]:
        """Find a page by title, optionally scoped to a directory."""
        if rel_dir:
            page = self.title_to_page.get(f"{rel_dir}/{title}")
            if page:
                return page
        return self.title_to_page.get(title)

    def compute_link(self, from_page: PagePath, to_title: str) -> Optional[str]:
        """Compute relative link from one page to another by title."""
        to_page: Optional[PagePath] = self.find_page_by_title(to_title)
        if not to_page:
            for page in self.title_to_page.values():
                if page.title == to_title:
                    to_page = page
                    break
        if not to_page:
            return None
        return from_page.relative_link_to(to_page)
