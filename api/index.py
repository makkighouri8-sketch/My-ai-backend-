from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__, static_folder='..')

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
    <!-- TOP NAVIGATION -->
    <div class="top-nav">
        <button class="nav-btn active" onclick="switchTab('chatTab')">AI Chat</button>
        <button class="nav-btn" onclick="switchTab('studioTab')">3D Video Studio</button>
    </div>

    <!-- AI CHAT TAB -->
    <div id="chatTab" class="tab-content active-tab">
        <h1 class="greeting">Hi Jamshed,</h1>
        <p class="subtext">Ask or speak anything to Tringo AI!</p>
        
        <div class="chat-box" id="chatBox">
            <div class="message ai-message">Hello Jamshed! How can I assist you today?</div>
        </div>

        <div class="bottom-bar">
            <div class="input-box">
                <textarea id="msgInput" placeholder="Message Tringo AI..." rows="1"></textarea>
                <button class="mic-btn" id="micBtn" title="Voice Input">
                    <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                </button>
                <button class="wave-btn" id="waveBtn" title="Live Wave">
                    <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>
                </button>
            </div>
            <button class="send-btn" id="sendBtn">
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
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H9l2 4H8L6 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/></svg>
                    </div>
                    <div>
                        <div class="card-title">3D Video Generator</div>
                        <div class="card-desc">Create 3D cinematic videos from text prompt</div>
                    </div>
                </div>
                <textarea class="studio-input" id="promptInput" placeholder="Describe the 3D scene you want to generate..."></textarea>
                <button class="gen-btn" id="genBtn" onclick="generate3DVideo()">⚡ Generate 3D Video</button>
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

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, '..'), filename)

if __name__ == '__main__':
    app.run()
    
