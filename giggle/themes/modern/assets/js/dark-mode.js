/**
 * Dark Mode Toggle
 * Handles dark mode functionality for the Modern theme
 */

document.addEventListener('DOMContentLoaded', function() {
    // Create dark mode toggle button
    const createDarkModeToggle = () => {
        const toggle = document.createElement('button');
        toggle.className = 'dark-mode-toggle';
        toggle.setAttribute('aria-label', 'Toggle dark mode');
        toggle.setAttribute('title', 'Toggle dark mode');
        
        // Create icon
        const icon = document.createElement('span');
        icon.className = 'dark-mode-icon';
        toggle.appendChild(icon);
        
        return toggle;
    };
    
    // Get user preference
    const getUserPreference = () => {
        // Check if preference is stored in localStorage
        const storedPreference = localStorage.getItem('darkMode');
        if (storedPreference) {
            return storedPreference === 'true';
        }
        
        // If no stored preference, check system preference
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    };
    
    // Set dark mode state
    const setDarkMode = (isDark) => {
        if (isDark) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'true');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'false');
        }
        
        // Update toggle button appearance
        const toggle = document.querySelector('.dark-mode-toggle');
        if (toggle) {
            toggle.setAttribute('aria-pressed', isDark);
        }
    };
    
    // Toggle dark mode
    const toggleDarkMode = () => {
        const isDark = document.body.classList.contains('dark-mode');
        setDarkMode(!isDark);
    };
    
    // Initialize dark mode
    const initDarkMode = () => {
        // Create toggle button
        const toggle = createDarkModeToggle();
        
        // Add toggle to header
        const header = document.querySelector('.header-content');
        if (header) {
            header.appendChild(toggle);
        }
        
        // Set initial state based on user preference
        const isDark = getUserPreference();
        setDarkMode(isDark);
        
        // Add event listener to toggle
        toggle.addEventListener('click', toggleDarkMode);
        
        // Listen for system preference changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            // Only update if user hasn't manually set preference
            if (!localStorage.getItem('darkMode')) {
                setDarkMode(e.matches);
            }
        });
    };
    
    // Initialize
    initDarkMode();
    
    // Add dark mode styles
    const addDarkModeStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            .dark-mode-toggle {
                background: none;
                border: none;
                cursor: pointer;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-left: 1rem;
                padding: 0;
                transition: background-color 0.2s ease;
            }
            
            .dark-mode-toggle:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            .dark-mode .dark-mode-toggle:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            .dark-mode-icon {
                display: inline-block;
                width: 24px;
                height: 24px;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23333'%3E%3Cpath d='M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06z'/%3E%3C/svg%3E");
                background-position: center;
                background-repeat: no-repeat;
                transition: transform 0.3s ease;
            }
            
            .dark-mode .dark-mode-icon {
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23fff'%3E%3Cpath d='M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z'/%3E%3C/svg%3E");
                transform: rotate(360deg);
            }
            
            /* Dark mode specific styles */
            .dark-mode .lightbox {
                background-color: rgba(0, 0, 0, 0.9);
            }
            
            .dark-mode code {
                background-color: #2d2d2d;
                color: #e6e6e6;
            }
            
            .dark-mode pre {
                background-color: #2d2d2d;
            }
            
            .dark-mode blockquote {
                background-color: rgba(255, 255, 255, 0.05);
            }
            
            .dark-mode .table-of-contents {
                background-color: rgba(255, 255, 255, 0.05);
                border-left: 3px solid var(--color-primary);
            }
        `;
        document.head.appendChild(style);
    };
    
    addDarkModeStyles();
});
