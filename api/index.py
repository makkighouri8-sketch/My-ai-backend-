from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

# Vercel environment variable se key lega, agar na mile toh fallback key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI 3D</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: sans-serif; background: #000; color: #fff; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
        #avatarContainer { flex: 1; width: 100%; position: relative; background: #080808; }
        
        #headerTitle { position: absolute; top: 15px; width: 100%; text-align: center; font-size: 1.2rem; font-weight: bold; color: #ff2a5f; z-index: 10; text-shadow: 0 0 10px rgba(255,42,95,0.5); }
        #subtitles { position: absolute; top: 50px; left: 5%; width: 90%; background: rgba(0,0,0,0.7); padding: 10px 14px; border-radius: 10px; text-align: center; font-size: 0.9rem; border: 1px solid #333; z-index: 5; }

        .controls-overlay { position: absolute; bottom: 20px; left: 0; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; z-index: 20; padding: 0 12px; }
        
        .chat-input { flex: 1; padding: 12px 16px; border-radius: 25px; border: 1px solid #444; background: rgba(20,20,20,0.9); color: #fff; font-size: 0.95rem; outline: none; }
        .send-btn { padding: 12px 18px; border-radius: 25px; border: none; background: #ff2a5f; color: #fff; font-weight: bold; cursor: pointer; flex-shrink: 0; }
        .mic-btn { width: 44px; height: 44px; border-radius: 50%; border: none; background: #22c55e; color: #fff; font-size: 1.2rem; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
        .mic-btn.listening { animation: pulse 1s infinite; background: #ef4444; }

        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
    </style>
</head>
<body>

    <div id="avatarContainer">
        <div id="headerTitle">🌀 Tringo AI</div>
        <div id="subtitles">Ask me anything or tap Mic to speak!</div>
        
        <div class="controls-overlay">
            <button class="mic-btn" id="micBtn" onclick="toggleVoiceInput()">🎙️</button>
            <input type="text" id="userInput" class="chat-input" placeholder="Message Tringo AI..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="sendTextMessage()">Send</button>
        </div>
    </div>

    <script>
        let scene, camera, renderer, model;
        let isSpeaking = false;

        function init3D() {
            const container = document.getElementById('avatarContainer');
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 1.4, 1.3); 

            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            const light = new THREE.AmbientLight(0xffffff, 1.5);
            scene.add(light);
            const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
            dirLight.position.set(0, 10, 10);
            scene.add(dirLight);

            const loader = new THREE.GLTFLoader();
            loader.load('/api/avatar.glb', function (gltf) {
                model = gltf.scene;
                model.position.set(0, 0, 0);
                scene.add(model);
                animate();
            }, undefined, function (error) {
                document.getElementById('subtitles').textContent = "Avatar loading... (Ensure avatar.glb is inside api/ folder)";
            });
        }

        function animate() {
            requestAnimationFrame(animate);
            if (isSpeaking && model) {
                model.rotation.y = Math.sin(Date.now() * 0.006) * 0.08;
                model.position.y = Math.sin(Date.now() * 0.01) * 0.005;
            } else if (model) {
                model.rotation.y = Math.sin(Date.now() * 0.001) * 0.02;
            }
            renderer.render(scene, camera);
        }

        const subtitles = document.getElementById('subtitles');

        async function processUserMessage(text) {
            if (!text.trim()) return;
            subtitles.textContent = "You: " + text;
            
            const botReply = await askGemini(text);
            subtitles.textContent = "Tringo: " + botReply;
            speakResponse(botReply);
        }

        function sendTextMessage() {
            const input = document.getElementById('userInput');
            const text = input.value;
            input.value = '';
            processUserMessage(text);
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') sendTextMessage();
        }

        // Speech Recognition
        const micBtn = document.getElementById('micBtn');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'en-US';

            function toggleVoiceInput() {
                try {
                    recognition.start();
                    micBtn.classList.add('listening');
                    subtitles.textContent = "Listening...";
                } catch(e) {
                    recognition.stop();
                    micBtn.classList.remove('listening');
                }
            }

            recognition.onresult = function(event) {
                micBtn.classList.remove('listening');
                const userText = event.results[0][0].transcript;
                processUserMessage(userText);
            };

            recognition.onerror = function() {
                micBtn.classList.remove('listening');
                subtitles.textContent = "Voice error or permission denied.";
            };
        }

        async function askGemini(text) {
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                return data.response || "No response received.";
            } catch(e) {
                return "Connection error.";
            }
        }

        function speakResponse(text) {
            if (!('speechSynthesis' in window)) return;
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            
            utterance.onstart = () => { isSpeaking = true; };
            utterance.onend = () => { isSpeaking = false; };
            utterance.onerror = () => { isSpeaking = false; };

            window.speechSynthesis.speak(utterance);
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
        "systemInstruction": {"parts": [{"text": "You are a friendly 3D AI assistant named Tringo AI. Give short, direct, and conversational responses."}]}
    }
    
    try:
        r = requests.post(url, json=payload, timeout=15).json()
        reply = r['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": "I am having trouble connecting right now."})

# Required for Vercel Serverless Function
app = app
                          
