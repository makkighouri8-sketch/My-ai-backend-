// Tab switching logic
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active-tab'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabId).classList.add('active-tab');

    if (tabId === 'chatTab') {
        document.getElementById('btnChat').classList.add('active');
    } else {
        document.getElementById('btnStudio').classList.add('active');
    }
}

// Mobile-Friendly Live Chat Wave Toggle
function setupLiveChatToggle() {
    const liveChatBtn = document.getElementById('liveChatBtn') || document.querySelector('.live-chat-btn');
    const neonWaveContainer = document.getElementById('neonWaveContainer') || document.querySelector('.neon-wave-container');

    if (!liveChatBtn || !neonWaveContainer) return;

    function toggleLiveChat(e) {
        if (e.type === 'touchstart') {
            e.preventDefault(); // Ghost clicks aur mobile delay roknay ke liye
        }
        neonWaveContainer.classList.toggle('active');
    }

    // Touch aur Click events handle karna
    liveChatBtn.addEventListener('touchstart', toggleLiveChat, { passive: false });
    liveChatBtn.addEventListener('click', toggleLiveChat);
}

// Dynamic input toggle & Auto-height adjustment
function handleInputToggle() {
    const input = document.getElementById('msgInput');
    const sendBtn = document.getElementById('sendBtn');
    const voiceGroup = document.getElementById('voiceGroup');

    if (!input || !sendBtn || !voiceGroup) return;

    // Auto resize input if it's a textarea
    input.style.height = 'auto';
    input.style.height = (input.scrollHeight) + 'px';

    if (input.value.trim().length > 0) {
        sendBtn.style.display = 'flex';
        voiceGroup.style.display = 'none';
    } else {
        sendBtn.style.display = 'none';
        voiceGroup.style.display = 'flex';
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage(event);
    }
}

// Chat history store
let chatHistory = [];

// AI Typing Effect Function
async function typeWriterEffect(element, text) {
    element.innerHTML = ''; 
    let formattedText = marked.parse(text); // Markdown to HTML conversion
    
    // Smooth insertion with parsed HTML
    element.innerHTML = formattedText;
    
    // Code blocks par syntax highlighting apply karna
    if (window.hljs) {
        element.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }

    // Modern Copy Button for code blocks
    element.querySelectorAll('pre').forEach(pre => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-code-btn';
        copyBtn.innerText = 'Copy';
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(pre.querySelector('code').innerText);
            copyBtn.innerText = 'Copied!';
            setTimeout(() => copyBtn.innerText = 'Copy', 2000);
        };
        pre.appendChild(copyBtn);
    });
}

// Send Message logic
async function sendMessage(event) {
    if (event) event.preventDefault();
    
    const input = document.getElementById('msgInput');
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById('chatBox');
    
    // User Message DOM
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.textContent = message;
    chatBox.appendChild(userDiv);

    // Reset input
    input.value = '';
    handleInputToggle();
    input.focus();
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });

    // AI Response Loader / Skeleton
    const aiDiv = document.createElement('div');
    aiDiv.className = 'message ai-message typing-indicator';
    aiDiv.innerHTML = '<span>.</span><span>.</span><span>.</span>';
    chatBox.appendChild(aiDiv);
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, history: chatHistory })
        });
        
        const data = await response.json();
        const reply = data.reply || "No response received.";

        aiDiv.classList.remove('typing-indicator');
        
        // Render Markdown & Highlight
        await typeWriterEffect(aiDiv, reply);

        // Update history
        chatHistory.push({ role: "user", text: message });
        chatHistory.push({ role: "model", text: reply });

    } catch (err) {
        aiDiv.classList.remove('typing-indicator');
        aiDiv.textContent = "Error connecting to server. Please try again.";
    }

    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

document.addEventListener('DOMContentLoaded', () => {
    handleInputToggle();
    setupLiveChatToggle(); // Live chat handler load hone par activate hoga
    
    const input = document.getElementById('msgInput');
    if (input) {
        input.addEventListener('input', handleInputToggle);
    }
});
