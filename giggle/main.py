import sys
import os
import click

from .builder import Builder
from . import __version__


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="giggle")
@click.option("-s", "--source", help="Path to the vault/notes directory", required=False)
@click.option("-o", "--output", default="./build", help="Output directory", show_default=True)
@click.option("-c", "--config", default=None, help="Path to site.yaml config file")
@click.pass_context
def cli(ctx, source, output, config):
    """Giggle — static site generator with Pandoc backend."""
    if ctx.invoked_subcommand is None:
        if not source:
            click.echo(ctx.get_help())
            sys.exit(0)
        vault_root: str = os.path.dirname(os.path.abspath(source))
        builder: Builder = Builder(source, output, vault_root, config)
        success: bool = builder.build()
        sys.exit(0 if success else 1)


@cli.command()
@click.option("-s", "--source", required=True, help="Path to the vault/notes directory")
@click.option("-o", "--output", default="./build", show_default=True)
@click.option("-c", "--config", default=None)
@click.option("-p", "--port", default=5500, show_default=True, help="Port for dev server")
def serve(source, output, config, port):
    """Build, serve locally, and watch for changes."""
    from livereload import Server
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    vault_root: str = os.path.dirname(os.path.abspath(source))

    def do_build():
        builder = Builder(source, output, vault_root, config)
        builder.build()

    do_build()

    class _Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.src_path.endswith(('.md', '.yaml', '.yml', '.css')):
                click.echo(f"[~] Change detected: {event.src_path}")
                do_build()

    observer = Observer()
    observer.schedule(_Handler(), source, recursive=True)
    observer.start()

    server = Server()
    server.watch(output)
    click.echo(f"[*] Serving at http://localhost:{port}  (watching {source})")
    server.serve(root=output, port=port, open_url_delay=1)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
