from __future__ import annotations
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom


def generate_sitemap(urls: list[dict], output: Path) -> None:
    NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", NS)
    urlset = ET.Element(f"{{{NS}}}urlset")

    for url in urls:
        url_el = ET.SubElement(urlset, f"{{{NS}}}url")
        ET.SubElement(url_el, f"{{{NS}}}loc").text = url["loc"]
        if url.get("lastmod"):
            ET.SubElement(url_el, f"{{{NS}}}lastmod").text = url["lastmod"]
        if url.get("changefreq"):
            ET.SubElement(url_el, f"{{{NS}}}changefreq").text = url["changefreq"]
        if url.get("priority") is not None:
            ET.SubElement(url_el, f"{{{NS}}}priority").text = str(url["priority"])

    rough = ET.tostring(urlset, encoding="unicode")
    reparsed = minidom.parseString(rough)
    output.write_bytes(reparsed.toprettyxml(indent="  ", encoding="utf-8"))
