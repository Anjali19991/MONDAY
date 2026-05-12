// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const chatForm = document.getElementById('chatForm');
const resetBtn = document.getElementById('resetBtn');
const healthBtn = document.getElementById('healthBtn');
const typingIndicator = document.getElementById('typingIndicator');

// Event Listeners
chatForm.addEventListener('submit', handleSendMessage);
resetBtn.addEventListener('click', handleReset);
healthBtn.addEventListener('click', handleHealth);

// Handle send message
async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    userInput.focus();
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            addMessage(data.response, 'assistant');
        } else {
            addMessage(`Error: ${data.error}`, 'assistant');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage(`Connection error: ${error.message}`, 'assistant');
    } finally {
        hideTypingIndicator();
    }
}

// Add message to chat
function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Parse text to handle lists and code blocks
    const lines = text.split('\n');
    let html = '';
    
    lines.forEach(line => {
        line = line.trim();
        if (line.startsWith('- ')) {
            html += `<li>${line.substring(2)}</li>`;
        } else if (line.startsWith('* ')) {
            html += `<li>${line.substring(2)}</li>`;
        } else if (line.match(/^\d+\./)) {
            html += `<li>${line.substring(line.indexOf('.') + 1).trim()}</li>`;
        } else if (line.startsWith('===') || line.startsWith('---')) {
            html += '<hr style="margin: 5px 0; border: none; border-top: 1px solid rgba(0,0,0,0.1);">';
        } else if (line) {
            html += `<p>${escapeHtml(line)}</p>`;
        }
    });
    
    // Wrap lists
    html = html.replace(/(<li>.*?<\/li>)/s, (match) => {
        if (!match.includes('<ul>')) {
            return `<ul style="margin-left: 20px;">${match}</ul>`;
        }
        return match;
    });
    
    contentDiv.innerHTML = html;
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

// Handle reset
async function handleReset() {
    if (!confirm('Clear conversation history?')) return;
    
    try {
        const response = await fetch('/api/reset', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            chatMessages.innerHTML = `
                <div class="message system">
                    <div class="message-content">
                        <p>👋 Conversation reset. Ready to help!</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error resetting: ${error.message}`);
    }
}

// Handle health check
async function handleHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            alert(`✅ Status: Healthy\nModel: ${data.model}\nOllama: ${data.api_url}`);
        } else {
            alert(`❌ Status: Error\n${data.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Connection error: ${error.message}`);
    }
}

// Utility: Escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Focus input on load
window.addEventListener('load', () => {
    userInput.focus();
});

// Allow Enter to send (Shift+Enter for newline)
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});
