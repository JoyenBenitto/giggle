import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateEngine:
    """Jinja2 template engine for all site pages."""

    def __init__(self, template_dir: str, css_file: str = None) -> None:
        self.template_dir: str = template_dir
        os.makedirs(template_dir, exist_ok=True)
        self.env: Environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self._create_default_templates()

    def _now(self) -> str:
        return datetime.now().strftime('%Y-%m-%d')

    def _create_default_templates(self) -> None:
        templates: dict = {
            'index.html': _INDEX_TEMPLATE,
            'page.html':  _PAGE_TEMPLATE,
            'tag.html':   _TAG_TEMPLATE,
        }
        for filename, content in templates.items():
            filepath: str = os.path.join(self.template_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

    def render_main_index(self, index_data: dict, navbar: list = None,
                          site_title: str = None, intro_html: str = None) -> str:
        template = self.env.get_template('index.html')
        return template.render(
            entries=index_data.get('entries', []),
            current_datetime=self._now(),
        )

    def render_page(self, title: str, body: str, metadata: dict,
                    navbar: list = None, site_title: str = None,
                    css_path: str = 'style.css') -> str:
        template = self.env.get_template('page.html')
        return template.render(
            title=title,
            body=body,
            description=metadata.get('description', ''),
            tags=metadata.get('tags', []),
            css_path=css_path,
            current_datetime=self._now(),
        )

    def render_tag_page(self, tag_data: dict) -> str:
        template = self.env.get_template('tag.html')
        return template.render(
            tag=tag_data['tag'],
            articles=tag_data['pages'],
            current_datetime=self._now(),
        )


# ── Templates — ported directly from vaults/builder_template/templates/ ──────

_INDEX_TEMPLATE = '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Knowledge archive of technical notes on algorithms, programming languages, computer architecture, and systems design by Joyen Benitto.">
    <meta name="keywords" content="algorithms, programming languages, computer architecture, systems design, notes, archive, Joyen, Joyen Benitto">
    <meta name="author" content="Joyen Benitto">
    <meta name="robots" content="index, follow">
    <meta name="theme-color" content="#f5f5f5">
    <meta property="og:type" content="website">
    <meta property="og:title" content="FTP site">
    <meta property="og:description" content="Technical notes, thoughts and research on algorithms, PL, comp arch and systems.">
    <meta property="og:url" content="https://joyenbenitto.com">
    <meta property="og:site_name" content="FTP Site">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="FTP site - Joyen Benitto">
    <meta name="twitter:description" content="Technical notes, thoughts and research on algorithms, PL, comp arch and systems.">
    <link rel="canonical" href="https://joyenbenitto.com">
    <title>FTP site - Joyen Benitto</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <header>
        <div class="nav-inner">
            <div class="logo"><a href="/">FTP SITE</a></div>
            <nav>
                <a href="/">Home</a>
                <a href="/About.html">About</a>
                <a href="/Contact.html">Contact</a>
            </nav>
        </div>
    </header>

    <main class="main-container">
    <section class="artwork">
        <img src="./constants/misty_mountains.jpg" alt="System Landscape" />
    </section>

    <section class="about-manifesto">
        <h1>Index: FTP Site</h1>
        <div class="dense-text">
            <p>
                This <u class="squiglly">FTP site</u> is an incremental repository for the structured decomposition of
                complex systems. It functions as a persistent memory buffer for research at the intersection
                of algorithms, PL theory, and computer architecture.
            </p>
        </div>
    </section>

    <hr class="section-divider" />

    {%- for entry in entries %}
        <article class="note">
            <h3><a href="{{ entry.link }}">{{ entry.name }}</a></h3>
            {%- if entry.tags %}
                <div class="tags">
                {%- for tag in entry.tags | sort %}
                    <a href="/tags/{{ tag }}.html">#{{ tag }}</a>{% if not loop.last %} &nbsp; {% endif %}
                {%- endfor %}
                </div>
            {%- endif %}
        </article>
    {%- endfor %}
    </main>

<footer>
    <div class="footer-inner">
        <p>JOYEN BENITTO</p>
        <p class="system-status">
            <a href="/CHANGELOG.html" class="changelog_footer">UPDATED:</a>
            <time datetime="{{ current_datetime }}">{{ current_datetime }}</time>
        </p>
    </div>
</footer>
</body>
</html>
'''

_PAGE_TEMPLATE = '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {% if description %}<meta name="description" content="{{ description }}">{% endif %}
    <meta name="author" content="Joyen Benitto">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{{ css_path }}" />
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
            <div class="logo"><a href="/">FTP SITE</a></div>
            <nav>
                <a href="/">Home</a>
                <a href="/About.html">About</a>
                <a href="/Contact.html">Contact</a>
            </nav>
        </div>
    </header>

    <main class="main-container">
        {{ body | safe }}
        {% if tags %}
        <div class="tags">
            {%- for tag in tags %}
            <a href="/tags/{{ tag }}.html">#{{ tag }}</a>{% if not loop.last %} &nbsp; {% endif %}
            {%- endfor %}
        </div>
        {% endif %}
    </main>

<footer>
    <div class="footer-inner">
        <p>JOYEN BENITTO</p>
        <p class="system-status">
            <a href="/CHANGELOG.html" class="changelog_footer">UPDATED:</a>
            <time datetime="{{ current_datetime }}">{{ current_datetime }}</time>
        </p>
    </div>
</footer>
</body>
</html>
'''

_TAG_TEMPLATE = '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Articles tagged with {{ tag }} — Knowledge Archive">
    <meta name="author" content="Joyen Benitto">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{{ tag }} — Knowledge Archive">
    <meta property="og:url" content="https://joyenbenitto.com/tags/{{ tag }}.html">
    <link rel="canonical" href="https://joyenbenitto.com/tags/{{ tag }}.html">
    <title>{{ tag }}</title>
    <link rel="stylesheet" href="../style.css" />
</head>
<body>
    <header>
        <div class="nav-inner">
            <div class="logo"><a href="/">FTP SITE</a></div>
            <nav>
                <a href="/">Home</a>
                <a href="/About.html">About</a>
                <a href="/Contact.html">Contact</a>
            </nav>
        </div>
    </header>

    <main class="main-container">
        <div class="manifesto-header">
            <h1>Filtered Index: <u class="squiglly">#{{ tag }}</u></h1>
        </div>
        <hr class="section-divider" />
        <div class="tagged-articles">
        {%- for article in articles %}
            <article class="note">
                <h3><a href="../{{ article.link }}">{{ article.title }}</a></h3>
                {%- if article.tags %}
                <div class="tags">
                    {%- for t in article.tags | sort %}
                        <a href="/tags/{{ t }}.html">#{{ t }}</a>{% if not loop.last %} &nbsp; {% endif %}
                    {%- endfor %}
                </div>
                {%- endif %}
            </article>
        {%- endfor %}
        </div>
    </main>

<footer>
    <div class="footer-inner">
        <p>JOYEN BENITTO</p>
        <p class="system-status">
            <a href="/CHANGELOG.html" class="changelog_footer">UPDATED:</a>
            <time datetime="{{ current_datetime }}">{{ current_datetime }}</time>
        </p>
    </div>
</footer>
</body>
</html>
'''
