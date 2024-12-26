"""Enhanced Static Site Generator for Giggle"""

import os
import pathlib
import logging
import sys
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

import yaml
import markdown
from markdown.extensions.meta import MetaExtension
from jinja2 import Environment, FileSystemLoader, select_autoescape

from giggle import __version__
import giggle.template as giggle_template

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
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
    
    def __init__(self, blogs_path: str, env: Environment):
        """
        Initialize blog processor.
        
        Args:
            blogs_path (str): Path to blog markdown files
            env (Environment): Jinja2 environment for template rendering
        """
        logger.info(f"Initializing BlogProcessor with path: {blogs_path}")
        self.blogs_path = blogs_path
        self.env = env
        self.blog_files = self._get_blog_files()
        logger.info(f"Found blog files: {self.blog_files}")
        self.blogs_metadata = self._process_all_blogs()
        logger.info(f"Processed {len(self.blogs_metadata)} blog posts")
    
    def _get_blog_files(self) -> List[str]:
        """
        Retrieve list of markdown blog files.
        
        Returns:
            List of blog markdown filenames
        """
        try:
            if not os.path.exists(self.blogs_path):
                logger.error(f"Blog directory does not exist: {self.blogs_path}")
                return []
            
            files = [
                file for file in os.listdir(self.blogs_path) 
                if file.endswith(".md")
            ]
            logger.debug(f"Found markdown files in {self.blogs_path}: {files}")
            return files
        except OSError as e:
            logger.error(f"Error reading blog directory: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string into datetime object.
        
        Args:
            date_str (str): Date string from blog metadata
            
        Returns:
            datetime object
        """
        if not date_str:
            return None
            
        try:
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%B %d, %Y", "%d %B %Y"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If no format matches, return None
            logger.warning(f"Could not parse date: {date_str}")
            return None
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {e}")
            return None

    def _extract_blog_metadata(self, blog_file: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a blog markdown file.
        
        Args:
            blog_file (str): Filename of the blog markdown
        
        Returns:
            Dictionary of blog metadata
        """
        try:
            full_path = os.path.join(self.blogs_path, blog_file)
            logger.debug(f"Extracting metadata from {full_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            md = markdown.Markdown(extensions=['meta', 'fenced_code', 'codehilite'])
            body = md.convert(content)
            
            # Extract metadata
            title = md.Meta.get('title', [os.path.splitext(blog_file)[0]])[0]
            description = md.Meta.get('description', [''])[0]
            date_str = md.Meta.get('date', [''])[0]
            date_obj = self._parse_date(date_str)
            
            logger.debug(f"Raw metadata for {blog_file}:")
            logger.debug(f"  Title: {title}")
            logger.debug(f"  Description: {description}")
            logger.debug(f"  Date: {date_str}")
            logger.debug(f"  Parsed date: {date_obj}")
            
            tags = []
            if 'tags' in md.Meta:
                # Clean up tags by removing brackets and extra whitespace
                raw_tags = md.Meta['tags'][0].strip('[]').split(',')
                tags = [tag.strip() for tag in raw_tags]
                logger.debug(f"  Tags: {tags}")
            
            # Generate URL - ensure it's in the blogs/ subdirectory
            url = f"blogs/{os.path.splitext(blog_file)[0]}.html"
            logger.debug(f"  URL: {url}")
            
            metadata = {
                'title': title,
                'description': description,
                'date': date_str,
                'datetime': date_obj or datetime.min,  # Use min date if parsing fails
                'tags': tags,
                'url': url,
                'body': body
            }
            logger.debug(f"Extracted metadata: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from {blog_file}: {e}")
            return None
    
    def _process_all_blogs(self) -> List[Dict[str, Any]]:
        """
        Process all blog files and sort by date.
        
        Returns:
            List of blog metadata dictionaries, sorted by date
        """
        blogs = []
        for blog_file in self.blog_files:
            metadata = self._extract_blog_metadata(blog_file)
            if metadata:
                blogs.append(metadata)
        
        # Sort blogs by date, newest first
        return sorted(blogs, key=lambda x: x['datetime'], reverse=True)
    
    def generate_blog_collection_page(self, recipe: Dict[str, Any]) -> str:
        """
        Generate a blog collection page with blog summaries.
        
        Args:
            recipe (Dict): Site configuration
        
        Returns:
            HTML string representing blog collection
        """
        logger.info("Generating blog collection page")
        logger.debug(f"Number of blog posts: {len(self.blogs_metadata)}")
        for post in self.blogs_metadata:
            logger.debug(f"Blog post: {post['title']}, URL: {post['url']}, Date: {post['date']}")
        
        # Render the blog index page directly - it already extends base.jinja
        rendered = self.env.get_template('blog_index.jinja').render(
            posts=self.blogs_metadata,
            recipe=recipe,
            css_path="."  # Blog index is in root directory
        )
        logger.debug("Generated blog index page")
        
        return rendered
    
    def generate_standalone_blog_pages(self, recipe: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Generate individual blog pages.
        
        Args:
            recipe (Dict): Site configuration
        
        Returns:
            List of tuples with (filename, rendered_content)
        """
        blog_pages = []
        template = self.env.get_template('blog_post.jinja')
        
        for blog in self.blogs_metadata:
            try:
                logger.debug(f"Generating standalone page for blog: {blog['title']}")
                rendered_content = template.render(
                    title=blog['title'],
                    date=blog['date'],
                    content=blog['body'],
                    tags=blog['tags'],
                    author=blog.get('author', ''),
                    description=blog['description'],
                    recipe=recipe,
                    css_path=".."  # Blog posts are one level deep
                )
                blog_pages.append((blog['url'], rendered_content))
                logger.debug(f"Generated page for {blog['url']}")
            except Exception as e:
                logger.error(f"Error processing blog page {blog['url']}: {e}")
        
        return blog_pages

class TagProcessor:
    """Advanced tag processing and generation."""
    
    def __init__(self, recipe: Dict[str, Any], env: Environment):
        """
        Initialize tag processor.
        
        Args:
            recipe (Dict): Site configuration
            env (Environment): Jinja2 environment
        """
        logger.info("Initializing TagProcessor")
        self.recipe = recipe
        self.env = env
        self.tag_db = {}
        logger.debug(f"Initialized TagProcessor with recipe: {recipe}")
    
    def process_tags(self, file_path: str, page_info: Dict[str, Any]) -> None:
        """
        Process tags from a file and update tag database.
        
        Args:
            file_path (str): Path to the file
            page_info (Dict): Page metadata including tags
        """
        if not os.path.isfile(file_path):
            logger.debug(f"Skipping directory {file_path} during tag processing")
            return
            
        try:
            tags = page_info.get('tags', [])
            if not tags:
                logger.debug(f"No tags found in {os.path.basename(file_path)}")
                return
                
            logger.info(f"Processing tags for {os.path.basename(file_path)}: {tags}")
            
            for tag in tags:
                if tag not in self.tag_db:
                    self.tag_db[tag] = []
                self.tag_db[tag].append(page_info)
                logger.debug(f"Added page to tag '{tag}': {page_info['title']}")
                
        except Exception as e:
            logger.error(f"Error processing tags in {file_path}: {e}")
    
    def generate_tag_pages(self, build_dir: str) -> None:
        """
        Generate individual tag pages and tag index.
        
        Args:
            build_dir (str): Build directory path
        """
        logger.info("Generating tag pages")
        
        # Create tags directory
        tags_dir = os.path.join(build_dir, 'tags')
        os.makedirs(tags_dir, exist_ok=True)
        
        # Prepare tag data for index page
        tag_counts = {tag: len(pages) for tag, pages in self.tag_db.items()}
        recipe_with_tags = dict(self.recipe)
        recipe_with_tags['tags'] = sorted(self.tag_db.keys())
        recipe_with_tags['tag_counts'] = tag_counts
        
        # Generate individual tag pages
        for tag, pages in self.tag_db.items():
            try:
                logger.debug(f"Generating page for tag: {tag}")
                rendered = self.env.get_template('tag_page.jinja').render(
                    tag=tag,
                    pages=sorted(pages, key=lambda x: x.get('date', ''), reverse=True),
                    recipe=recipe_with_tags,
                    css_path=".."  # Tag pages are one level deep
                )
                
                # Write tag page
                tag_file = os.path.join(tags_dir, f"{tag}.html")
                with open(tag_file, 'w', encoding='utf-8') as f:
                    f.write(rendered)
                logger.debug(f"Generated tag page: {tag_file}")
            except Exception as e:
                logger.error(f"Error generating page for tag {tag}: {e}")
        
        # Generate tags index
        try:
            logger.info("Generating tags index page")
            rendered = self.env.get_template('tags_index.jinja').render(
                recipe=recipe_with_tags,
                css_path="."  # Tags index is in root directory
            )
            
            # Write tags index
            index_file = os.path.join(build_dir, 'tags.html')
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(rendered)
            logger.debug("Generated tags index page")
        except Exception as e:
            logger.error(f"Error generating tags index: {e}")

class StaticSiteGenerator:
    """Modern static site generator with enhanced configuration handling."""
    
    def __init__(
                self, 
                site_config: Union[str, List[str]], 
                style_config: Optional[Union[str, List[str]]] = None, 
                build_dir: Optional[str] = None,
                production_mode: bool = False,
                site_url: Optional[str] = None
            ):
        """
        Initialize static site generator with flexible configuration.
        
        Args:
            site_config (Union[str, List[str]]): Path to site configuration file(s)
            style_config (Optional[Union[str, List[str]]]): Path to style configuration file(s)
            build_dir (Optional[str]): Output directory for generated site
            production_mode (bool): Whether to enable production optimizations
            site_url (Optional[str]): Base URL of the site (required for production mode)
        """
        # Resolve and load configuration files
        site_config_paths = ConfigurationLoader.resolve_config_paths(site_config)
        style_config_paths = ConfigurationLoader.resolve_config_paths(style_config or [])
        
        # Store config directory for relative path resolution
        self.config_dir = os.path.dirname(site_config_paths[0])
        
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
            level=logging.DEBUG,
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
        
        # Store production settings
        self.production_mode = production_mode
        self.site_url = site_url

        if production_mode and not site_url:
            raise ValueError("site_url is required when production_mode is enabled")

    def _resolve_path(self, path: str) -> str:
        """
        Resolve a path relative to the config file directory.
        
        Args:
            path (str): Path to resolve
            
        Returns:
            Absolute path
        """
        if os.path.isabs(path):
            return path
        return os.path.join(self.config_dir, path)
    
    def _normalize_recipe_structure(self):
        """
        Normalize the recipe dictionary to ensure compatibility with existing templates.
        """
        # Ensure 'style' key exists with all expected subkeys
        if 'style' not in self.recipe:
            self.recipe['style'] = {}
        
        # Move social links to top level if they are under 'site'
        if 'site' in self.recipe and 'social_links' in self.recipe['site']:
            self.recipe['social_links'] = self.recipe['site']['social_links']
        
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
                                pass
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
        try:
            blogs_config = self.recipe.get("pages", {}).get("blogs", {})
            if isinstance(blogs_config, dict):
                blog_path = blogs_config.get("path")
                if isinstance(blog_path, list):
                    blog_path = blog_path[0]  # Take the first path if multiple are provided
                if blog_path:
                    return self._resolve_path(blog_path)
            return None
        except Exception as e:
            logger.info("No blog path configured")
            return None
    
    def generate(self):
        """Generate the static site."""
        log_section("Generating Static Site")
        
        # Initialize processors
        if self.blogs_path:
            logger.info(f"Blog path configured: {self.blogs_path}")
            blog_processor = BlogProcessor(self.blogs_path, self.env)
        else:
            logger.info("No blog path configured")
            blog_processor = None
                
        tag_processor = TagProcessor(self.recipe, self.env)
        
        # Generate blog pages if configured
        if blog_processor:
            logger.info("Generating blog pages")
            self._generate_blog_pages(blog_processor)
            
            # Process blog tags
            logger.info("Processing blog tags")
            for blog in blog_processor.blogs_metadata:
                if blog.get('tags'):
                    logger.debug(f"Processing tags for blog: {blog['title']}")
                    tag_processor.process_tags(
                        os.path.join(self.blogs_path, blog['url'].replace('blogs/', '').replace('.html', '.md')),
                        {
                            'title': blog['title'],
                            'description': blog.get('description', ''),
                            'tags': blog.get('tags', []),
                            'date': blog['date'],
                            'url': blog['url']
                        }
                    )
            
            # Generate tag pages after processing all blog tags
            logger.info("Generating tag pages")
            tag_processor.generate_tag_pages(self.build_dir)
        
        # Generate regular pages
        logger.info("Generating regular pages")
        self._generate_pages(tag_processor)
        
        # Generate CSS
        logger.info("Generating CSS")
        self._generate_css()
        
        # Copy assets
        logger.info("Copying assets")
        self._copy_assets()
        
        # Apply production optimizations if in production mode
        self._apply_production_optimizations()
        
        logger.info("Site generation completed successfully!")

    def _generate_blog_pages(self, blog_processor: BlogProcessor):
        """Generate blog pages."""
        logger.info("Generating blog pages")
        logger.debug(f"Recipe features: {self.recipe.get('features', {})}")
        logger.debug(f"Blog pages enabled: {self.recipe.get('features', {}).get('blog_pages', False)}")
        
        # Generate individual blog pages
        logger.info("Generating blog pages")
        blog_pages = blog_processor.generate_standalone_blog_pages(self.recipe)
        
        # Create blogs directory if it doesn't exist
        blogs_dir = os.path.join(self.build_dir, 'blogs')
        os.makedirs(blogs_dir, exist_ok=True)
        
        # Save individual blog pages
        for filename, content in blog_pages:
            output_path = os.path.join(self.build_dir, filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Generate and save blog collection page if enabled
        if self.recipe.get('features', {}).get('blog_pages', False):
            logger.info("Blog pages feature enabled, generating blog index page")
            logger.info("Generating blog collection page")
            blogs_index = blog_processor.generate_blog_collection_page(self.recipe)
            with open(os.path.join(self.build_dir, 'blogs.html'), 'w', encoding='utf-8') as f:
                f.write(blogs_index)
            logger.info("Generated blog index page")
        else:
            logger.info("Blog pages feature not enabled, skipping blog index generation")

    def _generate_pages(self, tag_processor: TagProcessor):
        """Generate HTML pages from markdown sources."""
        pages = self.recipe.get("pages", {})
        
        # Process root pages
        root_pages = pages.get("root", {})
        for page, markdown_path in root_pages.items():
            try:
                logger.info(f"Processing page: {page} from {markdown_path}")
                
                # Skip commented out pages
                if isinstance(markdown_path, str) and markdown_path.startswith('#'):
                    logger.info(f"Skipping commented page: {page}")
                    continue
                
                # Resolve path relative to config directory
                resolved_path = self._resolve_path(markdown_path)
                
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    md = markdown.Markdown(extensions=['meta', 'fenced_code', 'codehilite'])
                    body = md.convert(content)
                    
                # Extract metadata
                title = md.Meta.get('title', [page])[0]
                description = md.Meta.get('description', [''])[0]
                tags = []
                if 'tags' in md.Meta:
                    tags = [tag.strip() for tag in md.Meta['tags'][0].split(',')]
                date = md.Meta.get('date', [''])[0]
                
                logger.debug(f"Extracted metadata for {page}: title='{title}', tags={tags}")
                
                # Store page info in tag database
                page_url = os.path.relpath(os.path.join(self.build_dir, f"{page}.html"), self.build_dir)
                page_info = {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'date': date,
                    'url': page_url
                }
                
                # Process tags
                tag_processor.process_tags(resolved_path, page_info)
                
                # Render page
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
                raise
    
    def _generate_css(self):
        """Generate CSS file from Jinja template."""
        env = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
            )
        )
        css_template = env.get_template("style.css.jinja")
        
        # Create default typography configuration
        default_typography = {
            'font_family': {
                'body': 'Inter, system-ui, -apple-system, sans-serif',
                'headers': 'Inter, system-ui, -apple-system, sans-serif'
            },
            'sizes': {
                'body': '16px',
                'headers': {
                    'h1': '3rem',
                    'h2': '2.25rem',
                    'h3': '1.875rem',
                    'h4': '1.5rem',
                    'h5': '1.25rem',
                    'h6': '1.125rem'
                }
            },
            'line_height': {
                'body': '1.75',
                'headers': '1.25'
            }
        }

        # Get user typography config or empty dict if none
        user_typography = self.style_config.get('typography', {}) or {}
        
        # Merge user typography with defaults, ensuring nested structure
        typography_config = {
            'font_family': {
                'body': user_typography.get('font_family', {}).get('body', default_typography['font_family']['body']) 
                        if isinstance(user_typography.get('font_family', {}), dict) 
                        else default_typography['font_family']['body'],
                'headers': user_typography.get('font_family', {}).get('headers', default_typography['font_family']['headers'])
                        if isinstance(user_typography.get('font_family', {}), dict)
                        else default_typography['font_family']['headers']
            },
            'sizes': {
                'body': user_typography.get('sizes', {}).get('body', default_typography['sizes']['body'])
                        if isinstance(user_typography.get('sizes', {}), dict)
                        else default_typography['sizes']['body'],
                'headers': default_typography['sizes']['headers'].copy()
            },
            'line_height': {
                'body': user_typography.get('line_height', {}).get('body', default_typography['line_height']['body'])
                        if isinstance(user_typography.get('line_height', {}), dict)
                        else default_typography['line_height']['body'],
                'headers': user_typography.get('line_height', {}).get('headers', default_typography['line_height']['headers'])
                        if isinstance(user_typography.get('line_height', {}), dict)
                        else default_typography['line_height']['headers']
            }
        }

        # Safely update header sizes if provided
        user_headers = user_typography.get('sizes', {}).get('headers', {})
        if isinstance(user_headers, dict):
            typography_config['sizes']['headers'].update(user_headers)

        style_context = {
            'colors': self.style_config.get('colors', {}) or {},
            'typography': typography_config,
            'styles': self.style_config.get('styles', {}) or {},
            'components': self.style_config.get('components', {}) or {},
            'table': self.style_config.get('table', {}) or {},
            'image': self.style_config.get('image', {}) or {}
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
            :root {
                --color-primary: #3b82f6;
                --color-background: #0f172a;
                --color-text: #f1f5f9;
                --color-text-secondary: #94a3b8;
            }
            
            body {
                font-family: Inter, system-ui, -apple-system, sans-serif;
                font-size: 16px;
                line-height: 1.75;
                color: var(--color-text);
                background-color: var(--color-background);
                margin: 0;
                padding: 20px;
            }
            
            a {
                color: var(--color-primary);
                text-decoration: none;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: var(--color-text);
                line-height: 1.25;
                margin-bottom: 1rem;
            }

            h1 { font-size: 3rem; }
            h2 { font-size: 2.25rem; }
            h3 { font-size: 1.875rem; }
            h4 { font-size: 1.5rem; }
            h5 { font-size: 1.25rem; }
            h6 { font-size: 1.125rem; }
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

    def _remove_html_extensions(self):
        """Remove .html extensions from internal links in all HTML files"""
        logger.info("Removing .html extensions from internal links...")
        
        for root, dirs, files in os.walk(self.build_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace internal .html links
                    content = content.replace('href=".html"', 'href="/"')
                    content = content.replace('href="index.html"', 'href="/"')
                    content = content.replace('.html"', '"')
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

    def _generate_sitemap(self):
        """Generate sitemap.xml for search engines"""
        logger.info("Generating sitemap.xml...")
        
        urlset = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        
        # Walk through the build directory
        for root, dirs, files in os.walk(self.build_dir):
            for file in files:
                if file.endswith('.html'):
                    # Create URL entry
                    url = ET.SubElement(urlset, 'url')
                    
                    # Get relative path and remove .html extension
                    rel_path = os.path.relpath(os.path.join(root, file), self.build_dir)
                    if rel_path == 'index.html':
                        rel_path = ''
                    else:
                        rel_path = rel_path.replace('.html', '')
                    
                    # Add URL elements
                    loc = ET.SubElement(url, 'loc')
                    loc.text = f"{self.site_url.rstrip('/')}/{rel_path}"
                    
                    lastmod = ET.SubElement(url, 'lastmod')
                    lastmod.text = datetime.now().strftime('%Y-%m-%d')
                    
                    changefreq = ET.SubElement(url, 'changefreq')
                    changefreq.text = 'weekly'
                    
                    priority = ET.SubElement(url, 'priority')
                    priority.text = '0.8'
        
        # Create the sitemap file
        xmlstr = minidom.parseString(ET.tostring(urlset)).toprettyxml(indent="   ")
        with open(os.path.join(self.build_dir, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write(xmlstr)

    def _apply_production_optimizations(self):
        """Apply all production-specific optimizations"""
        if not self.production_mode:
            return
            
        logger.info("Applying production optimizations...")
        self._remove_html_extensions()
        self._generate_sitemap()
        
        # Copy vercel.json for deployment
        vercel_template = os.path.join(os.path.dirname(__file__), "constants/vercel.json")
        if os.path.exists(vercel_template):
            logger.info("Copying vercel.json for deployment...")
            import shutil
            shutil.copy2(vercel_template, os.path.join(self.build_dir, "vercel.json"))
        else:
            logger.warning("vercel.json template not found in constants directory")

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ssg.py <site_config> [style_config] [build_dir]")
        sys.exit(1)
    
    site_config = sys.argv[1]
    style_config = sys.argv[2] if len(sys.argv) > 2 else None
    build_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    generator = StaticSiteGenerator(site_config, style_config, build_dir)
    generator.generate()
