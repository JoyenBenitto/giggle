from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple
import xml.etree.ElementTree as ET
from xml.dom import minidom


class FeedItem(NamedTuple):
    title: str
    url: str
    description: str
    date: str
    content: str = ""


def _parse_date(date_str: str) -> datetime:
    if not date_str:
        return datetime.now(timezone.utc)
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.now(timezone.utc)


def _pretty_xml(root: ET.Element) -> bytes:
    rough = ET.tostring(root, encoding="unicode")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8")


def generate_rss(items: list[FeedItem], site_title: str, site_url: str, site_description: str, output: Path) -> None:
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = site_title
    ET.SubElement(channel, "link").text = site_url
    ET.SubElement(channel, "description").text = site_description
    ET.SubElement(channel, "language").text = "en"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    self_link = ET.SubElement(channel, "atom:link")
    self_link.set("href", f"{site_url}/feed.rss")
    self_link.set("rel", "self")
    self_link.set("type", "application/rss+xml")

    for item in items:
        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = item.title
        ET.SubElement(entry, "link").text = item.url
        ET.SubElement(entry, "guid", isPermaLink="true").text = item.url
        ET.SubElement(entry, "description").text = item.description
        d = _parse_date(item.date)
        ET.SubElement(entry, "pubDate").text = d.strftime("%a, %d %b %Y %H:%M:%S +0000")

    output.write_bytes(_pretty_xml(rss))


def generate_atom(items: list[FeedItem], site_title: str, site_url: str, site_description: str, site_author: str, output: Path) -> None:
    NS = "http://www.w3.org/2005/Atom"
    ET.register_namespace("", NS)
    feed = ET.Element(f"{{{NS}}}feed")

    ET.SubElement(feed, f"{{{NS}}}title").text = site_title
    ET.SubElement(feed, f"{{{NS}}}subtitle").text = site_description

    link = ET.SubElement(feed, f"{{{NS}}}link")
    link.set("href", site_url)

    self_link = ET.SubElement(feed, f"{{{NS}}}link")
    self_link.set("href", f"{site_url}/feed.atom")
    self_link.set("rel", "self")

    ET.SubElement(feed, f"{{{NS}}}id").text = site_url
    ET.SubElement(feed, f"{{{NS}}}updated").text = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    author_el = ET.SubElement(feed, f"{{{NS}}}author")
    ET.SubElement(author_el, f"{{{NS}}}name").text = site_author

    for item in items:
        entry = ET.SubElement(feed, f"{{{NS}}}entry")
        ET.SubElement(entry, f"{{{NS}}}title").text = item.title
        entry_link = ET.SubElement(entry, f"{{{NS}}}link")
        entry_link.set("href", item.url)
        ET.SubElement(entry, f"{{{NS}}}id").text = item.url
        d = _parse_date(item.date)
        ET.SubElement(entry, f"{{{NS}}}updated").text = d.strftime("%Y-%m-%dT%H:%M:%SZ")
        ET.SubElement(entry, f"{{{NS}}}summary").text = item.description

    output.write_bytes(_pretty_xml(feed))
