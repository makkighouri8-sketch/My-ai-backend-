from flask import Flask, request, jsonify, render_template_string
import g4f

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tringo AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #fff; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        
        .header { padding: 15px 20px; background: #111827; border-bottom: 1px solid #1f2937; text-align: center; font-weight: bold; font-size: 1.1rem; color: #60a5fa; }
        
        #chatbox { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; background: radial-gradient(circle at center, #111827 0%, #0b0f19 100%); }
        
        .msg { padding: 12px 18px; border-radius: 18px; max-width: 80%; line-height: 1.5; font-size: 0.95rem; word-break: break-word; position: relative; }
        
        /* Pop Animation for User */
        .user { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2); animation: popUser 0.3s ease forwards; opacity: 0; transform: scale(0.9); }
        @keyframes popUser { to { opacity: 1; transform: scale(1); } }

        /* Bot Message */
        .bot { background: #1f2937; color: #e5e7eb; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #374151; opacity: 0; animation: popBot 0.3s ease forwards; }
        @keyframes popBot { to { opacity: 1; } }

        .typewriter-text.typing { display: inline; border-right: 2px solid #60a5fa; animation: blink 0.75s step-end infinite; }
        @keyframes blink { from, to { border-color: transparent } 50% { border-color: #60a5fa; } }

        /* Glowing Neon Wave Loader */
        .loading-container { display: flex; align-items: center; gap: 10px; background: #1f2937; padding: 12px 18px; border-radius: 18px; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #374151; }
        .pulse-wave { display: flex; gap: 6px; align-items: center; height: 20px; }
        .pulse-wave span { width: 4px; height: 100%; background: #60a5fa; border-radius: 4px; animation: wavePulse 1.2s ease-in-out infinite; box-shadow: 0 0 8px #60a5fa; }
        .pulse-wave span:nth-child(2) { animation-delay: 0.2s; background: #a855f7; box-shadow: 0 0 8px #a855f7; }
        .pulse-wave span:nth-child(3) { animation-delay: 0.4s; background: #ec4899; box-shadow: 0 0 8px #ec4899; }
        @keyframes wavePulse { 0%, 100% { transform: scaleY(0.3); opacity: 0.5; } 50% { transform: scaleY(1); opacity: 1; } }

        /* Custom Input Bar */
        .input-bar { padding: 10px 15px; background: #111827; border-top: 1px solid #1f2937; display: flex; align-items: center; gap: 12px; }
        .input-field-wrapper { flex: 1; background: #1f2937; border-radius: 28px; border: 1px solid #374151; display: flex; align-items: center; padding: 0 12px; }
        .input-field-wrapper:focus-within { border-color: #2563eb; background: #1a2233; }
        input { flex: 1; padding: 14px 12px; border: none; background: transparent; color: #fff; outline: none; font-size: 1rem; }
        
        .icon-btn { background: none; border: none; color: #6b7280; font-size: 1.4rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .icon-btn:hover { color: #60a5fa; }
        
        .send-btn { border-radius: 50%; width: 50px; height: 50px; border: none; background: #2563eb; color: #fff; font-size: 1.3rem; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3); }
    </style>
</head>
<body>
    <div class="header">Tringo AI</div>
    <div id="chatbox">
        <div class="msg bot"><span>Welcome to Tringo AI! How can I help you today?</span></div>
    </div>
    
    <div class="input-bar">
        <button class="icon-btn" title="Media Menu">+</button>
        <div class="input-field-wrapper">
            <input type="text" id="userInput" placeholder="Ask Tringo..." onkeydown="if(event.key==='Enter') sendMessage()">
            <button class="icon-btn" title="Voice Input">🎤</button>
        </div>
        <button class="send-btn" onclick="sendMessage()">➤</button>
    </div>

    <script>
        const chatbox = document.getElementById('chatbox');
        const input = document.getElementById('userInput');

        async function sendMessage() {
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
                <div class="loading-container" id="${loaderId}">
                    <div class="pulse-wave">
                        <span></span><span></span><span></span>
                    </div>
                </div>`;
            chatbox.scrollTop = chatbox.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msgText })
                });
                const data = await res.json();
                const aiResponse = data.response || data.error;
                document.getElementById(loaderId).remove();
                displayTypewriterMessage(aiResponse);
            } catch (err) {
                document.getElementById(loaderId).remove();
                displayTypewriterMessage("Error connecting to server.");
            }
        }

        function displayTypewriterMessage(text) {
            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            const textSpan = document.createElement('span');
            textSpan.className = 'typewriter-text typing';
            botMsg.appendChild(textSpan);
            chatbox.appendChild(botMsg);
            chatbox.scrollTop = chatbox.scrollHeight;

            let charIndex = 0;
            function typeChar() {
                if (charIndex < text.length) {
                    textSpan.textContent += text.charAt(charIndex);
                    charIndex++;
                    chatbox.scrollTop = chatbox.scrollHeight;
                    setTimeout(typeChar, 20);
                } else {
                    textSpan.classList.remove('typing');
                }
            }
            typeChar();
        }
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
        
