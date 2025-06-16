/**
 * AI Image Processing Functions
 * 
 * Handles AI processing of photographer images including:
 * - Emotion detection with DeepFace
 * - Caption generation with BLIP
 * - Face detection and cropping
 */

// Function to process images with AI models
function processImages() {
    // Show processing indicator
    showProcessingIndicator();
    
    // Send request to the process-ai endpoint
    fetch('/process-ai/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() // Django CSRF token
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        // Hide processing indicator
        hideProcessingIndicator();
        
        if (data.status === 'completed') {
            // Show success message with summary
            showSuccessMessage(data);
            
            // Redirect to editor dashboard after a short delay
            setTimeout(() => {
                window.location.href = '/editor-dashboard/';
            }, 2000);
        } else {
            // Show error message
            showErrorMessage(data.message || 'An unknown error occurred');
        }
    })
    .catch(error => {
        // Hide processing indicator
        hideProcessingIndicator();
        
        // Show error message
        showErrorMessage('Failed to process images: ' + error.message);
    });
}

// Helper function to get Django CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Helper function to show processing indicator
function showProcessingIndicator() {
    // Create or show processing overlay
    let overlay = document.getElementById('processing-overlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'processing-overlay';
        overlay.innerHTML = `
            <div class="processing-content">
                <div class="spinner"></div>
                <h3>Processing Images with AI</h3>
                <p>This may take a few minutes depending on the number of images.</p>
            </div>
        `;
        
        // Add styles to the overlay
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '1000';
        
        // Style the content
        const content = overlay.querySelector('.processing-content');
        content.style.backgroundColor = 'white';
        content.style.padding = '30px';
        content.style.borderRadius = '8px';
        content.style.textAlign = 'center';
        content.style.maxWidth = '400px';
        
        // Style the spinner
        const spinner = overlay.querySelector('.spinner');
        spinner.style.border = '8px solid #f3f3f3';
        spinner.style.borderTop = '8px solid #3498db';
        spinner.style.borderRadius = '50%';
        spinner.style.width = '60px';
        spinner.style.height = '60px';
        spinner.style.margin = '0 auto 20px auto';
        spinner.style.animation = 'spin 1s linear infinite';
        
        // Add keyframes for spinner animation
        const style = document.createElement('style');
        style.innerHTML = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(overlay);
    } else {
        overlay.style.display = 'flex';
    }
}

// Helper function to hide processing indicator
function hideProcessingIndicator() {
    const overlay = document.getElementById('processing-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Helper function to show success message
function showSuccessMessage(data) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'toast-notification success';
    toast.innerHTML = `
        <div class="toast-icon">✓</div>
        <div class="toast-message">
            <h4>Processing Complete!</h4>
            <p>Processed ${data.processed_images} images and detected ${data.detected_faces} faces.</p>
            <p>Redirecting to editor dashboard...</p>
        </div>
    `;
    
    // Style the toast
    styleToast(toast);
    
    // Add to document and remove after delay
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

// Helper function to show error message
function showErrorMessage(message) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'toast-notification error';
    toast.innerHTML = `
        <div class="toast-icon">×</div>
        <div class="toast-message">
            <h4>Error</h4>
            <p>${message}</p>
        </div>
    `;
    
    // Style the toast
    styleToast(toast);
    toast.style.backgroundColor = '#f44336';
    
    // Add to document and remove after delay
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

// Helper function to style toast notifications
function styleToast(toast) {
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.backgroundColor = '#4CAF50';
    toast.style.color = 'white';
    toast.style.padding = '10px';
    toast.style.borderRadius = '5px';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    toast.style.zIndex = '1001';
    toast.style.minWidth = '300px';
    toast.style.opacity = '1';
    toast.style.transition = 'opacity 0.5s';
    
    // Style the icon
    const icon = toast.querySelector('.toast-icon');
    icon.style.fontSize = '24px';
    icon.style.marginRight = '15px';
    icon.style.display = 'flex';
    icon.style.alignItems = 'center';
    icon.style.justifyContent = 'center';
    
    // Style the message
    const message = toast.querySelector('.toast-message');
    message.style.flex = '1';
}
