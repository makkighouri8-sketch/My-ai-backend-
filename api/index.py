from flask import Flask, request, jsonify, render_template_string
import g4f

app = Flask(__name__)

# Aapki uploaded ImgBB GIF ka exact link
GIF_URL = "https://i.ibb.co/dsH5qcZc/56698194ba8737a1c0c66786390374b0.gif"

HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI</title>
    
    <!-- Favicon / App Tab Icon -->
    <link rel="icon" type="image/gif" href="{GIF_URL}">
    <link rel="apple-touch-icon" href="{GIF_URL}">

    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #fff; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
        
        .header {{ padding: 12px 20px; background: #111827; border-bottom: 1px solid #1f2937; display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: bold; font-size: 1.2rem; color: #f43f5e; }}
        .header-icon {{ width: 32px; height: 32px; border-radius: 50%; object-fit: cover; box-shadow: 0 0 10px rgba(244, 63, 94, 0.6); }}

        #chatbox {{ flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 12px; background: radial-gradient(circle at center, #111827 0%, #0b0f19 100%); }}
        
        .msg {{ padding: 12px 16px; border-radius: 18px; max-width: 82%; line-height: 1.5; font-size: 0.95rem; word-break: break-word; }}
        .user {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2); animation: popUser 0.3s ease forwards; opacity: 0; transform: scale(0.95); }}
        @keyframes popUser {{ to {{ opacity: 1; transform: scale(1); }} }}

        .bot {{ background: #1f2937; color: #e5e7eb; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #374151; opacity: 0; animation: popBot 0.3s ease forwards; }}
        @keyframes popBot {{ to {{ opacity: 1; }} }}

        .typewriter-text.typing {{ display: inline; border-right: 2px solid #f43f5e; animation: blink 0.75s step-end infinite; }}
        @keyframes blink {{ from, to {{ border-color: transparent }} 50% {{ border-color: #f43f5e; }} }}

        .vortex-loader {{ display: flex; align-items: center; gap: 10px; background: #1f2937; padding: 8px 14px; border-radius: 18px; align-self: flex-start; border: 1px solid #374151; }}
        .vortex-loader img {{ width: 28px; height: 28px; border-radius: 50%; }}
        .vortex-loader span {{ font-size: 0.85rem; color: #f43f5e; font-weight: 500; }}

        .input-bar {{ padding: 10px 8px; background: #111827; border-top: 1px solid #1f2937; display: flex; align-items: center; gap: 6px; width: 100%; position: relative; }}
        .input-field-wrapper {{ flex: 1; background: #1f2937; border-radius: 24px; border: 1px solid #374151; display: flex; align-items: center; padding: 0 10px; min-width: 0; }}
        .input-field-wrapper:focus-within {{ border-color: #f43f5e; background: #1a2233; }}
        input {{ flex: 1; padding: 10px 6px; border: none; background: transparent; color: #fff; outline: none; font-size: 0.95rem; min-width: 0; }}
        
        .icon-btn {{ background: none; border: none; color: #9ca3af; font-size: 1.3rem; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 6px; flex-shrink: 0; }}
        .icon-btn:hover {{ color: #f43f5e; }}
        
        .mic-btn svg {{ width: 20px; height: 20px; fill: currentColor; }}
        .send-btn {{ border-radius: 50%; width: 42px; height: 42px; border: none; background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%); color: #fff; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; box-shadow: 0 4px 10px rgba(244, 63, 94, 0.3); }}

        .menu-modal {{ display: none; position: absolute; bottom: 65px; left: 10px; background: #1f2937; border: 1px solid #374151; border-radius: 12px; padding: 8px 0; box-shadow: 0 10px 25px rgba(0,0,0,0.5); z-index: 100; min-width: 160px; }}
        .menu-modal.active {{ display: block; animation: popUp 0.2s ease; }}
        @keyframes popUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .menu-item {{ padding: 10px 16px; color: #e5e7eb; font-size: 0.9rem; display: flex; align-items: center; gap: 10px; cursor: pointer; }}
        .menu-item:hover {{ background: #374151; color: #f43f5e; }}
    </style>
</head>
<body>
    <div class="header">
        <img src="{GIF_URL}" class="header-icon" alt="Tringo Icon">
        <span>Tringo AI</span>
    </div>
    <div id="chatbox">
        <div class="msg bot"><span>Welcome to Tringo AI! How can I assist you today?</span></div>
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
            chatbox.innerHTML += `
                <div class="vortex-loader" id="${{loaderId}}">
                    <img src="{GIF_URL}">
                    <span>Tringo is thinking...</span>
                </div>`;
            chatbox.scrollTop = chatbox.scrollHeight;

            try {{
                const res = await fetch('/chat', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: msgText }})
                }});
                const data = await res.json();
                const aiResponse = data.response || data.error;
                document.getElementById(loaderId).remove();
                displayTypewriterMessage(aiResponse);
            }} catch (err) {{
                document.getElementById(loaderId).remove();
                displayTypewriterMessage("Error connecting to server.");
            }}
        }}

        function displayTypewriterMessage(text) {{
            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            const textSpan = document.createElement('span');
            textSpan.className = 'typewriter-text typing';
            botMsg.appendChild(textSpan);
            chatbox.appendChild(botMsg);
            chatbox.scrollTop = chatbox.scrollHeight;

            let charIndex = 0;
            function typeChar() {{
                if (charIndex < text.length) {{
                    textSpan.textContent += text.charAt(charIndex);
                    charIndex++;
                    chatbox.scrollTop = chatbox.scrollHeight;
                    setTimeout(typeChar, 20);
                }} else {{
                    textSpan.classList.remove('typing');
                }}
            }}
            typeChar();
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
    if not user_message: return jsonify({"error": "Message is required"}), 400
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": user_message}]
        )
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
