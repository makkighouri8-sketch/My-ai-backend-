from flask import Flask, request, jsonify, render_template_string
import os
import requests
import time

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "r8_TjDtv9s6nWDFPGcuW7btlVAWCpY5qEk138nnF")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        html, body { width: 100%; height: 100%; background: #050505; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }

        .app-container { display: flex; flex-direction: column; width: 100vw; height: 100vh; background: #050505; }

        /* Top Bar */
        .top-nav { display: flex; height: 55px; background: #111111; border-bottom: 1px solid #222; flex-shrink: 0; }
        .nav-btn { flex: 1; background: transparent; border: none; color: #777777; font-weight: bold; font-size: 0.95rem; cursor: pointer; border-bottom: 3px solid transparent; }
        .nav-btn.active { color: #d037fd; border-bottom: 3px solid #d037fd; background: rgba(208, 55, 253, 0.08); }

        /* Content Area */
        .main-content { flex: 1; position: relative; width: 100%; height: calc(100vh - 55px); overflow: hidden; }
        .panel { display: none; width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
        .panel.active { display: flex; flex-direction: column; }

        /* Panel 1: AI Chat */
        #chatPanel { position: relative; background: #050505; }
        #avatarCanvas { width: 100%; height: 100%; display: block; }
        
        .greeting-box { position: absolute; top: 62%; left: 0; width: 100%; text-align: center; z-index: 5; }
        .greeting-text { font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 6px; }
        .sub-greeting { font-size: 0.9rem; color: #888888; }

        .subtitle-box { position: absolute; top: 16px; left: 4%; width: 92%; background: rgba(20, 20, 20, 0.85); border: 1px solid #333; border-radius: 14px; padding: 12px 16px; text-align: center; font-size: 0.9rem; z-index: 5; color: #fff; }
        .chat-bar { position: absolute; bottom: 20px; left: 4%; width: 92%; display: flex; gap: 8px; z-index: 5; }
        .chat-bar input { flex: 1; height: 48px; background: #151515; border: 1px solid #333; border-radius: 24px; padding: 0 16px; color: #fff; outline: none; font-size: 0.95rem; }
        .chat-bar input:focus { border-color: #d037fd; }
        .chat-bar button { padding: 0 20px; height: 48px; background: #d037fd; border: none; border-radius: 24px; color: #fff; font-weight: bold; cursor: pointer; }

        /* Panel 2: Studio */
        #studioPanel { overflow-y: auto; padding: 16px; background: #050505; }
        .studio-box { max-width: 500px; margin: 0 auto; width: 100%; display: flex; flex-direction: column; gap: 16px; }
        
        .sub-nav { display: flex; background: #121212; padding: 4px; border-radius: 20px; border: 1px solid #222; }
        .sub-btn { flex: 1; padding: 10px; background: transparent; border: none; color: #777; font-weight: bold; font-size: 0.85rem; border-radius: 16px; cursor: pointer; }
        .sub-btn.active { background: #2563eb; color: #fff; }

        .card { background: #121212; border: 1px solid #222; border-radius: 16px; padding: 16px; }
        .card h3 { color: #d037fd; font-size: 1rem; margin-bottom: 12px; }
        .card textarea { width: 100%; height: 100px; background: #000; border: 1px solid #333; border-radius: 12px; padding: 12px; color: #fff; resize: none; outline: none; font-size: 0.9rem; margin-bottom: 12px; }

        .upload-area { border: 2px dashed #333; background: #000; border-radius: 12px; padding: 20px; text-align: center; cursor: pointer; margin-bottom: 12px; position: relative; min-height: 120px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .upload-area img { width: 100%; max-height: 180px; object-fit: contain; border-radius: 8px; display: none; }
        .btn-del { position: absolute; top: 8px; right: 8px; background: #ff2a5f; color: #fff; border: none; width: 26px; height: 26px; border-radius: 50%; font-weight: bold; cursor: pointer; display: none; }

        .btn-submit { width: 100%; padding: 12px; background: #2563eb; border: none; border-radius: 20px; color: #fff; font-weight: bold; font-size: 0.95rem; cursor: pointer; }
        
        .loader-ring { border: 3px solid #222; border-top: 3px solid #2563eb; border-radius: 50%; width: 28px; height: 28px; animation: spin 0.8s linear infinite; margin: 10px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- Navigation -->
        <div class="top-nav">
            <button class="nav-btn active" id="tabChat" onclick="changeTab('chat')">AI Chat</button>
            <button class="nav-btn" id="tabStudio" onclick="changeTab('studio')">3D Video Studio</button>
        </div>

        <div class="main-content">
            <!-- AI Chat Panel -->
            <div id="chatPanel" class="panel active">
                <canvas id="avatarCanvas"></canvas>
                
                <div class="greeting-box" id="greetingContainer">
                    <div class="greeting-text" id="userNameLabel">Hi Jamshed,</div>
                    <div class="sub-greeting">Ask or speak anything to Tringo AI!</div>
                </div>

                <div class="subtitle-box" id="subBox" style="display:none;"></div>

                <div class="chat-bar">
                    <input type="text" id="msgInput" placeholder="Message Tringo AI..." onkeypress="onKey(event)">
                    <button onclick="sendChat()">Send</button>
                </div>
            </div>

            <!-- Studio Panel -->
            <div id="studioPanel" class="panel">
                <div class="studio-box">
                    <div class="sub-nav">
                        <button class="sub-btn active" id="subText" onclick="changeStudioMode('text')">Prompt to 3D</button>
                        <button class="sub-btn" id="subPic" onclick="changeStudioMode('pic')">Pic to Animation</button>
                    </div>

                    <!-- Text Mode -->
                    <div class="card" id="textCard">
                        <h3>Generate 3D Animation</h3>
                        <textarea id="textPromptInput" placeholder="Describe 3D scene..."></textarea>
                        <button class="btn-submit" onclick="startGeneration('text')">Render 3D Video</button>
                    </div>

                    <!-- Pic Mode -->
                    <div class="card" id="picCard" style="display:none;">
                        <h3>Animate Image to 3D</h3>
                        <div class="upload-area" id="upArea" onclick="document.getElementById('fileInput').click()">
                            <button class="btn-del" id="delBtn" onclick="removeSelectedImage(event)">✕</button>
                            <div id="upText">
                                <span style="color:#fff; font-weight:bold;">Tap to Upload Photo</span>
                                <p style="color:#777; font-size:0.8rem; margin-top:4px;">JPG or PNG file</p>
                            </div>
                            <img id="imgPreview" alt="Preview">
                            <input type="file" id="fileInput" accept="image/*" style="display:none;" onchange="onFilePicked(this)">
                        </div>
                        <button class="btn-submit" onclick="startGeneration('pic')">Animate Image</button>
                    </div>

                    <!-- Status Display -->
                    <div class="card" id="statusCard" style="display:none;">
                        <h3>Status</h3>
                        <div class="loader-ring" id="loaderRing" style="display:none;"></div>
                        <p id="statusTxt" style="text-align:center; font-size:0.85rem; color:#aaa;"></p>
                        <div id="videoHolder" style="margin-top:10px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let uploadedImgBase64 = null;

        // User Login Greeting Handler
        function setUserGreeting(nameOrEmail) {
            let firstName = "User";
            if (nameOrEmail) {
                let clean = nameOrEmail.split('@')[0];
                clean = clean.split('.')[0].split('_')[0];
                firstName = clean.charAt(0).toUpperCase() + clean.slice(1);
            }
            document.getElementById('userNameLabel').textContent = "Hi " + firstName + ",";
        }

        // Example trigger (Pass dynamic username or email here)
        setUserGreeting("Jamshed");

        function changeTab(tab) {
            document.getElementById('tabChat').classList.remove('active');
            document.getElementById('tabStudio').classList.remove('active');
            document.getElementById('chatPanel').classList.remove('active');
            document.getElementById('studioPanel').classList.remove('active');

            if (tab === 'chat') {
                document.getElementById('tabChat').classList.add('active');
                document.getElementById('chatPanel').classList.add('active');
            } else {
                document.getElementById('tabStudio').classList.add('active');
                document.getElementById('studioPanel').classList.add('active');
            }
        }

        function changeStudioMode(mode) {
            document.getElementById('subText').classList.remove('active');
            document.getElementById('subPic').classList.remove('active');
            if (mode === 'text') {
                document.getElementById('subText').classList.add('active');
                document.getElementById('textCard').style.display = 'block';
                document.getElementById('picCard').style.display = 'none';
            } else {
                document.getElementById('subPic').classList.add('active');
                document.getElementById('textCard').style.display = 'none';
                document.getElementById('picCard').style.display = 'block';
            }
        }

        function onFilePicked(input) {
            const file = input.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadedImgBase64 = e.target.result;
                    const preview = document.getElementById('imgPreview');
                    preview.src = uploadedImgBase64;
                    preview.style.display = 'block';
                    document.getElementById('upText').style.display = 'none';
                    document.getElementById('delBtn').style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        }

        function removeSelectedImage(e) {
            e.stopPropagation();
            uploadedImgBase64 = null;
            document.getElementById('fileInput').value = '';
            document.getElementById('imgPreview').src = '';
            document.getElementById('imgPreview').style.display = 'none';
            document.getElementById('upText').style.display = 'block';
            document.getElementById('delBtn').style.display = 'none';
        }

        async function startGeneration(type) {
            const statusCard = document.getElementById('statusCard');
            const statusTxt = document.getElementById('statusTxt');
            const loaderRing = document.getElementById('loaderRing');
            const videoHolder = document.getElementById('videoHolder');

            statusCard.style.display = 'block';
            loaderRing.style.display = 'block';
            videoHolder.innerHTML = '';

            let payload = { type: type };

            if (type === 'text') {
                const txt = document.getElementById('textPromptInput').value;
                if (!txt.trim()) return alert('Please enter prompt text!');
                payload.prompt = txt;
                statusTxt.textContent = 'Generating 3D Animation... Please wait.';
            } else {
                if (!uploadedImgBase64) return alert('Please upload an image first!');
                payload.image = uploadedImgBase64;
                statusTxt.textContent = 'Animating image into 3D... Please wait.';
            }

            try {
                const res = await fetch('/generate-3d', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                loaderRing.style.display = 'none';

                if (data.status === 'success' && data.video_url) {
                    statusTxt.textContent = 'Completed!';
                    videoHolder.innerHTML = `<video controls autoplay loop width="100%" style="border-radius:10px;"><source src="${data.video_url}" type="video/mp4"></video>`;
                } else {
                    statusTxt.textContent = 'Error: ' + (data.message || 'Generation failed');
                }
            } catch (err) {
                loaderRing.style.display = 'none';
                statusTxt.textContent = 'Server connection error!';
            }
        }

        /* Tringo AI Icon Matching Rotating Spiral Galaxy Animation */
        const canvas = document.getElementById('avatarCanvas');
        const ctx = canvas.getContext('2d');
        let rotationAngle = 0;

        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }

        function drawTringoSpiralIcon() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const centerX = canvas.width / 2;
            const centerY = (canvas.height / 2) - 60; 
            
            rotationAngle += 0.03; // Rotation speed

            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(rotationAngle);

            const numArms = 5;
            const particlesPerArm = 18;

            for (let arm = 0; arm < numArms; arm++) {
                const baseAngle = (arm * Math.PI * 2) / numArms;

                for (let i = 0; i < particlesPerArm; i++) {
                    const distance = i * 4.5 + 8;
                    const spiralAngle = baseAngle + (i * 0.15);

                    const x = Math.cos(spiralAngle) * distance;
                    const y = Math.sin(spiralAngle) * distance;

                    const radius = 2 + (i * 0.35);

                    // Purple to Magenta Neon Colors matching Tringo Icon
                    const hue = 270 + (i * 4); 
                    ctx.fillStyle = `hsl(${hue}, 90%, 65%)`;
                    ctx.shadowColor = `hsl(${hue}, 100%, 70%)`;
                    ctx.shadowBlur = 10;

                    ctx.beginPath();
                    ctx.arc(x, y, radius, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            ctx.restore();
            requestAnimationFrame(drawTringoSpiralIcon);
        }

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
        drawTringoSpiralIcon();

        async function sendChat() {
            const inp = document.getElementById('msgInput');
            const val = inp.value;
            if (!val.trim()) return;
            
            document.getElementById('greetingContainer').style.display = 'none';
            const subBox = document.getElementById('subBox');
            subBox.style.display = 'block';
            subBox.textContent = "You: " + val;
            inp.value = '';

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: val })
                });
                const data = await res.json();
                subBox.textContent = "Tringo: " + (data.response || "No response");
            } catch (e) {
                subBox.textContent = "Connection error!";
            }
        }

        function onKey(e) { if (e.key === 'Enter') sendChat(); }
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
    
    if not GEMINI_API_KEY:
        return jsonify({"response": "Gemini API key is missing in environment variables."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": user_msg}]}]
    }
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        res_data = r.json()
        if 'candidates' in res_data:
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"response": reply})
        else:
            return jsonify({"response": "API Key Error or Quota Limit."})
    except Exception as e:
        return jsonify({"response": f"Connection Exception: {str(e)}"})

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
            elif poll_res.get("status") == "failed":
                return jsonify({"status": "error", "message": "3D Generation failed."}), 500

        return jsonify({"status": "error", "message": "Rendering timed out."}), 504
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
