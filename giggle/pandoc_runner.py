from __future__ import annotations
import subprocess
import tempfile
from pathlib import Path
import yaml


SUPPORTED_FORMATS = {".md": "markdown+yaml_metadata_block+footnotes+fenced_code_attributes+smart", ".tex": "latex", ".html": "html"}


def detect_format(path: Path) -> str:
    return SUPPORTED_FORMATS.get(path.suffix.lower(), "markdown")


def run_pandoc(source: Path, template: Path, metadata: dict, extra_args: list | None = None) -> str:
    source_fmt = detect_format(source)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        yaml.dump(metadata, f, allow_unicode=True, default_flow_style=False)
        meta_file = Path(f.name)

    try:
        cmd = [
            "pandoc",
            str(source),
            f"--from={source_fmt}",
            "--to=html5",
            "--standalone",
            f"--template={template}",
            f"--metadata-file={meta_file}",
            "--highlight-style=kate",
            f"--resource-path={source.parent}",
        ]
        if metadata.get("math"):
            cmd.append("--mathjax")
        if extra_args:
            cmd.extend(extra_args)

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pandoc failed for {source.name}:\n{e.stderr.strip()}") from e
    finally:
        meta_file.unlink(missing_ok=True)


def run_pandoc_pdf(source: Path, output: Path) -> None:
    """Generate a PDF from a markdown/tex file using pdflatex."""
    source_fmt = detect_format(source)
    cmd = [
        "pandoc",
        str(source),
        f"--from={source_fmt}",
        "--pdf-engine=pdflatex",
        f"--resource-path={source.parent}",
        "-o", str(output),
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pandoc PDF failed for {source.name}:\n{e.stderr.strip()}") from e


def run_pandoc_string(content: str, suffix: str, template: Path, metadata: dict, extra_args: list | None = None) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp = Path(f.name)
    try:
        return run_pandoc(tmp, template, metadata, extra_args)
    finally:
        tmp.unlink(missing_ok=True)
