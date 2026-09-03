from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import re

app = Flask(__name__)

# Google Gemini API Key Set Ho Gayi Hai
GEMINI_API_KEY = "AQ.Ab8RN6JkF4wgt9a6aJTPDP11MyZP4-faPZboIy6qOgmj1TRD8A"
genai.configure(api_key=GEMINI_API_KEY)

GIF_URL = "https://i.ibb.co/dsH5qcZc/56698194ba8737a1c0c66786390374b0.gif"

HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI</title>
    
    <link rel="icon" type="image/gif" href="{GIF_URL}">
    <link rel="apple-touch-icon" href="{GIF_URL}">

    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #000000; color: #fff; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
        
        .header {{ padding: 14px 20px; background: #000000; border-bottom: 1px solid #1a1a1a; display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: 700; font-size: 1.2rem; color: #f43f5e; }}
        .header-icon {{ width: 30px; height: 30px; border-radius: 50%; object-fit: cover; box-shadow: 0 0 10px rgba(244, 63, 94, 0.5); }}

        #chatbox {{ flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 14px; background: #000000; }}
        
        .msg {{ padding: 4px 0; max-width: 85%; line-height: 1.5; font-size: 0.95rem; word-break: break-word; font-weight: 400; }}
        
        /* User Message */
        .user {{ background: transparent !important; color: #ffffff; align-self: flex-end; text-align: right; border: none !important; box-shadow: none !important; opacity: 1; }}

        /* Bot Message Fade-in Animation */
        .bot {{ background: transparent !important; color: #f3f4f6; align-self: flex-start; text-align: left; border: none !important; box-shadow: none !important; animation: fadeInMsg 0.4s ease-out forwards; }}
        @keyframes fadeInMsg {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        /* Loader Without Frame */
        .vortex-loader {{ display: flex; align-items: center; gap: 12px; padding: 6px 0; align-self: flex-start; background: transparent !important; border: none !important; box-shadow: none !important; }}
        .vortex-loader img {{ width: 32px; height: 32px; border-radius: 50%; object-fit: cover; filter: drop-shadow(0 0 6px rgba(244, 63, 94, 0.4)); }}
        .vortex-loader span {{ font-size: 0.92rem; color: #f43f5e; font-weight: 500; opacity: 0.95; }}

        .input-bar {{ padding: 12px 10px; background: #000000; border-top: 1px solid #1a1a1a; display: flex; align-items: center; gap: 8px; width: 100%; position: relative; }}
        .input-field-wrapper {{ flex: 1; background: #121212; border-radius: 26px; border: 1px solid #262626; display: flex; align-items: center; padding: 0 12px; min-width: 0; }}
        .input-field-wrapper:focus-within {{ border-color: #f43f5e; background: #171717; }}
        input {{ flex: 1; padding: 12px 6px; border: none; background: transparent; color: #fff; outline: none; font-size: 0.95rem; min-width: 0; }}
        
        .icon-btn {{ background: none; border: none; color: #a3a3a3; font-size: 1.3rem; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 6px; flex-shrink: 0; }}
        .icon-btn:hover {{ color: #f43f5e; }}
        
        .mic-btn svg {{ width: 20px; height: 20px; fill: currentColor; }}
        .send-btn {{ border-radius: 50%; width: 44px; height: 44px; border: none; background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%); color: #fff; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; box-shadow: 0 4px 12px rgba(244, 63, 94, 0.35); }}

        .menu-modal {{ display: none; position: absolute; bottom: 70px; left: 10px; background: #121212; border: 1px solid #262626; border-radius: 14px; padding: 8px 0; box-shadow: 0 10px 25px rgba(0,0,0,0.8); z-index: 100; min-width: 170px; }}
        .menu-modal.active {{ display: block; animation: popUp 0.2s ease; }}
        @keyframes popUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .menu-item {{ padding: 10px 16px; color: #e5e7eb; font-size: 0.9rem; display: flex; align-items: center; gap: 10px; cursor: pointer; }}
        .menu-item:hover {{ background: #262626; color: #f43f5e; }}
    </style>
</head>
<body>
    <div class="header">
        <img src="{GIF_URL}" class="header-icon" alt="Tringo Icon">
        <span>Tringo AI</span>
    </div>
    <div id="chatbox">
        <div class="msg bot"><span>Hello! How can I assist you today?</span></div>
    </div>
    
    <div class="menu-modal" id="plusMenu">
        <div class="menu-item" onclick="triggerOption('Image Upload')">📷 Upload Image</div>
        <div class="menu-item" onclick="triggerOption('File Attachment')">📁 Attach File</div>
        <div class="menu-item" onclick="triggerOption('Code Snippet')">💻 Paste Code</div>
    </div>

    <div class="input-bar">
        <button class="icon-btn" onclick="toggleMenu(event)" title="Options">+</button>
        <div class="input-field-wrapper">
            <input type="text" id="userInput" placeholder="Ask Tringo..." onkeydown="if(event.key==='Enter') sendMessage()">
            <button class="icon-btn mic-btn" title="Voice Input" onclick="triggerOption('Voice Input')">
                <svg viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
            </button>
        </div>
        <button class="send-btn" onclick="sendMessage()">➤</button>
    </div>

    <script>
        const chatbox = document.getElementById('chatbox');
        const input = document.getElementById('userInput');
        const plusMenu = document.getElementById('plusMenu');

        function toggleMenu(e) {{ e.stopPropagation(); plusMenu.classList.toggle('active'); }}
        document.addEventListener('click', () => plusMenu.classList.remove('active'));

        function triggerOption(optionName) {{
            plusMenu.classList.remove('active');
            input.value = `[${{optionName}}] `;
            input.focus();
        }}

        async function sendMessage() {{
            const msgText = input.value.trim();
            if (!msgText) return;

            const userMsg = document.createElement('div');
            userMsg.className = 'msg user';
            userMsg.textContent = msgText;
            chatbox.appendChild(userMsg);
            input.value = '';
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
                    body: JSON.stringify({{ message: msgText }})
                }});
                const data = await res.json();
                const aiResponse = data.response || data.error;
                
                const currentLoader = document.getElementById(loaderId);
                if (currentLoader) currentLoader.remove();
                
                displayFadeMessage(aiResponse);
            }} catch (err) {{
                const currentLoader = document.getElementById(loaderId);
                if (currentLoader) currentLoader.remove();
                
                displayFadeMessage("Server connection error.");
            }}
        }}

        function displayFadeMessage(text) {{
            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            
            const textSpan = document.createElement('span');
            textSpan.textContent = text;
            botMsg.appendChild(textSpan);
            
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
    if not user_message: 
        return jsonify({"error": "Message required"}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        system_instruction = (
            "You are Tringo AI, a helpful AI assistant.\n"
            "Strict Instructions:\n"
            "1. If user speaks in Roman Urdu, reply in Roman Urdu.\n"
            "2. If user speaks in English, reply in English.\n"
            "3. DO NOT output Chinese characters.\n"
            "4. Be smart, helpful, and clear."
        )
        
        prompt = f"{system_instruction}\n\nUser: {user_message}"
        res = model.generate_content(prompt)
        
        reply = res.text if res.text else "Bilkul, batao kya madad chahiye?"
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500

