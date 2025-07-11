#!/usr/bin/env python
"""
Giggle - A powerful and flexible static site generator

Main entry point for the Giggle CLI.
"""

import click
from giggle.cli.commands import cli
from giggle.__init__ import __version__


if __name__ == "__main__":
    cli()

