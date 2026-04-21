import os
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateEngine:
    """Jinja2 template engine for layout pages (index, tags, nav wrappers)."""

    def __init__(self, template_dir: str, css_file: str = None) -> None:
        self.template_dir: str = template_dir
        os.makedirs(template_dir, exist_ok=True)
        self.env: Environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self._create_default_templates()

    def _create_default_templates(self) -> None:
        templates: dict = {
            'base.html': _BASE_TEMPLATE,
            'page.html': _PAGE_TEMPLATE,
            'main_index.html': _MAIN_INDEX_TEMPLATE,
            'tag.html': _TAG_TEMPLATE,
        }
        for filename, content in templates.items():
            filepath: str = os.path.join(self.template_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

    def render_page(self, title: str, body: str, metadata: dict,
                    navbar: list = None, site_title: str = None,
                    css_path: str = 'style.css') -> str:
        template = self.env.get_template('page.html')
        return template.render(
            title=title,
            body=body,
            description=metadata.get('description', ''),
            tags=metadata.get('tags', []),
            navbar=navbar or [],
            site_title=site_title or 'Archive',
            css_path=css_path,
        )

    def render_main_index(self, index_data: dict, navbar: list = None,
                          site_title: str = None, intro_html: str = None) -> str:
        template = self.env.get_template('main_index.html')
        return template.render(
            **index_data,
            navbar=navbar or [],
            site_title=site_title or 'Archive',
            intro_html=intro_html or '',
            css_path='style.css',
        )

    def render_tag_page(self, tag_data: dict) -> str:
        template = self.env.get_template('tag.html')
        return template.render(**tag_data, css_path='../style.css')


# ── Templates ─────────────────────────────────────────────────────────────────

_BASE_TEMPLATE = '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}{{ title }}{% endblock %} — {{ site_title }}</title>
  <link rel="stylesheet" href="{{ css_path }}">
  <script>
    MathJax = {
      tex: {
        inlineMath: [["$","$"],["\\\\(","\\\\)"]],
        displayMath: [["$$","$$"],["\\\\[","\\\\]"]]
      }
    };
  </script>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
<header>
  <div class="nav-inner">
    <div class="logo"><a href="/">{{ site_title }}</a></div>
    {% if navbar %}
    <nav>
      {% for link in navbar %}
        {% if link.url %}
          <a href="{{ link.url }}">{{ link.title }}</a>
        {% else %}
          <a href="/{{ link.path }}">{{ link.title }}</a>
        {% endif %}
      {% endfor %}
    </nav>
    {% endif %}
  </div>
</header>
{% block content %}{% endblock %}
<footer>
  <div class="footer-inner">
    <p>{{ site_title }}</p>
  </div>
</footer>
</body>
</html>
'''

_PAGE_TEMPLATE = '''\
{% extends "base.html" %}
{% block content %}
<main class="main-container">
  <article>
    {{ body | safe }}
    {% if tags %}
    <div class="tags">
      {% for tag in tags %}
      <a href="{{ css_path | replace("style.css","") }}tags/{{ tag }}.html" class="tag-link">{{ tag }}</a>
      {% endfor %}
    </div>
    {% endif %}
  </article>
</main>
{% endblock %}
'''

_MAIN_INDEX_TEMPLATE = '''\
{% extends "base.html" %}
{% block content %}
<main class="main-container">
  {% if intro_html %}
  <div class="intro">{{ intro_html | safe }}</div>
  {% endif %}
  {% for entry in entries %}
  <div class="index-entry">
    <h2><a href="{{ entry.link }}">{{ entry.name }}</a></h2>
    {% if entry.description %}<p>{{ entry.description }}</p>{% endif %}
    {% if entry.tags %}
    <p class="entry-tags">
      {% for tag in entry.tags %}
      <a href="tags/{{ tag }}.html" class="tag-link">{{ tag }}</a>{% if not loop.last %} {% endif %}
      {% endfor %}
    </p>
    {% endif %}
  </div>
  {% endfor %}
</main>
{% endblock %}
'''

_TAG_TEMPLATE = '''\
{% extends "base.html" %}
{% block title %}#{{ tag }}{% endblock %}
{% block content %}
<main class="main-container">
  <h1>#{{ tag }}</h1>
  <ul>
    {% for page in pages %}
    <li><a href="../{{ page.link }}">{{ page.title }}</a></li>
    {% endfor %}
  </ul>
</main>
{% endblock %}
'''
