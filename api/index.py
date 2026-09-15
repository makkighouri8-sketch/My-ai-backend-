from flask import Flask, send_from_directory, render_template_string, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__, static_folder='..')

# Gemini API Setup (Pehle se set API key env se uthayega ya fallback)
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
    <link rel="stylesheet" href="/style.css">
    <link rel="stylesheet" href="/animations.css">
</head>
<body>
    <!-- LOGIN MODAL -->
    <div id="loginModal" class="login-modal">
        <div class="login-box">
            <h2>Welcome to Tringo AI</h2>
            <p>Enter your name to start conversation</p>
            <input type="text" id="userNameInput" placeholder="Enter your name (e.g. Jamshed)">
            <button onclick="handleLogin()" class="login-btn">Start Chatting</button>
        </div>
    </div>

    <!-- MAIN APP WRAPPER -->
    <div class="app-container">
        
        <!-- SIDEBAR FOR CHAT HISTORY -->
        <div class="sidebar" id="sidebar">
            <button class="new-chat-btn" onclick="startNewChat()">+ New Chat</button>
            <div class="history-list" id="historyList">
                <div class="history-item active">Current Conversation</div>
            </div>
            <div class="user-profile">
                <span id="userDisplayName">Guest</span>
            </div>
        </div>

        <!-- MAIN CONTENT AREA -->
        <div class="main-content">
            <!-- TOP NAVIGATION -->
            <div class="top-nav">
                <button class="toggle-sidebar" onclick="toggleSidebar()">☰</button>
                <button class="nav-btn active" onclick="switchTab('chatTab')">AI Chat</button>
                <button class="nav-btn" onclick="switchTab('studioTab')">3D Video Studio</button>
            </div>

            <!-- AI CHAT TAB -->
            <div id="chatTab" class="tab-content active-tab">
                <h1 class="greeting" id="welcomeText">Hi Jamshed,</h1>
                <p class="subtext">Ask or speak anything to Tringo AI!</p>
                
                <div class="chat-box" id="chatBox">
                    <div class="message ai-message">Hello! How can I assist you today?</div>
                </div>

                <div class="bottom-bar">
                    <div class="input-box">
                        <textarea id="msgInput" placeholder="Message Tringo AI..." rows="1"></textarea>
                        <button class="mic-btn" id="micBtn" onclick="toggleVoiceInput()" title="Voice Input">
                            <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                        </button>
                    </div>
                    <button class="send-btn" id="sendBtn" onclick="sendMessage()">
                        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                    </button>
                </div>
            </div>

            <!-- 3D STUDIO TAB -->
            <div id="studioTab" class="tab-content">
                <h1 class="greeting">3D Studio Generator</h1>
                <p class="subtext">Generate high quality 3D Videos & Animations</p>

                <div class="studio-container">
                    <div class="studio-card">
                        <div class="card-header">
                            <div class="card-title">3D Video Generator</div>
                        </div>
                        <textarea class="studio-input" id="promptInput" placeholder="Describe the 3D scene you want to generate..."></textarea>
                        <button class="gen-btn" id="genBtn" onclick="generate3DVideo()">⚡ Generate 3D Video</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/app.js"></script>
    <script src="/ai-engine.js"></script>
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
            return jsonify({"reply": "API Key not configured on Vercel environment variables!"})

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_message)
        
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, '..'), filename)

if __name__ == '__main__':
    app.run()
    
