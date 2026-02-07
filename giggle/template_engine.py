import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Optional

class TemplateEngine:
    """Jinja2 template engine for rendering HTML pages."""
    
    def __init__(self, template_dir: str, css_file: str = None) -> None:
        self.template_dir: str = template_dir
        self.css_file: str = css_file
        self.css_content: str = ""
        os.makedirs(template_dir, exist_ok=True)
        
        self.env: Environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        self._load_css()
        self._create_default_templates()
    
    def _load_css(self) -> None:
        """Load CSS from external file."""
        if self.css_file and os.path.exists(self.css_file):
            with open(self.css_file, 'r', encoding='utf-8') as f:
                self.css_content = f.read()
    
    def _create_default_templates(self) -> None:
        """Create default templates if they don't exist."""
        templates: dict = {
            'base.html': self._base_template(),
            'page.html': self._page_template(),
            'index.html': self._index_template(),
            'main_index.html': self._main_index_template(),
            'archive.html': self._archive_template(),
            'tag.html': self._tag_template()
        }
        
        for filename, content in templates.items():
            filepath: str = os.path.join(self.template_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def render_page(self, title: str, content: str, metadata: dict, site_title: str = None) -> str:
        """Render a page with given title and content."""
        template = self.env.get_template('page.html')
        return template.render(
            title=title,
            content=content,
            description=metadata.get('description', ''),
            tags=metadata.get('tags', []),
            site_title=site_title or 'Archive'
        )
    
    def render_external_page(self, title: str, content: str, metadata: dict, navbar: list = None, site_title: str = None) -> str:
        """Render external page with navbar."""
        template = self.env.get_template('page.html')
        return template.render(
            title=title,
            content=content,
            description=metadata.get('description', ''),
            tags=metadata.get('tags', []),
            navbar=navbar or [],
            site_title=site_title or 'Archive'
        )
    
    def render_index(self, pages: list[dict]) -> str:
        """Render index page with list of pages."""
        template = self.env.get_template('index.html')
        return template.render(pages=pages)
    
    def render_main_index(self, index_data: dict, navbar: list = None, site_title: str = None, intro_html: str = None) -> str:
        """Render main index page with L1 directories."""
        template = self.env.get_template('main_index.html')
        index_data['navbar'] = navbar or []
        index_data['site_title'] = site_title or 'Archive'
        index_data['intro_html'] = intro_html or ''
        return template.render(**index_data)
    
    def render_archive(self, archive_data: dict) -> str:
        """Render archive page with all pages."""
        template = self.env.get_template('archive.html')
        return template.render(**archive_data)
    
    def render_tag_page(self, tag_data: dict) -> str:
        """Render tag page with all pages for that tag."""
        template = self.env.get_template('tag.html')
        return template.render(**tag_data)
    
    def _base_template(self) -> str:
        """Base template with stylesheet."""
        css = self.css_content
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{{{{ title }}}}{{% endblock %}}</title>
    <style>
{css}
    </style>
</head>
<body>
    <header>
        <div class="logo"><a href="index.html" style="text-decoration: none; color: #000;">{{{{ site_title | default('Archive') }}}}</a></div>
        {{% block navbar %}}{{% endblock %}}
    </header>
    {{% block content %}}{{% endblock %}}
    <script>
      MathJax = {{
        tex: {{
          inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
          displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
        }}
      }};
    </script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <footer>
        <p>Updated: <span id="timestamp"></span></p>
        <script>
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        </script>
    </footer>
</body>
</html>
'''
    
    def _page_template(self) -> str:
        """Page template for individual articles."""
        return '''{% extends "base.html" %}

{% block navbar %}
{% if navbar %}
<nav>
    {% for link in navbar %}
    <a href="../{{ link.path }}">{{ link.title }}</a>
    {% endfor %}
</nav>
{% endif %}
{% endblock %}

{% block content %}
<article>
    {% if not navbar %}
    <h1>{{ title }}</h1>
    {% endif %}
    
    
    <div class="content">
        {{ content | safe }}
    </div>
    
    
    <div class="tags">
        {% for tag in tags %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
    </div>
    
</article>
{% endblock %}
'''
    
    def _index_template(self) -> str:
        """Index template for listing pages."""
        return '''{% extends "base.html" %}

{% block content %}
<h1>Index</h1>
<ul>
    {% for page in pages %}
    <li>
        <a href="{{ page.html_path }}">{{ page.title }}</a>
        {% if page.description %}
        <p>{{ page.description }}</p>
        {% endif %}
    </li>
    {% endfor %}
</ul>
{% endblock %}
'''
    
    def _main_index_template(self) -> str:
        """Main index template with L1 directories."""
        return '''{% extends "base.html" %}

{% block navbar %}
{% if navbar %}
<nav>
    {% for link in navbar %}
    <a href="{{ link.path }}">{{ link.title }}</a>
    {% endfor %}
</nav>
{% endif %}
{% endblock %}

{% block content %}
{% if intro_html %}
<div class="intro">
    {{ intro_html | safe }}
</div>
{% endif %}

{% for entry in entries %}
<div class="index-entry">
    <h2><a href="{{ entry.link }}">{{ entry.name }}</a></h2>
    {% if entry.tags %}
    <p class="entry-tags">
        {% for tag in entry.tags %}
        <a href="tags/{{ tag }}.html" class="tag-link">{{ tag }}</a>{% if not loop.last %}; {% endif %}
        {% endfor %}
    </p>
    {% endif %}
</div>
{% endfor %}
{% endblock %}
'''
    
    def _archive_template(self) -> str:
        """Archive template with all pages organized by directory."""
        return '''{% extends "base.html" %}

{% block content %}
<h1>Archive</h1>

{% for section in sections %}
<h2>{{ section.directory }}</h2>
<ul>
    {% for page in section.pages %}
    <li><a href="{{ page.link }}">{{ page.title }}</a></li>
    {% endfor %}
</ul>
{% endfor %}
{% endblock %}
'''
    
    def _tag_template(self) -> str:
        """Tag page template showing all pages with a specific tag."""
        return '''{% extends "base.html" %}

{% block content %}
<h1>Tag: {{ tag }}</h1>

<ul>
    {% for page in pages %}
    <li><a href="../{{ page.link }}">{{ page.title }}</a></li>
    {% endfor %}
</ul>
{% endblock %}
'''
