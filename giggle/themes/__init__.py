from pathlib import Path

THEMES_DIR = Path(__file__).parent


def resolve_theme(theme: str) -> Path:
    # Absolute or relative path
    p = Path(theme)
    if p.exists():
        return p.resolve()
    # Built-in theme
    builtin = THEMES_DIR / theme
    if builtin.exists():
        return builtin
    # Fall back to default
    return THEMES_DIR / "default"


def get_template(theme_dir: Path, name: str) -> Path:
    tmpl = theme_dir / "templates" / f"{name}.html5"
    if tmpl.exists():
        return tmpl
    # Fall back to default theme template
    default = THEMES_DIR / "default" / "templates" / f"{name}.html5"
    if default.exists():
        return default
    # Final fallback: page template
    return THEMES_DIR / "default" / "templates" / "page.html5"
