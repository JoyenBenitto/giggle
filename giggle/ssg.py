"""The static site genrator"""

import os
import pathlib
import logging as logger
import markdown
from jinja2 import Environment, FileSystemLoader
import giggle.template as giggle_template

here= os.path.abspath(os.path.dirname(__file__))

class blog_creater():
    def __init__(self, **kwargs):
        self.recipe= kwargs["recipe"]
        self.blogs_path= self.recipe["nav_items"]["blogs"]["path"]
        self.blog_list=[]
        for file in os.listdir(self.blogs_path):
            if file.endswith(".md"):
                self.blog_list.append(file)

    def blog_collection_page(self):
        """Generates a page with all the blogs and its content"""
        blog_body=""
        for blog in self.blog_list:
            data = pathlib.Path(f"{self.blogs_path}/{blog}").read_text(encoding='utf-8')
            md = markdown.Markdown(extensions = ['meta'])
            md.convert(data)
            blog_body += giggle_template.blog_template.format(
                date= md.Meta["date"][0],
                blog_title= md.Meta["title"][0],
                tiny_desc=md.Meta["desc"][0],
                blog_header=blog.replace(".md",""))
        return blog_body 

    def blog_standalone_page_gen(self):
        """Generates the individual pages"""
        for blog in self.blog_list:
            data = pathlib.Path(f"{self.blogs_path}/{blog}").read_text(encoding='utf-8')
            md = markdown.Markdown(extensions = ['meta'])
            site_body= md.convert(data)
            yield (blog.replace(".md",".html"), site_body)

class tag_creater():
    def __init__(self, **kwargs):
        self.recipe= kwargs["recipe"]
        self.file_list= kwargs["file_list"]

class ssg():
    """Collection of methods and attr for the generating the static site"""
    def __init__(self, **kwargs):
        self.recipe= kwargs["recipe"]
        self.build= kwargs["build"]
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
        for blog in self.blog_list:
            blog_file_path= os.path.join(self.blogs_path, blog)
            data = pathlib.Path(blog_file_path).read_text(encoding='utf-8')
            md = markdown.Markdown(extensions = ['meta'])
            md.convert(data)
            if "tags" in md.Meta:
                tag_list= md.Meta["tags"][0].split(",")
                for tag in tag_list:
                    if tag not in tag_db:
                        tag_db.update({tag:[html_path]})
                    else:
                        tag_db[tag].append(html_path)
        return tag_db

    def tag_page_generator(self):
        """Generates tag site"""
        tag_html="<h1>Tags</h1>\n"
        tag_db= self.tag_db_creater()
        environment = Environment(loader=FileSystemLoader(
            f"{here}/constants/jinja_templates"))

        for tag in tag_db:
            page_name= tag.replace("#","") +".html"
            tag_html += f'<div class="tag"><a href="./tags/{page_name}">{tag}</a></div>\n'
            template = environment.get_template("back_base.jinja")
            site_list= tag_db[tag]

            list_ele=""
            for sites in site_list:
                #body_html += template.tag  #f'<a href="{sites}"> ok cool </a>\n'
                list_ele +=  giggle_template.tag_site_template.format(
                    path_to_page=sites,
                    site_name=sites.replace("../","").replace(".html",""),
                ) + "\n"

            rendered_tag_page= template.render(
                recipe=self.recipe,
                back=".",
                body= giggle_template.tag_site_head.format(
                    tag_list=list_ele))

            with open(f"{self.build}/tags/{page_name}","w") as file:
                file.write(rendered_tag_page)

        template = environment.get_template("base.jinja")
        rendered_blog= template.render(recipe=self.recipe,
                                        body= tag_html,
                                        back=" ")

        with open(f"{self.build}/tags.html","w") as file:
            file.write(rendered_blog)

    def blog_renderer(self):
        """renders the blog page"""
        blog_creater_inst= blog_creater(recipe= self.recipe)
        blog_body= blog_creater_inst.blog_collection_page()
        blog_collection= blog_creater_inst.blog_standalone_page_gen()
        environment = Environment(loader=FileSystemLoader(
            f"{here}/constants/jinja_templates"))
        template = environment.get_template("back_base.jinja")
        for val in blog_collection:
            blog_file, blog_content= val
            rendered_blog= template.render(recipe=self.recipe,
                                            body= blog_content,
                                            back=".")

            with open(f"{self.build}/blog/{blog_file}", "w") as file:
                file.write(rendered_blog)
        return blog_body

    def generate(self):
        """generates the static site"""
        logger.info("generating html srcs")
        environment = Environment(loader=FileSystemLoader(
            f"{here}/constants/jinja_templates"))
        template = environment.get_template("base.jinja")

        #rendering html src
        for page in self.recipe["pages"]:
            #rendering markdown
            logger.info(f"generating {page}.html")
            data = pathlib.Path(self.recipe["pages"][page]).read_text(encoding='utf-8')
            md = markdown.Markdown(extensions = ['meta'])
            site_body= md.convert(data)
            rendered_index= template.render(
                recipe=self.recipe,
                body= site_body,
                back=" ")

            with open(f"{self.build}/{page}.html","w") as file:
                file.write(rendered_index)

        #rendering css src
        logger.info("generating css srcs")
        template = environment.get_template("style.css.jinja")
        rendered_index= template.render(recipe=self.recipe)
        with open(f"{self.build}/style.css","w") as file:
            file.write(rendered_index)

        #blog page renderer
        logger.info("generating blogs page srcs")
        blog_body= self.blog_renderer()
        environment = Environment(loader=FileSystemLoader(
            f"{here}/constants/jinja_templates"))
        template = environment.get_template("base.jinja")
        rendered_blog= template.render(recipe=self.recipe,
                                        body= blog_body,
                                        back=" ")
        with open(f"{self.build}/blogs.html","w") as file:
            file.write(rendered_blog)

        #tag page renderer
        logger.info("generating tag page srcs")
        self.tag_page_generator()
