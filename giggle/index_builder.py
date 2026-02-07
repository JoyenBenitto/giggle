import os
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class DirectoryInfo:
    """Information about a directory level."""
    name: str
    pages: List[Dict]
    tags: Set[str]
    description: str = ""

class IndexBuilder:
    """Builds improved index pages organized by directory structure."""
    
    def __init__(self, pages: List[Dict]) -> None:
        self.pages: List[Dict] = pages
        self.l1_dirs: Dict[str, DirectoryInfo] = {}
        self._organize_pages()
    
    def _organize_pages(self) -> None:
        """Organize pages by L1 directory."""
        for page in self.pages:
            html_path: str = page['html_path']
            parts: List[str] = html_path.split('/')
            
            if len(parts) > 1:
                l1_dir: str = parts[0]
            else:
                l1_dir: str = 'root'
            
            if l1_dir not in self.l1_dirs:
                self.l1_dirs[l1_dir] = DirectoryInfo(
                    name=l1_dir,
                    pages=[],
                    tags=set()
                )
            
            self.l1_dirs[l1_dir].pages.append(page)
            
            tags: List[str] = page['metadata'].get('tags', [])
            if isinstance(tags, list):
                self.l1_dirs[l1_dir].tags.update(tags)
    
    def _get_directory_description(self, dir_name: str) -> str:
        """Extract description from directory's index file."""
        for page in self.l1_dirs[dir_name].pages:
            title: str = page['title'].lower()
            if title == 'index':
                content: str = page['content']
                lines: List[str] = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('[') and not line.startswith('-'):
                        cleaned = line.replace('*', '').replace('_', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                        if cleaned and len(cleaned) > 3:
                            return cleaned[:120]
        return ""
    
    def build_main_index(self) -> Dict:
        """Build main index data with L1 directories."""
        for dir_name in self.l1_dirs:
            self.l1_dirs[dir_name].description = self._get_directory_description(dir_name)
        
        l1_entries: List[Dict] = []
        for dir_name in sorted(self.l1_dirs.keys()):
            if dir_name == 'root':
                continue
            
            dir_info: DirectoryInfo = self.l1_dirs[dir_name]
            l1_entries.append({
                'name': dir_name,
                'description': dir_info.description,
                'tags': sorted(list(dir_info.tags)),
                'page_count': len(dir_info.pages),
                'link': f"{dir_name}/index.html"
            })
        
        return {
            'entries': l1_entries,
            'total_directories': len(l1_entries),
            'total_pages': len(self.pages)
        }
    
    def build_archive(self) -> Dict:
        """Build archive with all pages organized by directory."""
        archive_sections: List[Dict] = []
        
        for dir_name in sorted(self.l1_dirs.keys()):
            dir_info: DirectoryInfo = self.l1_dirs[dir_name]
            
            section_pages: List[Dict] = []
            for page in sorted(dir_info.pages, key=lambda p: p['title']):
                section_pages.append({
                    'title': page['title'],
                    'link': page['html_path'],
                    'tags': page['metadata'].get('tags', [])
                })
            
            archive_sections.append({
                'directory': dir_name if dir_name != 'root' else 'Root',
                'pages': section_pages,
                'count': len(section_pages)
            })
        
        return {
            'sections': archive_sections,
            'total_pages': len(self.pages)
        }
