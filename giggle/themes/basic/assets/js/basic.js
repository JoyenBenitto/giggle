/**
 * Basic Theme JavaScript for Giggle
 * Minimal JavaScript functionality for the basic theme
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add active class to current navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navigation a');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        
        // Check if the current path matches the link path
        if (currentPath === linkPath || 
            (currentPath.startsWith(linkPath) && linkPath !== '/')) {
            link.classList.add('active');
        }
    });
    
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
                    top: targetElement.offsetTop - 20,
                    behavior: 'smooth'
                });
                
                // Update URL hash without scrolling
                history.pushState(null, null, targetId);
            }
        });
    });
    
    // Add responsive menu toggle for mobile
    const menuToggle = document.createElement('button');
    menuToggle.className = 'menu-toggle';
    menuToggle.setAttribute('aria-label', 'Toggle navigation menu');
    menuToggle.innerHTML = '☰';
    
    const navigation = document.querySelector('.navigation');
    if (navigation) {
        navigation.parentNode.insertBefore(menuToggle, navigation);
        
        menuToggle.addEventListener('click', function() {
            navigation.classList.toggle('active');
        });
    }
});
