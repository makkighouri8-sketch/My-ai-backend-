// Tab switching logic
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active-tab');
    });
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(tabId).classList.add('active-tab');

    if (tabId === 'chatTab') {
        document.getElementById('btnChat').classList.add('active');
    } else {
        document.getElementById('btnStudio').classList.add('active');
    }
}

// Toggle Send button vs Mic/Live icons dynamically
function handleInputToggle() {
    const input = document.getElementById('msgInput');
    const sendBtn = document.getElementById('sendBtn');
    const voiceGroup = document.getElementById('voiceGroup');

    if (!input || !sendBtn || !voiceGroup) return;

    if (input.value.trim().length > 0) {
        sendBtn.style.display = 'flex';
        voiceGroup.style.display = 'none';
    } else {
        sendBtn.style.display = 'none';
        voiceGroup.style.display = 'flex';
    }
}

// Handle Enter key for sending messages
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Send Message logic
async function sendMessage() {
    const input = document.getElementById('msgInput');
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById('chatBox');
    
    // Append User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.style.alignSelf = 'flex-end';
    userDiv.style.background = '#27272a';
    userDiv.style.color = '#fff';
    userDiv.textContent = message;
    chatBox.appendChild(userDiv);

    // Clear Input and reset buttons
    input.value = '';
    handleInputToggle();
    chatBox.scrollTop = chatBox.scrollHeight;

    // AI Loading Indicator
    const aiDiv = document.createElement('div');
    aiDiv.className = 'message ai-message';
    aiDiv.textContent = 'Thinking...';
    chatBox.appendChild(aiDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        aiDiv.textContent = data.reply || "No response received.";
    } catch (err) {
        aiDiv.textContent = "Error connecting to server.";
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Initialize button visibility on page load
document.addEventListener('DOMContentLoaded', () => {
    handleInputToggle();
    
    const input = document.getElementById('msgInput');
    if (input) {
        input.addEventListener('input', handleInputToggle);
    }
});
