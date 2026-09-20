from __future__ import annotations
from pathlib import Path
import sys
import click
from .builder import Builder


@click.group()
def cli():
    pass


@cli.command()
@click.option("-c", "--config", default="site.yaml", show_default=True, help="Path to site.yaml")
@click.option("-o", "--output", default="dist", show_default=True, help="Output directory")
def build(config: str, output: str):
    """Build the static site."""
    config_path = Path(config).resolve()
    output_path = Path(output).resolve()

    try:
        builder = Builder(config_path, output_path)
        builder.build()
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Build failed: {e}", err=True)
        sys.exit(1)


def _iter_watch_paths(root_dir: Path, config_path: Path):
    if config_path.exists():
        yield config_path
    content_dir = root_dir / "content"
    if content_dir.exists():
        yield from content_dir.rglob("*")


def _snapshot_mtimes(root_dir: Path, config_path: Path) -> dict:
    snapshot = {}
    for p in _iter_watch_paths(root_dir, config_path):
        if p.is_file():
            try:
                snapshot[p] = p.stat().st_mtime
            except OSError:
                pass
    return snapshot


def _watch_and_rebuild(config_path: Path, output_path: Path, root_dir: Path, stop_event) -> None:
    import time

    last = _snapshot_mtimes(root_dir, config_path)
    while not stop_event.is_set():
        time.sleep(1)
        current = _snapshot_mtimes(root_dir, config_path)
        if current != last:
            last = current
            try:
                Builder(config_path, output_path).build()
                click.echo("Rebuilt.")
            except Exception as e:
                click.echo(f"Rebuild failed: {e}", err=True)


@cli.command()
@click.option("-c", "--config", default="site.yaml", show_default=True)
@click.option("-o", "--output", default="dist", show_default=True)
@click.option("-p", "--port", default=8000, show_default=True)
def serve(config: str, output: str, port: int):
    """Build and serve locally with live reload."""
    import functools
    import http.server
    import threading

    config_path = Path(config).resolve()
    output_path = Path(output).resolve()
    root_dir = config_path.parent

    try:
        builder = Builder(config_path, output_path)
        builder.build()
    except Exception as e:
        click.echo(f"Build failed: {e}", err=True)
        sys.exit(1)

    stop_event = threading.Event()
    watcher = threading.Thread(
        target=_watch_and_rebuild,
        args=(config_path, output_path, root_dir, stop_event),
        daemon=True,
    )
    watcher.start()

    # Bind the handler to a fixed directory rather than relying on process cwd:
    # the watcher thread rebuilds (rmtree + recreate) output_path concurrently
    # with requests, and a cwd-based handler calls os.getcwd() per request,
    # which raises FileNotFoundError if it lands mid-rmtree.
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(output_path))
    httpd = http.server.ThreadingHTTPServer(("", port), handler)
    click.echo(f"Serving at http://localhost:{port} (auto-rebuilds on change)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()


def main():
    cli()


if __name__ == "__main__":
    main()
