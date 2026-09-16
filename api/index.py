from flask import Flask, request, jsonify, render_template_string
import os
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background: #09090b;
            color: #f2f2f7;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .top-nav {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 12px 16px;
            background: #09090b;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            z-index: 10;
        }

        .nav-btn {
            background: transparent;
            border: none;
            color: #71717a;
            font-size: 14px;
            font-weight: 600;
            padding: 8px 18px;
            border-radius: 20px;
            cursor: pointer;
            transition: 0.2s;
        }

        .nav-btn.active {
            background: #27272a;
            color: #ffffff;
        }

        .main-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 16px;
            max-width: 650px;
            margin: 0 auto;
            width: 100%;
            overflow-y: auto;
        }

        .tab-content {
            display: none;
            flex-direction: column;
            flex: 1;
        }

        .active-tab {
            display: flex;
        }

        .greeting {
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }

        .subtext {
            font-size: 13px;
            color: #71717a;
            margin-bottom: 20px;
        }

        .chat-box {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 12px;
            overflow-y: auto;
            padding-bottom: 90px;
        }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14.5px;
            line-height: 1.45;
            word-wrap: break-word;
        }

        .ai-message {
            background: #18181b;
            color: #e4e4e7;
            align-self: flex-start;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-top-left-radius: 4px;
        }

        .user-message {
            background: #2563eb;
            color: #ffffff;
            align-self: flex-end;
            border-top-right-radius: 4px;
        }

        /* DYNAMIC CAPSULE DOCK */
        .dock-wrapper {
            position: fixed;
            bottom: 14px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: center;
            padding: 0 14px;
            z-index: 100;
        }

        .gemini-dock {
            width: 100%;
            max-width: 600px;
            background: #1e1f23;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 28px;
            padding: 6px 8px 6px 14px;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 6px 30px rgba(0, 0, 0, 0.6);
        }

        .icon-btn {
            background: transparent;
            border: none;
            color: #9aa0a6;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            flex-shrink: 0;
            transition: background 0.2s, transform 0.15s;
        }

        .icon-btn:active {
            background: rgba(255, 255, 255, 0.1);
            transform: scale(0.92);
        }

        .icon-btn svg {
            width: 20px;
            height: 20px;
            fill: #9aa0a6;
        }

        .dock-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #ffffff;
            font-size: 15px;
            padding: 8px 0;
            min-width: 0;
        }

        .dock-input::placeholder {
            color: #80868b;
        }

        /* DYNAMIC VISIBILITY CONTROLS */
        .voice-group {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .send-btn {
            display: none; /* Initially hidden */
            background: #2563eb;
            border: none;
            border-radius: 50%;
            width: 38px;
            height: 38px;
            cursor: pointer;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: transform 0.1s;
        }

        .send-btn:active {
            transform: scale(0.95);
        }

        .send-btn svg {
            width: 18px;
            height: 18px;
            fill: #ffffff;
            margin-left: 2px;
        }

        .studio-card {
            background: #18181b;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 16px;
        }

        .studio-input {
            width: 100%;
            height: 120px;
            background: #09090b;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            padding: 12px;
            border-radius: 14px;
            resize: none;
            outline: none;
            font-size: 14px;
            margin-bottom: 12px;
        }

        .gen-btn {
            width: 100%;
            padding: 14px;
            background: #2563eb;
            border: none;
            color: #ffffff;
            font-weight: bold;
            border-radius: 25px;
            cursor: pointer;
            font-size: 15px;
        }
    </style>
</head>
<body>

    <div class="top-nav">
        <button class="nav-btn active" id="btnChat" onclick="switchTab('chatTab')">AI Chat</button>
        <button class="nav-btn" id="btnStudio" onclick="switchTab('studioTab')">3D Video Studio</button>
    </div>

    <div class="main-container">
        <!-- AI CHAT TAB -->
        <div id="chatTab" class="tab-content active-tab">
            <h1 class="greeting">Hi Jamshed,</h1>
            <p class="subtext">Ask or speak anything to Tringo AI!</p>

            <div class="chat-box" id="chatBox">
                <div class="message ai-message">Hello Jamshed! How can I help you today?</div>
            </div>
        </div>

        <!-- 3D STUDIO TAB -->
        <div id="studioTab" class="tab-content">
            <h1 class="greeting">3D Studio</h1>
            <p class="subtext">Generate high quality 3D Videos & Animations</p>

            <div class="studio-card">
                <textarea class="studio-input" id="promptInput" placeholder="Describe the 3D scene you want to generate..."></textarea>
                <button class="gen-btn" onclick="alert('3D Studio feature coming soon!')">⚡ Generate 3D Video</button>
            </div>
        </div>
    </div>

    <!-- DYNAMIC GEMINI INPUT CAPSULE -->
    <div class="dock-wrapper" id="dockWrapper">
        <div class="gemini-dock">
            <!-- Add Button -->
            <button class="icon-btn" title="Add File">
                <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            </button>
            
            <!-- Dynamic Input Box -->
            <input type="text" class="dock-input" id="msgInput" placeholder="Message Tringo AI..." oninput="handleInputToggle()" onkeypress="handleKeyPress(event)">
            
            <!-- Voice Group (Visible when Empty) -->
            <div class="voice-group" id="voiceGroup">
                <!-- Voice to Text Mic Button -->
                <button class="icon-btn" onclick="toggleVoiceInput()" title="Voice to Text">
                    <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                </button>

                <!-- Live Voice Chat Wave Button -->
                <button class="icon-btn" onclick="alert('Live Voice Mode Active')" title="Live Voice Chat">
                    <svg viewBox="0 0 24 24"><path d="M12 3v18m-4-14v10m8-10v10m-12-6v2m16-2v2" stroke="#9aa0a6" stroke-width="2.2" stroke-linecap="round"/></svg>
                </button>
            </div>

            <!-- Send Button (Visible when Typing) -->
            <button class="send-btn" id="sendBtn" onclick="sendMessage()" title="Send">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </div>

    <script>
        function handleInputToggle() {
            const input = document.getElementById("msgInput");
            const voiceGroup = document.getElementById("voiceGroup");
            const sendBtn = document.getElementById("sendBtn");

            if (input.value.trim().length > 0) {
                voiceGroup.style.display = "none";
                sendBtn.style.display = "flex";
            } else {
                voiceGroup.style.display = "flex";
                sendBtn.style.display = "none";
            }
        }

        function switchTab(tabId) {
            document.getElementById('chatTab').classList.remove('active-tab');
            document.getElementById('studioTab').classList.remove('active-tab');
            document.getElementById('btnChat').classList.remove('active');
            document.getElementById('btnStudio').classList.remove('active');

            if(tabId === 'chatTab') {
                document.getElementById('chatTab').classList.add('active-tab');
                document.getElementById('btnChat').classList.add('active');
                document.getElementById('dockWrapper').style.display = 'flex';
            } else {
                document.getElementById('studioTab').classList.add('active-tab');
                document.getElementById('btnStudio').classList.add('active');
                document.getElementById('dockWrapper').style.display = 'none';
            }
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') sendMessage();
        }

        async function sendMessage() {
            const input = document.getElementById("msgInput");
            const text = input.value.trim();
            if (!text) return;

            const chatBox = document.getElementById("chatBox");
            chatBox.innerHTML += `<div class="message user-message">${text}</div>`;
            input.value = "";
            handleInputToggle();
            chatBox.scrollTop = chatBox.scrollHeight;

            const loadingId = "load_" + Date.now();
            chatBox.innerHTML += `<div class="message ai-message" id="${loadingId}">Thinking...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                document.getElementById(loadingId).innerText = data.reply;
            } catch (err) {
                document.getElementById(loadingId).innerText = "Server Error. Please try again.";
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function toggleVoiceInput() {
            if (!('webkitSpeechRecognition' in window)) {
                alert("Voice recognition is not supported on this browser.");
                return;
            }
            const rec = new webkitSpeechRecognition();
            rec.lang = 'en-US';
            rec.start();
            rec.onresult = function(e) {
                document.getElementById("msgInput").value = e.results[0][0].transcript;
                handleInputToggle();
                sendMessage();
            };
        }
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.json
        user_message = data.get("message", "")
        
        if not GEMINI_API_KEY:
            return jsonify({"reply": "API Key missing in environment variables!"})

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_message)
        
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run()
