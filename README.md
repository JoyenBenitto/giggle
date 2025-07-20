# Giggle Static Site Generator

Giggle is a modern, feature-rich static site generator built with Python. Create beautiful, responsive websites with a dark theme and modern design out of the box. Giggle uses Jinja2 templates, YAML configuration, and Markdown content to generate static websites quickly and efficiently.

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
   giggle new my-site
   cd my-site
   ```

3. Create new content:
   ```bash
   giggle new_content post "My First Post"
   giggle new_content page "About"
   giggle new_content project "My Project"
   ```

4. Build your site:
   ```bash
   giggle build
   ```

5. Serve your site locally with live reload:
   ```bash
   giggle serve
   ```

Visit `http://localhost:8000` to see your site!

## Configuration

Giggle uses a single YAML configuration file (`giggle.yaml`) for site settings:

```yaml
# Site information
site:
  title: "Your Site Title"
  description: "Your site description for SEO"
  author: "Your Name"
  url: "https://example.com"
  language: "en"
  copyright: "© 2025 Your Name"

# Theme configuration
theme: "modern"  # Options: modern, basic, or custom theme name
theme_config:
  # Modern theme specific settings
  colors:
    primary: "#3498db"  # Primary brand color
    secondary: "#2ecc71"  # Secondary color
    accent: "#e74c3c"  # Accent color for highlights
  fonts:
    heading: "'Roboto', sans-serif"
    body: "'Open Sans', sans-serif"
  features:
    dark_mode: true  # Enable dark mode toggle
    comments: false  # Enable comments section
    analytics:
      enabled: false
      id: ""  # Google Analytics ID

# Navigation menu
navigation:
  - title: "Home"
    url: "/"
  - title: "Blog"
    url: "/blog/"
  - title: "Projects"
    url: "/projects/"
  - title: "About"
    url: "/about/"

# Content directories
content:
  pages: "content/pages"  # Regular pages
  posts: "content/posts"  # Blog posts
  projects: "content/projects"  # Project pages

# Output settings
output:
  dir: "_site"  # Output directory
  pretty_urls: true  # Use pretty URLs (no .html extension)
  assets:
    optimize: true  # Optimize assets during build
```

## Directory Structure

When you create a new Giggle site, it will have the following structure:

```
my-site/
├── giggle.yaml            # Main configuration file
├── content/
│   ├── pages/            # Regular pages
│   │   ├── index.md      # Homepage
│   │   └── about.md      # About page
│   ├── posts/            # Blog posts
│   │   └── first-post.md # Sample blog post
│   └── projects/         # Project pages
│       └── my-project.md # Sample project
├── assets/
│   ├── css/             # Custom CSS files
│   ├── js/              # Custom JavaScript files
│   └── images/          # Image files
└── _site/               # Generated output (after build)
    └── (generated files)
```

## Writing Content

Giggle supports three main content types: pages, posts, and projects. You can create them using the CLI or manually.

### Using the CLI

The easiest way to create new content is with the CLI:

```bash
# Create a new page
giggle new_content page "Page Title"

# Create a new blog post
giggle new_content post "Blog Post Title"

# Create a new project
giggle new_content project "Project Title"
```

### Pages

Pages are for static content like your homepage, about page, etc. Create Markdown files in your `content/pages` directory with frontmatter:

```markdown
---
title: My Page Title
description: Page description for SEO
date: 2025-07-11
draft: false
layout: page
---

# Welcome to My Page

Content goes here...
```

### Blog Posts

Blog posts are for chronological content. They support additional metadata:

```markdown
---
title: My First Blog Post
description: A brief description
date: 2025-07-11
author: Your Name
tags: [tutorial, getting-started]
categories: [development]
featured_image: /assets/images/featured-post.jpg
draft: false
layout: post
---

# My First Blog Post

Blog content goes here...
```

### Projects

Projects are for showcasing your work with additional metadata:

```markdown
---
title: My Amazing Project
description: A brief description of the project
date: 2025-07-11
tags: [web, design]
status: completed  # Options: completed, in-progress, planned
links:
  website: https://example.com
  github: https://github.com/username/repo
technologies: [Python, JavaScript, HTML/CSS]
gallery:
  - /assets/images/project-1.jpg
  - /assets/images/project-2.jpg
draft: false
layout: project
---

# My Amazing Project

Project description and details go here...
```

## CLI Commands

Giggle provides several CLI commands to help you manage your site:

```bash
# Create a new Giggle site
giggle new [SITE_NAME]

# Build the site
giggle build

# Serve the site locally with live reload
giggle serve [--port PORT] [--host HOST]

# Create new content
giggle new_content [TYPE] [TITLE]
# Types: page, post, project

# Apply a theme to your site
giggle theme [THEME_NAME]
# Available themes: modern, basic
```

## Themes

Giggle comes with two built-in themes:

1. **Modern** - A clean, responsive theme with dark mode support, optimized for blogs and portfolios
2. **Basic** - A minimal starter theme that's easy to customize

### Theme Structure

Each theme includes:

```
theme-name/
├── templates/       # Jinja2 templates
│   ├── base.html    # Base template with common elements
│   ├── page.html    # Template for pages
│   ├── post.html    # Template for blog posts
│   ├── project.html # Template for projects
│   └── taxonomy.html # Template for tag/category pages
└── assets/
    ├── css/         # Stylesheets
    │   ├── main.css # Main stylesheet
    │   └── syntax.css # Code syntax highlighting
    └── js/          # JavaScript files
        ├── main.js  # Main JavaScript file
        └── dark-mode.js # Dark mode toggle functionality
```

### Custom Templates

You can override any theme template by creating a file with the same name in your site's `templates` directory. Giggle uses Jinja2 for templating, which provides powerful features like template inheritance, macros, and filters.

## Features

### Responsive Design

All built-in themes are fully responsive and work well on all devices from mobile phones to desktop computers.

### Dark Mode

The Modern theme includes built-in dark mode support with a toggle button and system preference detection.

### Syntax Highlighting

Code blocks in your Markdown content are automatically syntax-highlighted using Pygments.

### Live Reload

The development server includes live reload functionality, so your browser automatically refreshes when you make changes to your content or templates.

### SEO Optimization

Giggle generates SEO-friendly HTML with proper meta tags, sitemap.xml, and clean URLs.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please file an issue on GitHub.