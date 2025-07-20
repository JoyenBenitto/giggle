# Giggle Configuration Guide

This guide details all available configuration options in Giggle.

## Site Configuration

The site configuration file (`site_config.yaml`) controls your site's content, structure, and features.

### Basic Site Information

```yaml
site:
  title: "Your Site Title"
  description: "A brief description of your site"
  author: "Your Name"
  url: "https://example.com"
  copyright: "2024"
  language: "en"
  favicon: "./assets/favicon.ico"
```

### Social Links

```yaml
social_links:
  GitHub: "https://github.com/username"
  LinkedIn: "https://linkedin.com/in/username"
  Twitter: "https://twitter.com/username"
  Email: "mailto:you@example.com"
  # Add any other social platforms
```

### Navigation

```yaml
navigation:
  - title: "Home"
    url: "./index.html"
  - title: "Blog"
    url: "./blogs.html"
  - title: "Projects"
    url: "./projects.html"
    children:
      - title: "Project 1"
        url: "./projects/project1.html"
      - title: "Project 2"
        url: "./projects/project2.html"
```

### Content Pages

```yaml
pages:
  # Single pages
  index: ./markdowns/main.md
  about: ./markdowns/about.md
  contact: ./markdowns/contact.md
  
  # Directory of posts
  blogs: ./markdowns/blog/
  projects: ./markdowns/projects/
```

### Feature Flags

```yaml
features:
  tag_pages: true      # Enable tag-based navigation
  blog_pages: true     # Enable blog functionality
  dark_mode: true      # Enable dark mode
  search: true         # Enable search functionality
  toc: true           # Enable table of contents
  syntax_highlight: true  # Enable code syntax highlighting
  comments: false      # Enable comment system
```

### Build Settings

```yaml
build:
  output_dir: "./build"
  assets_dir: "./assets"
  templates_dir: "./templates"
  minify: true
  compress_images: true
  cache: true
```

### SEO Settings

```yaml
seo:
  meta_description: "Site-wide meta description"
  keywords: ["keyword1", "keyword2"]
  og_image: "./assets/images/og-image.jpg"
  twitter_card: "summary_large_image"
  google_analytics: "UA-XXXXXXXXX-X"
```

## Style Configuration

The style configuration file (`style_config.yaml`) controls your site's appearance.

### Colors

```yaml
colors:
  # Base colors
  background: "#121212"
  text: "#E0E0E0"
  
  # Primary colors
  primary: "#2196F3"
  primary_light: "#64B5F6"
  primary_dark: "#1976D2"
  
  # Secondary colors
  secondary: "#FF4081"
  secondary_light: "#FF80AB"
  secondary_dark: "#F50057"
  
  # Accent colors
  accent: "#64B5F6"
  accent_light: "#90CAF9"
  accent_dark: "#42A5F5"
  
  # Background variations
  background_secondary: "#1E1E1E"
  background_tertiary: "#2D2D2D"
  
  # Text variations
  text_secondary: "#A0A0A0"
  text_tertiary: "#757575"
  
  # Status colors
  success: "#4CAF50"
  warning: "#FFC107"
  error: "#F44336"
  info: "#2196F3"
```

### Typography

```yaml
typography:
  # Font families
  font_family:
    body: '"Inter", sans-serif'
    headers: '"Roboto", sans-serif'
    code: '"Fira Code", monospace'
  
  # Font sizes
  sizes:
    body: "16px"
    small: "14px"
    headers:
      h1: "2rem"
      h2: "1.5rem"
      h3: "1.3rem"
      h4: "1.2rem"
      h5: "1.1rem"
      h6: "1rem"
  
  # Line heights
  line_height:
    body: "1.6"
    headers: "1.3"
    code: "1.5"
  
  # Font weights
  weights:
    normal: 400
    medium: 500
    bold: 700
```

### Layout

```yaml
layout:
  # Spacing
  spacing:
    xs: "0.25rem"
    sm: "0.5rem"
    md: "1rem"
    lg: "2rem"
    xl: "4rem"
  
  # Border radius
  border_radius:
    sm: "4px"
    md: "8px"
    lg: "16px"
    round: "50%"
  
  # Container
  container:
    max_width: "1200px"
    padding: "2rem"
  
  # Grid
  grid:
    columns: 12
    gap: "2rem"
```

### Components

```yaml
components:
  # Buttons
  button:
    padding: "0.5rem 1rem"
    border_radius: "4px"
    transition: "all 0.3s ease"
    
  # Cards
  card:
    padding: "1.5rem"
    border_radius: "8px"
    shadow: "0 4px 6px rgba(0, 0, 0, 0.1)"
    
  # Navigation
  nav:
    height: "60px"
    shadow: "0 2px 4px rgba(0, 0, 0, 0.1)"
    
  # Footer
  footer:
    padding: "2rem"
    border_top: "1px solid rgba(255, 255, 255, 0.1)"
```

### Animations

```yaml
animations:
  duration:
    fast: "0.2s"
    normal: "0.3s"
    slow: "0.5s"
    
  timing:
    default: "ease"
    bounce: "cubic-bezier(0.68, -0.55, 0.265, 1.55)"
    
  hover:
    scale: 1.05
    brightness: 1.1
```

### Media Queries

```yaml
breakpoints:
  mobile: "576px"
  tablet: "768px"
  desktop: "1024px"
  wide: "1200px"
```

## Using Configuration Values

### In Templates

```html
<div class="container" style="max-width: {{ layout.container.max_width }}">
    <h1 style="font-family: {{ typography.font_family.headers }}">
        {{ site.title }}
    </h1>
</div>
```

### In CSS

```css
:root {
    --color-bg: {{ colors.background }};
    --color-text: {{ colors.text }};
    --font-body: {{ typography.font_family.body }};
    --spacing-lg: {{ layout.spacing.lg }};
}

.button {
    padding: {{ components.button.padding }};
    border-radius: {{ components.button.border_radius }};
    transition: {{ components.button.transition }};
}
```

## Best Practices

1. **Organization**
   - Keep related settings grouped together
   - Use meaningful names for custom values
   - Document any custom additions

2. **Maintenance**
   - Regular review of configuration
   - Version control for configuration files
   - Backup configurations

3. **Performance**
   - Minimize custom fonts
   - Optimize image quality settings
   - Enable minification in production

4. **Accessibility**
   - Maintain sufficient color contrast
   - Use relative units where appropriate
   - Consider font sizing for readability
