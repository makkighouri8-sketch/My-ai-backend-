from flask import Flask, request, jsonify, render_template_string
import os
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
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
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        /* MAIN APP CONTAINER */
        .app-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            width: 100vw;
            background: #09090b;
        }

        /* TOP NAVIGATION */
        .top-nav {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 12px 16px;
            background: #09090b;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
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

        /* TAB CONTENT AREA */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px 16px;
            overflow: hidden;
            max-width: 600px;
            margin: 0 auto;
            width: 100%;
        }

        .tab-content {
            display: none;
            flex: 1;
            flex-direction: column;
            height: 100%;
        }

        .active-tab {
            display: flex;
        }

        .greeting {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }

        .subtext {
            font-size: 13px;
            color: #71717a;
            margin-bottom: 20px;
        }

        /* CHAT MESSAGES AREA */
        .chat-box {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding-bottom: 10px;
        }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
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

        /* GEMINI EXACT CAPSULE INPUT DOCK */
        .bottom-bar {
            padding: 10px 0 16px 0;
            background: #09090b;
        }

        .gemini-input-pill {
            display: flex;
            align-items: center;
            background: #1e1f23;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            padding: 6px 8px 6px 14px;
            gap: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }

        .plus-btn, .mic-btn {
            background: transparent;
            border: none;
            color: #9aa0a6;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            padding: 4px;
        }

        .plus-btn svg, .mic-btn svg {
            width: 22px;
            height: 22px;
            fill: #9aa0a6;
        }

        .gemini-input-pill input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #e8eaed;
            font-size: 15px;
        }

        .live-voice-btn {
            background: #2563eb;
            border: none;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .live-voice-btn svg {
            width: 18px;
            height: 18px;
            fill: #ffffff;
        }

        /* 3D STUDIO TAB STYLES */
        .studio-card {
            background: #18181b;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 16px;
        }

        .studio-input {
            width: 100%;
            height: 110px;
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

    <div class="app-container">
        <!-- TOP NAVIGATION -->
        <div class="top-nav">
            <button class="nav-btn active" id="btnChat" onclick="switchTab('chatTab')">AI Chat</button>
            <button class="nav-btn" id="btnStudio" onclick="switchTab('studioTab')">3D Video Studio</button>
        </div>

        <div class="main-content">
            <!-- AI CHAT TAB -->
            <div id="chatTab" class="tab-content active-tab">
                <h1 class="greeting">Hi Jamshed,</h1>
                <p class="subtext">Ask or speak anything to Tringo AI!</p>
                
                <div class="chat-box" id="chatBox">
                    <div class="message ai-message">Hello! How can I assist you today?</div>
                </div>

                <!-- GEMINI CAPSULE INPUT DOCK -->
                <div class="bottom-bar">
                    <div class="gemini-input-pill">
                        <button class="plus-btn" title="Add attachment">
                            <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                        </button>
                        <input type="text" id="msgInput" placeholder="Ask Tringo AI..." onkeypress="handleKeyPress(event)">
                        <button class="mic-btn" id="micBtn" onclick="toggleVoiceInput()" title="Voice input">
                            <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                        </button>
                        <button class="live-voice-btn" onclick="sendMessage()" title="Send Message">
                            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- 3D STUDIO TAB -->
            <div id="studioTab" class="tab-content">
                <h1 class="greeting">3D Studio</h1>
                <p class="subtext">Generate high quality 3D Videos & Animations</p>

                <div class="studio-card">
                    <textarea class="studio-input" id="promptInput" placeholder="Describe the 3D scene you want to generate..."></textarea>
                    <button class="gen-btn" onclick="generate3DVideo()">⚡ Generate 3D Video</button>
                </div>
            </div>
        </div>
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
            } else {
                document.getElementById('studioTab').classList.add('active-tab');
                document.getElementById('btnStudio').classList.add('active');
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
                alert("Voice recognition not supported");
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
</html>
"""

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
    
