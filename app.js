let currentUserName = localStorage.getItem("tringo_user") || "";
let chatHistory = JSON.parse(localStorage.getItem("tringo_history")) || [];

// Initialization
window.onload = function() {
    if (currentUserName) {
        document.getElementById("loginModal").style.display = "none";
        document.getElementById("userDisplayName").innerText = currentUserName;
        document.getElementById("welcomeText").innerText = `Hi ${currentUserName},`;
    }
    renderHistory();
};

function handleLogin() {
    const input = document.getElementById("userNameInput").value.trim();
    if (input) {
        currentUserName = input;
        localStorage.setItem("tringo_user", currentUserName);
        document.getElementById("loginModal").style.display = "none";
        document.getElementById("userDisplayName").innerText = currentUserName;
        document.getElementById("welcomeText").innerText = `Hi ${currentUserName},`;
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");
}

async function sendMessage() {
    const inputField = document.getElementById("msgInput");
    const message = inputField.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chatBox");

    // Add User Message
    chatBox.innerHTML += `<div class="message user-message">${message}</div>`;
    inputField.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Loading Indicator
    const loadingId = "load_" + Date.now();
    chatBox.innerHTML += `<div class="message ai-message" id="${loadingId}">Thinking...</div>`;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        
        document.getElementById(loadingId).innerText = data.reply;
        speakText(data.reply);
        
        // Save History
        chatHistory.push({ user: message, ai: data.reply });
        localStorage.setItem("tringo_history", JSON.stringify(chatHistory));
    } catch (err) {
        document.getElementById(loadingId).innerText = "Server Error. Please try again.";
    }
    
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Speech-to-Text (Voice Input)
function toggleVoiceInput() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Voice recognition not supported on this browser.");
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.start();

    document.getElementById("micBtn").classList.add("listening");

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("msgInput").value = transcript;
        document.getElementById("micBtn").classList.remove("listening");
        sendMessage();
    };

    recognition.onerror = function() {
        document.getElementById("micBtn").classList.remove("listening");
    };
}

// Text-to-Speech (Voice Reply)
function speakText(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
    }
}

function startNewChat() {
    document.getElementById("chatBox").innerHTML = `<div class="message ai-message">Hello ${currentUserName}! How can I assist you today?</div>`;
}

function renderHistory() {
    const list = document.getElementById("historyList");
    if (chatHistory.length > 0) {
        list.innerHTML = chatHistory.slice(-5).map(item => `<div class="history-item">${item.user.substring(0, 20)}...</div>`).join('');
    }
}
