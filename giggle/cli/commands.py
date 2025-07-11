"""CLI commands for Giggle."""

import os
import sys
import click
import logging
import datetime
from pathlib import Path
import shutil

from giggle.core.site import GiggleSite
from giggle.core.config import create_default_config, default_config
from giggle.__init__ import __version__

# Set up logger
logger = logging.getLogger(__name__)

def setup_logging(log_level: str) -> None:
    """
    Set up logging with specified verbosity.
    
    Args:
        log_level: Logging level (debug, info, warning, error)
    """
    # Map string levels to logging levels
    level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
    }
    
    # Set level
    level = level_map.get(log_level.lower(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

@click.group()
@click.version_option(version=__version__)
def cli():
    """Giggle - A powerful and flexible static site generator."""
    pass

@cli.command()
@click.argument('name')
@click.option('--theme', '-t', default='modern', help='Theme to use')
@click.option('--verbose', '-v', default='info', show_default=True,
              help='Set verbosity level', type=click.Choice(['debug', 'info', 'warning', 'error']))
def new(name, theme, verbose):
    """Create a new Giggle site."""
    setup_logging(verbose)
    
    # Create site directory
    site_dir = Path(name)
    if site_dir.exists():
        logger.error(f"Directory {name} already exists. Choose a different name or delete the existing directory.")
        sys.exit(1)
    
    logger.info(f"Creating new Giggle site: {name}")
    
    # Create directory structure
    site_dir.mkdir(parents=True)
    
    # Create content directories
    content_dirs = [
        'content/pages',
        'content/posts',
        'content/projects',
        'content/data',
        'assets/images',
        'assets/css',
        'assets/js',
        'layouts',
    ]
    
    for content_dir in content_dirs:
        (site_dir / content_dir).mkdir(parents=True, exist_ok=True)
    
    # Create configuration file
    config_path = site_dir / 'giggle.yaml'
    create_default_config(config_path)
    
    # Create sample content
    _create_sample_content(site_dir)
    
    logger.info(f"Created default configuration file: {config_path}")
    logger.info(f"\nNew Giggle site created successfully at {site_dir}")
    logger.info(f"Run 'cd {name}' and then 'giggle serve' to start the development server")

@cli.command()
@click.option('--port', '-p', default=8000, help='Port to serve on')
@click.option('--host', '-h', default='localhost', help='Host to serve on')
@click.option('--directory', '-d', default='.', help='Directory of the site')
@click.option('--verbose', '-v', default='info', show_default=True,
              help='Set verbosity level', type=click.Choice(['debug', 'info', 'warning', 'error']))
def serve(port, host, directory, verbose):
    """Serve the site locally with live reload."""
    setup_logging(verbose)
    
    # Create a site instance
    site = GiggleSite(directory)
    
    # Serve the site
    site.serve(host=host, port=port)

@cli.command()
@click.option('--directory', '-d', default='.', help='Directory of the site')
@click.option('--output', '-o', help='Output directory (defaults to _site in the site directory)')
@click.option('--verbose', '-v', default='info', show_default=True,
              help='Set verbosity level', type=click.Choice(['debug', 'info', 'warning', 'error']))
def build(directory, output, verbose):
    """Build the site for production."""
    setup_logging(verbose)
    
    # Create a site instance
    site = GiggleSite(directory, output_dir=output)
    
    # Build the site
    output_dir = site.build_site()
    
    logger.info(f"Site built successfully in {output_dir}")

@cli.command()
@click.argument('title')
@click.option('--directory', '-d', default='.', help='Directory of the site')
@click.option('--type', '-t', default='page', type=click.Choice(['page', 'post', 'project']),
              help='Type of content to create')
def new_content(title, directory, type):
    """Create new content page, post, or project."""
    site_dir = Path(directory)
    
    # Determine content directory based on type
    if type == 'post':
        content_dir = site_dir / 'content' / 'posts'
    elif type == 'project':
        content_dir = site_dir / 'content' / 'projects'
    else:
        content_dir = site_dir / 'content' / 'pages'
    
    # Create directory if it doesn't exist
    content_dir.mkdir(exist_ok=True, parents=True)
    
    # Create slug from title
    slug = title.lower().replace(' ', '-')
    
    # Create file path
    if type == 'post':
        # Create post with date prefix
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        file_path = content_dir / f"{today}-{slug}.md"
        
        # Create front matter
        front_matter = f"""---
title: "{title}"
date: {today}
layout: post
description: ""
tags: []
categories: []
---

# {title}

Write your post content here.
"""
    elif type == 'project':
        file_path = content_dir / f"{slug}.md"
        
        # Create front matter
        front_matter = f"""---
title: "{title}"
layout: project
description: ""
featured_image: ""
github: ""
demo: ""
tags: []
---

# {title}

Write your project description here.
"""
    else:
        # Create regular page
        file_path = content_dir / f"{slug}.md"
        
        # Create front matter
        front_matter = f"""---
title: "{title}"
layout: page
description: ""
---

# {title}

Write your page content here.
"""
    
    # Create the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(front_matter)
    
    print(f"Created {type}: {file_path}")

@cli.command()
@click.argument('name')
@click.option('--directory', '-d', default='.', help='Directory of the site')
def theme(name, directory):
    """Add a theme to your site."""
    # Get path to themes directory
    themes_dir = Path(__file__).parent.parent / 'themes'
    available_themes = [d.name for d in themes_dir.iterdir() if d.is_dir()]
    
    if name not in available_themes:
        print(f"Error: Theme '{name}' not found. Available themes: {', '.join(available_themes)}")
        return
    
    # Update the config file
    config_path = Path(directory) / 'giggle.yaml'
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return
    
    # Create a site instance to handle config
    site = GiggleSite(directory)
    
    # Update theme in config
    site.config['theme']['name'] = name
    
    # Write updated config
    import yaml
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(site.config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Theme '{name}' applied to the site. Run 'giggle serve' to see the changes.")

def _create_sample_content(site_dir: Path) -> None:
    """
    Create sample content for a new site.
    
    Args:
        site_dir: Site directory
    """
    # Create sample home page
    home_page = site_dir / 'content' / 'pages' / 'index.md'
    with open(home_page, 'w', encoding='utf-8') as f:
        f.write("""---
title: "Home"
layout: page
---

# Welcome to My Giggle Site

This is a sample home page created by Giggle. Edit this file to customize your home page.

## Features

- **Simple**: Write content in Markdown
- **Flexible**: Customize your site with YAML configuration
- **Powerful**: Built-in support for blogs, projects, and more

[Learn more about Giggle](https://github.com/JoyenBenitto/giggle)
""")
    
    # Create sample about page
    about_page = site_dir / 'content' / 'pages' / 'about.md'
    with open(about_page, 'w', encoding='utf-8') as f:
        f.write("""---
title: "About"
layout: page
---

# About Me

This is a sample about page. Replace this content with information about yourself or your project.

## Contact

- Email: your.email@example.com
- GitHub: [yourusername](https://github.com/yourusername)
- Twitter: [@yourusername](https://twitter.com/yourusername)
""")
    
    # Create sample blog post
    posts_dir = site_dir / 'content' / 'posts'
    posts_dir.mkdir(exist_ok=True, parents=True)
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    sample_post = posts_dir / f"{today}-hello-world.md"
    
    with open(sample_post, 'w', encoding='utf-8') as f:
        f.write(f"""---
title: "Hello World"
date: {today}
layout: post
description: "My first blog post with Giggle"
tags: ["giggle", "markdown"]
categories: ["General"]
---

# Hello World

This is a sample blog post created by Giggle. Edit this file or create new posts in the `content/posts` directory.

## Markdown Support

Giggle supports all standard Markdown features:

- **Bold** and *italic* text
- Lists and nested lists
- [Links](https://example.com)
- Code blocks with syntax highlighting:

```python
def hello_world():
    print("Hello from Giggle!")
```

## Front Matter

Each content file starts with YAML front matter that defines metadata:

```yaml
---
title: "Hello World"
date: {today}
layout: post
description: "My first blog post with Giggle"
tags: ["giggle", "markdown"]
categories: ["General"]
---
```

This metadata is used to organize and display your content.
""")
    
    # Create sample project
    projects_dir = site_dir / 'content' / 'projects'
    projects_dir.mkdir(exist_ok=True, parents=True)
    
    sample_project = projects_dir / "sample-project.md"
    with open(sample_project, 'w', encoding='utf-8') as f:
        f.write("""---
title: "Sample Project"
layout: project
description: "A sample project created with Giggle"
featured_image: ""
github: "https://github.com/yourusername/project"
demo: "https://example.com"
tags: ["web", "python"]
---

# Sample Project

This is a sample project created by Giggle. Edit this file or create new projects in the `content/projects` directory.

## Project Description

Describe your project here. What does it do? What technologies does it use? What problem does it solve?

## Features

- Feature 1
- Feature 2
- Feature 3

## Technologies Used

- Technology 1
- Technology 2
- Technology 3
""")
