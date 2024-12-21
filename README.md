# Giggle Static Site Generator

Giggle is a modern, feature-rich static site generator built with Python. Create beautiful, responsive websites with a dark theme and modern design out of the box.

## Features

- 🎨 Modern dark theme with customizable colors and typography
- 📱 Responsive design for all devices
- 📝 Markdown support with frontmatter
- 🏷️ Tag system for content organization
- 📚 Built-in blog support
- 🎯 SEO-friendly output
- 🚀 Fast and lightweight
- 🔧 Highly configurable

## Quick Start

1. Install Giggle:
   ```bash
   pip install giggle
   ```

2. Create a new site:
   ```bash
   mkdir my-site
   cd my-site
   giggle init
   ```

3. Build your site:
   ```bash
   giggle cook --site-config config_srcs/site_config.yaml --style-config config_srcs/style_config.yaml
   ```

4. Serve your site locally:
   ```bash
   cd build
   python -m http.server 8000
   ```

Visit `http://localhost:8000` to see your site!

## Configuration

Giggle uses two main configuration files:

### Site Configuration (`site_config.yaml`)

```yaml
site:
  title: "Your Site Title"
  description: "Site description"
  author: "Your Name"
  url: "https://example.com"
  copyright: "2024"
  social_links:
    GitHub: "https://github.com/username"
    LinkedIn: "https://linkedin.com/in/username"

navigation:
  - title: "Home"
    url: "./index.html"
  - title: "Blog"
    url: "./blogs.html"

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

### Style Configuration (`style_config.yaml`)

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
```

## Directory Structure

```
my-site/
├── config_srcs/
│   ├── site_config.yaml
│   ├── style_config.yaml
│   └── markdowns/
│       ├── main.md
│       ├── about.md
│       └── blog/
│           └── first-post.md
└── build/
    └── (generated files)
```

## Writing Content

### Pages

Create Markdown files in your content directory with frontmatter:

```markdown
---
title: My Page Title
description: Page description for SEO
tags: [tag1, tag2]
---

# Welcome to My Page

Content goes here...
```

### Blog Posts

Blog posts use the same format with additional metadata:

```markdown
---
title: My First Blog Post
description: A brief description
date: 2024-01-01
tags: [blog, first-post]
---

# My First Blog Post

Blog content goes here...
```

## Advanced Features

### Custom Templates

Giggle uses Jinja2 for templating. You can customize the templates by creating your own in the `templates` directory:

- `base.jinja`: Base template for all pages
- `blog_index.jinja`: Blog listing page
- `blog_post.jinja`: Individual blog post template
- `tag_page.jinja`: Tag listing pages

### Asset Management

Place static assets (images, JavaScript, etc.) in the `assets` directory. They will be automatically copied to the build directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please file an issue on GitHub.