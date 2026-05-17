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


@cli.command()
@click.option("-c", "--config", default="site.yaml", show_default=True)
@click.option("-o", "--output", default="dist", show_default=True)
@click.option("-p", "--port", default=8000, show_default=True)
def serve(config: str, output: str, port: int):
    """Build and serve locally with live reload."""
    import http.server
    import os

    config_path = Path(config).resolve()
    output_path = Path(output).resolve()

    try:
        builder = Builder(config_path, output_path)
        builder.build()
    except Exception as e:
        click.echo(f"Build failed: {e}", err=True)
        sys.exit(1)

    os.chdir(output_path)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("", port), handler)
    click.echo(f"Serving at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


def main():
    cli()


if __name__ == "__main__":
    main()
