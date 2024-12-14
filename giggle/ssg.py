"""The static site generator"""

import os
import pathlib
import logging
from typing import Dict, List, Generator, Optional, Any

import markdown
from jinja2 import Environment, FileSystemLoader

from giggle import __version__
import giggle.template as giggle_template

logger = logging.getLogger(__name__)

class blog_creater():
    def __init__(self, **kwargs):
        self.recipe= kwargs["recipe"]
        self.blog_list= None
        if "blogs" in self.recipe["nav_items"]:
            self.blogs_path= self.recipe["nav_items"]["blogs"]["path"]
            self.blog_list=[]
            for file in os.listdir(self.blogs_path):
                if file.endswith(".md"):
                    self.blog_list.append(file)

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

    def generate_blog_collection_page(self) -> str:
        """
        Generate a blog collection page with blog summaries.
        
        Returns:
            HTML string representing blog collection
        """
        blog_list_html = ""
        for blog in self.blog_list:
            try:
                blog_metadata = self._extract_blog_metadata(blog)
                if blog_metadata:
                    blog_list_html += giggle_template.blog_template.format(**blog_metadata)
            except Exception as e:
                logger.warning(f"Could not process blog {blog}: {e}")

        return f"""
        <ul>
            {blog_list_html}
        </ul>
        """

class ssg():
    """Collection of methods and attr for the generating the static site"""
    def __init__(self, **kwargs):
        self.recipe= kwargs["recipe"]
        self.build= kwargs["build"]
        self.blogs_path=None
        self.blog_list= None
        if "blogs" in self.recipe["nav_items"]:
            self.blogs_path= self.recipe["nav_items"]["blogs"]["path"]
            self.blog_list=[]
            for file in os.listdir(self.blogs_path):
                if file.endswith(".md"):
                    self.blog_list.append(file)

    def tag_db_creater(self):
        tag_db={}
        for page in self.recipe["pages"]:
            file_path= self.recipe["pages"][page]
            html_path= "../"+page+".html"
            data = pathlib.Path(file_path).read_text(encoding='utf-8')
            md = markdown.Markdown(extensions = ['meta'])
            md.convert(data)
            if "tags" in md.Meta:
                tag_list= md.Meta["tags"][0].split(",")
                for tag in tag_list:
                    if tag not in tag_db:
                        tag_db.update({tag:[html_path]})
                    else:
                        tag_db[tag].append(html_path)
        if self.blog_list is not None:
            for blog in self.blog_list:
                blog_file_path= os.path.join(self.blogs_path, blog)
                data = pathlib.Path(blog_file_path).read_text(encoding='utf-8')
                md = markdown.Markdown(extensions = ['meta'])
                md.convert(data)
                file= blog.replace(".md",".html")
                html_path= "../blog/"+ file
                if "tags" in md.Meta:
                    tag_list= md.Meta["tags"][0].split(",")
                    for tag in tag_list:
                        if tag not in tag_db:
                            tag_db.update({tag:[html_path]})
                        else:
                            tag_db[tag].append(html_path)
        return tag_db


class TagProcessor:
    """Manages tag-related processing and generation."""
    
    def __init__(self, recipe: Dict[str, Any], file_list: List[str]):
        """
        Initialize tag processor.
        
        Args:
            recipe (Dict): Site configuration
            file_list (List[str]): List of files to process
        """
        self.recipe = recipe
        self.file_list = file_list

    def create_tag_database(self) -> Dict[str, Dict[str, Any]]:
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


