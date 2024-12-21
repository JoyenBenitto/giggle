#!/usr/bin/env python
"""Main entry point for Giggle Static Site Generator."""

import sys
import argparse
from giggle.ssg import StaticSiteGenerator

def main():
    parser = argparse.ArgumentParser(
        description="Giggle Static Site Generator - A modern static site generator"
    )
    parser.add_argument(
        "command",
        choices=["cook"],
        help="Command to execute (currently only 'cook' is supported)"
    )
    parser.add_argument(
        "site_config",
        help="Path to site configuration file"
    )
    parser.add_argument(
        "--style-config",
        help="Optional path to style configuration file",
        default=None
    )
    parser.add_argument(
        "--build-dir",
        help="Optional build directory path",
        default=None
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.command == "cook":
        generator = StaticSiteGenerator(
            args.site_config,
            args.style_config,
            args.build_dir
        )
        generator.generate()

if __name__ == "__main__":
    main()
