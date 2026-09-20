from __future__ import annotations
import re
from pathlib import Path

# {{download id="some-id"}} — looks up `some-id` in the site's `downloads:` registry
# (site.yaml), so the href/label/description live in one place instead of being
# retyped in every post that links to the same file.
DOWNLOAD_RE = re.compile(r'^\{\{download\s+id="([^"]+)"\s*\}\}\s*$', re.MULTILINE)

DOWNLOAD_ICON_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M4 19h16"/>'
    '</svg>'
)


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _resolve_asset_path(href: str, content_root: Path) -> Path | None:
    """`href` is a relative link out of a rendered page, e.g. '../assets/downloads/x.tar.gz'.
    Every page in this site's collections lives one directory below the site root, so stripping
    up to and including the first 'assets/' segment gives the path under content/assets/."""
    marker = "assets/"
    idx = href.find(marker)
    if idx == -1:
        return None
    return content_root / "assets" / href[idx + len(marker):]


def render_download_card(entry, content_root: Path) -> str:
    href = entry.href
    name = href.rsplit("/", 1)[-1]
    label = entry.label
    desc = entry.desc

    hint = desc
    asset_path = _resolve_asset_path(href, content_root)
    if asset_path is not None and asset_path.is_file():
        size = _human_size(asset_path.stat().st_size)
        hint = f"{desc} &middot; {size}" if desc else size

    return (
        '<div class="download-card">'
        f'<div class="download-card__label">{label}</div>'
        f'<a class="download-card__link" href="{href}" download>'
        f'<span class="download-card__icon" aria-hidden="true">{DOWNLOAD_ICON_SVG}</span>'
        f'{name}'
        '</a>'
        f'<div class="download-card__hint">{hint}</div>'
        '</div>'
    )


def expand_shortcodes(markdown_text: str, downloads: dict, content_root: Path) -> str:
    def replace(m: re.Match) -> str:
        did = m.group(1)
        entry = downloads.get(did)
        if entry is None:
            return f'<p><em>[unknown download id: {did}]</em></p>'
        return render_download_card(entry, content_root)

    return DOWNLOAD_RE.sub(replace, markdown_text)
