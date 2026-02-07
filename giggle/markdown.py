import markdown as md
from typing import Optional

def markdown(content: str) -> str:
    """Convert markdown content to HTML."""
    return md.markdown(
        content,
        extensions=[
            'extra',
            'codehilite',
            'toc',
            'tables',
            'fenced_code'
        ]
    )
