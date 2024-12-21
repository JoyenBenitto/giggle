"""Enhanced Static Site Generator for Giggle"""

import os
import pathlib
import logging
import sys
from typing import Dict, List, Optional, Any, Union, Tuple

import yaml
import markdown
from markdown.extensions.meta import MetaExtension
from jinja2 import Environment, FileSystemLoader, select_autoescape

from giggle import __version__
import giggle.template as giggle_template

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def log_section(title):
    """Log a section header to make logs more readable."""
    logger.info("")
    logger.info("=" * 50)
    logger.info(title)
    logger.info("=" * 50)
    logger.info("")

class ConfigurationLoader:
    """
    Advanced configuration loader with support for multiple config files
    and configuration merging.
    """
    
    @staticmethod
    def load_config(config_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Load and merge multiple configuration files.
        
        Args:
            config_paths (Union[str, List[str]]): Path or list of paths to config files
        
        Returns:
            Merged configuration dictionary
        """
        if isinstance(config_paths, str):
            config_paths = [config_paths]
        
        merged_config = {}
        
        for config_path in config_paths:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    merged_config = ConfigurationLoader._deep_merge(merged_config, config)
            except FileNotFoundError:
                logger.warning(f"Configuration file not found: {config_path}")
            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML file {config_path}: {e}")
        
        return merged_config
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.
        
        Args:
            base (Dict): Base dictionary
            update (Dict): Dictionary to merge into base
        
        Returns:
            Merged dictionary
        """
        for key, value in update.items():
            if isinstance(value, dict):
                base[key] = ConfigurationLoader._deep_merge(
                    base.get(key, {}), value
                )
            else:
                base[key] = value
        return base
    
    @staticmethod
    def resolve_config_paths(config_paths: Union[str, List[str]]) -> List[str]:
        """
        Resolve configuration file paths.
        
        Args:
            config_paths (Union[str, List[str]]): Path or list of paths to config files
        
        Returns:
            List of resolved absolute paths
        """
        if isinstance(config_paths, str):
            config_paths = [config_paths]
        
        return [
            os.path.abspath(path) 
            for path in config_paths 
            if os.path.exists(path)
        ]

class BlogProcessor:
    """Advanced blog processing and rendering."""
    
    def __init__(self, blogs_path: str):
        """
        Initialize blog processor.
        
        Args:
            blogs_path (str): Path to blog markdown files
        """
        self.blogs_path = blogs_path
        self.blog_files = self._get_blog_files()
    
    def _get_blog_files(self) -> List[str]:
        """
        Retrieve list of markdown blog files.
        
        Returns:
            List of blog markdown filenames
        """
        try:
            return [
                file for file in os.listdir(self.blogs_path) 
                if file.endswith(".md")
            ]
        except OSError as e:
            logger.error(f"Error reading blog directory: {e}")
            return []
    
    def _extract_blog_metadata(self, blog_file: str) -> Dict[str, str]:
        """
        Extract metadata from a blog markdown file.
        
        Args:
            blog_file (str): Filename of the blog markdown
        
        Returns:
            Dictionary of blog metadata
        """
        try:
            with open(os.path.join(self.blogs_path, blog_file), 'r', encoding='utf-8') as f:
                content = f.read()
                md = markdown.Markdown(extensions=['meta'])
                md.convert(content)
                
                metadata = {
                    'title': md.Meta.get('title', [blog_file])[0],
                    'date': md.Meta.get('date', ['Unknown'])[0],
                    'summary': md.Meta.get('summary', ['No summary available'])[0],
                    'filename': blog_file.replace('.md', '.html')
                }
                return metadata
        except Exception as e:
            logger.warning(f"Could not process blog {blog_file}: {e}")
            return {}
    
    def generate_blog_collection_page(self) -> str:
        """
        Generate a blog collection page with blog summaries.
        
        Returns:
            HTML string representing blog collection
        """
        blog_list_html = ""
        for blog in self.blog_files:
            blog_metadata = self._extract_blog_metadata(blog)
            if blog_metadata:
                blog_list_html += giggle_template.blog_template.format(**blog_metadata)
        
        return f"""
        <div class="blog-collection">
            <h1>Blog Posts</h1>
            <ul>
                {blog_list_html}
            </ul>
        </div>
        """
    
    def generate_standalone_blog_pages(self) -> List[Tuple[str, str]]:
        """
        Generate individual blog pages.
        
        Returns:
            List of tuples with (filename, rendered_content)
        """
        blog_pages = []
        for blog_file in self.blog_files:
            try:
                with open(os.path.join(self.blogs_path, blog_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    md = markdown.Markdown(extensions=['meta', 'fenced_code', 'codehilite'])
                    html_content = md.convert(content)
                    
                    blog_pages.append((
                        blog_file.replace('.md', '.html'),
                        f"""
                        <article class="blog-post">
                            <h1>{md.Meta.get('title', [blog_file])[0]}</h1>
                            <div class="blog-meta">
                                <span class="blog-date">{md.Meta.get('date', ['Unknown'])[0]}</span>
                            </div>
                            {html_content}
                        </article>
                        """
                    ))
            except Exception as e:
                logger.error(f"Error processing blog page {blog_file}: {e}")
        
        return blog_pages

class TagProcessor:
    """Advanced tag processing and generation."""
    
    def __init__(self, recipe: Dict[str, Any]):
        """
        Initialize tag processor.
        
        Args:
            recipe (Dict): Site configuration
        """
        self.recipe = recipe
        self.tag_db = self._create_tag_database()
    
    def _create_tag_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Create a comprehensive tag database.
        
        Returns:
            Dictionary mapping normalized tags to their metadata
        """
        tag_db = {}
        
        def process_tags(file_path: str, html_path: str):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    md = markdown.Markdown(extensions=['meta'])
                    md.convert(content)
                    
                    if 'tags' in md.Meta:
                        tag_list = [tag.strip() for tag in md.Meta['tags'][0].split(',')]
                        for tag in tag_list:
                            normalized_tag = tag.lower().replace(" ", "-")
                            if normalized_tag not in tag_db:
                                tag_db[normalized_tag] = {
                                    'display_name': tag,
                                    'pages': [html_path]
                                }
                            else:
                                tag_db[normalized_tag]['pages'].append(html_path)
            except Exception as e:
                logger.error(f"Error processing tags in {file_path}: {e}")
        
        # Process main pages
        for page, file_path in self.recipe.get("pages", {}).items():
            html_path = f"../{page}.html"
            process_tags(file_path, html_path)
        
        return tag_db
    
    def _process_tags(self):
        """Process tags from markdown files and generate tag pages."""
        tag_dict = {}
        
        # Process all markdown files
        for page, markdown_path in self.recipe.get("pages", {}).items():
            try:
                logger.info(f"Processing tags for {markdown_path}")
                
                # Skip if it's a directory
                if os.path.isdir(markdown_path):
                    logger.info(f"Skipping directory {markdown_path} during tag processing")
                    continue
                
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    md = markdown.Markdown(extensions=['meta'])
                    md.convert(content)
                    
                    # Extract tags from metadata
                    if 'tags' in md.Meta:
                        tags = [tag.strip() for tag in md.Meta['tags'][0].strip('[]').split(',')]
                        logger.info(f"Found tags in {page}: {tags}")
                        
                        # Add page to each tag's list
                        for tag in tags:
                            tag = tag.strip()
                            if tag not in tag_dict:
                                tag_dict[tag] = []
                            tag_dict[tag].append({
                                'page': page,
                                'title': md.Meta.get('title', [page])[0],
                                'description': md.Meta.get('description', [''])[0]
                            })
                    else:
                        logger.info(f"No tags found in {page}")
            except Exception as e:
                logger.error(f"Error processing tags in {markdown_path}: {e}")
                continue
        
        # Generate tag pages if enabled
        if self.recipe.get("features", {}).get("tag_pages", False):
            logger.info("Generating tag pages...")
            env = Environment(
                loader=FileSystemLoader(
                    os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
                )
            )
            tag_template = env.get_template("tag_page.jinja")
            
            for tag, pages in tag_dict.items():
                try:
                    rendered_page = tag_template.render(
                        recipe=self.recipe,
                        tag=tag,
                        pages=pages
                    )
                    
                    # Write tag page
                    tag_file = os.path.join(self.build_dir, f"tag_{tag}.html")
                    with open(tag_file, "w", encoding='utf-8') as f:
                        f.write(rendered_page)
                    logger.info(f"Generated tag page: tag_{tag}.html")
                except Exception as e:
                    logger.error(f"Error generating tag page for {tag}: {e}")
    
    def generate_tag_pages(self, build_dir: str) -> None:
        """
        Generate individual tag pages and tag index.
        
        Args:
            build_dir (str): Build directory path
        """
        self.build_dir = build_dir
        self._process_tags()
        
        tag_dir = os.path.join(build_dir, 'tags')
        os.makedirs(tag_dir, exist_ok=True)
        
        # Check if tag page templates exist
        try:
            env = Environment(
                loader=FileSystemLoader(
                    os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
                ),
                autoescape=select_autoescape()
            )
            tag_index_template = env.get_template("tag_index.jinja")
        except Exception as e:
            logger.warning(f"Tag page templates not found. Skipping tag page generation: {e}")
            return
        
        # Prepare default typography and styles
        default_typography = {
            'font_family': {
                'body': '"Inter", sans-serif',
                'headers': '"Roboto", sans-serif'
            },
            'sizes': {
                'body': '16px',
                'headers': {
                    'h1': '1.8rem',
                    'h2': '1.5rem',
                    'h3': '1.3rem'
                }
            }
        }
        
        default_styles = {
            'dark_mode': {
                'background_color': '#121212',
                'text_color': '#E0E0E0',
                'primary_color': '#2196F3',
                'secondary_color': '#A0A0A0'
            }
        }
        
        # Ensure styles is a dictionary with dark_mode
        styles = self.recipe.get('styles', {})
        if 'dark_mode' not in styles:
            styles['dark_mode'] = default_styles['dark_mode']
        
        # Debug logging
        logger.info(f"Typography: {default_typography}")
        logger.info(f"Styles: {styles}")
        
        # Generate tag index page
        try:
            rendered_tag_index = tag_index_template.render(
                tag_db=self.tag_db,
                typography=self.recipe.get('typography', default_typography),
                styles=styles
            )
            
            with open(os.path.join(build_dir, "tags.html"), "w", encoding='utf-8') as f:
                f.write(rendered_tag_index)
        except Exception as e:
            logger.error(f"Error generating tag index page: {e}")

class StaticSiteGenerator:
    """Modern static site generator with enhanced configuration handling."""
    
    def __init__(
        self, 
        site_config: Union[str, List[str]], 
        style_config: Optional[Union[str, List[str]]] = None, 
        build_dir: Optional[str] = None
    ):
        """
        Initialize static site generator with flexible configuration.
        
        Args:
            site_config (Union[str, List[str]]): Path to site configuration file(s)
            style_config (Optional[Union[str, List[str]]]): Path to style configuration file(s)
            build_dir (Optional[str]): Output directory for generated site
        """
        # Resolve and load configuration files
        site_config_paths = ConfigurationLoader.resolve_config_paths(site_config)
        style_config_paths = ConfigurationLoader.resolve_config_paths(style_config or [])
        
        # Merge configurations
        self.site_config = ConfigurationLoader.load_config(site_config_paths)
        self.style_config = ConfigurationLoader.load_config(style_config_paths)
        
        # Merge site and style configurations
        self.recipe = ConfigurationLoader._deep_merge(
            self.site_config, 
            self.style_config
        )
        
        # Ensure compatibility with existing templates
        self._normalize_recipe_structure()
        
        # Set build directory
        self.build_dir = build_dir or os.path.join(os.getcwd(), 'build')
        
        # Determine blogs path from configuration
        self.blogs_path = self._get_blogs_path()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Initialize tag database
        self.tag_db = {}
        
        # Initialize Jinja environment
        self.env = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
            ),
            autoescape=select_autoescape()
        )
    
    def _normalize_recipe_structure(self):
        """
        Normalize the recipe dictionary to ensure compatibility with existing templates.
        """
        # Ensure 'style' key exists with all expected subkeys
        if 'style' not in self.recipe:
            self.recipe['style'] = {}
        
        # Map components to style structure
        style_mapping = {
            'body': ['body', 'main'],
            'a': ['links'],
            'h1': ['headers'],
            'h2': ['headers'],
            'h3': ['headers'],
            'h4': ['headers'],
            'h5': ['headers'],
            'h6': ['headers'],
            'blockquote': ['blockquotes'],
            'tag': ['tags'],
            'navbar': ['navbar'],
            'footer': ['footer']
        }
        
        # Populate style dictionary from components
        for key, component_keys in style_mapping.items():
            self.recipe['style'][key] = {}
            for component_key in component_keys:
                component = self.recipe.get('components', {}).get(component_key, {})
                
                # Handle cases where component might be a string or not a dictionary
                if not isinstance(component, dict):
                    # If it's a string, try to parse it as a reference
                    if isinstance(component, str):
                        try:
                            # Remove curly braces and split
                            ref_path = component.strip('{}').split('.')
                            component = self._get_nested_value(self.recipe, ref_path)
                        except Exception:
                            component = {}
                    else:
                        component = {}
                
                # Merge component styles
                for style_prop, value in component.items():
                    if style_prop not in ['font_family', 'font_style', 'font_weight']:
                        # Handle nested references
                        if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                            try:
                                ref_path = value.strip('{}').split('.')
                                value = self._get_nested_value(self.recipe, ref_path)
                            except Exception:
                                continue
                        
                        self.recipe['style'][key][style_prop] = value
        
        # Add some default values if missing
        default_styles = {
            'body': {'bg_color': 'white', 'color': 'black'},
            'a': {'color': 'blue'},
            'h1': {'color': 'black'},
            'tag': {'color': 'red', 'mb': 1, 'ml': 0, 'mr': 0, 'mt': 0},
            'navbar': {'color': 'black'},
            'footer': {'color': 'black'}
        }
        
        for key, defaults in default_styles.items():
            if key in self.recipe['style']:
                for prop, value in defaults.items():
                    if prop not in self.recipe['style'][key]:
                        self.recipe['style'][key][prop] = value
        
        # Ensure fonts are present
        if 'fonts' not in self.recipe:
            self.recipe['fonts'] = ''
        
        # Ensure favicon is present
        if 'favicon' not in self.recipe:
            self.recipe['favicon'] = '🌐'
    
    def _get_nested_value(self, data: Dict[str, Any], keys: List[str]) -> Any:
        """
        Retrieve a nested value from a dictionary.
        
        Args:
            data (Dict): Source dictionary
            keys (List[str]): List of keys to traverse
        
        Returns:
            Value at the specified nested location
        """
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, {})
            else:
                return {}
        return data
    
    def _get_blogs_path(self) -> Optional[str]:
        """
        Extract blogs path from configuration.
        
        Returns:
            Optional path to blogs directory
        """
        nav_items = self.site_config.get('navigation', [])
        blogs_nav = next(
            (item for item in nav_items if item.get('name', '').lower() == 'blogs'), 
            None
        )
        return blogs_nav.get('path') if blogs_nav else None
    
    def generate(self):
        """Generate the static site."""
        log_section("Starting Static Site Generation")
        
        try:
            # Generate pages from markdown
            log_section("Generating Pages")
            self._generate_pages()
            
            # Generate CSS from template
            log_section("Generating Styles")
            self._generate_css()
            
            # Copy static assets
            log_section("Copying Assets")
            self._copy_assets()
            
            # Process tags
            if self.recipe.get("features", {}).get("tag_pages", False):
                log_section("Processing Tags")
                self._process_tags()
            
            log_section("Build Complete")
            logger.info("Static site generation completed successfully!")
            logger.info(f"Output directory: {self.build_dir}")
            
        except Exception as e:
            logger.error(f"Error during site generation: {e}")
            raise
    
    def _process_blog_directory(self, blog_dir: str) -> None:
        """Process a directory of blog posts."""
        logger.info(f"Processing blog directory: {blog_dir}")
        
        try:
            # Get all markdown files in the blog directory
            blog_files = [f for f in os.listdir(blog_dir) if f.endswith('.md')]
            logger.info(f"Found blog files: {blog_files}")
            
            # Process each blog post
            blog_posts = []
            for blog_file in blog_files:
                blog_path = os.path.join(blog_dir, blog_file)
                try:
                    # Read and parse blog post
                    with open(blog_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse markdown with metadata
                    md = markdown.Markdown(extensions=['meta', 'fenced_code'])
                    html_content = md.convert(content)
                    meta = md.Meta
                    
                    # Extract metadata
                    title = meta.get('title', [blog_file])[0]
                    description = meta.get('description', [''])[0]
                    date = meta.get('date', [''])[0]
                    tags = meta.get('tags', [])[0].split(',') if 'tags' in meta else []
                    tags = [tag.strip() for tag in tags]
                    
                    # Generate output path
                    output_filename = os.path.splitext(blog_file)[0] + '.html'
                    output_path = os.path.join(self.build_dir, 'blog', output_filename)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Store in tag database
                    relative_url = os.path.join('blog', output_filename)
                    self.tag_db[output_path] = {
                        'title': title,
                        'description': description,
                        'tags': tags,
                        'date': date,
                        'url': relative_url
                    }
                    
                    # Render blog post
                    template = self.env.get_template('blog_post.jinja')
                    rendered = template.render(
                        content=html_content,
                        title=title,
                        description=description,
                        date=date,
                        tags=tags,
                        recipe=self.recipe,
                        site=self.recipe.get('site', {}),
                        style=self.style_config
                    )
                    
                    # Write blog post
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(rendered)
                    
                    # Add to blog posts list
                    blog_posts.append({
                        'title': title,
                        'description': description,
                        'date': date,
                        'tags': tags,
                        'url': relative_url
                    })
                    
                    logger.info(f"Processed blog post: {title}")
                    
                except Exception as e:
                    logger.error(f"Error processing blog post {blog_file}: {str(e)}")
                    continue
            
            # Sort blog posts by date (newest first)
            blog_posts.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Generate blog index
            try:
                template = self.env.get_template('blog_index.jinja')
                index_path = os.path.join(self.build_dir, 'blogs.html')
                
                rendered = template.render(
                    posts=blog_posts,
                    recipe=self.recipe,
                    site=self.recipe.get('site', {}),
                    style=self.style_config
                )
                
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(rendered)
                logger.info("Generated blog index page")
                
            except Exception as e:
                logger.error(f"Error generating blog index: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error processing blog directory: {str(e)}")
            raise
    
    def _generate_pages(self):
        """Generate HTML pages from markdown sources."""
        for page, markdown_path in self.recipe.get("pages", {}).items():
            try:
                # Handle blog directory separately
                if os.path.isdir(markdown_path):
                    if page == 'blogs':
                        self._process_blog_directory(markdown_path)
                    logger.info(f"Skipping directory {markdown_path}, will be processed separately")
                    continue
                    
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    md = markdown.Markdown(extensions=['meta', 'fenced_code', 'codehilite'])
                    body = md.convert(content)
                    
                # Extract metadata
                title = md.Meta.get('title', [page])[0]
                description = md.Meta.get('description', [''])[0]
                tags = md.Meta.get('tags', [])[0].split(',') if 'tags' in md.Meta else []
                tags = [tag.strip() for tag in tags]
                date = md.Meta.get('date', [''])[0]
                
                # Store page info in tag database
                page_url = os.path.relpath(os.path.join(self.build_dir, f"{page}.html"), self.build_dir)
                self.tag_db[os.path.join(self.build_dir, f"{page}.html")] = {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'date': date,
                    'url': page_url
                }
                
                rendered_page = self.env.get_template("base.jinja").render(
                    recipe=self.recipe, 
                    body=body, 
                    back=" ",
                    version=__version__
                )
                
                output_path = os.path.join(self.build_dir, f"{page}.html")
                with open(output_path, "w", encoding='utf-8') as f:
                    f.write(rendered_page)
                
                logger.info(f"Generated page: {page}.html")
            except Exception as e:
                logger.error(f"Error generating page {page}: {e}")
    
    def _generate_css(self):
        """Generate CSS file from Jinja template."""
        env = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
            )
        )
        css_template = env.get_template("style.css.jinja")
        
        # Extract style-related configuration
        style_context = {
            'colors': self.style_config.get('colors', {}),
            'typography': self.style_config.get('typography', {}),
            'styles': self.style_config.get('styles', {}),
            'components': self.style_config.get('components', {}),
            'table': self.style_config.get('table', {}),
            'image': self.style_config.get('image', {})
        }
        
        try:
            rendered_css = css_template.render(**style_context)
            
            with open(os.path.join(self.build_dir, "style.css"), "w", encoding='utf-8') as f:
                f.write(rendered_css)
            
            logger.info("Generated style.css with theme configuration")
        except Exception as e:
            logger.error(f"Error generating CSS: {e}")
            # Create a minimal fallback CSS if template rendering fails
            fallback_css = """
            body { background-color: #121212; color: #E0E0E0; }
            a { color: #2196F3; }
            """
            with open(os.path.join(self.build_dir, "style.css"), "w", encoding='utf-8') as f:
                f.write(fallback_css)
            logger.info("Generated fallback style.css due to error")
    
    def _copy_assets(self):
        """Copy JavaScript and other static assets to build directory."""
        import shutil
        
        # Copy JavaScript files from templates
        template_dir = os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
        js_files = [f for f in os.listdir(template_dir) if f.endswith('.js.jinja')]
        
        for js_file in js_files:
            try:
                # Read the template
                with open(os.path.join(template_dir, js_file), 'r', encoding='utf-8') as f:
                    js_content = f.read()
                
                # Write to build directory without .jinja extension
                output_file = os.path.join(self.build_dir, js_file.replace('.jinja', ''))
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                
                logger.info(f"Copied JavaScript file: {js_file}")
            except Exception as e:
                logger.error(f"Error copying JavaScript file {js_file}: {e}")
        
        # Copy other static assets
        for asset_path in self.recipe.get('mover', []):
            if not os.path.exists(asset_path):
                logger.warning(f"Asset path does not exist: {asset_path}")
                continue
                
            try:
                if os.path.isdir(asset_path):
                    # Copy directory
                    dest_dir = os.path.join(self.build_dir, os.path.basename(asset_path))
                    if os.path.exists(dest_dir):
                        shutil.rmtree(dest_dir)
                    shutil.copytree(asset_path, dest_dir)
                else:
                    # Copy file
                    shutil.copy2(asset_path, self.build_dir)
                logger.info(f"Copied asset: {asset_path}")
            except Exception as e:
                logger.error(f"Error copying asset {asset_path}: {e}")
        
        # Copy favicon files if they exist
        favicon_files = ['favicon.svg', 'favicon-16x16.png']
        assets_dir = './assets'
        if os.path.exists(assets_dir):
            for favicon in favicon_files:
                src_path = os.path.join(assets_dir, favicon)
                if os.path.exists(src_path):
                    try:
                        shutil.copy2(src_path, os.path.join(self.build_dir, favicon))
                        logger.info(f"Copied favicon: {favicon}")
                    except Exception as e:
                        logger.error(f"Error copying favicon {favicon}: {e}")
    
    def _generate_blog_pages(self, blog_processor: BlogProcessor):
        """Generate blog pages."""
        env = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
            ),
            autoescape=select_autoescape()
        )
        base_template = env.get_template("base.jinja")
        blog_template = env.get_template("back_base.jinja")
        
        # Blog collection page
        blog_body = blog_processor.generate_blog_collection_page()
        rendered_blog_collection = base_template.render(
            recipe=self.recipe,
            body=blog_body,
            back=" ",
            version=__version__
        )
        
        with open(os.path.join(self.build_dir, "blogs.html"), "w", encoding='utf-8') as f:
            f.write(rendered_blog_collection)
        
        # Individual blog pages
        blog_dir = os.path.join(self.build_dir, "blog")
        os.makedirs(blog_dir, exist_ok=True)
        
        for blog_file, blog_content in blog_processor.generate_standalone_blog_pages():
            rendered_blog = blog_template.render(
                recipe=self.recipe,
                body=blog_content,
                back="."
            )
            
            blog_output_path = os.path.join(blog_dir, blog_file)
            try:
                with open(blog_output_path, "w", encoding='utf-8') as f:
                    f.write(rendered_blog)
                
                # Extract metadata
                title = blog_content.split('<h1>')[1].split('</h1>')[0]
                description = blog_content.split('<p>')[1].split('</p>')[0]
                date = blog_content.split('<span class="blog-date">')[1].split('</span>')[0]
                tags = []
                
                # Store page info in tag database
                page_url = os.path.relpath(blog_output_path, self.build_dir)
                self.tag_db[blog_output_path] = {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'date': date,
                    'url': page_url
                }
            except Exception as e:
                logger.error(f"Error generating blog post page for {blog_file}: {e}")
    
    def _process_tags(self):
        """Process and generate tag pages."""
        logger.info("Processing tags from all content")
        
        # Debug: Print tag database
        logger.debug("Tag Database Contents:")
        for path, info in self.tag_db.items():
            logger.debug(f"Path: {path}")
            logger.debug(f"Info: {info}")
        
        # Collect all tags and their associated pages
        tag_pages = {}
        for page_info in self.tag_db.values():
            for tag in page_info.get('tags', []):
                if tag not in tag_pages:
                    tag_pages[tag] = []
                tag_pages[tag].append({
                    'title': page_info.get('title', ''),
                    'description': page_info.get('description', ''),
                    'url': page_info.get('url', ''),
                    'date': page_info.get('date', '')
                })
        
        # Debug: Print collected tags
        logger.debug("Collected Tags:")
        logger.debug(tag_pages)
        
        # Generate tag pages
        tag_template = self.env.get_template('tag_page.jinja')
        tags_dir = os.path.join(self.build_dir, 'tags')
        os.makedirs(tags_dir, exist_ok=True)
        
        for tag, pages in tag_pages.items():
            output_path = os.path.join(tags_dir, f"{tag}.html")
            try:
                # Sort pages by date if available
                pages.sort(key=lambda x: x.get('date', ''), reverse=True)
                
                # Debug: Print context for tag page
                logger.debug(f"Rendering tag page for {tag}")
                logger.debug(f"Pages: {pages}")
                logger.debug(f"Recipe: {self.recipe}")
                
                # Render tag page
                html_content = tag_template.render(
                    tag=tag,
                    pages=pages,
                    recipe=self.recipe,  # Pass recipe instead of site
                    site=self.recipe.get('site', {}),
                    style=self.style_config
                )
                
                # Write tag page
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Generated tag page: {tag}.html")
                
            except Exception as e:
                logger.error(f"Error generating tag page for '{tag}': {str(e)}")
                logger.debug(f"Template context: tag={tag}, pages={pages}, recipe={self.recipe}, style={self.style_config}")
                continue
        
        # Generate tags index
        try:
            tags_template = self.env.get_template('tags_index.jinja')
            tags_index_path = os.path.join(self.build_dir, 'tags.html')
            
            # Sort tags alphabetically
            sorted_tags = sorted(tag_pages.keys())
            
            # Debug: Print context for tags index
            logger.debug("Rendering tags index")
            logger.debug(f"Tags: {sorted_tags}")
            logger.debug(f"Tag counts: {tag_pages}")
            
            # Render tags index
            html_content = tags_template.render(
                tags=sorted_tags,
                tag_counts={tag: len(pages) for tag, pages in tag_pages.items()},
                recipe=self.recipe,  # Pass recipe here too
                site=self.recipe.get('site', {}),
                style=self.style_config
            )
            
            # Write tags index
            with open(tags_index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info("Generated tags index page")
            
        except Exception as e:
            logger.error(f"Error generating tags index: {str(e)}")
            logger.debug(f"Template context: tags={sorted_tags}, recipe={self.recipe}, style={self.style_config}")

class ssg(StaticSiteGenerator):
    """
    Backward compatibility wrapper for StaticSiteGenerator.
    Maintains the exact same method signature as the original ssg class.
    """
    def __init__(self, recipe, build=None):
        """
        Initialize the ssg instance.
        
        Args:
            recipe (Dict): Site configuration dictionary
            build (str, optional): Build directory path
        """
        super().__init__(recipe, build)
