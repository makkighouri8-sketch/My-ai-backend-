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
    <title>Tringo AI</title>
    <!-- Three.js & GLTFLoader for 3D Studio -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        body { width: 100vw; height: 100vh; background: #000; color: #fff; font-family: sans-serif; overflow: hidden; display: flex; flex-direction: column; }
        
        /* TOP NAVIGATION TABS */
        .top-nav { display: flex; padding: 12px; gap: 10px; background: #000; z-index: 10; }
        .nav-btn { flex: 1; padding: 10px; background: #141414; border: 1px solid #262626; border-radius: 20px; color: #888; font-weight: bold; cursor: pointer; text-align: center; }
        .nav-btn.active { color: #fff; background: #222; border-color: #d037fd; }

        /* TAB CONTENTS */
        .tab-content { flex: 1; display: none; flex-direction: column; align-items: center; justify-content: flex-start; padding: 16px; overflow-y: auto; padding-bottom: 90px; }
        .tab-content.active-tab { display: flex; }

        .greeting { font-size: 1.4rem; font-weight: bold; margin-top: 10px; margin-bottom: 6px; }
        .subtext { font-size: 0.85rem; color: #666; margin-bottom: 20px; text-align: center; }
        .chat-box { width: 100%; max-width: 500px; color: #ccc; text-align: center; margin-bottom: 20px; font-size: 0.95rem; word-break: break-word; }

        /* 3D CANVAS & STUDIO LAYOUT */
        #canvas3d-container {
            width: 100%;
            height: 320px;
            background: #0a0a0a;
            border-radius: 16px;
            border: 1px solid #222;
            position: relative;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .studio-controls {
            width: 100%;
            max-width: 500px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .action-btn {
            padding: 12px;
            background: #141414;
            border: 1px solid #333;
            border-radius: 12px;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
        }
        .action-btn:active { background: #222; }

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
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
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

        /* MIC BUTTON WITH PURPLE WAVES */
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
        <div class="greeting">🎬 3D Video Studio</div>
        <div class="subtext">Interactive 3D Avatar & Workspace</div>

        <!-- 3D Canvas Viewport -->
        <div id="canvas3d-container"></div>

        <div class="studio-controls">
            <button class="action-btn" onclick="rotateAvatar()">🔄 Rotate 3D Model</button>
            <button class="action-btn" onclick="resetView()">🎯 Reset View</button>
        </div>
    </div>

    <script>
        let isWaveActive = false;
        let scene, camera, renderer, model;

        function switchTab(t) {
            document.getElementById('chatTab').classList.toggle('active-tab', t === 'chat');
            document.getElementById('studioTab').classList.toggle('active-tab', t === 'studio');
            document.getElementById('chatBtn').classList.toggle('active', t === 'chat');
            document.getElementById('studioBtn').classList.toggle('active', t === 'studio');

            if (t === 'studio' && !scene) {
                init3DStudio();
            }
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

        /* THREE.JS 3D AVATAR STUDIO INIT */
        function init3DStudio() {
            const container = document.getElementById('canvas3d-container');
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a);

            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 1.2, 3);

            const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xd037fd, 2);
            dirLight.position.set(2, 4, 2);
            scene.add(dirLight);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            const loader = new THREE.GLTFLoader();
            loader.load('/public/avatar.glb', (gltf) => {
                model = gltf.scene;
                model.position.set(0, 0, 0);
                scene.add(model);
            }, undefined, (err) => {
                console.log("Loading fallback cube model");
                const geo = new THREE.BoxGeometry(1, 1, 1);
                const mat = new THREE.MeshStandardMaterial({ color: 0xd037fd });
                model = new THREE.Mesh(geo, mat);
                scene.add(model);
            });

            function animate() {
                requestAnimationFrame(animate);
                if (model) model.rotation.y += 0.005;
                renderer.render(scene, camera);
            }
            animate();
        }

        function rotateAvatar() {
            if (model) model.rotation.y += 0.5;
        }

        function resetView() {
            if (model) model.rotation.set(0, 0, 0);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

app = app
