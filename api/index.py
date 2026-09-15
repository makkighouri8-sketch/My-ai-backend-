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
        
        .top-nav { display: flex; padding: 12px; gap: 10px; background: #000; z-index: 10; border-bottom: 1px solid #1a1a1a; }
        .nav-btn { flex: 1; padding: 10px; background: #121212; border: 1px solid #262626; border-radius: 20px; color: #888; font-weight: 600; cursor: pointer; text-align: center; font-size: 0.9rem; transition: all 0.2s; }
        .nav-btn.active { color: #fff; background: #1a1a1a; border-color: #a855f7; box-shadow: 0 0 10px rgba(168, 85, 247, 0.2); }

        .tab-content { flex: 1; display: none; flex-direction: column; align-items: center; justify-content: flex-start; padding: 16px; overflow-y: auto; padding-bottom: 90px; position: relative; }
        .tab-content.active-tab { display: flex; }

        .greeting { font-size: 1.4rem; font-weight: 700; margin-top: 10px; margin-bottom: 4px; text-align: center; }
        .subtext { font-size: 0.85rem; color: #777; margin-bottom: 20px; text-align: center; }
        .chat-box { width: 100%; max-width: 500px; color: #ccc; text-align: center; margin-bottom: 20px; font-size: 0.95rem; word-break: break-word; z-index: 2; }

        /* CIRCULAR NEON VOICE WAVES OVERLAY */
        .live-overlay {
            position: absolute;
            top: 45%;
            left: 50%;
            transform: translate(-50%, -50%);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 5;
        }
        .live-overlay.active { display: flex; }

        .neon-circle-container {
            position: relative;
            width: 140px;
            height: 140px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .neon-wave {
            position: absolute;
            border-radius: 50%;
            border: 2px solid #a855f7;
            box-shadow: 0 0 15px #a855f7, inset 0 0 15px #a855f7;
            animation: neon-pulse 2s infinite ease-out;
            opacity: 0;
        }

        .neon-wave:nth-child(1) { width: 60px; height: 60px; animation-delay: 0s; }
        .neon-wave:nth-child(2) { width: 100px; height: 100px; animation-delay: 0.6s; }
        .neon-wave:nth-child(3) { width: 140px; height: 140px; animation-delay: 1.2s; }

        .center-glow-orb {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #a855f7, #d037fd);
            box-shadow: 0 0 25px #d037fd;
            z-index: 2;
            animation: orb-bounce 1.2s infinite alternate ease-in-out;
        }

        @keyframes neon-pulse {
            0% { transform: scale(0.4); opacity: 0.9; }
            80% { opacity: 0.4; }
            100% { transform: scale(1.4); opacity: 0; }
        }

        @keyframes orb-bounce {
            0% { transform: scale(0.95); box-shadow: 0 0 15px #a855f7; }
            100% { transform: scale(1.1); box-shadow: 0 0 30px #d037fd; }
        }

        .live-status-text {
            margin-top: 25px;
            font-size: 0.9rem;
            color: #d037fd;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-shadow: 0 0 8px rgba(208, 55, 253, 0.6);
        }

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

        .card-header { display: flex; align-items: center; gap: 12px; }
        
        /* WHITE OUTLINE ICONS */
        .header-icon {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.4);
            flex-shrink: 0;
        }
        .header-icon svg { width: 20px; height: 20px; stroke: #ffffff; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

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
            padding: 16px;
            text-align: center;
            background: #121212;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            min-height: 120px;
            position: relative;
            overflow: hidden;
        }
        .upload-area:hover { border-color: #a855f7; background: #161616; }
        .upload-icon-svg { width: 28px; height: 28px; stroke: #888; fill: none; stroke-width: 2; }
        .upload-text { font-size: 0.8rem; color: #888; }

        .preview-wrapper {
            position: relative;
            width: 100%;
            display: none;
            align-items: center;
            justify-content: center;
        }

        .img-preview {
            width: 100%;
            max-height: 180px;
            object-fit: contain;
            border-radius: 8px;
        }

        .remove-btn {
            position: absolute;
            top: 6px;
            right: 6px;
            width: 26px;
            height: 26px;
            background: rgba(0, 0, 0, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            color: #fff;
            font-size: 14px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 5;
            transition: background 0.2s;
        }
        .remove-btn:hover { background: #ff3b30; border-color: #ff3b30; }

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

        /* BOTTOM INPUT BAR */
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
            transition: all 0.2s ease;
        }

        .mic-btn svg { width: 16px; height: 16px; fill: #fff; }
        .mic-btn.active { border-color: #a855f7; background: #333; }

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
            background: linear-gradient(135deg, #d037fd, #a855f7);
            box-shadow: 0 0 12px rgba(208, 55, 253, 0.8);
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
            <!-- SECTION 1: 3D VIDEO CREATOR -->
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
                <textarea class="studio-input" rows="3" placeholder="Describe the 3D scene you want to generate... (e.g. A futuristic cyberpunk city in 3D animation)"></textarea>
                <button class="gen-btn" onclick="alert('Generating 3D Video...')">
                    ⚡ Generate 3D Video
                </button>
            </div>

            <!-- SECTION 2: PIC TO 3D ANIMATION -->
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

        /* TOGGLE CIRCULAR NEON VOICE WAVES */
        function toggleLiveWave() {
            const waveBtn = document.getElementById('waveBtn');
            const liveOverlay = document.getElementById('liveOverlay');
            
            isWaveActive = !isWaveActive;
            waveBtn.classList.toggle('listening', isWaveActive);
            liveOverlay.classList.toggle('active', isWaveActive);
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

        function triggerUpload(e) {
            if (e.target.classList.contains('remove-btn')) return;
            document.getElementById('imgUpload').click();
        }

        function previewImage(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.getElementById('imgPreview');
                    img.src = e.target.result;
                    document.getElementById('previewWrapper').style.display = 'flex';
                    document.getElementById('uploadIcon').style.display = 'none';
                    document.getElementById('uploadText').style.display = 'none';
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function removeImage(e) {
            e.stopPropagation();
            const fileInput = document.getElementById('imgUpload');
            fileInput.value = '';
            document.getElementById('imgPreview').src = '';
            document.getElementById('previewWrapper').style.display = 'none';
            document.getElementById('uploadIcon').style.display = 'block';
            document.getElementById('uploadText').style.display = 'block';
        }
    </script>
</body>
</html>
