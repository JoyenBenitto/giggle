import sys
import os
from argparse import ArgumentParser
from .builder import Builder
from . import __version__

def main() -> None:
    """Main entry point for Giggle static site generator."""
    parser: ArgumentParser = ArgumentParser(description="Giggle - Static site generator")
    
    parser.add_argument("-v", "--version",
                        action="version",
                        version=f"%(prog)s {__version__}")
    
    parser.add_argument("-s", "--source",
                        help="Path to the vault directory",
                        required=True)
    
    parser.add_argument("-o", "--output",
                        help="Path to the output directory",
                        default="./build")
    
    parser.add_argument("-c", "--config",
                        help="Path to site configuration YAML file",
                        default=None)
    
    args = parser.parse_args()
    
    vault_root: str = os.path.dirname(args.source)
    builder: Builder = Builder(args.source, args.output, vault_root, args.config)
    success: bool = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
