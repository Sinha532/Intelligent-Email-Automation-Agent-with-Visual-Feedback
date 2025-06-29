const socket = io();
let sessionId = generateSessionId();
let isWaitingForResponse = false;

// DOM elements
const chatContainer = document.getElementById('chatContainer');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const connectionStatus = document.getElementById('connectionStatus');
const agentStatus = document.getElementById('agentStatus');
const automationStatus = document.getElementById('automationStatus');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const currentStep = document.getElementById('currentStep');
const screenshotContainer = document.getElementById('screenshotContainer');
const screenshotInfo = document.getElementById('screenshotInfo');
const currentUrl = document.getElementById('currentUrl');
const lastUpdate = document.getElementById('lastUpdate');
const emailPreviewSection = document.getElementById('emailPreviewSection');
const emailPreviewContent = document.getElementById('emailPreviewContent');

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

// Initialize the application
function initializeApp() {
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendButton.addEventListener('click', sendMessage);
    
    // Auto-focus on chat input
    chatInput.focus();
}

// Send message function
function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || isWaitingForResponse) return;

    // Add user message to chat
    addChatMessage('user', message);
    
    // Clear input and disable
    chatInput.value = '';
    setInputState(false, 'AI is thinking...');
    isWaitingForResponse = true;

    // Send to backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            session_id: sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        handleChatResponse(data);
        setInputState(true);
        isWaitingForResponse = false;
    })
    .catch(error => {
        console.error('Error:', error);
        addChatMessage('error', 'Sorry, there was an error processing your message. Please try again.');
        setInputState(true);
        isWaitingForResponse = false;
    });
}

// Handle chat response from backend
function handleChatResponse(data) {
    const messageType = data.type || 'system';
    addChatMessage(messageType, data.response);

    // Update agent status based on response type
    switch(data.type) {
        case 'username_request':
            updateAgentStatus('Waiting for your name');
            break;
        case 'gmail_request':
            updateAgentStatus('Waiting for Gmail address');
            break;
        case 'password_request':
            updateAgentStatus('Waiting for password');
            break;
        case 'recipient_request':
            updateAgentStatus('Waiting for recipient');
            break;
        case 'ready_to_send':
            updateAgentStatus('Starting automation...');
            updateAutomationStatus('Initializing...');
            break;
        default:
            updateAgentStatus('Ready');
    }
}

// Add message to chat container
function addChatMessage(type, message, timestamp = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    
    const avatar = getAvatarForType(type);
    const time = timestamp || new Date().toLocaleTimeString();
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-text">${formatMessage(message)}</div>
            <div class="message-time">${time}</div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Add animation
    messageDiv.style.animation = 'fadeInUp 0.3s ease';
}

// Get avatar emoji based on message type
function getAvatarForType(type) {
    const avatars = {
        'user': '👤',
        'system': '🤖',
        'success': '✅',
        'error': '❌',
        'username_request': '👋',
        'gmail_request': '📧',
        'password_request': '🔐',
        'recipient_request': '📬',
        'ready_to_send': '🚀'
    };
    return avatars[type] || '🤖';
}

