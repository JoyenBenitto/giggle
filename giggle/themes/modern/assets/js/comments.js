/**
 * Comments System for Giggle Modern Theme
 * 
 * This is a simple client-side comment system that stores comments in localStorage.
 * For a production site, you would want to replace this with a server-side solution.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if comments section exists
    const commentsSection = document.querySelector('.comments-section');
    if (!commentsSection) return;
    
    // Get post identifier from data attribute or fallback to URL path
    const postId = commentsSection.dataset.postId || window.location.pathname;
    
    // Comment storage key in localStorage
    const storageKey = `giggle-comments-${postId}`;
    
    // Elements
    const commentsList = document.querySelector('.comments-list');
    const commentForm = document.querySelector('.comment-form');
    const nameInput = document.querySelector('#comment-name');
    const emailInput = document.querySelector('#comment-email');
    const contentInput = document.querySelector('#comment-content');
    
    // Load existing comments
    function loadComments() {
        const savedComments = localStorage.getItem(storageKey);
        const comments = savedComments ? JSON.parse(savedComments) : [];
        
        // Clear comments list
        commentsList.innerHTML = '';
        
        if (comments.length === 0) {
            commentsList.innerHTML = '<p class="no-comments">No comments yet. Be the first to comment!</p>';
            return;
        }
        
        // Add each comment to the list
        comments.forEach((comment, index) => {
            const commentElement = createCommentElement(comment, index);
            commentsList.appendChild(commentElement);
        });
    }
    
    // Create comment element
    function createCommentElement(comment, index) {
        const commentEl = document.createElement('div');
        commentEl.className = 'comment';
        commentEl.dataset.index = index;
        
        // Create avatar with first letter of name
        const avatar = document.createElement('div');
        avatar.className = 'comment-avatar';
        avatar.textContent = comment.name.charAt(0).toUpperCase();
        
        // Create comment content
        const content = document.createElement('div');
        content.className = 'comment-content';
        
        // Create comment header with name and date
        const header = document.createElement('div');
        header.className = 'comment-header';
        
        const name = document.createElement('span');
        name.className = 'comment-name';
        name.textContent = comment.name;
        
        const date = document.createElement('span');
        date.className = 'comment-date';
        date.textContent = new Date(comment.date).toLocaleDateString();
        
        header.appendChild(name);
        header.appendChild(date);
        
        // Create comment text
        const text = document.createElement('div');
        text.className = 'comment-text';
        text.textContent = comment.content;
        
        // Create reply button
        const replyButton = document.createElement('button');
        replyButton.className = 'reply-button';
        replyButton.textContent = 'Reply';
        replyButton.addEventListener('click', function() {
            // Set reply placeholder
            contentInput.placeholder = `Replying to ${comment.name}...`;
            contentInput.dataset.replyTo = index;
            contentInput.focus();
            
            // Scroll to form
            commentForm.scrollIntoView({ behavior: 'smooth' });
        });
        
        // Assemble comment
        content.appendChild(header);
        content.appendChild(text);
        content.appendChild(replyButton);
        
        commentEl.appendChild(avatar);
        commentEl.appendChild(content);
        
        // Add replies if any
        if (comment.replies && comment.replies.length > 0) {
            const repliesContainer = document.createElement('div');
            repliesContainer.className = 'comment-replies';
            
            comment.replies.forEach(reply => {
                const replyEl = document.createElement('div');
                replyEl.className = 'comment reply';
                
                // Create reply avatar
                const replyAvatar = document.createElement('div');
                replyAvatar.className = 'comment-avatar';
                replyAvatar.textContent = reply.name.charAt(0).toUpperCase();
                
                // Create reply content
                const replyContent = document.createElement('div');
                replyContent.className = 'comment-content';
                
                // Create reply header
                const replyHeader = document.createElement('div');
                replyHeader.className = 'comment-header';
                
                const replyName = document.createElement('span');
                replyName.className = 'comment-name';
                replyName.textContent = reply.name;
                
                const replyDate = document.createElement('span');
                replyDate.className = 'comment-date';
                replyDate.textContent = new Date(reply.date).toLocaleDateString();
                
                replyHeader.appendChild(replyName);
                replyHeader.appendChild(replyDate);
                
                // Create reply text
                const replyText = document.createElement('div');
                replyText.className = 'comment-text';
                replyText.textContent = reply.content;
                
                // Assemble reply
                replyContent.appendChild(replyHeader);
                replyContent.appendChild(replyText);
                
                replyEl.appendChild(replyAvatar);
                replyEl.appendChild(replyContent);
                
                repliesContainer.appendChild(replyEl);
            });
            
            commentEl.appendChild(repliesContainer);
        }
        
        return commentEl;
    }
    
    // Save a new comment
    function saveComment(name, email, content, replyTo = null) {
        const savedComments = localStorage.getItem(storageKey);
        const comments = savedComments ? JSON.parse(savedComments) : [];
        
        const newComment = {
            name,
            email,
            content,
            date: new Date().toISOString()
        };
        
        // If it's a reply, add to the parent comment's replies
        if (replyTo !== null) {
            const replyIndex = parseInt(replyTo);
            if (!comments[replyIndex].replies) {
                comments[replyIndex].replies = [];
            }
            comments[replyIndex].replies.push(newComment);
        } else {
            // Otherwise add as a new comment
            comments.push(newComment);
        }
        
        localStorage.setItem(storageKey, JSON.stringify(comments));
        loadComments();
    }
    
    // Handle form submission
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate inputs
            if (!nameInput.value.trim() || !contentInput.value.trim()) {
                alert('Please fill in your name and comment.');
                return;
            }
            
            // Get reply-to index if any
            const replyTo = contentInput.dataset.replyTo || null;
            
            // Save the comment
            saveComment(
                nameInput.value.trim(),
                emailInput ? emailInput.value.trim() : '',
                contentInput.value.trim(),
                replyTo
            );
            
            // Reset form
            commentForm.reset();
            contentInput.placeholder = 'Write your comment...';
            delete contentInput.dataset.replyTo;
            
            // Show success message
            const successMessage = document.createElement('div');
            successMessage.className = 'comment-success';
            successMessage.textContent = 'Comment submitted successfully!';
            commentForm.appendChild(successMessage);
            
            // Remove success message after 3 seconds
            setTimeout(() => {
                commentForm.removeChild(successMessage);
            }, 3000);
        });
    }
    
    // Initialize
    loadComments();
});
