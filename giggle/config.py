from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class NavItem:
    title: str
    href: str


@dataclass
class PageConfig:
    id: str
    slug: str
    title: str
    source: str
    description: str = ""
    tags: list = field(default_factory=list)
    template: str = "page"
    date: str = ""
    in_feed: bool = True


@dataclass
class CollectionConfig:
    id: str
    name: str
    source_dir: str
    output_dir: str
    description: str = ""
    index: bool = True
    item_template: str = "page"
    index_template: str = "listing"
    auto_tag: str = ""
    items: dict = field(default_factory=dict)  # source-path-without-ext → metadata dict


@dataclass
class FeedsConfig:
    rss: bool = True
    atom: bool = True
    max_items: int = 20
    output: str = "feed"


@dataclass
class SEOConfig:
    twitter: str = ""
    og_image: str = ""


@dataclass
class SiteInfo:
    title: str
    author: str
    url: str
    description: str
    email: str = ""
    lang: str = "en"
    theme: str = "default"


@dataclass
class SiteConfig:
    site: SiteInfo
    navbar: list
    pages: list
    collections: list = field(default_factory=list)
    feeds: FeedsConfig = field(default_factory=FeedsConfig)
    seo: SEOConfig = field(default_factory=SEOConfig)

    @classmethod
    def load(cls, path: Path | str) -> SiteConfig:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        with open(p) as f:
            data = yaml.safe_load(f)

        site = SiteInfo(**data["site"])
        navbar = [NavItem(**n) for n in data.get("navbar", [])]

        pages = []
        for pd in data.get("pages", []):
            pd.setdefault("tags", [])
            pd.setdefault("description", "")
            pd.setdefault("template", "page")
            pd.setdefault("date", "")
            pd.setdefault("in_feed", True)
            pages.append(PageConfig(**pd))

        collections = []
        for cd in data.get("collections", []):
            cd.setdefault("description", "")
            cd.setdefault("index", True)
            cd.setdefault("item_template", "page")
            cd.setdefault("index_template", "listing")
            cd.setdefault("auto_tag", "")
            items_raw = cd.pop("items", []) or []
            items_dict: dict = {}
            for item in items_raw:
                src = item.get("source", "")
                key = str(Path(src).with_suffix("")) if src else src
                items_dict[key] = item
            cd["items"] = items_dict
            collections.append(CollectionConfig(**cd))

        feeds_data = data.get("feeds", {})
        feeds = FeedsConfig(**feeds_data) if feeds_data else FeedsConfig()

        seo_data = data.get("seo", {})
        seo = SEOConfig(**seo_data) if seo_data else SEOConfig()

        return cls(
            site=site,
            navbar=navbar,
            pages=pages,
            collections=collections,
            feeds=feeds,
            seo=seo,
        )
