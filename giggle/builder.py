from __future__ import annotations
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import frontmatter
from rich.console import Console
from rich.table import Table
from rich import box

from .config import SiteConfig, PageConfig, CollectionConfig
from .pandoc_runner import run_pandoc, run_pandoc_string, run_pandoc_pdf
from .feeds import FeedItem, generate_rss, generate_atom
from .sitemap import generate_sitemap
from .themes import resolve_theme, get_template

console = Console()


class Builder:
    def __init__(self, config_path: Path, output_dir: Path):
        self.config_path = config_path.resolve()
        self.root_dir = self.config_path.parent
        self.config = SiteConfig.load(config_path)
        self.output_dir = output_dir.resolve()
        self.theme_dir = resolve_theme(self.config.site.theme)
        self.feed_items: list[FeedItem] = []
        self.sitemap_urls: list[dict] = []
        self._page_registry: dict[str, str] = {}
        # tag -> list of {title, url (from dist root), description, date}
        self._tag_registry: dict[str, list[dict]] = {}

    def build(self) -> None:
        start = datetime.now()
        console.print(f"\n[bold cyan]giggle[/bold cyan] → [dim]{self.output_dir}[/dim]\n")

        self._setup_output()
        self._copy_assets()
        self._register_pages()

        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Title", style="cyan", min_width=20)
        table.add_column("Source", style="dim")
        table.add_column("Output", style="dim")
        table.add_column("", min_width=6)

        for page in self.config.pages:
            source = self.root_dir / page.source
            out_rel, status = self._build_page(page, source)
            table.add_row(page.title, page.source, out_rel, status)

        for collection in self.config.collections:
            self._build_collection(collection, table)

        self._build_tag_pages()

        console.print(table)

        if self.config.feeds.rss or self.config.feeds.atom:
            sorted_items = sorted(self.feed_items, key=lambda x: x.date, reverse=True)
            sorted_items = sorted_items[: self.config.feeds.max_items]

            if self.config.feeds.rss:
                rss_path = self.output_dir / f"{self.config.feeds.output}.rss"
                generate_rss(sorted_items, self.config.site.title, self.config.site.url,
                             self.config.site.description, rss_path)

            if self.config.feeds.atom:
                atom_path = self.output_dir / f"{self.config.feeds.output}.atom"
                generate_atom(sorted_items, self.config.site.title, self.config.site.url,
                              self.config.site.description, self.config.site.author, atom_path)

        sitemap_path = self.output_dir / "sitemap.xml"
        generate_sitemap(self.sitemap_urls, sitemap_path)

        elapsed = (datetime.now() - start).total_seconds()
        n = len(list(self.output_dir.rglob("*.html")))
        p = len(list(self.output_dir.rglob("*.pdf")))
        console.print(f"[green]✓[/green] {n} pages · {p} PDFs · {elapsed:.2f}s\n")

    def _setup_output(self) -> None:
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)

    def _copy_assets(self) -> None:
        assets_dst = self.output_dir / "assets"

        theme_assets = self.theme_dir / "assets"
        if theme_assets.exists():
            shutil.copytree(theme_assets, assets_dst)
        else:
            assets_dst.mkdir(parents=True)

        if self.config.site.theme == "dark":
            from .themes import THEMES_DIR
            dark_css = THEMES_DIR / "dark" / "assets" / "style.css"
            if dark_css.exists():
                shutil.copy(dark_css, assets_dst / "style.css")

        user_assets = self.root_dir / "content" / "assets"
        if user_assets.exists():
            shutil.copytree(user_assets, assets_dst, dirs_exist_ok=True)

    def _register_pages(self) -> None:
        for page in self.config.pages:
            out = "index.html" if not page.slug else f"{page.slug}.html"
            self._page_registry[page.id] = out
            self._page_registry[page.slug] = out

        for collection in self.config.collections:
            src_dir = self.root_dir / collection.source_dir
            if not src_dir.exists():
                continue
            for source in src_dir.rglob("*"):
                if source.suffix.lower() not in (".md", ".html", ".tex"):
                    continue
                rel = source.relative_to(src_dir)
                is_pdf = self._check_is_pdf(source)
                ext = ".pdf" if is_pdf else ".html"
                slug = f"{collection.output_dir}/{rel.with_suffix('')}"
                out = f"{slug}{ext}"
                self._page_registry[str(rel.with_suffix(""))] = out
                self._page_registry[source.stem] = out

    def _check_is_pdf(self, source: Path) -> bool:
        if source.suffix.lower() == ".tex":
            return True
        try:
            post = frontmatter.load(str(source))
            return bool(post.metadata.get("is_pdf", False))
        except Exception:
            return False

    def _register_tags(self, tags: list[str], title: str, url_from_root: str,
                        description: str, date: str) -> None:
        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue
            self._tag_registry.setdefault(tag, []).append({
                "title": title,
                "url": url_from_root,
                "description": description,
                "date": date,
            })

    def _build_page(self, page: PageConfig, source: Path) -> tuple[str, str]:
        if not source.exists():
            return "—", "[red]missing[/red]"

        try:
            out_name = "index.html" if not page.slug else f"{page.slug}.html"
            output_path = self.output_dir / out_name
            root = ""
            canonical = self.config.site.url if not page.slug else f"{self.config.site.url}/{page.slug}.html"

            fm = self._read_frontmatter(source)
            metadata = self._build_metadata(page, fm, root, canonical,
                                            active_href=f"{page.slug}.html" if page.slug else "index.html")

            template_name = page.template if page.template else "page"
            template = get_template(self.theme_dir, template_name)

            html = run_pandoc(source, template, metadata)
            html = self._resolve_crossrefs(html, root)
            output_path.write_text(html, encoding="utf-8")

            tags = fm.get("tags", page.tags) or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",")]
            if tags:
                self._register_tags(tags, fm.get("title", page.title), out_name,
                                    fm.get("description", page.description), str(fm.get("date", page.date) or ""))

            if page.in_feed and fm.get("date"):
                self.feed_items.append(FeedItem(
                    title=fm.get("title", page.title),
                    url=canonical,
                    description=fm.get("description", page.description),
                    date=str(fm.get("date", page.date)),
                ))

            self.sitemap_urls.append({
                "loc": canonical,
                "lastmod": str(fm.get("date", "")),
                "changefreq": "monthly",
                "priority": 1.0 if not page.slug else 0.8,
            })

            return out_name, "[green]ok[/green]"
        except Exception as e:
            return "—", f"[red]{e}[/red]"

    def _build_collection(self, collection: CollectionConfig, table: Table) -> None:
        src_dir = self.root_dir / collection.source_dir
        if not src_dir.exists():
            return

        out_dir = self.output_dir / collection.output_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        index_entries: list[dict] = []

        for source in sorted(src_dir.rglob("*")):
            if source.suffix.lower() not in (".md", ".html", ".tex"):
                continue
            if source.name.startswith("_"):
                continue

            rel = source.relative_to(src_dir)
            depth = len(rel.parts)
            root = "../" * depth

            fm = self._read_frontmatter(source)
            is_pdf = bool(fm.get("is_pdf", False)) or source.suffix.lower() == ".tex"

            if source.name.startswith("index."):
                out_rel_path = rel.parent / "index.html"
                slug = f"{collection.output_dir}/{rel.parent}" if str(rel.parent) != "." else collection.output_dir
                is_index = True
            else:
                ext = ".pdf" if is_pdf else ".html"
                out_rel_path = rel.with_suffix(ext)
                slug = f"{collection.output_dir}/{rel.with_suffix('')}"
                is_index = False

            output_path = out_dir / out_rel_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            canonical_ext = ".pdf" if (is_pdf and not is_index) else ".html"
            canonical = f"{self.config.site.url}/{slug}{canonical_ext}"

            # Merge yaml item metadata with frontmatter (fm wins per-field, tags are unioned)
            yaml_meta = collection.items.get(str(rel.with_suffix("")), {})
            page_title = fm.get("title") or yaml_meta.get("title") or source.stem.replace("-", " ").title()
            page_desc = fm.get("description") or yaml_meta.get("description", "")
            page_date = str(fm.get("date") or yaml_meta.get("date") or "")
            fm_tags = fm.get("tags", [])
            yaml_tags = yaml_meta.get("tags", [])
            if isinstance(fm_tags, str):
                fm_tags = [t.strip() for t in fm_tags.split(",")]
            if isinstance(yaml_tags, str):
                yaml_tags = [t.strip() for t in yaml_tags.split(",")]
            seen: set = set()
            page_tags: list = []
            for t in list(fm_tags) + [t for t in yaml_tags if t not in fm_tags]:
                if t not in seen:
                    seen.add(t)
                    page_tags.append(t)
            if collection.auto_tag and collection.auto_tag not in seen:
                page_tags.append(collection.auto_tag)

            status: str
            if is_pdf and not is_index:
                try:
                    run_pandoc_pdf(source, output_path)
                    status = "[cyan]pdf[/cyan]"
                except Exception as e:
                    status = f"[red]pdf fail: {e}[/red]"
            else:
                fake_page = PageConfig(
                    id=slug,
                    slug=slug,
                    title=page_title,
                    source=str(source.relative_to(self.root_dir)),
                    description=page_desc,
                    tags=page_tags,
                    template=collection.item_template,
                    date=page_date,
                    in_feed=fm.get("in_feed", True),
                )
                template = get_template(self.theme_dir, collection.item_template)
                metadata = self._build_metadata(fake_page, fm, root, canonical,
                                                active_href=f"{collection.output_dir}/index.html")
                try:
                    html = run_pandoc(source, template, metadata)
                    html = self._resolve_crossrefs(html, root)
                    output_path.write_text(html, encoding="utf-8")
                    status = "[green]ok[/green]"
                except Exception as e:
                    status = f"[red]{e}[/red]"

            if not is_index and "ok" in status or "pdf" in status:
                if not is_index:
                    index_entries.append({
                        "title": page_title,
                        "url": str(out_rel_path),
                        "description": page_desc,
                        "date": page_date,
                        "tags": page_tags,
                        "is_pdf": is_pdf,
                    })

                if page_tags:
                    self._register_tags(page_tags, page_title,
                                        f"{collection.output_dir}/{str(out_rel_path)}",
                                        page_desc, page_date)

                if not is_pdf and fm.get("in_feed", True) and page_date:
                    self.feed_items.append(FeedItem(
                        title=page_title, url=canonical,
                        description=page_desc, date=page_date,
                    ))

                if not is_pdf:
                    self.sitemap_urls.append({
                        "loc": canonical, "lastmod": page_date,
                        "changefreq": "monthly", "priority": 0.7,
                    })

            table.add_row(page_title, str(rel), str(out_rel_path), status)

        if collection.index:
            self._build_collection_index(collection, index_entries, out_dir)

    def _build_collection_index(self, collection: CollectionConfig, entries: list[dict], out_dir: Path) -> None:
        depth = len(Path(collection.output_dir).parts)
        root = "../" * depth
        canonical = f"{self.config.site.url}/{collection.output_dir}/index.html"

        sorted_entries = sorted(entries, key=lambda x: x.get("date", ""), reverse=True)

        fake_page = PageConfig(
            id=f"{collection.id}-index",
            slug=f"{collection.output_dir}/index",
            title=collection.name,
            source="",
            description=collection.description,
            in_feed=False,
        )

        metadata = self._build_metadata(fake_page, {}, root, canonical,
                                        active_href=f"{collection.output_dir}/index.html")

        if collection.index_template == "archive":
            self._build_archive_index(collection, sorted_entries, out_dir, root, canonical, metadata)
            return

        if collection.index_template == "blog":
            parts = ['<div class="blog-grid">']
            for e in sorted_entries:
                parts.append('<div class="blog-card">')
                if e.get("date"):
                    parts.append(f'<div class="blog-card-date">{e["date"]}</div>')
                parts.append(f'<a class="blog-card-title" href="{e["url"]}">{e["title"]}</a>')
                if e.get("description"):
                    parts.append(f'<div class="blog-card-desc">{e["description"]}</div>')
                tags = e.get("tags", [])
                if tags:
                    tag_links = " ".join(f'<a class="tag" href="{root}tags/{t}.html">{t}</a>' for t in tags)
                    parts.append(f'<div class="blog-card-tags">{tag_links}</div>')
                parts.append('</div>')
            parts.append('</div>')
            content = "\n\n".join(parts)
            template = get_template(self.theme_dir, "blog")
            try:
                html = run_pandoc_string(content, ".md", template, metadata)
                html = self._resolve_crossrefs(html, root)
                (out_dir / "index.html").write_text(html, encoding="utf-8")
            except Exception as e:
                console.print(f"[red]blog index failed: {e}[/red]")
            return

        lines = [f"# {collection.name}\n"]
        if collection.description:
            lines.append(f"{collection.description}\n")

        for e in sorted_entries:
            line = f"- [{e['title']}]({e['url']})"
            if e.get("is_pdf"):
                line += " `PDF`"
            if e.get("date"):
                line += f" `{e['date']}`"
            if e.get("description"):
                line += f"  \n  {e['description']}"
            lines.append(line)

        template = get_template(self.theme_dir, "listing")

        try:
            html = run_pandoc_string("\n".join(lines), ".md", template, metadata)
            html = self._resolve_crossrefs(html, root)
            (out_dir / "index.html").write_text(html, encoding="utf-8")
        except Exception as e:
            console.print(f"[red]collection index failed: {e}[/red]")

    def _build_archive_index(self, collection, entries: list[dict], out_dir, root: str, canonical: str, metadata: dict) -> None:
        from collections import defaultdict

        fake_page = PageConfig(
            id=f"{collection.id}-index",
            slug=f"{collection.output_dir}/index",
            title=collection.name,
            source="",
            description=collection.description,
            in_feed=False,
        )
        meta = self._build_metadata(fake_page, {}, root, canonical,
                                    active_href=f"{collection.output_dir}/index.html")

        groups: dict = defaultdict(list)
        for e in entries:
            parts = e["url"].split("/")
            group = parts[0] if len(parts) > 1 else "general"
            groups[group].append(e)

        html_parts = [
            '<div class="archive-banner">',
            f'<p>{collection.description}</p>',
            '<p class="archive-hint">Use <kbd>Ctrl+F</kbd> to search by title, topic, or tag.</p>',
            '</div>',
        ]

        for group_name in sorted(groups.keys()):
            group_entries = sorted(groups[group_name], key=lambda x: x.get("title", "").lower())
            html_parts.append('<section class="archive-group">')
            html_parts.append(f'<h2 class="archive-group-title">{group_name.replace("-", " ").title()}</h2>')
            html_parts.append('<ul class="archive-list">')
            for e in group_entries:
                is_pdf = e.get("is_pdf", False)
                fmt = "PDF" if is_pdf else "HTML"
                fmt_class = "pdf" if is_pdf else "html-badge"
                html_parts.append('<li class="archive-item">')
                html_parts.append('<div class="archive-item-header">')
                html_parts.append(f'<a href="{e["url"]}" class="archive-item-title">{e["title"]}</a>')
                html_parts.append(f'<span class="archive-badge {fmt_class}">{fmt}</span>')
                html_parts.append('</div>')
                if e.get("description"):
                    html_parts.append(f'<p class="archive-item-desc">{e["description"]}</p>')
                tags = e.get("tags", [])
                if tags:
                    tag_links = " ".join(f'<a class="tag" href="{root}tags/{t}.html">{t}</a>' for t in tags)
                    html_parts.append(f'<div class="archive-item-tags">{tag_links}</div>')
                html_parts.append('</li>')
            html_parts.append('</ul>')
            html_parts.append('</section>')

        content = "\n".join(html_parts)
        template = get_template(self.theme_dir, "archive")
        try:
            html = run_pandoc_string(content, ".html", template, meta)
            html = self._resolve_crossrefs(html, root)
            (out_dir / "index.html").write_text(html, encoding="utf-8")
        except Exception as e:
            console.print(f"[red]archive index failed: {e}[/red]")

    def _build_tag_pages(self) -> None:
        if not self._tag_registry:
            return

        tags_dir = self.output_dir / "tags"
        tags_dir.mkdir(exist_ok=True)
        root = "../"

        for tag, pages in sorted(self._tag_registry.items()):
            sorted_pages = sorted(pages, key=lambda x: x.get("date", ""), reverse=True)

            lines = [f"# {tag}\n"]
            for p in sorted_pages:
                line = f"- [{p['title']}]({root}{p['url']})"
                if p.get("date"):
                    line += f" `{p['date']}`"
                if p.get("description"):
                    line += f"  \n  {p['description']}"
                lines.append(line)

            slug = f"tags/{tag}"
            canonical = f"{self.config.site.url}/tags/{tag}.html"

            fake_page = PageConfig(
                id=slug,
                slug=slug,
                title=tag,
                source="",
                description=f"Pages tagged with {tag}",
                in_feed=False,
            )

            metadata = self._build_metadata(fake_page, {}, root, canonical, active_href="")
            metadata["tag_listing"] = True
            template = get_template(self.theme_dir, "listing")

            try:
                html = run_pandoc_string("\n".join(lines), ".md", template, metadata)
                (tags_dir / f"{tag}.html").write_text(html, encoding="utf-8")
            except Exception as e:
                console.print(f"[red]tag page failed [{tag}]: {e}[/red]")

        self._build_tag_index(tags_dir, root)

    def _build_tag_index(self, tags_dir: Path, root: str) -> None:
        canonical = f"{self.config.site.url}/tags/index.html"

        fake_page = PageConfig(
            id="tags-index",
            slug="tags/index",
            title="Tags",
            source="",
            description="All tags",
            in_feed=False,
        )
        metadata = self._build_metadata(fake_page, {}, root, canonical, active_href="")

        # Sort tags by count descending, then alphabetically
        sorted_tags = sorted(self._tag_registry.keys(), key=lambda t: (-len(self._tag_registry[t]), t))
        max_count = max((len(v) for v in self._tag_registry.values()), default=1)

        html_parts = [
            '<div class="tags-banner">',
            '<p>All topics across posts, notes, and research. Use <kbd>Ctrl+F</kbd> to jump to a tag.</p>',
            '</div>',
            '<div class="tags-cloud">',
        ]
        for tag in sorted_tags:
            count = len(self._tag_registry[tag])
            weight = "sm" if count == 1 else ("lg" if count >= max_count * 0.6 else "md")
            html_parts.append(
                f'<a href="{tag}.html" class="tag-chip tag-chip-{weight}">'
                f'<span class="tag-chip-name">{tag}</span>'
                f'<span class="tag-chip-count">{count}</span>'
                f'</a>'
            )
        html_parts.append('</div>')

        content = "\n".join(html_parts)
        template = get_template(self.theme_dir, "tags")
        try:
            html = run_pandoc_string(content, ".html", template, metadata)
            (tags_dir / "index.html").write_text(html, encoding="utf-8")
        except Exception as e:
            console.print(f"[red]tag index failed: {e}[/red]")

    def _build_metadata(self, page: PageConfig, fm: dict, root: str, canonical: str, active_href: str = "") -> dict:
        site = self.config.site

        nav = []
        for item in self.config.navbar:
            nav.append({
                "title": item.title,
                "href": item.href,
                "active": item.href == active_href or (active_href and active_href.startswith(item.href.split("/")[0])),
            })

        tags = fm.get("tags", page.tags) or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        return {
            "site-title": site.title,
            "site-author": site.author,
            "site-url": site.url,
            "site-description": site.description,
            "lang": site.lang,
            "title": fm.get("title") or page.title,
            "description": fm.get("description") or page.description,
            "date": str(fm.get("date", page.date) or ""),
            "tags": tags,
            "math": fm.get("math", False),
            "canonical": canonical,
            "root": root,
            "nav": nav,
            "year": str(datetime.now().year),
            "twitter": self.config.seo.twitter,
            "hero": fm.get("hero", ""),
            "tagline": fm.get("tagline", ""),
            "rss-url": f"{root}feed.rss",
            "atom-url": f"{root}feed.atom",
        }

    def _read_frontmatter(self, path: Path) -> dict:
        if path.suffix.lower() == ".tex":
            return {}
        try:
            post = frontmatter.load(str(path))
            return dict(post.metadata)
        except Exception:
            return {}

    def _resolve_crossrefs(self, html: str, root: str) -> str:
        def replace(m: re.Match) -> str:
            slug = m.group(1)
            target = self._page_registry.get(slug, f"{slug}.html")
            return f'href="{root}{target}"'
        return re.sub(r'href="page:([^"]+)"', replace, html)
