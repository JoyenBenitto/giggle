import os
import sys
import logging
from pathlib import Path
import shutil
import time
import datetime
from typing import Optional, Dict, List, Any, Union
import re
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import Markdown
import frontmatter
from livereload import Server
import webbrowser

from giggle.core.config import load_config, default_config, validate_config
from giggle.core.content import process_content, discover_content, build_taxonomies
from giggle.core.renderer import setup_jinja_env
from giggle.core.utils import clean_directory, copy_assets, generate_sitemap
from giggle.__init__ import __version__

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class GiggleSite:
    """Core site generator for Giggle"""
    
    def __init__(self, site_dir: str, config_file: str = 'giggle.yaml', output_dir: str = None):
        """
        Initialize a new Giggle site generator
        
        Args:
            site_dir: Root directory of the site
            config_file: Path to configuration file relative to site_dir
            output_dir: Output directory for generated site (default: site_dir/_site)
        """
        self.site_dir = Path(site_dir).absolute()
        self.config_path = self.site_dir / config_file
        self.output_dir = Path(output_dir) if output_dir else self.site_dir / '_site'
        
        # Initialize core attributes
        self.config = {}
        self.content = {}
        self.taxonomies = {}
        self.templates_dir = None
        self.jinja_env = None
        
        # Load the configuration
        self._load_config()
        
        # Set up directories
        self._setup_directories()
        
        # Set up Markdown parser with extensions
        self.md = Markdown(extensions=[
            'markdown.extensions.meta',
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.toc',
            'markdown.extensions.codehilite',
            'markdown.extensions.attr_list',
        ])
        
        # Set up Jinja environment
        self._setup_templates()
    
    def _load_config(self):
        """Load site configuration from YAML file"""
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}. Using default configuration.")
            self.config = default_config()
        else:
            try:
                self.config = load_config(self.config_path)
                logger.info(f"Configuration loaded from {self.config_path}")
                
                # Validate configuration
                validate_config(self.config)
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                self.config = default_config()
    
    def _setup_directories(self):
        """Set up directory structure"""
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Set up content directories
        content_config = self.config.get('content', {}).get('directories', {})
        
        self.content_dirs = {
            'posts': self.site_dir / content_config.get('posts', 'content/posts'),
            'pages': self.site_dir / content_config.get('pages', 'content/pages'),
            'projects': self.site_dir / content_config.get('projects', 'content/projects'),
            'data': self.site_dir / content_config.get('data', 'content/data'),
        }
        
        # Create content directories if they don't exist
        for dir_path in self.content_dirs.values():
            dir_path.mkdir(exist_ok=True, parents=True)
        
        # Set up assets directory
        self.assets_dir = self.site_dir / 'assets'
        self.assets_dir.mkdir(exist_ok=True, parents=True)
        
        # Set up theme directories
        theme_name = self.config.get('theme', {}).get('name', 'modern')
        theme_path = self.config.get('theme', {}).get('path', None)
        
        if theme_path:
            self.theme_dir = self.site_dir / theme_path
            if not self.theme_dir.exists():
                logger.warning(f"Custom theme directory not found at {self.theme_dir}. Using default theme.")
                self.theme_dir = Path(__file__).parent.parent / 'themes' / theme_name
        else:
            self.theme_dir = Path(__file__).parent.parent / 'themes' / theme_name
        
        self.templates_dir = self.theme_dir / 'templates'
        self.theme_assets_dir = self.theme_dir / 'assets'
        
        logger.info(f"Using theme: {theme_name}")
    
    def _setup_templates(self):
        """Set up Jinja2 template environment"""
        # Create Jinja environment with both theme templates and user templates
        user_templates_dir = self.site_dir / 'layouts'
        template_dirs = []
        
        if user_templates_dir.exists():
            template_dirs.append(str(user_templates_dir))
        
        if self.templates_dir.exists():
            template_dirs.append(str(self.templates_dir))
        
        if not template_dirs:
            logger.error("No template directories found. Cannot continue.")
            sys.exit(1)
        
        self.jinja_env = setup_jinja_env(template_dirs, self.md)
        
        # Add site config to global template context
        self.jinja_env.globals['site'] = self.config.get('site', {})
        self.jinja_env.globals['theme'] = self.config.get('theme', {})
        self.jinja_env.globals['navigation'] = self.config.get('navigation', {})
        self.jinja_env.globals['current_year'] = datetime.datetime.now().year
        self.jinja_env.globals['giggle_version'] = __version__
    
    def discover_content(self):
        """Discover and process all content files"""
        logger.info("Discovering content...")
        
        # Discover content from all content directories
        self.content = {}
        for content_type, dir_path in self.content_dirs.items():
            if dir_path.exists():
                self.content[content_type] = discover_content(dir_path, content_type, self.site_dir)
                logger.info(f"Found {len(self.content[content_type])} {content_type}")
        
        # Build taxonomies (categories, tags, etc.)
        taxonomy_config = self.config.get('content', {}).get('taxonomies', [])
        self.taxonomies = build_taxonomies(self.content, taxonomy_config)
        
        return self.content
    
    def generate_navigation(self):
        """Generate site navigation"""
        # If navigation is defined in config, use that
        if 'navigation' in self.config and self.config['navigation'].get('main'):
            return self.config['navigation']
        
        # Otherwise, generate navigation from pages
        nav_items = []
        
        # Add home page
        nav_items.append({
            'title': 'Home',
            'url': '/',
        })
        
        # Add pages to navigation
        if 'pages' in self.content:
            for page in self.content['pages']:
                # Skip pages with 'exclude_from_nav' set to True
                if page.get('exclude_from_nav'):
                    continue
                
                nav_items.append({
                    'title': page.get('title', page.get('url', '').strip('/')),
                    'url': page.get('url', ''),
                })
        
        # Add content sections if they exist
        for section in ['posts', 'projects']:
            if section in self.content and self.content[section]:
                nav_items.append({
                    'title': section.capitalize(),
                    'url': f'/{section}/',
                })
        
        return {'main': nav_items}
    
    def build_site(self):
        """Build the entire site"""
        start_time = time.time()
        logger.info(f"Building site to {self.output_dir}...")
        
        # Clean output directory
        clean_directory(self.output_dir)
        
        # Discover content
        self.discover_content()
        
        # Generate navigation
        navigation = self.generate_navigation()
        self.jinja_env.globals['navigation'] = navigation
        
        # Process and write all content
        for content_type, items in self.content.items():
            for item in items:
                self._write_page(item, navigation)
        
        # Generate taxonomy pages
        for taxonomy_type, terms in self.taxonomies.items():
            for term, items in terms.items():
                self._write_taxonomy_page(taxonomy_type, term, items, navigation)
        
        # Copy theme assets
        if self.theme_assets_dir.exists():
            # Copy CSS
            css_dir = self.theme_assets_dir / 'css'
            if css_dir.exists():
                copy_assets(css_dir, self.output_dir / 'theme' / 'css')
            
            # Copy JS
            js_dir = self.theme_assets_dir / 'js'
            if js_dir.exists():
                copy_assets(js_dir, self.output_dir / 'theme' / 'js')
            
            # Copy other assets (images, fonts, etc.)
            for asset_dir in self.theme_assets_dir.iterdir():
                if asset_dir.is_dir() and asset_dir.name not in ['css', 'js']:
                    copy_assets(asset_dir, self.output_dir / 'theme' / asset_dir.name)
        
        # Copy user assets
        asset_dirs = self.config.get('build', {}).get('assets', [])
        for asset_dir in asset_dirs:
            asset_path = self.site_dir / asset_dir
            if asset_path.exists():
                copy_assets(asset_path, self.output_dir / asset_path.relative_to(self.site_dir))
        
        # Generate CSS from theme configuration
        self._generate_css()
        
        # Generate sitemap
        site_url = self.config.get('site', {}).get('url', '')
        if site_url:
            generate_sitemap(self.output_dir, site_url)
        
        # Print build summary
        end_time = time.time()
        build_time = end_time - start_time
        logger.info(f"Site built successfully in {build_time:.2f} seconds")
        
        return self.output_dir
    
    def _write_page(self, page, navigation):
        """Generate and write an HTML page"""
        # Determine template
        layout = page.get('layout', 'page')
        template_name = f"{layout}.html"
        
        try:
            template = self.jinja_env.get_template(template_name)
        except Exception as e:
            logger.error(f"Template '{template_name}' not found: {e}")
            template = self.jinja_env.get_template('page.html')
        
        # Prepare context
        site_config = self.config.get('site', {})
        # Add features to site config for template compatibility
        site_config['features'] = self.config.get('features', {})
        
        # Add current year for footer copyright
        current_year = datetime.datetime.now().year
        
        # Set up theme with appearance settings
        theme_config = self.config.get('theme', {})
        if 'appearance' not in theme_config:
            theme_config['appearance'] = {}
        
        # Set dark mode based on features
        theme_config['appearance']['dark_mode'] = self.config.get('features', {}).get('dark_mode', False)
        
        context = {
            'page': page,
            'content': page.get('content', ''),
            'site': site_config,
            'navigation': navigation,
            'theme': theme_config,
            'current_year': current_year,
        }
        
        # Render template
        try:
            html = template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template for {page.get('url')}: {e}")
            html = f"<h1>Error</h1><p>{e}</p>"
        
        # Write output file
        output_path = self.output_dir / page.get('url').lstrip('/')
        
        # Ensure directory exists
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Determine output filename
        permalink_style = self.config.get('build', {}).get('permalink_style', 'pretty')
        if permalink_style == 'pretty' and not output_path.name.endswith('.html'):
            # Create directory for pretty URLs
            output_path.mkdir(exist_ok=True, parents=True)
            output_file = output_path / 'index.html'
        else:
            if not output_path.name.endswith('.html'):
                output_file = output_path.with_suffix('.html')
            else:
                output_file = output_path
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.debug(f"Generated {output_file}")
    
    def _write_taxonomy_page(self, taxonomy_type, term, items, navigation):
        """Generate and write a taxonomy page"""
        # Get taxonomy configuration
        taxonomy_config = next((t for t in self.config.get('content', {}).get('taxonomies', []) 
                             if t.get('name') == taxonomy_type), {})
        
        # Prepare page data
        page = {
            'title': f"{term} - {taxonomy_config.get('singular', taxonomy_type)}",
            'layout': 'taxonomy',
            'url': f"{taxonomy_config.get('path', f'/{taxonomy_type}/')}{term}/",
            'taxonomy_type': taxonomy_type,
            'taxonomy_term': term,
            'items': items,
        }
        
        # Write the page
        self._write_page(page, navigation)
    
    def _generate_css(self):
        """Generate CSS from theme configuration"""
        # Get theme configuration
        theme_config = self.config.get('theme', {})
        colors = theme_config.get('colors', {})
        fonts = theme_config.get('fonts', {})
        layout = theme_config.get('layout', {})
        components = theme_config.get('components', {})
        
        # Create CSS variables
        css_vars = []
        
        # Add color variables
        for name, value in colors.items():
            css_vars.append(f"--color-{name}: {value};")
        
        # Add font variables
        for name, value in fonts.items():
            css_vars.append(f"--font-{name}: {value};")
        
        # Add layout variables
        for name, value in layout.items():
            css_vars.append(f"--layout-{name}: {value};")
        
        # Add component variables
        for component, props in components.items():
            for name, value in props.items():
                css_vars.append(f"--component-{component}-{name}: {value};")
        
        # Create CSS root
        css = ":root {\n  " + "\n  ".join(css_vars) + "\n}\n"
        
        # Write CSS file
        css_dir = self.output_dir / 'static' / 'css'
        css_dir.mkdir(exist_ok=True, parents=True)
        
        with open(css_dir / 'variables.css', 'w', encoding='utf-8') as f:
            f.write(css)
        
        logger.debug("Generated CSS variables")
    
    def serve(self, host='localhost', port=8000):
        """Serve the site with live reload"""
        # Build the site first
        self.build_site()
        
        # Create server
        server = Server()
        
        # Watch content directories
        for dir_path in self.content_dirs.values():
            if dir_path.exists():
                server.watch(str(dir_path) + '/**/*', lambda: self.build_site())
        
        # Watch templates
        if self.templates_dir.exists():
            server.watch(str(self.templates_dir) + '/**/*', lambda: self.build_site())
        
        # Watch user templates
        user_templates_dir = self.site_dir / 'layouts'
        if user_templates_dir.exists():
            server.watch(str(user_templates_dir) + '/**/*', lambda: self.build_site())
        
        # Watch assets
        server.watch(str(self.assets_dir) + '/**/*', lambda: self.build_site())
        
        # Watch config file
        server.watch(str(self.config_path), lambda: self.build_site())
        
        # Serve
        url = f"http://{host}:{port}"
        logger.info(f"Serving site at {url}")
        logger.info("Press Ctrl+C to stop")
        
        # Open browser
        webbrowser.open(url)
        
        # Start server
        server.serve(root=str(self.output_dir), host=host, port=port, liveport=35729)