// Format message text (convert newlines, etc.)
function formatMessage(message) {
    return message
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

// Set input state (enabled/disabled with placeholder)
function setInputState(enabled, placeholder = 'Type your message...') {
    chatInput.disabled = !enabled;
    sendButton.disabled = !enabled;
    chatInput.placeholder = placeholder;
    
    if (enabled) {
        chatInput.focus();
    }
}

// Update agent status
function updateAgentStatus(status) {
    agentStatus.textContent = status;
    agentStatus.className = 'agent-status';
    
    if (status.includes('automation') || status.includes('Starting')) {
        agentStatus.classList.add('running');
    }
}

// Update automation status
function updateAutomationStatus(status) {
    automationStatus.textContent = status;
    
    if (status !== 'Idle') {
        automationStatus.classList.add('running');
        progressSection.style.display = 'block';
    } else {
        automationStatus.classList.remove('running');
        progressSection.style.display = 'none';
    }
}

// Update progress
function updateProgress(progress, step) {
    progressFill.style.width = progress + '%';
    progressText.textContent = progress + '%';
    currentStep.textContent = step;
    updateAutomationStatus('Running...');
}

// Update screenshot display
function updateScreenshot(screenshotData, step, timestamp, url) {
    screenshotContainer.innerHTML = `
        <div style="text-align: center;">
            <h3 style="margin-bottom: 10px; color: #333;">${step}</h3>
            <img src="${screenshotData}" alt="Live Screenshot" style="max-width: 100%; max-height: 350px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">Updated: ${timestamp}</p>
        </div>
    `;
    
    // Update screenshot info
    currentUrl.textContent = url || 'Loading...';
    lastUpdate.textContent = timestamp;
}

// Show email preview
function showEmailPreview(emailContent) {
    emailPreviewContent.innerHTML = `
        <div class="email-field">
            <label>Subject:</label>
            <div class="field-value">${emailContent.subject}</div>
        </div>
        <div class="email-field">
            <label>Body:</label>
            <div class="field-value">${emailContent.body.replace(/\n/g, '<br>')}</div>
        </div>
    `;
    
    emailPreviewSection.style.display = 'block';
    
    // Scroll to preview
    emailPreviewSection.scrollIntoView({ behavior: 'smooth' });
}



// Socket event handlers
socket.on('connect', function() {
    connectionStatus.textContent = 'Connected';
    connectionStatus.className = 'connection-status connected';
    console.log('Connected to server');
});

socket.on('disconnect', function() {
    connectionStatus.textContent = 'Disconnected';
    connectionStatus.className = 'connection-status disconnected';
    console.log('Disconnected from server');
});

socket.on('connected', function(data) {
    console.log('Server connection confirmed:', data.message);
});

socket.on('status_update', function(data) {
    console.log('Status update:', data);
    updateProgress(data.progress, data.step);
    
    if (data.screenshot) {
        updateScreenshot(data.screenshot, data.step, data.timestamp, data.url);
    }
});

socket.on('automation_complete', function(data) {
    console.log('Automation complete:', data);
    updateAutomationStatus('Completed Successfully');
    updateAgentStatus('Ready');
    
    // Show success message
    addChatMessage('success', data.message);
    
    // Show email preview if available
    if (data.email_content) {
        showEmailPreview(data.email_content);
    }
    
    // Reset progress after a delay
    setTimeout(() => {
        updateAutomationStatus('Idle');
        progressSection.style.display = 'none';
    }, 5000);
});

socket.on('automation_error', function(data) {
    console.error('Automation error:', data);
    updateAutomationStatus('Error Occurred');
    updateAgentStatus('Ready');
    
    addChatMessage('error', `Automation failed: ${data.error}`);
    
    // Reset after a delay
    setTimeout(() => {
        updateAutomationStatus('Idle');
        progressSection.style.display = 'none';
    }, 5000);
});

socket.on('chat_message', function(data) {
    console.log('Chat message from server:', data);
    addChatMessage(data.type || 'system', data.message, data.timestamp);
});

socket.on('error', function(data) {
    console.error('Socket error:', data);
    addChatMessage('error', data.message || 'An unexpected error occurred');
});

// Utility functions
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function clearChat() {
    const messages = chatContainer.querySelectorAll('.chat-message:not(.system)');
    messages.forEach(msg => msg.remove());
}

// Enhanced error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    addChatMessage('error', 'An unexpected error occurred. Please refresh the page if issues persist.');
});

// Visibility change handling (for when user switches tabs)
document.addEventListener('visibilitychange', function() {
    if (!document.hidden && socket.disconnected) {
        socket.connect();
    }
});

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    
    // Add initial system message
//     setTimeout(() => {
//         addChatMessage('system', `
//             Welcome! I'm your AI-powered Gmail automation assistant. 
//             <br><br>
//             I can help you send professional emails automatically with AI-generated content.
//             <br><br>
//             To get started, please tell me your full name so I can personalize your emails properly.
//         `);
//     }, 500);
});


window.clearChat = clearChat;