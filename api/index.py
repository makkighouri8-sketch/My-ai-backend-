from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    <title>Tringo AI Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        body { width: 100vw; height: 100vh; background: #000; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; overflow: hidden; display: flex; flex-direction: column; }
        
        /* TOP NAVIGATION TABS */
        .top-nav { display: flex; padding: 12px; gap: 10px; background: #000; z-index: 10; border-bottom: 1px solid #1a1a1a; }
        .nav-btn { flex: 1; padding: 10px; background: #121212; border: 1px solid #262626; border-radius: 20px; color: #888; font-weight: 600; cursor: pointer; text-align: center; font-size: 0.9rem; transition: all 0.2s; }
        .nav-btn.active { color: #fff; background: #1a1a1a; border-color: #a855f7; box-shadow: 0 0 10px rgba(168, 85, 247, 0.2); }

        /* TAB CONTENTS */
        .tab-content { flex: 1; display: none; flex-direction: column; align-items: center; justify-content: flex-start; padding: 16px; overflow-y: auto; padding-bottom: 90px; }
        .tab-content.active-tab { display: flex; }

        .greeting { font-size: 1.4rem; font-weight: 700; margin-top: 10px; margin-bottom: 4px; text-align: center; }
        .subtext { font-size: 0.85rem; color: #777; margin-bottom: 20px; text-align: center; }
        .chat-box { width: 100%; max-width: 500px; color: #ccc; text-align: center; margin-bottom: 20px; font-size: 0.95rem; word-break: break-word; }

        /* 3D STUDIO CARDS */
        .studio-container { width: 100%; max-width: 500px; display: flex; flex-direction: column; gap: 20px; }
        
        .studio-card { 
            background: #0d0d0d; 
            border: 1px solid #222; 
            border-radius: 18px; 
            padding: 18px; 
            display: flex; 
            flex-direction: column; 
            gap: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            transition: border-color 0.3s;
        }
        .studio-card:focus-within { border-color: #a855f7; }

        .card-header { display: flex; align-items: center; gap: 10px; }
        .card-title { font-weight: 700; font-size: 1.05rem; color: #fff; }
        .card-desc { font-size: 0.8rem; color: #777; line-height: 1.3; }

        .studio-input {
            width: 100%;
            background: #141414;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 12px;
            color: #fff;
            font-size: 0.88rem;
            outline: none;
            resize: none;
            font-family: inherit;
        }
        .studio-input:focus { border-color: #a855f7; }

        .upload-area {
            border: 2px dashed #2a2a2a;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            background: #121212;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
        }
        .upload-area:hover { border-color: #a855f7; background: #161616; }
        .upload-area svg { width: 28px; height: 28px; fill: #888; }
        .upload-text { font-size: 0.8rem; color: #888; }

        .gen-btn {
            background: linear-gradient(135deg, #a855f7, #d037fd);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 12px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
            transition: opacity 0.2s;
        }
        .gen-btn:active { opacity: 0.8; }

        /* BOTTOM CHAT INPUT BAR */
        .bottom-bar { 
            position: fixed; 
            bottom: 12px; 
            left: 0; 
            width: 100%; 
            padding: 0 10px; 
            display: flex; 
            align-items: flex-end; 
            gap: 6px; 
            z-index: 100;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
        }

        .input-box { 
            flex: 1; 
            display: flex; 
            align-items: center; 
            background: #121212; 
            border: 1px solid #282828; 
            border-radius: 20px; 
            padding: 6px 8px 6px 12px; 
            gap: 6px; 
            min-width: 0; 
        }

        .input-box textarea { 
            flex: 1; 
            background: transparent; 
            border: none; 
            outline: none; 
            color: #fff; 
            font-size: 0.9rem; 
            font-family: inherit; 
            resize: none; 
            height: 24px; 
            max-height: 120px; 
            line-height: 20px; 
            overflow-y: auto; 
        }

        .mic-btn { 
            width: 30px; 
            height: 30px; 
            border-radius: 50%; 
            background: #222; 
            border: 1px solid #444; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            cursor: pointer; 
            flex-shrink: 0; 
            position: relative;
            transition: all 0.3s ease;
        }

        .mic-btn svg { width: 16px; height: 16px; fill: #fff; z-index: 2; }

        .mic-btn.active {
            background: #222;
            border-color: #a855f7;
            animation: mic-wave-pulse 1.2s infinite ease-in-out;
        }

        @keyframes mic-wave-pulse {
            0% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.8), 0 0 0 0 rgba(208, 55, 253, 0.5); }
            70% { box-shadow: 0 0 0 10px rgba(168, 85, 247, 0), 0 0 0 20px rgba(208, 55, 253, 0); }
            100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0), 0 0 0 0 rgba(208, 55, 253, 0); }
        }

        .wave-btn { 
            width: 32px; 
            height: 32px; 
            border-radius: 50%; 
            background: #a855f7; 
            border: none; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            cursor: pointer; 
            flex-shrink: 0;
            transition: all 0.3s ease;
        }
        .wave-btn svg { width: 16px; height: 16px; stroke: #fff; }

        .wave-btn.listening {
            animation: pulse-wave 1.2s infinite ease-in-out;
            background: linear-gradient(135deg, #d037fd, #a855f7);
        }

        @keyframes pulse-wave {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(208, 55, 253, 0.7); }
            50% { transform: scale(1.15); box-shadow: 0 0 0 10px rgba(208, 55, 253, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(208, 55, 253, 0); }
        }

        .send-btn { width: 38px; height: 38px; background: #222; border: 1px solid #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; cursor: pointer; margin-bottom: 2px; }
        .send-btn svg { width: 16px; height: 16px; fill: #fff; margin-left: 2px; }
    </style>
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
        <div class="greeting">✨ 3D Studio Generator</div>
        <div class="subtext">Generate high quality 3D Videos & Animations</div>

        <div class="studio-container">
            <!-- SECTION 1: 3D VIDEO CREATOR -->
            <div class="studio-card">
                <div class="card-header">
                    <span style="font-size:1.4rem;">🎥</span>
                    <div>
                        <div class="card-title">3D Video Generator</div>
                        <div class="card-desc">Create 3D cinematic videos from text prompt</div>
                    </div>
                </div>
                <textarea class="studio-input" rows="3" placeholder="Describe the 3D scene you want to generate... (e.g. A futuristic cyberpunk city in 3D animation)"></textarea>
                <button class="gen-btn" onclick="alert('Generating 3D Video...')">
                    ⚡ Generate 3D Video
                </button>
            </div>

            <!-- SECTION 2: PIC TO 3D ANIMATION -->
            <div class="studio-card">
                <div class="card-header">
                    <span style="font-size:1.4rem;">🖼️</span>
                    <div>
                        <div class="card-title">Pic to 3D Animation</div>
                        <div class="card-desc">Convert flat photos into 3D animated motions</div>
                    </div>
                </div>
                
                <input type="file" id="imgUpload" accept="image/*" style="display:none;" onchange="previewImage(this)">
                <div class="upload-area" onclick="document.getElementById('imgUpload').click()">
                    <svg viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/></svg>
                    <div class="upload-text" id="uploadStatus">Click or tap to upload photo</div>
                </div>

                <textarea class="studio-input" rows="2" placeholder="Optional motion instructions (e.g. Make hair blow in the wind, add 3D camera pan)"></textarea>
                
                <button class="gen-btn" onclick="alert('Converting Photo to 3D Animation...')">
                    ✨ Animate Photo to 3D
                </button>
            </div>
        </div>
    </div>

    <script>
        let isWaveActive = false;

        function switchTab(t) {
            document.getElementById('chatTab').classList.toggle('active-tab', t === 'chat');
            document.getElementById('studioTab').classList.toggle('active-tab', t === 'studio');
            document.getElementById('chatBtn').classList.toggle('active', t === 'chat');
            document.getElementById('studioBtn').classList.toggle('active', t === 'studio');
        }

        function autoResize(textarea) {
            textarea.style.height = '24px';
            textarea.style.height = (textarea.scrollHeight > 120 ? 120 : textarea.scrollHeight) + 'px';
        }

        function startDictation(event) {
            if (event) event.preventDefault();
            const input = document.getElementById('msgInput');
            const micBtn = document.getElementById('micBtn');

            if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
                return alert('Voice recognition not supported');
            }

            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SR();

            rec.onstart = () => micBtn.classList.add('active');
            rec.onresult = (e) => { input.value = e.results[0][0].transcript; autoResize(input); };
            rec.onend = () => { micBtn.classList.remove('active'); input.focus(); };

            rec.start();
            input.focus();
        }

        function toggleLiveWave() {
            const waveBtn = document.getElementById('waveBtn');
            isWaveActive = !isWaveActive;
            waveBtn.classList.toggle('listening', isWaveActive);
        }

        function sendMsg() {
            const input = document.getElementById('msgInput');
            const val = input.value.trim();
            if (val) {
                document.getElementById('chatDisplay').textContent = "You: " + val;
                input.value = ''; 
                input.style.height = '24px';
            }
        }

        function previewImage(input) {
            if (input.files && input.files[0]) {
                document.getElementById('uploadStatus').textContent = "Selected: " + input.files[0].name;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

app = app
