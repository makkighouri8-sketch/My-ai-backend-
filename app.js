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

// Dynamic input icon toggle (Send vs Mic/Live)
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

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage(event);
    }
}

// Send Message (Keyboard open rehney ki fix ke sath)
async function sendMessage(event) {
    if (event) event.preventDefault();
    
    const input = document.getElementById('msgInput');
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById('chatBox');
    
    // User Message DOM
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.style.alignSelf = 'flex-end';
    userDiv.style.background = '#27272a';
    userDiv.style.color = '#fff';
    userDiv.textContent = message;
    chatBox.appendChild(userDiv);

    // Clear input & retain focus (Keep Keyboard OPEN)
    input.value = '';
    handleInputToggle();
    input.focus();
    chatBox.scrollTop = chatBox.scrollHeight;

    // AI Response Loader
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

// Live Call Animation Toggle Function
function startLiveCall() {
    const overlay = document.getElementById('liveOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function stopLiveCall() {
    const overlay = document.getElementById('liveOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    handleInputToggle();
    const input = document.getElementById('msgInput');
    if (input) {
        input.addEventListener('input', handleInputToggle);
    }
});
