import subprocess
import shutil


def check_pandoc() -> bool:
    return shutil.which("pandoc") is not None


def render_html_body(md_path: str) -> str:
    """Convert a markdown file to an HTML fragment (no wrapping html/head/body)."""
    result = subprocess.run([
        "pandoc", md_path,
        "--from", "markdown+yaml_metadata_block",
        "--to", "html5",
        "--highlight-style=pygments",
    ], capture_output=True, text=True, check=True)
    return result.stdout


def render_pdf(md_path: str, output_path: str, template_path: str, resource_path: str) -> None:
    """Render a markdown file to PDF via pdflatex."""
    subprocess.run([
        "pandoc", md_path,
        "--pdf-engine=pdflatex",
        f"--template={template_path}",
        f"--resource-path=.:{resource_path}",
        "-o", output_path,
    ], check=True)
