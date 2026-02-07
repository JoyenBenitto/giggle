import os
from typing import Dict, List, Set

class TagGenerator:
    """Generates tag pages for all unique tags in the site."""
    
    def __init__(self, pages: List[Dict]) -> None:
        self.pages: List[Dict] = pages
        self.tags: Dict[str, List[Dict]] = {}
        self._organize_by_tags()
    
    def _organize_by_tags(self) -> None:
        """Organize pages by tags."""
        for page in self.pages:
            tags: List[str] = page['metadata'].get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    if tag not in self.tags:
                        self.tags[tag] = []
                    self.tags[tag].append(page)
    
    def get_tag_pages(self) -> Dict[str, Dict]:
        """Get data for all tag pages."""
        tag_pages: Dict[str, Dict] = {}
        
        for tag in sorted(self.tags.keys()):
            pages_with_tag: List[Dict] = sorted(
                self.tags[tag],
                key=lambda p: p['title']
            )
            
            tag_pages[tag] = {
                'tag': tag,
                'pages': [
                    {
                        'title': page['title'],
                        'link': page['html_path']
                    }
                    for page in pages_with_tag
                ],
                'count': len(pages_with_tag)
            }
        
        return tag_pages
