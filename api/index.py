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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tringo AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background: #09090b;
            color: #f2f2f7;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .top-nav {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 14px 16px;
            background: #09090b;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .nav-btn {
            background: transparent;
            border: none;
            color: #71717a;
            font-size: 14px;
            font-weight: 600;
            padding: 8px 20px;
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
            max-width: 600px;
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
            margin-bottom: 16px;
        }

        .chat-box {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 12px;
            overflow-y: auto;
            padding-bottom: 80px;
        }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
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

        /* GEMINI CAPSULE BOTTOM DOCK */
        .bottom-dock {
            position: fixed;
            bottom: 12px;
            left: 50%;
            transform: translateX(-50%);
            width: 92%;
            max-width: 580px;
            background: #1e1f23;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 30px;
            padding: 6px 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 25px rgba(0,0,0,0.6);
            z-index: 100;
        }

        .dock-btn {
            background: transparent;
            border: none;
            color: #9aa0a6;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            padding: 6px;
        }

        .dock-btn svg {
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
            padding: 6px 0;
        }

        .send-btn {
            background: #2563eb;
            border: none;
            border-radius: 50%;
            width: 38px;
            height: 38px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .send-btn svg {
            width: 18px;
            height: 18px;
            fill: #ffffff;
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
                <div class="message ai-message">Hello Jamshed! How can I assist you today?</div>
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

    <!-- FIXED GEMINI INPUT DOCK -->
    <div class="bottom-dock" id="bottomDock">
        <button class="dock-btn" title="Add attachment">
            <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
        </button>
        <input type="text" class="dock-input" id="msgInput" placeholder="Message Tringo AI..." onkeypress="handleKeyPress(event)">
        <button class="dock-btn" onclick="toggleVoiceInput()" title="Voice input">
            <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
        </button>
        <button class="send-btn" onclick="sendMessage()" title="Send Message">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
    </div>

    <script>
        function switchTab(tabId) {
            document.getElementById('chatTab').classList.remove('active-tab');
            document.getElementById('studioTab').classList.remove('active-tab');
            document.getElementById('btnChat').classList.remove('active');
            document.getElementById('btnStudio').classList.remove('active');

            if(tabId === 'chatTab') {
                document.getElementById('chatTab').classList.add('active-tab');
                document.getElementById('btnChat').classList.add('active');
                document.getElementById('bottomDock').style.display = 'flex';
            } else {
                document.getElementById('studioTab').classList.add('active-tab');
                document.getElementById('btnStudio').classList.add('active');
                document.getElementById('bottomDock').style.display = 'none';
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
                alert("Voice recognition not supported in this browser");
                return;
            }
            const rec = new webkitSpeechRecognition();
            rec.lang = 'en-US';
            rec.start();
            rec.onresult = function(e) {
                document.getElementById("msgInput").value = e.results[0][0].transcript;
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
    
