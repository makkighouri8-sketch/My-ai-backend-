from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

GEMINI_API_KEY = "AQ.Ab8RN6K6W9bHr3x-issUTTrhHn"
GIF_URL = "https://i.ibb.co/dsH5qcZc/56698194ba8737a1c0c66786390374b0.gif"

HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI</title>
    <link rel="icon" type="image/gif" href="{GIF_URL}">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #000000; color: #fff; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
        .header {{ padding: 14px 20px; background: #000000; border-bottom: 1px solid #1a1a1a; display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: 700; font-size: 1.2rem; color: #f43f5e; }}
        .header-icon {{ width: 30px; height: 30px; border-radius: 50%; object-fit: cover; box-shadow: 0 0 10px rgba(244, 63, 94, 0.5); }}
        #chatbox {{ flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 14px; background: #000000; }}
        .msg {{ padding: 4px 0; max-width: 85%; line-height: 1.5; font-size: 0.95rem; word-break: break-word; font-weight: 400; }}
        .user {{ background: transparent !important; color: #ffffff; align-self: flex-end; text-align: right; }}
        .bot {{ background: transparent !important; color: #f3f4f6; align-self: flex-start; text-align: left; animation: fadeInMsg 0.4s ease-out forwards; }}
        .vortex-loader {{ display: flex; align-items: center; gap: 12px; padding: 6px 0; align-self: flex-start; }}
        .vortex-loader img {{ width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }}
        .vortex-loader span {{ font-size: 0.92rem; color: #f43f5e; font-weight: 500; }}
        
        /* Image Preview Area */
        #previewContainer {{ display: none; padding: 8px 14px; background: #121212; border-top: 1px solid #262626; align-items: center; gap: 10px; }}
        #previewContainer img {{ width: 50px; height: 50px; border-radius: 8px; object-fit: cover; border: 1px solid #f43f5e; }}
        #removeImgBtn {{ color: #f43f5e; cursor: pointer; font-weight: bold; font-size: 1.2rem; background: none; border: none; }}

        .input-bar {{ padding: 12px 10px; background: #000000; border-top: 1px solid #1a1a1a; display: flex; align-items: center; gap: 8px; width: 100%; position: relative; }}
        .input-field-wrapper {{ flex: 1; background: #121212; border-radius: 26px; border: 1px solid #262626; display: flex; align-items: center; padding: 0 12px; }}
        .input-field-wrapper:focus-within {{ border-color: #f43f5e; background: #171717; }}
        input[type="text"] {{ flex: 1; padding: 12px 6px; border: none; background: transparent; color: #fff; outline: none; font-size: 0.95rem; }}
        .icon-btn {{ background: none; border: none; color: #a3a3a3; font-size: 1.3rem; cursor: pointer; padding: 6px; }}
        .send-btn {{ border-radius: 50%; width: 44px; height: 44px; border: none; background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%); color: #fff; font-size: 1.1rem; cursor: pointer; }}
        
        .menu-modal {{ display: none; position: absolute; bottom: 70px; left: 10px; background: #121212; border: 1px solid #262626; border-radius: 14px; padding: 8px 0; z-index: 100; min-width: 170px; }}
        .menu-modal.active {{ display: block; }}
        .menu-item {{ padding: 10px 16px; color: #e5e7eb; font-size: 0.9rem; display: flex; align-items: center; gap: 10px; cursor: pointer; }}
        .menu-item:hover {{ background: #262626; color: #f43f5e; }}
    </style>
</head>
<body>
    <div class="header">
        <img src="{GIF_URL}" class="header-icon">
        <span>Tringo AI</span>
    </div>
    <div id="chatbox">
        <div class="msg bot"><span>Hello! How can I assist you today?</span></div>
    </div>

    <!-- Hidden Input Fields -->
    <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageSelect(event)">
    <input type="file" id="fileInput" accept="*/*" style="display: none;" onchange="handleFileSelect(event)">

    <!-- Image Preview Container -->
    <div id="previewContainer">
        <img id="imgPreview" src="" alt="Preview">
        <span id="fileNameDisplay" style="font-size: 0.85rem; color: #ccc;"></span>
        <button id="removeImgBtn" onclick="clearSelectedFile()">✕</button>
    </div>

    <div class="menu-modal" id="plusMenu">
        <div class="menu-item" onclick="openGallery()">📷 Upload Image</div>
        <div class="menu-item" onclick="openFilePicker()">📁 Attach File</div>
        <div class="menu-item" onclick="pasteCodeTemplate()">💻 Paste Code</div>
    </div>

    <div class="input-bar">
        <button class="icon-btn" onclick="toggleMenu(event)">+</button>
        <div class="input-field-wrapper">
            <input type="text" id="userInput" placeholder="Ask Tringo..." onkeydown="if(event.key==='Enter') sendMessage()">
        </div>
        <button class="send-btn" onclick="sendMessage()">➤</button>
    </div>

    <script>
        const chatbox = document.getElementById('chatbox');
        const input = document.getElementById('userInput');
        const plusMenu = document.getElementById('plusMenu');
        let selectedBase64 = null;
        let selectedMimeType = null;

        function toggleMenu(e) {{ e.stopPropagation(); plusMenu.classList.toggle('active'); }}
        document.addEventListener('click', () => plusMenu.classList.remove('active'));

        function openGallery() {{
            plusMenu.classList.remove('active');
            document.getElementById('imageInput').click();
        }}

        function openFilePicker() {{
            plusMenu.classList.remove('active');
            document.getElementById('fileInput').click();
        }}

        function pasteCodeTemplate() {{
            plusMenu.classList.remove('active');
            input.value = "```\n// Paste code here\n```";
            input.focus();
        }}

        function handleImageSelect(event) {{
            const file = event.target.files[0];
            if (!file) return;

            selectedMimeType = file.type;
            const reader = new FileReader();
            reader.onload = function(e) {{
                selectedBase64 = e.target.result.split(',')[1];
                document.getElementById('imgPreview').src = e.target.result;
                document.getElementById('imgPreview').style.display = "block";
                document.getElementById('fileNameDisplay').textContent = file.name;
                document.getElementById('previewContainer').style.display = "flex";
            }};
            reader.readAsDataURL(file);
        }}

        function handleFileSelect(event) {{
            const file = event.target.files[0];
            if (!file) return;

            selectedMimeType = file.type || "application/octet-stream";
            const reader = new FileReader();
            reader.onload = function(e) {{
                selectedBase64 = e.target.result.split(',')[1];
                document.getElementById('imgPreview').style.display = "none";
                document.getElementById('fileNameDisplay').textContent = "📁 " + file.name;
                document.getElementById('previewContainer').style.display = "flex";
            }};
            reader.readAsDataURL(file);
        }}

        function clearSelectedFile() {{
            selectedBase64 = null;
            selectedMimeType = null;
            document.getElementById('imageInput').value = "";
            document.getElementById('fileInput').value = "";
            document.getElementById('previewContainer').style.display = "none";
        }}

        async function sendMessage() {{
            const msgText = input.value.trim();
            if (!msgText && !selectedBase64) return;

            const userMsg = document.createElement('div');
            userMsg.className = 'msg user';
            userMsg.textContent = msgText + (selectedBase64 ? " 📷 [Attachment Attached]" : "");
            chatbox.appendChild(userMsg);

            const payloadData = {{
                message: msgText,
                image_base64: selectedBase64,
                mime_type: selectedMimeType
            }};

            input.value = '';
            clearSelectedFile();
            chatbox.scrollTop = chatbox.scrollHeight;

            const loaderId = 'loader-' + Date.now();
            const loaderDiv = document.createElement('div');
            loaderDiv.className = 'vortex-loader';
            loaderDiv.id = loaderId;
            loaderDiv.innerHTML = `<img src="{GIF_URL}"><span>Tringo is thinking...</span>`;
            chatbox.appendChild(loaderDiv);
            chatbox.scrollTop = chatbox.scrollHeight;

            try {{
                const res = await fetch('/chat', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payloadData)
                }});
                const data = await res.json();
                
                const currentLoader = document.getElementById(loaderId);
                if (currentLoader) currentLoader.remove();
                
                displayFadeMessage(data.response || data.error);
            }} catch (err) {{
                const currentLoader = document.getElementById(loaderId);
                if (currentLoader) currentLoader.remove();
                displayFadeMessage("Server Connection Error.");
            }}
        }}

        function displayFadeMessage(text) {{
            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = `<span>${{text}}</span>`;
            chatbox.appendChild(botMsg);
            chatbox.scrollTop = chatbox.scrollHeight;
        }}
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '')
    image_base64 = data.get('image_base64')
    mime_type = data.get('mime_type', 'image/jpeg')

    parts = []
    if user_message:
        parts.append({"text": user_message})
    
    if image_base64:
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": image_base64
            }
        })

    if not parts:
        return jsonify({"error": "Message or Image required"}), 400

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "systemInstruction": {
            "parts": [{"text": "You are Tringo AI. Help the user intelligently."}]
        }
    }

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
        res_data = response.json()

        if "candidates" in res_data and len(res_data["candidates"]) > 0:
            reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"response": reply})
        elif "error" in res_data:
            return jsonify({"response": f"API Error: {res_data['error'].get('message')}"})
        else:
            return jsonify({"response": "No response received."})

    except Exception as e:
        return jsonify({"response": f"Server Error: {str(e)}"})
