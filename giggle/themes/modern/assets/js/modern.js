/**
 * Modern Theme JavaScript
 * Provides interactive functionality for the Modern theme
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const mainNavigation = document.querySelector('.main-navigation');
    
    if (menuToggle && mainNavigation) {
        menuToggle.addEventListener('click', function() {
            mainNavigation.classList.toggle('active');
            const expanded = mainNavigation.classList.contains('active');
            menuToggle.setAttribute('aria-expanded', expanded);
        });
    }
    
    // Handle external links
    const links = document.querySelectorAll('a[href^="http"]');
    links.forEach(link => {
        // Skip links that already have target attribute
        if (!link.hasAttribute('target')) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            
            // Skip if it's just "#" or empty
            if (targetId === '#' || !targetId) {
                return;
            }
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Account for fixed header
                    behavior: 'smooth'
                });
                
                // Update URL hash without scrolling
                history.pushState(null, null, targetId);
            }
        });
    });
    
    // Add active class to current navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.main-navigation a');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        
        // Check if the current path matches the link path
        // or if we're on a subpage and the link is to a parent section
        if (currentPath === linkPath || 
            (currentPath.startsWith(linkPath) && linkPath !== '/')) {
            link.parentElement.classList.add('active');
        }
    });
    
    // Initialize image lightbox for gallery images
    const galleryImages = document.querySelectorAll('.gallery-image');
    if (galleryImages.length > 0) {
        galleryImages.forEach(image => {
            image.addEventListener('click', function() {
                const lightbox = document.createElement('div');
                lightbox.className = 'lightbox';
                
                const lightboxContent = document.createElement('div');
                lightboxContent.className = 'lightbox-content';
                
                const lightboxImage = document.createElement('img');
                lightboxImage.src = this.src;
                lightboxImage.alt = this.alt;
                
                const closeButton = document.createElement('button');
                closeButton.className = 'lightbox-close';
                closeButton.innerHTML = '&times;';
                closeButton.addEventListener('click', function() {
                    document.body.removeChild(lightbox);
                });
                
                lightboxContent.appendChild(lightboxImage);
                lightboxContent.appendChild(closeButton);
                lightbox.appendChild(lightboxContent);
                
                document.body.appendChild(lightbox);
                
                // Close lightbox when clicking outside the image
                lightbox.addEventListener('click', function(e) {
                    if (e.target === lightbox) {
                        document.body.removeChild(lightbox);
                    }
                });
                
                // Add keyboard navigation
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape') {
                        if (document.querySelector('.lightbox')) {
                            document.body.removeChild(lightbox);
                        }
                    }
                });
            });
        });
    }
    
    // Add table of contents for long articles
    const article = document.querySelector('.post-content, .page-content');
    if (article) {
        const headings = article.querySelectorAll('h2, h3');
        
        // Only create TOC if there are at least 3 headings
        if (headings.length >= 3) {
            const toc = document.createElement('div');
            toc.className = 'table-of-contents';
            
            const tocTitle = document.createElement('h2');
            tocTitle.textContent = 'Table of Contents';
            toc.appendChild(tocTitle);
            
            const tocList = document.createElement('ul');
            
            headings.forEach((heading, index) => {
                // Add ID to the heading if it doesn't have one
                if (!heading.id) {
                    heading.id = `heading-${index}`;
                }
                
                const listItem = document.createElement('li');
                const link = document.createElement('a');
                
                link.href = `#${heading.id}`;
                link.textContent = heading.textContent;
                
                // Add class based on heading level
                if (heading.tagName === 'H3') {
                    listItem.className = 'toc-subitem';
                }
                
                listItem.appendChild(link);
                tocList.appendChild(listItem);
            });
            
            toc.appendChild(tocList);
            
            // Insert TOC after the first heading
            const firstHeading = article.querySelector('h1');
            if (firstHeading) {
                firstHeading.parentNode.insertBefore(toc, firstHeading.nextSibling);
            } else {
                article.insertBefore(toc, article.firstChild);
            }
        }
    }
});
