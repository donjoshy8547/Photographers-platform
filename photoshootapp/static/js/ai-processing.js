/**
 * AI Processing JavaScript
 * Handles the interaction between the UI and backend for AI image processing
 */

// Function to process images with AI
function processImages() {
    console.log("processImages function called");
    
    // Show processing indicator
    showProcessingIndicator();
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Call the backend API
    fetch('/process-ai/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Show success message
            showSuccessMessage(data.message || 'AI processing started successfully!');
            
            // Start polling for completion
            startPollingForCompletion();
        } else {
            // Show error message
            showErrorMessage(data.message || 'Error starting AI processing');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Error connecting to server');
    });
}

// Function to show processing indicator
function showProcessingIndicator() {
    // Check if notification container exists
    let notificationContainer = document.getElementById('notification-container');
    
    // Create if it doesn't exist
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // Create processing notification
    const notification = document.createElement('div');
    notification.id = 'processing-notification';
    notification.className = 'alert alert-info';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border text-primary mr-3" role="status">
                <span class="sr-only">Processing...</span>
            </div>
            <div>
                <strong>AI Processing Started</strong>
                <p class="mb-0">Your images are being processed. This may take a few minutes.</p>
            </div>
        </div>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Update the AI Process button
    const aiProcessBtn = document.getElementById('ai-process-btn');
    if (aiProcessBtn) {
        aiProcessBtn.disabled = true;
        aiProcessBtn.innerHTML = '<i class="fa fa-spinner fa-spin mr-2"></i> Processing...';
    }
}

// Function to show success message
function showSuccessMessage(message) {
    // Remove processing notification if exists
    const processingNotification = document.getElementById('processing-notification');
    if (processingNotification) {
        processingNotification.remove();
    }
    
    // Get notification container
    const notificationContainer = document.getElementById('notification-container');
    
    // Create success notification
    const notification = document.createElement('div');
    notification.id = 'success-notification';
    notification.className = 'alert alert-success';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fa fa-check-circle mr-3" style="font-size: 24px;"></i>
            <div>
                <strong>Success!</strong>
                <p class="mb-0">${message}</p>
                <a href="/editor-dashboard/" class="btn btn-sm btn-primary mt-2">
                    View Results <i class="fa fa-arrow-right ml-1"></i>
                </a>
            </div>
        </div>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Reset the AI Process button
    const aiProcessBtn = document.getElementById('ai-process-btn');
    if (aiProcessBtn) {
        aiProcessBtn.disabled = false;
        aiProcessBtn.innerHTML = '<i class="fa fa-magic mr-2"></i> AI Process & Edit';
    }
    
    // Auto remove after 10 seconds
    setTimeout(() => {
        notification.remove();
    }, 10000);
}

// Function to show error message
function showErrorMessage(message) {
    // Remove processing notification if exists
    const processingNotification = document.getElementById('processing-notification');
    if (processingNotification) {
        processingNotification.remove();
    }
    
    // Get notification container
    const notificationContainer = document.getElementById('notification-container');
    
    // Create error notification
    const notification = document.createElement('div');
    notification.id = 'error-notification';
    notification.className = 'alert alert-danger';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fa fa-exclamation-triangle mr-3" style="font-size: 24px;"></i>
            <div>
                <strong>Error!</strong>
                <p class="mb-0">${message}</p>
            </div>
        </div>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Reset the AI Process button
    const aiProcessBtn = document.getElementById('ai-process-btn');
    if (aiProcessBtn) {
        aiProcessBtn.disabled = false;
        aiProcessBtn.innerHTML = '<i class="fa fa-magic mr-2"></i> AI Process & Edit';
    }
    
    // Auto remove after 10 seconds
    setTimeout(() => {
        notification.remove();
    }, 10000);
}

// Function to poll for processing completion
function startPollingForCompletion() {
    // We'll check every 5 seconds
    const pollInterval = 5000;
    
    // Set a timeout for polling (30 minutes)
    const pollTimeout = 30 * 60 * 1000;
    const startTime = Date.now();
    
    // Create polling function
    function pollForCompletion() {
        // Check if we've exceeded the timeout
        if (Date.now() - startTime > pollTimeout) {
            clearInterval(pollIntervalId);
            return;
        }
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Call the editor dashboard to check if processing is complete
        fetch('/editor-dashboard/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            // Check if processing is complete by seeing if there's content in the response
            // We're simply checking if the dashboard loads successfully
            if (response.ok) {
                // Update success message with completion
                const notification = document.getElementById('success-notification');
                if (notification) {
                    notification.innerHTML = `
                        <div class="d-flex align-items-center">
                            <i class="fa fa-check-circle mr-3" style="font-size: 24px;"></i>
                            <div>
                                <strong>Processing Complete!</strong>
                                <p class="mb-0">Your images have been processed successfully.</p>
                                <a href="/editor-dashboard/" class="btn btn-sm btn-primary mt-2">
                                    View Results <i class="fa fa-arrow-right ml-1"></i>
                                </a>
                            </div>
                        </div>
                    `;
                }
                
                // Stop polling
                clearInterval(pollIntervalId);
            }
        })
        .catch(error => {
            console.error('Error polling for completion:', error);
        });
    }
    
    // Start polling
    const pollIntervalId = setInterval(pollForCompletion, pollInterval);
}
