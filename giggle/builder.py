import os
import tempfile
from typing import Optional
from pathlib import Path

from .file_manager import ParseInputDir
from .markdown_processor import copy_markdown_files, copy_images, process_markdown_file
from .template_engine import TemplateEngine
from .markdown import markdown
from .path_resolver import PathResolver, PagePath
from .index_builder import IndexBuilder
from .tag_generator import TagGenerator
from .site_config import SiteConfig

class Builder:
    """Orchestrates the build pipeline: discover -> copy -> process -> render."""
    
    def __init__(self, src_dir: str, build_dir: str, vault_root: str, config_file: str = None) -> None:
        self.src_dir: str = src_dir
        self.build_dir: str = build_dir
        self.vault_root: str = vault_root
        self.temp_dir: str = tempfile.mkdtemp(prefix='giggle_')
        self.template_dir: str = os.path.join(os.path.dirname(__file__), 'templates')
        css_file: str = os.path.join(os.path.dirname(__file__), 'constants', 'style.css')
        self.engine: TemplateEngine = TemplateEngine(self.template_dir, css_file)
        self.path_resolver: PathResolver = PathResolver(vault_root)
        self.config: SiteConfig = SiteConfig(config_file)
    
    def build(self) -> bool:
        """Execute the full build pipeline."""
        try:
            print(f"[*] Building from {self.src_dir}")
            self._discover_and_copy()
            self._build_file_map()
            self._copy_images()
            self._process_files()
            self._render_html()
            self._render_index_pages()
            print("[+] Build completed successfully!")
            return True
        except Exception as e:
            print(f"[-] Build failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self._cleanup()
    
    def _discover_and_copy(self) -> None:
        """Discover markdown files and copy to temp directory."""
        print("[*] Discovering and copying markdown files...")
        
        parser: ParseInputDir = ParseInputDir(self.src_dir)
        src_files = parser.normalize()
        
        print(f"  Found {len(src_files)} markdown files")
        
        for src_meta in src_files:
            src_path: str = src_meta.path
            rel_path: str = os.path.relpath(src_path, self.src_dir)
            dest_path: str = os.path.join(self.temp_dir, rel_path)
            
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            import shutil
            shutil.copy2(src_path, dest_path)
    
    def _build_file_map(self) -> None:
        """Build map of markdown file titles to PagePath objects."""
        print("[*] Building file map...")
        
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path: str = os.path.join(root, file)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        import frontmatter
                        post = frontmatter.load(f)
                    
                    title: str = post.metadata.get('title', os.path.splitext(file)[0])
                    html_name: str = self._get_html_name(title)
                    
                    page_path: PagePath = self.path_resolver.register_page(
                        file_path,
                        title,
                        html_name,
                        self.temp_dir
                    )
    
    def _copy_images(self) -> None:
        """Copy all images to common assets directory."""
        print("[*] Copying images...")
        copy_images(self.src_dir, self.build_dir)
    
    def _process_files(self) -> None:
        """Process markdown files: resolve links, extract metadata."""
        print("[*] Processing markdown files...")
        
        self.pages: list[dict] = []
        
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path: str = os.path.join(root, file)
                    rel_path: str = os.path.relpath(file_path, self.temp_dir)
                    rel_dir: str = os.path.dirname(rel_path).replace(os.sep, '/')
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        import frontmatter
                        post = frontmatter.load(f)
                    
                    title: str = post.metadata.get('title', os.path.splitext(file)[0])
                    page_path: Optional[PagePath] = self.path_resolver.find_page_by_title(title, rel_dir if rel_dir != '.' else '')
                    
                    if not page_path:
                        continue
                    
                    md_file = process_markdown_file(file_path, file_path, page_path, self.path_resolver)
                    
                    self.pages.append({
                        'title': md_file.title,
                        'content': md_file.content,
                        'metadata': md_file.metadata,
                        'file_path': file_path,
                        'html_path': page_path.html_path(),
                        'page_path': page_path
                    })
                    
                    print(f"  Processed: {md_file.title} ({page_path.html_path()})")
    
    def _render_html(self) -> None:
        """Render HTML files from processed markdown."""
        print("[*] Rendering HTML files...")
        
        navbar: list = self.config.get_navbar_links()
        site_title: str = self.config.title
        
        for page in self.pages:
            rendered: str = self.engine.render_external_page(
                title=page['title'],
                content=markdown(page['content']),
                metadata=page['metadata'],
                navbar=navbar,
                site_title=site_title
            )
            
            output_file: str = os.path.join(self.build_dir, page['html_path'])
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered)
            
            print(f"  Rendered: {page['html_path']}")
        
        self._render_index()
    
    def _render_index(self) -> None:
        """Render index.html from all pages."""
        print("[*] Generating index...")
        
        index_pages: list[dict] = []
        for page in self.pages:
            index_pages.append({
                'title': page['title'],
                'description': page['metadata'].get('description', ''),
                'html_path': page['html_path']
            })
        
        rendered: str = self.engine.render_index(index_pages)
        index_path: str = os.path.join(self.build_dir, 'index.html')
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        print(f"  Generated: index.html")
    
    def _render_index_pages(self) -> None:
        """Render main index page and tag pages."""
        print("[*] Generating index page...")
        
        index_builder: IndexBuilder = IndexBuilder(self.pages)
        
        main_index_data: dict = index_builder.build_main_index()
        navbar: list = self.config.get_navbar_links()
        site_title: str = self.config.title
        intro_html: str = markdown(self.config.intro_content) if self.config.intro_content else ""
        main_index_html: str = self.engine.render_main_index(main_index_data, navbar, site_title, intro_html)
        main_index_path: str = os.path.join(self.build_dir, 'index.html')
        
        with open(main_index_path, 'w', encoding='utf-8') as f:
            f.write(main_index_html)
        
        print(f"  Generated: index.html")
        
        self._render_external_pages()
        self._render_tag_pages()
    
    def _render_external_pages(self) -> None:
        """Render external markdown pages from config."""
        print("[*] Generating external pages...")
        
        external_pages: list = self.config.get_external_pages()
        navbar: list = self.config.get_navbar_links()
        site_title: str = self.config.title
        
        for page_config in external_pages:
            markdown_file: str = page_config.get('markdown', '')
            output_path: str = page_config.get('path', '')
            title: str = page_config.get('title', '')
            
            if not markdown_file or not os.path.exists(markdown_file):
                print(f"  Warning: Markdown file not found: {markdown_file}")
                continue
            
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content: str = f.read()
            
            html_content: str = markdown(content)
            page_html: str = self.engine.render_external_page(title, html_content, {'tags': []}, navbar, site_title)
            
            output_file: str = os.path.join(self.build_dir, output_path)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(page_html)
            
            print(f"  Generated: {output_path}")
    
    def _render_tag_pages(self) -> None:
        """Render tag pages for all unique tags."""
        print("[*] Generating tag pages...")
        
        tag_generator: TagGenerator = TagGenerator(self.pages)
        tag_pages: dict = tag_generator.get_tag_pages()
        
        tags_dir: str = os.path.join(self.build_dir, 'tags')
        os.makedirs(tags_dir, exist_ok=True)
        
        for tag, tag_data in tag_pages.items():
            tag_html: str = self.engine.render_tag_page(tag_data)
            tag_path: str = os.path.join(tags_dir, f"{tag}.html")
            
            with open(tag_path, 'w', encoding='utf-8') as f:
                f.write(tag_html)
            
            print(f"  Generated: tags/{tag}.html")
    
    def _get_html_name(self, title: str) -> str:
        """Convert title to safe HTML filename."""
        safe: str = title.lower().replace(' ', '-')
        safe = ''.join(c for c in safe if c.isalnum() or c in '-_')
        return f"{safe}.html"
    
    def _cleanup(self) -> None:
        """Clean up temporary directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("[*] Cleaned up temp directory")