class StaticSiteGenerator:
    """Main class for generating a static site."""
    
    def __init__(self, recipe: Dict[str, Any], build_dir: str):
        """
        Initialize static site generator.
        
        Args:
            recipe (Dict): Site configuration
            build_dir (str): Output directory for generated site
        """
        self.recipe = recipe
        self.build_dir = build_dir
        self.blogs_path = recipe.get("nav_items", {}).get("blogs", {}).get("path")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def generate(self):
        """
        Generate entire static site.
        """
        logger.info("Starting static site generation")
        
        self._generate_pages()
        self._generate_css()
        self._copy_javascript_files()
        self._generate_blog_pages()
        self._generate_tag_pages()
        
        logger.info("Static site generation completed")

    def _generate_pages(self):
        """Generate HTML pages from markdown sources."""
        env = Environment(loader=FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
        ))
        base_template = env.get_template("base.jinja")
        
        for page, markdown_path in self.recipe.get("pages", {}).items():
            try:
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    md = markdown.Markdown(extensions=['meta'])
                    body = md.convert(content)
                    
                rendered_page = base_template.render(
                    recipe=self.recipe, 
                    body=body, 
                    back=" "
                )
                
                output_path = os.path.join(self.build_dir, f"{page}.html")
                with open(output_path, "w", encoding='utf-8') as f:
                    f.write(rendered_page)
                
                logger.info(f"Generated page: {page}.html")
            except Exception as e:
                logger.error(f"Error generating page {page}: {e}")

    def _generate_css(self):
        """Generate CSS file from Jinja template."""
        env = Environment(loader=FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
        ))
        css_template = env.get_template("style.css.jinja")
        
        rendered_css = css_template.render(recipe=self.recipe)
        
        with open(os.path.join(self.build_dir, "style.css"), "w", encoding='utf-8') as f:
            f.write(rendered_css)
        
        logger.info("Generated style.css")

    def _copy_javascript_files(self):
        """Copy JavaScript files to build directory."""
        import shutil
        
        js_dir = os.path.join(os.path.dirname(__file__), "constants")
        js_files = [f for f in os.listdir(js_dir) if f.endswith('.js')]
        
        for js_file in js_files:
            src_path = os.path.join(js_dir, js_file)
            dest_path = os.path.join(self.build_dir, js_file)
            
            try:
                shutil.copy2(src_path, dest_path)
                logger.info(f"Copied JavaScript file: {js_file}")
            except Exception as e:
                logger.error(f"Error copying {js_file}: {e}")

    def _generate_blog_pages(self):
        """Generate blog pages."""
        if not self.blogs_path:
            logger.warning("No blog path configured")
            return
        
        blog_processor = BlogProcessor(self.blogs_path)
        blog_body = blog_processor.generate_blog_collection_page()
        
        env = Environment(loader=FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "constants/jinja_templates")
        ))
        base_template = env.get_template("base.jinja")
        
        # Blog collection page
        rendered_blog = base_template.render(
            recipe=self.recipe,
            body=blog_body,
            back=" ",
            version=__version__
        )
        
        with open(os.path.join(self.build_dir, "blogs.html"), "w", encoding='utf-8') as f:
            f.write(rendered_blog)
        
        # Individual blog pages
        blog_template = env.get_template("back_base.jinja")
        for blog_file, blog_content in blog_processor.generate_standalone_blog_pages():
            rendered_blog = blog_template.render(
                recipe=self.recipe,
                body=blog_content,
                back="."
            )
            
            blog_output_path = os.path.join(self.build_dir, "blog", blog_file)
            os.makedirs(os.path.dirname(blog_output_path), exist_ok=True)
            
            with open(blog_output_path, "w", encoding='utf-8') as f:
                f.write(rendered_blog)

    def _generate_tag_pages(self):
        """Generate tag-related pages."""
        tag_processor = TagProcessor(self.recipe, [])
        tag_db = tag_processor.create_tag_database()
        
        # TODO: Implement tag page generation logic
        # This part was commented out in the original code
        logger.info(f"Tag database created with {len(tag_db)} tags")

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

        #blog page renderer
        logger.info("generating blogs page srcs")
        if self.blogs_path is not None:
            blog_body= self.blog_renderer()
            environment = Environment(loader=FileSystemLoader(
                f"{here}/constants/jinja_templates"))
            template = environment.get_template("base.jinja")
            rendered_blog= template.render(recipe=self.recipe,
                                            body= blog_body,
                                            back=" ",
                                            version=__version__)
            with open(f"{self.build}/blogs.html","w") as file:
                file.write(rendered_blog)
