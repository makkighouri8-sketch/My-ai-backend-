from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI Studio</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="stylesheet" href="/animations.css">
</head>
<body>
    <div class="top-nav">
        <button class="nav-btn active" id="chatBtn" onclick="switchTab('chat')">AI Chat</button>
        <button class="nav-btn" id="studioBtn" onclick="switchTab('studio')">3D Video Studio</button>
    </div>

    <!-- AI CHAT TAB -->
    <div class="tab-content active-tab" id="chatTab">
        <div class="greeting">Hi Jamshed,</div>
        <div class="subtext">Ask or speak anything to Tringo AI!</div>
        <div class="chat-box" id="chatDisplay">Type or speak your prompt...</div>

        <!-- NEON GOAL/CIRCULAR WAVES OVERLAY -->
        <div class="live-overlay" id="liveOverlay">
            <div class="neon-circle-container">
                <div class="neon-wave"></div>
                <div class="neon-wave"></div>
                <div class="neon-wave"></div>
                <div class="center-glow-orb"></div>
            </div>
            <div class="live-status-text">Tringo AI Listening...</div>
        </div>

        <div class="bottom-bar">
            <div class="input-box">
                <textarea id="msgInput" rows="1" placeholder="Message Tringo AI..." oninput="autoResize(this)"></textarea>
                
                <button class="mic-btn" id="micBtn" onclick="startDictation(event)" title="Voice to Text">
                    <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                </button>

                <button class="wave-btn" id="waveBtn" onclick="toggleLiveWave()" title="Live Voice">
                    <svg viewBox="0 0 24 24"><path d="M12 3v18M8 6v12M4 9v6M16 6v12M20 9v6" stroke-width="2.5" stroke-linecap="round"/></svg>
                </button>
            </div>

            <button class="send-btn" onclick="sendMsg()">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </div>

    <!-- 3D STUDIO TAB -->
    <div class="tab-content" id="studioTab">
        <div class="greeting">3D Studio Generator</div>
        <div class="subtext">Generate high quality 3D Videos & Animations</div>

        <div class="studio-container">
            <div class="studio-card">
                <div class="card-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
                    </div>
                    <div>
                        <div class="card-title">3D Video Generator</div>
                        <div class="card-desc">Create 3D cinematic videos from text prompt</div>
                    </div>
                </div>
                <textarea class="studio-input" rows="3" placeholder="Describe the 3D scene you want to generate..."></textarea>
                <button class="gen-btn" onclick="generate3DVideo('text')">⚡ Generate 3D Video</button>
            </div>

            <div class="studio-card">
                <div class="card-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                    </div>
                    <div>
                        <div class="card-title">Pic to 3D Animation</div>
                        <div class="card-desc">Convert flat photos into 3D animated motions</div>
                    </div>
                </div>
                
                <input type="file" id="imgUpload" accept="image/*" style="display:none;" onchange="previewImage(this)">
                
                <div class="upload-area" id="uploadArea" onclick="triggerUpload(event)">
                    <svg class="upload-icon-svg" id="uploadIcon" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                    <div class="upload-text" id="uploadText">Click or tap to upload photo</div>
                    
                    <div class="preview-wrapper" id="previewWrapper">
                        <span class="remove-btn" onclick="removeImage(event)" title="Remove Image">✕</span>
                        <img id="imgPreview" class="img-preview" alt="Preview">
                    </div>
                </div>

                <button class="gen-btn" onclick="generate3DVideo('pic')">✨ Animate Photo to 3D</button>
            </div>
        </div>
    </div>

    <script src="/app.js"></script>
    <script src="/ai-engine.js"></script>
</body>
</html>"""
        
        self.wfile.write(html_content.encode('utf-8'))
        return
        
