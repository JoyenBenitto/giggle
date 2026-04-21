import os
import tempfile
import shutil
from typing import Optional
from pathlib import Path

import frontmatter

from .file_manager import ParseInputDir
from .markdown_processor import copy_images, process_markdown_file
from .template_engine import TemplateEngine
from .pandoc_renderer import render_html_body, render_pdf, check_pandoc
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
        self.constants_dir: str = os.path.join(os.path.dirname(__file__), 'constants')
        self.css_file: str = os.path.join(self.constants_dir, 'style.css')
        self.pdf_template: str = os.path.join(self.constants_dir, 'pdf.template')
        self.engine: TemplateEngine = TemplateEngine(self.template_dir, self.css_file)
        self.path_resolver: PathResolver = PathResolver(vault_root)
        self.config: SiteConfig = SiteConfig(config_file)

    def build(self) -> bool:
        """Execute the full build pipeline."""
        if not check_pandoc():
            print("[-] pandoc not found. Install it: https://pandoc.org/installing.html")
            return False
        try:
            print(f"[*] Building from {self.src_dir}")
            self._discover_and_copy()
            self._build_file_map()
            self._copy_images()
            self._copy_css()
            self._copy_constants()
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
        print("[*] Discovering markdown files...")
        parser: ParseInputDir = ParseInputDir(self.src_dir)
        src_files = parser.normalize()
        print(f"  Found {len(src_files)} markdown files")

        for src_meta in src_files:
            src_path: str = src_meta.path
            rel_path: str = os.path.relpath(src_path, self.src_dir)
            dest_path: str = os.path.join(self.temp_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)

    def _build_file_map(self) -> None:
        print("[*] Building file map...")
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path: str = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                    title: str = post.metadata.get('title', os.path.splitext(file)[0])
                    html_name: str = self._get_html_name(title)
                    self.path_resolver.register_page(file_path, title, html_name, self.temp_dir)

    def _copy_images(self) -> None:
        print("[*] Copying images...")
        copy_images(self.src_dir, self.build_dir)

    def _copy_css(self) -> None:
        """Copy style.css to build root so pages can link to it."""
        if os.path.exists(self.css_file):
            shutil.copy2(self.css_file, os.path.join(self.build_dir, 'style.css'))

    def _copy_constants(self) -> None:
        """Copy constants/ assets (images etc.) to build/constants/."""
        src = os.path.join(self.constants_dir, 'images')
        dst = os.path.join(self.build_dir, 'constants')
        if os.path.exists(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)

    def _process_files(self) -> None:
        print("[*] Processing markdown files...")
        self.pages: list[dict] = []

        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                if not file.endswith('.md'):
                    continue

                file_path: str = os.path.join(root, file)
                rel_path: str = os.path.relpath(file_path, self.temp_dir)
                rel_dir: str = os.path.dirname(rel_path).replace(os.sep, '/')

                with open(file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)

                title: str = post.metadata.get('title', os.path.splitext(file)[0])
                scope: str = rel_dir if rel_dir and rel_dir != '.' else ''
                page_path: Optional[PagePath] = self.path_resolver.find_page_by_title(title, scope)

                if not page_path:
                    continue

                md_file = process_markdown_file(file_path, file_path, page_path, self.path_resolver)

                # Keep the original source path for PDF rendering (Pandoc needs it
                # to resolve --resource-path relative to the source directory).
                src_original: str = os.path.join(self.src_dir, rel_path)

                self.pages.append({
                    'title': md_file.title,
                    'content': md_file.content,
                    'metadata': md_file.metadata,
                    'file_path': file_path,
                    'src_path': src_original,
                    'html_path': page_path.html_path(),
                    'page_path': page_path,
                    'is_pdf': post.metadata.get('is_pdf', False),
                })

                print(f"  Processed: {md_file.title}")

    def _render_html(self) -> None:
        print("[*] Rendering pages...")
        navbar: list = self.config.get_navbar_links()
        site_title: str = self.config.title

        for page in self.pages:
            if page.get('is_pdf'):
                self._render_page_as_pdf(page)
                continue

            # Write processed markdown to temp file and run Pandoc
            tmp_md = os.path.join(self.temp_dir, '_render_tmp.md')
            with open(tmp_md, 'w', encoding='utf-8') as f:
                f.write(page['content'])

            html_body: str = render_html_body(tmp_md)

            depth: int = page['html_path'].count('/')
            css_rel: str = '../' * depth + 'style.css'

            rendered: str = self.engine.render_page(
                title=page['title'],
                body=html_body,
                metadata=page['metadata'],
                navbar=navbar,
                site_title=site_title,
                css_path=css_rel,
            )

            output_file: str = os.path.join(self.build_dir, page['html_path'])
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered)

            print(f"  Rendered: {page['html_path']}")

    def _render_page_as_pdf(self, page: dict) -> None:
        if not os.path.exists(self.pdf_template):
            print(f"  Warning: pdf.template not found, skipping PDF for {page['title']}")
            return

        pdf_path: str = os.path.splitext(
            os.path.join(self.build_dir, page['html_path'])
        )[0] + '.pdf'
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        src_path: str = page.get('src_path', page['file_path'])
        resource_path: str = os.path.dirname(src_path)
        render_pdf(src_path, pdf_path, self.pdf_template, resource_path)
        print(f"  Rendered PDF: {os.path.relpath(pdf_path, self.build_dir)}")

    def _render_index_pages(self) -> None:
        print("[*] Generating index and tag pages...")
        index_builder: IndexBuilder = IndexBuilder(self.pages)
        main_index_data: dict = index_builder.build_main_index()
        navbar: list = self.config.get_navbar_links()
        site_title: str = self.config.title

        intro_html: str = ""
        if self.config.intro_content:
            import tempfile as tf
            tmp = tf.NamedTemporaryFile(suffix='.md', mode='w', delete=False, encoding='utf-8')
            tmp.write(self.config.intro_content)
            tmp.close()
            intro_html = render_html_body(tmp.name)
            os.unlink(tmp.name)

        main_index_html: str = self.engine.render_main_index(
            main_index_data, navbar, site_title, intro_html
        )
        with open(os.path.join(self.build_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(main_index_html)
        print("  Generated: index.html")

        self._render_static_pages()
        self._render_external_pages()
        self._render_tag_pages()

    def _render_static_pages(self) -> None:
        """Render built-in static pages: About.html and Contact.html."""
        about_html = self.engine.render_about()
        with open(os.path.join(self.build_dir, 'About.html'), 'w', encoding='utf-8') as f:
            f.write(about_html)

        contact_html = self.engine.render_contact()
        with open(os.path.join(self.build_dir, 'Contact.html'), 'w', encoding='utf-8') as f:
            f.write(contact_html)

        print("  Generated: About.html, Contact.html")

    def _render_external_pages(self) -> None:
        print("[*] Generating external pages...")
        external_pages: list = self.config.get_external_pages()
        navbar: list = self.config.get_navbar_links()
        site_title: str = self.config.title

        for page_config in external_pages:
            markdown_file: str = page_config.get('markdown', '')
            output_path: str = page_config.get('path', '')
            title: str = page_config.get('title', '')

            if not markdown_file or not os.path.exists(markdown_file):
                print(f"  Warning: markdown file not found: {markdown_file}")
                continue

            with open(markdown_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            title = post.metadata.get('title', title)
            metadata = dict(post.metadata)

            tmp_md = os.path.join(self.temp_dir, '_ext_tmp.md')
            with open(tmp_md, 'w', encoding='utf-8') as f:
                f.write(post.content)

            html_body: str = render_html_body(tmp_md)

            rendered: str = self.engine.render_page(
                title=title,
                body=html_body,
                metadata=metadata,
                navbar=navbar,
                site_title=site_title,
                css_path='style.css',
            )

            output_file: str = os.path.join(self.build_dir, output_path)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered)
            print(f"  Generated: {output_path}")

    def _render_tag_pages(self) -> None:
        tag_generator: TagGenerator = TagGenerator(self.pages)
        tag_pages: dict = tag_generator.get_tag_pages()

        tags_dir: str = os.path.join(self.build_dir, 'tags')
        os.makedirs(tags_dir, exist_ok=True)

        for tag, tag_data in tag_pages.items():
            tag_html: str = self.engine.render_tag_page(tag_data)
            with open(os.path.join(tags_dir, f"{tag}.html"), 'w', encoding='utf-8') as f:
                f.write(tag_html)

        print(f"  Generated: {len(tag_pages)} tag pages")

    def _get_html_name(self, title: str) -> str:
        safe: str = title.lower().replace(' ', '-')
        safe = ''.join(c for c in safe if c.isalnum() or c in '-_')
        return f"{safe}.html"

    def _cleanup(self) -> None:
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
