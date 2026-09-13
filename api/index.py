from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

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
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Tringo AI</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { font-family: sans-serif; background: #000000; color: #fff; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
        
        /* Navigation Tabs */
        .nav-tabs { display: flex; background: #000000; border-bottom: 1px solid #222; z-index: 30; }
        .tab-btn { 
            flex: 1; 
            padding: 14px 0; 
            background: #000000; 
            border: none; 
            color: #888; 
            font-weight: bold; 
            font-size: 0.95rem; 
            cursor: pointer; 
            transition: 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .tab-btn svg {
            width: 18px;
            height: 18px;
            stroke: #888;
            fill: none;
            stroke-width: 1.8;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: 0.3s;
        }
        .tab-btn.active { color: #ff2a5f; border-bottom: 2px solid #ff2a5f; }
        .tab-btn.active svg { stroke: #ff2a5f; }

        .section { display: none; flex: 1; width: 100%; height: 100%; position: relative; background: #000000; }
        .section.active { display: flex; flex-direction: column; }

        /* Section 1: Chat Mode */
        #avatarContainer { width: 100%; height: 100%; background: #000000; position: relative; }
        #subtitles { position: absolute; top: 20px; left: 5%; width: 90%; background: rgba(10,10,10,0.85); padding: 12px; border-radius: 12px; text-align: center; font-size: 0.9rem; border: 1px solid #222; z-index: 5; }
        .controls-overlay { position: absolute; bottom: 20px; left: 0; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; z-index: 20; padding: 0 12px; }
        .chat-input { flex: 1; padding: 12px 16px; border-radius: 25px; border: 1px solid #333; background: #000000; color: #fff; font-size: 0.95rem; outline: none; }
        .send-btn { padding: 12px 18px; border-radius: 25px; border: none; background: #ff2a5f; color: #fff; font-weight: bold; cursor: pointer; flex-shrink: 0; }
        .mic-btn { width: 44px; height: 44px; border-radius: 50%; border: none; background: #22c55e; color: #fff; font-size: 1.2rem; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }

        /* Section 2: Video Generator Mode */
        #videoStudio { padding: 20px; background: #000000; display: flex; flex-direction: column; gap: 15px; }
        .studio-card { background: #0a0a0a; border: 1px solid #222; padding: 15px; border-radius: 12px; }
        .studio-card h3 { color: #ff2a5f; font-size: 1.1rem; margin-bottom: 10px; }
        .studio-input { width: 100%; height: 80px; background: #000000; border: 1px solid #333; color: #fff; padding: 10px; border-radius: 8px; resize: none; margin-bottom: 10px; outline: none; }
        .gen-btn { width: 100%; padding: 12px; background: #2563eb; border: none; color: #ffffff; font-weight: bold; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .gen-btn:active { background: #1d4ed8; }
    </style>
</head>
<body>

    <!-- Header Tabs -->
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

    <!-- Section 1: AI Chat -->
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

    <!-- Section 2: AI Video Generator -->
    <div id="studioSection" class="section">
        <div id="videoStudio">
            <div class="studio-card">
                <h3>🎥 Generate 3D Animation Video</h3>
                <textarea class="studio-input" id="promptInput" placeholder="Describe your 3D animation scene (e.g., A funny 3D character talking about finance in space)..."></textarea>
                <button class="gen-btn" onclick="generateVideo()">Render 3D Video</button>
            </div>
            <div class="studio-card" id="statusCard" style="display:none;">
                <h3>Status</h3>
                <p id="statusText">Processing prompt and creating 3D scene...</p>
            </div>
        </div>
    </div>

    <script>
        let scene, camera, renderer, model;

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
            const botReply = await askGemini(text);
            document.getElementById('subtitles').textContent = "Tringo: " + botReply;
        }

        function sendTextMessage() {
            const input = document.getElementById('userInput');
            processUserMessage(input.value);
            input.value = '';
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') sendTextMessage();
        }

        async function askGemini(text) {
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                return data.response || "No response";
            } catch(e) { return "Connection error"; }
        }

        function generateVideo() {
            const prompt = document.getElementById('promptInput').value;
            if(!prompt) return alert('Please enter a prompt!');
            document.getElementById('statusCard').style.display = 'block';
            document.getElementById('statusText').textContent = 'Generating 3D Automation Script & Visuals for: "' + prompt + '"';
        }

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
    except Exception as e:
        return jsonify({"response": "Error connecting."})

app = app
                        
