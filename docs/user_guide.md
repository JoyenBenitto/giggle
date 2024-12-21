# Giggle User Guide

This guide provides detailed information about using Giggle to create and maintain your static website.

## Table of Contents

1. [Installation](#installation)
2. [Project Setup](#project-setup)
3. [Configuration](#configuration)
4. [Content Creation](#content-creation)
5. [Templating](#templating)
6. [Styling](#styling)
7. [Advanced Features](#advanced-features)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installing Giggle

```bash
pip install giggle
```

Verify the installation:
```bash
giggle --version
```

## Project Setup

### Creating a New Site

1. Create a project directory:
   ```bash
   mkdir my-site
   cd my-site
   ```

2. Initialize a new Giggle site:
   ```bash
   giggle init
   ```

   This creates the following structure:
   ```
   my-site/
   ├── config_srcs/
   │   ├── site_config.yaml
   │   ├── style_config.yaml
   │   └── markdowns/
   │       ├── main.md
   │       ├── about.md
   │       └── blog/
   ├── assets/
   │   ├── images/
   │   └── js/
   └── templates/
       ├── base.jinja
       ├── blog_index.jinja
       └── blog_post.jinja
   ```

## Configuration

### Site Configuration

The `site_config.yaml` file controls your site's content and features:

```yaml
site:
  title: "Site Title"
  description: "Site description"
  author: "Author Name"
  url: "https://example.com"
  copyright: "2024"
  social_links:
    GitHub: "https://github.com/username"
    LinkedIn: "https://linkedin.com/in/username"
    Twitter: "https://twitter.com/username"

navigation:
  - title: "Home"
    url: "./index.html"
  - title: "Blog"
    url: "./blogs.html"
  - title: "About"
    url: "./about.html"

pages:
  index: ./markdowns/main.md
  blogs: ./markdowns/blog/
  about: ./markdowns/about.md

features:
  tag_pages: true
  blog_pages: true
  dark_mode: true
  search: true
```

### Style Configuration

The `style_config.yaml` file controls your site's appearance:

```yaml
colors:
  background: "#121212"
  text: "#E0E0E0"
  primary: "#2196F3"
  accent: "#64B5F6"
  background_secondary: "#1E1E1E"
  text_secondary: "#A0A0A0"

typography:
  font_family:
    body: '"Inter", sans-serif'
    headers: '"Roboto", sans-serif'
  sizes:
    body: "16px"
    headers:
      h1: "2rem"
      h2: "1.5rem"
      h3: "1.3rem"
  line_height:
    body: "1.6"
    headers: "1.3"
```

## Content Creation

### Writing Pages

Create Markdown files in your content directory with YAML frontmatter:

```markdown
---
title: About Me
description: Learn more about who I am
tags: [about, personal]
---

# About Me

Content goes here...
```

### Writing Blog Posts

Blog posts require additional metadata:

```markdown
---
title: My First Blog Post
description: An introduction to my blog
date: 2024-01-01
tags: [blog, introduction]
---

# Welcome to My Blog

Blog content goes here...
```

### Using Tags

Tags help organize your content:

1. Add tags in the frontmatter:
   ```yaml
   tags: [programming, python, web]
   ```

2. Enable tag pages in `site_config.yaml`:
   ```yaml
   features:
     tag_pages: true
   ```

3. Tag pages will be automatically generated at `/tags/tag-name.html`

## Templating

### Available Templates

- `base.jinja`: Base template for all pages
- `blog_index.jinja`: Blog listing page
- `blog_post.jinja`: Individual blog post template
- `tag_page.jinja`: Tag listing pages

### Customizing Templates

Create your own templates in the `templates` directory:

```html
{% extends "base.jinja" %}

{% block content %}
<div class="custom-layout">
    {{ content | safe }}
</div>
{% endblock %}
```

## Styling

### CSS Variables

Giggle uses CSS variables for consistent styling:

```css
:root {
    --color-background: {{ colors.background }};
    --color-text: {{ colors.text }};
    --color-primary: {{ colors.primary }};
    --font-body: {{ typography.font_family.body }};
}
```

### Responsive Design

All templates include responsive design breakpoints:

```css
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
}
```

## Advanced Features

### Custom JavaScript

Add JavaScript files to `assets/js/`:

```javascript
// assets/js/custom.js
document.addEventListener('DOMContentLoaded', () => {
    // Your code here
});
```

### Asset Management

1. Place assets in the `assets` directory:
   ```
   assets/
   ├── images/
   │   └── photo.jpg
   └── js/
       └── custom.js
   ```

2. Reference in markdown:
   ```markdown
   ![Photo](../assets/images/photo.jpg)
   ```

## Deployment

### Building for Production

```bash
giggle cook --site-config config_srcs/site_config.yaml --style-config config_srcs/style_config.yaml --minify
```

### Deployment Options

1. GitHub Pages:
   ```bash
   # In .github/workflows/deploy.yml
   name: Deploy to GitHub Pages
   on:
     push:
       branches: [main]
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Build
           run: |
             pip install giggle
             giggle cook
         - name: Deploy
           uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./build
   ```

2. Netlify:
   Create `netlify.toml`:
   ```toml
   [build]
     command = "giggle cook"
     publish = "build"
   ```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Template Not Found**
   - Check template paths in configuration
   - Ensure template files exist in correct location

3. **Build Errors**
   - Check log file at `giggle_build.log`
   - Verify YAML syntax in configuration files

### Getting Help

1. Check the [GitHub Issues](https://github.com/JoyenBenitto/giggle/issues)
2. Join our [Discord Community](https://discord.gg/giggle)
3. Read the [FAQ](https://github.com/JoyenBenitto/giggle/wiki/FAQ)

## Best Practices

1. **Content Organization**
   - Use meaningful file names
   - Organize content by type (blog, pages, etc.)
   - Use tags consistently

2. **Performance**
   - Optimize images before adding to assets
   - Minify CSS and JavaScript in production
   - Use appropriate image formats

3. **SEO**
   - Always include meta descriptions
   - Use semantic heading structure
   - Add alt text to images

4. **Maintenance**
   - Keep dependencies updated
   - Backup your content regularly
   - Use version control
