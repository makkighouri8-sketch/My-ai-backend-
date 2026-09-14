from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os
import requests
import base64
import time

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "r8_TjDtv9s6nWDFPGcuW7btlVAWCpY5qEk138nnF")

@app.route('/avatar.glb')
def serve_avatar():
    return send_from_directory(os.path.dirname(__file__), 'avatar.glb')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI Studio</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        html, body { width: 100%; height: 100%; background: #000000; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }

        /* Root Layout Fix: Forces full viewport screen, removing nested cards */
        .app-shell { display: flex; flex-direction: column; width: 100vw; height: 100vh; background: #000000; }

        /* Top Dynamic Navigation */
        .nav-header { display: flex; height: 60px; background: #090909; border-bottom: 1px solid #1f1f1f; flex-shrink: 0; z-index: 999; }
        .tab-btn { flex: 1; background: transparent; border: none; color: #777777; font-weight: 700; font-size: 0.95rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; border-bottom: 3px solid transparent; transition: all 0.2s ease; }
        .tab-btn.active { color: #ff2a5f; border-bottom: 3px solid #ff2a5f; background: rgba(255, 42, 95, 0.05); }

        /* Main Viewport Container */
        .viewport-container { flex: 1; position: relative; width: 100%; height: calc(100vh - 60px); overflow: hidden; }
        .view-panel { display: none; width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
        .view-panel.active { display: flex; flex-direction: column; }

        /* Panel 1: AI Chat Dashboard */
        #chatView { background: #000000; position: relative; }
        #canvas3D { width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 1; }
        .chat-subtitle { position: absolute; top: 20px; left: 5%; width: 90%; background: rgba(15, 15, 15, 0.85); backdrop-filter: blur(12px); border: 1px solid #2a2a2a; border-radius: 16px; padding: 14px 18px; text-align: center; font-size: 0.95rem; z-index: 10; color: #ffffff; box-shadow: 0 8px 32px rgba(0,0,0,0.8); }
        .chat-controls { position: absolute; bottom: 24px; left: 5%; width: 90%; display: flex; align-items: center; gap: 10px; z-index: 10; }
        .chat-input { flex: 1; height: 50px; background: rgba(18, 18, 18, 0.9); border: 1px solid #333333; border-radius: 25px; padding: 0 20px; color: #ffffff; font-size: 0.95rem; outline: none; }
        .chat-input:focus { border-color: #ff2a5f; }
        .btn-send { height: 50px; padding: 0 24px; background: #ff2a5f; border: none; border-radius: 25px; color: #ffffff; font-weight: 700; cursor: pointer; flex-shrink: 0; }
        .btn-mic { width: 50px; height: 50px; border-radius: 50%; background: #22c55e; border: none; color: #ffffff; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; }

        /* Panel 2: 3D Video Studio */
        #studioView { overflow-y: auto; padding: 20px 16px; background: #000000; }
        .studio-wrapper { max-width: 550px; margin: 0 auto; width: 100%; display: flex; flex-direction: column; gap: 20px; }
        .sub-nav { display: flex; background: #111111; padding: 6px; border-radius: 30px; border: 1px solid #222222; }
        .sub-tab-btn { flex: 1; padding: 12px; background: transparent; border: none; color: #888888; font-weight: 700; font-size: 0.85rem; border-radius: 24px; cursor: pointer; transition: all 0.2s; }
        .sub-tab-btn.active { background: #2563eb; color: #ffffff; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4); }

        .card-block { background: #0d0d0d; border: 1px solid #1f1f1f; border-radius: 20px; padding: 20px; }
        .card-block h3 { color: #ff2a5f; font-size: 1.05rem; margin-bottom: 14px; font-weight: 700; }
        .studio-textarea { width: 100%; height: 110px; background: #000000; border: 1px solid #2a2a2a; border-radius: 14px; padding: 14px; color: #ffffff; font-size: 0.9rem; resize: none; outline: none; margin-bottom: 14px; }
        
        .dropzone { border: 2px dashed #333333; background: #000000; border-radius: 14px; padding: 24px; text-align: center; cursor: pointer; margin-bottom: 14px; position: relative; min-height: 140px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; }
        .preview-img { width: 100%; max-height: 200px; object-fit: contain; border-radius: 10px; display: none; }
        .btn-remove { position: absolute; top: 10px; right: 10px; background: #ff2a5f; color: #ffffff; border: none; width: 28px; height: 28px; border-radius: 50%; font-weight: bold; cursor: pointer; display: none; z-index: 10; }

        .btn-action { width: 100%; padding: 14px; background: #2563eb; border: none; border-radius: 30px; color: #ffffff; font-weight: 700; font-size: 0.95rem; cursor: pointer; box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35); }
        .btn-action:disabled { background: #444444; cursor: not-allowed; box-shadow: none; }

        .spinner { border: 3px solid #1f1f1f; border-top: 3px solid #2563eb; border-radius: 50%; width: 30px; height: 30px; animation: spin 0.9s linear infinite; margin: 12px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

    <div class="app-shell">
        <!-- Top Navigation -->
        <div class="nav-header">
            <button class="tab-btn active" id="btnTabChat" onclick="openTab('chat')">AI Chat</button>
            <button class="tab-btn" id="btnTabStudio" onclick="openTab('studio')">3D Video Studio</button>
        </div>

        <div class="viewport-container">
            <!-- AI Chat Panel -->
            <div id="chatView" class="view-panel active">
                <div id="canvas3D"></div>
                <div class="chat-subtitle" id="subtitleText">Ask me anything or speak to Tringo!</div>
                <div class="chat-controls">
                    <button class="btn-mic" onclick="alert('Mic Active!')">🎙️</button>
                    <input type="text" id="chatInput" class="chat-input" placeholder="Message Tringo AI..." onkeypress="handleKeyPress(event)">
                    <button class="btn-send" onclick="sendChatMessage()">Send</button>
                </div>
            </div>

            <!-- 3D Video Studio Panel -->
            <div id="studioView" class="view-panel">
                <div class="studio-wrapper">
                    <div class="sub-nav">
                        <button class="sub-tab-btn active" id="btnSubText" onclick="openSubMode('text')">Prompt to 3D</button>
                        <button class="sub-tab-btn" id="btnSubPic" onclick="openSubMode('pic')">Pic to Animation</button>
                    </div>

                    <!-- Text Mode -->
                    <div class="card-block" id="cardTextMode">
                        <h3>Generate 3D Animation Video</h3>
                        <textarea class="studio-textarea" id="textPrompt" placeholder="Describe your 3D animation scene (e.g., A funny 3D character talking about finance in space)..."></textarea>
                        <button class="btn-action" id="btnGenText" onclick="processStudio('text')">Render 3D Video</button>
                    </div>

                    <!-- Image Mode -->
                    <div class="card-block" id="cardPicMode" style="display: none;">
                        <h3>Animate Image to 3D</h3>
                        <div class="dropzone" id="dropArea" onclick="document.getElementById('imgFile').click()">
                            <button class="btn-remove" id="btnRemoveImg" onclick="resetImage(event)">✕</button>
                            <div id="uploadContent">
                                <span style="color:#ffffff; font-weight: 600;">Tap to Upload Image</span>
                                <p style="color:#777777; font-size: 0.8rem; margin-top: 4px;">Select JPG/PNG photo</p>
                            </div>
                            <img id="imgPreview" class="preview-img" alt="Preview">
                            <input type="file" id="imgFile" accept="image/*" style="display:none;" onchange="handleImageUpload(this)">
                        </div>
                        <button class="btn-action" id="btnGenPic" onclick="processStudio('pic')">Animate Image</button>
                    </div>

                    <!-- Output & Loader Status -->
                    <div class="card-block" id="cardStatus" style="display: none;">
                        <h3>Generation Status</h3>
                        <div id="statusSpinner" class="spinner" style="display:none;"></div>
                        <p id="statusMsg" style="text-align:center; color:#888888; font-size:0.9rem;"></p>
                        <div id="mediaResult" style="margin-top:14px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedBase64Img = null;

        // Guaranteed Tab Switch Logic
        function openTab(tabName) {
            document.getElementById('btnTabChat').classList.remove('active');
            document.getElementById('btnTabStudio').classList.remove('active');
            document.getElementById('chatView').classList.remove('active');
            document.getElementById('studioView').classList.remove('active');

            if (tabName === 'chat') {
                document.getElementById('btnTabChat').classList.add('active');
                document.getElementById('chatView').classList.add('active');
                resizeRenderer();
            } else {
                document.getElementById('btnTabStudio').classList.add('active');
                document.getElementById('studioView').classList.add('active');
            }
        }

        // Sub-mode Switch Logic
        function openSubMode(mode) {
            document.getElementById('btnSubText').classList.remove('active');
            document.getElementById('btnSubPic').classList.remove('active');
            if (mode === 'text') {
                document.getElementById('btnSubText').classList.add('active');
                document.getElementById('cardTextMode').style.display = 'block';
                document.getElementById('cardPicMode').style.display = 'none';
            } else {
                document.getElementById('btnSubPic').classList.add('active');
                document.getElementById('cardTextMode').style.display = 'none';
                document.getElementById('cardPicMode').style.display = 'block';
            }
        }

        // Image Handling Functions
        function handleImageUpload(input) {
            const file = input.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedBase64Img = e.target.result;
                    document.getElementById('imgPreview').src = selectedBase64Img;
                    document.getElementById('imgPreview').style.display = 'block';
                    document.getElementById('uploadContent').style.display = 'none';
                    document.getElementById('btnRemoveImg').style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        }

        function resetImage(e) {
            e.stopPropagation();
            selectedBase64Img = null;
            document.getElementById('imgFile').value = '';
            document.getElementById('imgPreview').src = '';
            document.getElementById('imgPreview').style.display = 'none';
            document.getElementById('uploadContent').style.display = 'block';
            document.getElementById('btnRemoveImg').style.display = 'none';
        }

        // Video Studio API Caller
        async function processStudio(type) {
            const statusCard = document.getElementById('cardStatus');
            const statusMsg = document.getElementById('statusMsg');
            const spinner = document.getElementById('statusSpinner');
            const mediaResult = document.getElementById('mediaResult');

            statusCard.style.display = 'block';
            spinner.style.display = 'block';
            mediaResult.innerHTML = '';

            let bodyPayload = { type: type };

            if (type === 'text') {
                const promptVal = document.getElementById('textPrompt').value;
                if (!promptVal.trim()) return alert('Please write a prompt!');
                bodyPayload.prompt = promptVal;
                statusMsg.textContent = 'Rendering 3D Scene... (30-60 sec)';
            } else {
                if (!selectedBase64Img) return alert('Please upload an image!');
                bodyPayload.image = selectedBase64Img;
                statusMsg.textContent = 'Animating uploaded photo... (30-60 sec)';
            }

            try {
                const res = await fetch('/generate-3d', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodyPayload)
                });
                const data = await res.json();
                spinner.style.display = 'none';

                if (data.status === 'success' && data.video_url) {
                    statusMsg.textContent = 'Render Complete!';
                    mediaResult.innerHTML = `<video controls autoplay loop width="100%" style="border-radius:12px;"><source src="${data.video_url}" type="video/mp4"></video>`;
                } else {
                    statusMsg.textContent = 'Error: ' + (data.message || 'Generation failed.');
                }
            } catch (err) {
                spinner.style.display = 'none';
                statusMsg.textContent = 'Connection or Server Error!';
            }
        }

        // Three.js 3D Avatar Rendering with Safe Crash Guard
        let scene, camera, renderer, avatarMesh;
        function initThreeJS() {
            try {
                const holder = document.getElementById('canvas3D');
                scene = new THREE.Scene();
                camera = new THREE.PerspectiveCamera(45, holder.clientWidth / holder.clientHeight, 0.1, 1000);
                camera.position.set(0, 1.4, 1.4);

                renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                renderer.setSize(holder.clientWidth, holder.clientHeight);
                renderer.setClearColor(0x000000, 1);
                holder.appendChild(renderer.domElement);

                const light = new THREE.AmbientLight(0xffffff, 1.5);
                scene.add(light);

                const loader = new THREE.GLTFLoader();
                loader.load('/avatar.glb', function(gltf) {
                    avatarMesh = gltf.scene;
                    scene.add(avatarMesh);
                }, undefined, function() {
                    // Fallback visual mesh if avatar.glb is missing
                    const geom = new THREE.SphereGeometry(0.35, 32, 32);
                    const mat = new THREE.MeshBasicMaterial({ color: 0xff2a5f, wireframe: true });
                    avatarMesh = new THREE.Mesh(geom, mat);
                    avatarMesh.position.set(0, 1.3, 0);
                    scene.add(avatarMesh);
                });

                window.addEventListener('resize', resizeRenderer);
                runAnimationLoop();
            } catch (err) {
                console.warn("3D Render Non-blocking warning:", err);
            }
        }

        function resizeRenderer() {
            const holder = document.getElementById('canvas3D');
            if (holder && camera && renderer) {
                camera.aspect = holder.clientWidth / holder.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(holder.clientWidth, holder.clientHeight);
            }
        }

        function runAnimationLoop() {
            requestAnimationFrame(runAnimationLoop);
            if (avatarMesh) avatarMesh.rotation.y += 0.008;
            if (renderer && scene && camera) renderer.render(scene, camera);
        }

        // AI Chat Messaging
        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const text = input.value;
            if (!text.trim()) return;
            
            document.getElementById('subtitleText').textContent = "You: " + text;
            input.value = '';

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                document.getElementById('subtitleText').textContent = "Tringo: " + (data.response || "No reply");
            } catch(e) {
                document.getElementById('subtitleText').textContent = "Connection error!";
            }
        }

        function handleKeyPress(e) { if (e.key === 'Enter') sendChatMessage(); }

        window.onload = initThreeJS;
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_msg = data.get('message', '')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
        "systemInstruction": {"parts": [{"text": "You are Tringo AI assistant."}]}
    }
    try:
        r = requests.post(url, json=payload, timeout=15).json()
        reply = r['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"response": reply})
    except Exception:
        return jsonify({"response": "Error connecting to Gemini API."})

@app.route('/generate-3d', methods=['POST'])
def generate_3d():
    data = request.json or {}
    gen_type = data.get('type')
    
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        if gen_type == 'text':
            prompt = data.get('prompt', '3D animation scene')
            payload = {
                "version": "3f04576467027955424075957e893da7f5b7816cd7669f464c968256923e15a3",
                "input": {"prompt": prompt}
            }
        else:
            image_b64 = data.get('image')
            payload = {
                "version": "3f04576467027955424075957e893da7f5b7816cd7669f464c968256923e15a3",
                "input": {"input_image": image_b64}
            }

        response = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        res_data = response.json()

        if "id" not in res_data:
            return jsonify({"status": "error", "message": res_data.get("detail", "Failed to start generation")}), 400

        prediction_id = res_data["id"]
        poll_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
        
        for _ in range(30):
            time.sleep(3)
            poll_res = requests.get(pol
