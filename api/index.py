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
    <meta name="theme-color" content="#000000">
    <title>Tringo AI</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { font-family: sans-serif; background: #000000; color: #fff; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
        
        .nav-tabs { display: flex; background: #000000; border-bottom: 1px solid #222; z-index: 30; }
        .tab-btn { 
            flex: 1; padding: 14px 0; background: #000000; border: none; color: #888; font-weight: bold; font-size: 0.95rem; cursor: pointer; transition: 0.3s;
            display: flex; align-items: center; justify-content: center; gap: 8px;
        }
        .tab-btn svg { width: 18px; height: 18px; stroke: #888; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; transition: 0.3s; }
        .tab-btn.active { color: #ff2a5f; border-bottom: 2px solid #ff2a5f; }
        .tab-btn.active svg { stroke: #ff2a5f; }

        .section { display: none; flex: 1; width: 100%; height: 100%; position: relative; background: #000000; overflow-y: auto; }
        .section.active { display: flex; flex-direction: column; }

        #avatarContainer { width: 100%; height: 100%; background: #000000; position: relative; }
        #subtitles { position: absolute; top: 20px; left: 5%; width: 90%; background: rgba(10,10,10,0.85); padding: 12px; border-radius: 16px; text-align: center; font-size: 0.9rem; border: 1px solid #222; z-index: 5; }
        .controls-overlay { position: absolute; bottom: 20px; left: 0; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; z-index: 20; padding: 0 12px; }
        .chat-input { flex: 1; padding: 12px 16px; border-radius: 25px; border: 1px solid #333; background: #000000; color: #fff; font-size: 0.95rem; outline: none; }
        .send-btn { padding: 12px 20px; border-radius: 25px; border: none; background: #ff2a5f; color: #fff; font-weight: bold; cursor: pointer; flex-shrink: 0; }
        .mic-btn { width: 44px; height: 44px; border-radius: 50%; border: none; background: #22c55e; color: #fff; font-size: 1.2rem; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }

        #videoStudio { padding: 16px; background: #000000; display: flex; flex-direction: column; gap: 16px; }
        
        /* Rounded Mode Selector */
        .mode-selector { display: flex; gap: 8px; background: #0a0a0a; padding: 6px; border-radius: 20px; border: 1px solid #222; }
        .sub-mode-btn { 
            flex: 1; padding: 12px; border: 1px solid transparent; background: transparent; color: #888; font-weight: bold; font-size: 0.85rem; border-radius: 14px; cursor: pointer; transition: 0.3s;
            display: flex; align-items: center; justify-content: center; gap: 6px;
        }
        .sub-mode-btn svg { width: 16px; height: 16px; stroke: #888; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; transition: 0.3s; }
        .sub-mode-btn.active { background: #2563eb; color: #ffffff; border-color: transparent; box-shadow: 0 0 12px rgba(37, 99, 235, 0.4); }
        .sub-mode-btn.active svg { stroke: #ffffff; }

        .studio-card { background: #0a0a0a; border: 1px solid #222; padding: 16px; border-radius: 20px; }
        .studio-card h3 { color: #ff2a5f; font-size: 1.05rem; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
        .studio-card h3 svg { width: 20px; height: 20px; stroke: #ff2a5f; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
        
        /* Rounded Input Field */
        .studio-input { width: 100%; height: 100px; background: #000000; border: 1px solid #333; color: #fff; padding: 14px; border-radius: 16px; resize: none; margin-bottom: 14px; outline: none; font-size: 0.9rem; }
        
        .upload-box { 
            position: relative; border: 2px dashed #333; padding: 16px; text-align: center; border-radius: 16px; background: #000000; cursor: pointer; margin-bottom: 12px; min-height: 140px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; overflow: hidden;
        }
        .upload-box svg { width: 24px; height: 24px; stroke: #2563eb; fill: none; stroke-width: 1.8; }
        .upload-box span { color: #fff; font-size: 0.9rem; font-weight: 500; }
        .upload-box p { color: #888; font-size: 0.8rem; }
        
        .preview-img { width: 100%; max-height: 180px; object-fit: contain; border-radius: 12px; display: none; }
        .remove-img-btn { position: absolute; top: 8px; right: 8px; background: rgba(255, 42, 95, 0.9); color: white; border: none; width: 26px; height: 26px; border-radius: 50%; cursor: pointer; display: none; font-weight: bold; font-size: 14px; z-index: 10; }

        /* Rounded Blue Action Buttons */
        .gen-btn { width: 100%; padding: 14px; background: #2563eb; border: none; color: #ffffff; font-weight: bold; border-radius: 25px; cursor: pointer; transition: 0.2s; font-size: 0.95rem; box-shadow: 0 0 12px rgba(37, 99, 235, 0.4); }
        .gen-btn:disabled { background: #555; cursor: not-allowed; }
        
        .loader { border: 3px solid #333; border-top: 3px solid #2563eb; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; margin: 10px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('chat')">
            <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            AI Chat
        </button>
        <button class="tab-btn" onclick="switchTab('studio')">
            <svg viewBox="0 0 24 24"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
            3D Video Studio
        </button>
    </div>

    <div id="chatSection" class="section active">
        <div id="avatarContainer">
            <div id="subtitles">Ask me anything or speak to Tringo!</div>
            <div class="controls-overlay">
                <button class="mic-btn" id="micBtn" onclick="toggleVoiceInput()">🎙️</button>
                <input type="text" id="userInput" class="chat-input" placeholder="Message Tringo AI..." onkeypress="handleKeyPress(event)">
                <button class="send-btn" onclick="sendTextMessage()">Send</button>
            </div>
        </div>
    </div>

    <div id="studioSection" class="section">
        <div id="videoStudio">
            <div class="mode-selector">
                <button class="sub-mode-btn active" id="textModeBtn" onclick="switchStudioMode('text')">
                    <svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    Prompt to 3D
                </button>
                <button class="sub-mode-btn" id="picModeBtn" onclick="switchStudioMode('pic')">
                    <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                    Pic to Animation
                </button>
            </div>

            <!-- Option A: Text Prompt -->
            <div class="studio-card" id="textPromptCard">
                <h3>Generate 3D Animation Video</h3>
                <textarea class="studio-input" id="promptInput" placeholder="Describe your 3D animation scene (e.g., A funny 3D robot dancing)..."></textarea>
                <button class="gen-btn" id="btnTextGen" onclick="generateVideo('text')">Render 3D Video</button>
            </div>

            <!-- Option B: Pic Animation -->
            <div class="studio-card" id="picPromptCard" style="display:none;">
                <h3>Animate Image to 3D</h3>
                <div class="upload-box" id="uploadBox" onclick="document.getElementById('imageUpload').click()">
                    <button class="remove-img-btn" id="removeImgBtn" onclick="clearImage(event)">✕</button>
                    <div id="uploadPlaceholder" style="display:flex; flex-direction:column; align-items:center; gap:6px;">
                        <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                        <span>Tap to Upload Image</span>
                        <p id="fileName">Select JPG/PNG photo</p>
                    </div>
                    <img id="imagePreview" class="preview-img" alt="Uploaded Preview">
                    <input type="file" id="imageUpload" accept="image/*" style="display:none;" onchange="previewSelectedImage(this)">
                </div>
                <button class="gen-btn" id="btnPicGen" onclick="generateVideo('pic')">Animate Image</button>
            </div>

            <div class="studio-card" id="statusCard" style="display:none;">
                <h3>Status</h3>
                <div id="loader" class="loader" style="display:none;"></div>
                <p id="statusText" style="text-align:center; margin-top:10px; font-size:0.9rem; color:#aaa;"></p>
                <div id="resultContainer" style="margin-top:12px;"></div>
            </div>
        </div>
    </div>

    <script>
        let base64Image = null;

        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
            if (tab === 'chat') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('chatSection').classList.add('active');
            } else {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('studioSection').classList.add('active');
            }
        }

        function switchStudioMode(mode) {
            document.getElementById('textModeBtn').classList.remove('active');
            document.getElementById('picModeBtn').classList.remove('active');
            if (mode === 'text') {
                document.getElementById('textModeBtn').classList.add('active');
                document.getElementById('textPromptCard').style.display = 'block';
                document.getElementById('picPromptCard').style.display = 'none';
            } else {
                document.getElementById('picModeBtn').classList.add('active');
                document.getElementById('textPromptCard').style.display = 'none';
                document.getElementById('picPromptCard').style.display = 'block';
            }
        }

        function previewSelectedImage(input) {
            const file = input.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    base64Image = e.target.result;
                    const imgPreview = document.getElementById('imagePreview');
                    imgPreview.src = base64Image;
                    imgPreview.style.display = 'block';
                    document.getElementById('uploadPlaceholder').style.display = 'none';
                    document.getElementById('removeImgBtn').style.display = 'block';
                    document.getElementById('uploadBox').style.borderColor = '#2563eb';
                }
                reader.readAsDataURL(file);
            }
        }

        function clearImage(e) {
            e.stopPropagation();
            base64Image = null;
            document.getElementById('imageUpload').value = '';
            document.getElementById('imagePreview').src = '';
            document.getElementById('imagePreview').style.display = 'none';
            document.getElementById('uploadPlaceholder').style.display = 'flex';
            document.getElementById('removeImgBtn').style.display = 'none';
            document.getElementById('uploadBox').style.borderColor = '#333';
        }

        async function generateVideo(type) {
            const statusCard = document.getElementById('statusCard');
            const statusText = document.getElementById('statusText');
            const loader = document.getElementById('loader');
            const resultContainer = document.getElementById('resultContainer');
            
            statusCard.style.display = 'block';
            loader.style.display = 'block';
            resultContainer.innerHTML = '';

            let payload = { type: type };

            if (type === 'text') {
                const prompt = document.getElementById('promptInput').value;
                if(!prompt.trim()) return alert('Please enter a description!');
                payload.prompt = prompt;
                statusText.textContent = 'Rendering 3D scene using AI... (May take 30-60s)';
            } else {
                if(!base64Image) return alert('Please upload an image first!');
                payload.image = base64Image;
                statusText.textContent = 'Animating image into 3D... (May take 30-60s)';
            }

            try {
                const res = await fetch('/generate-3d', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                loader.style.display = 'none';

                if (data.status === 'success' && data.video_url) {
                    statusText.textContent = 'Render Complete!';
                    resultContainer.innerHTML = `
                        <video controls autoplay loop width="100%" style="border-radius:12px; border:1px solid #333;">
                            <source src="${data.video_url}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>`;
                } else {
                    statusText.textContent = 'Error: ' + (data.message || 'Rendering failed.');
                }
            } catch(err) {
                loader.style.display = 'none';
                statusText.textContent = 'Network or Server Error!';
            }
        }

        let scene, camera, renderer, model;
        function init3D() {
            const container = document.getElementById('avatarContainer');
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 1.4, 1.3); 

            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setClearColor(0x000000, 1);
            container.appendChild(renderer.domElement);

            const light = new THREE.AmbientLight(0xffffff, 1.5);
            scene.add(light);

            const loader = new THREE.GLTFLoader();
            loader.load('/avatar.glb', function (gltf) {
                model = gltf.scene;
                scene.add(model);
                animate();
            }, undefined, function () {});
        }

        function animate() {
            requestAnimationFrame(animate);
            if (model) model.rotation.y = Math.sin(Date.now() * 0.001) * 0.02;
            renderer.render(scene, camera);
        }

        async function processUserMessage(text) {
            if (!text.trim()) return;
            document.getElementById('subtitles').textContent = "You: " + text;
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                document.getElementById('subtitles').textContent = "Tringo: " + (data.response || "No reply");
            } catch(e) { document.getElementById('subtitles').textContent = "Connection error"; }
        }

        function sendTextMessage() {
            const input = document.getElementById('userInput');
            processUserMessage(input.value);
            input.value = '';
        }

        function handleKeyPress(e) { if (e.key === 'Enter') sendTextMessage(); }
        window.onload = init3D;
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
        return jsonify({"response": "Error connecting."})

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
            poll_res = requests.get(poll_url, headers=headers).json()
            if poll_res.get("status") == "succeeded":
                output_url = poll_res.get("output")
                if isinstance(output_url, list):
                    output_url = output_url[0]
                return jsonify({"status": "success", "video_url": output_url})
      
