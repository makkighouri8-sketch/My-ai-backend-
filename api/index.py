from flask import Flask, request, jsonify, render_template_string
import g4f

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #fff; height: 100vh; display: flex; flex-direction: column; }
        .header { padding: 15px 20px; background: #111827; border-bottom: 1px solid #1f2937; text-align: center; font-weight: bold; font-size: 1.1rem; color: #60a5fa; }
        #chatbox { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 12px; }
        .msg { padding: 12px 16px; border-radius: 16px; max-width: 80%; line-height: 1.4; font-size: 0.95rem; word-break: break-word; }
        .user { background: #2563eb; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #1f2937; color: #e5e7eb; align-self: flex-start; border-bottom-left-radius: 4px; }
        
        /* Modern Glowing AI Pulse Animation */
        .loading-container { display: flex; align-items: center; gap: 10px; background: #1f2937; padding: 12px 18px; border-radius: 16px; align-self: flex-start; border-bottom-left-radius: 4px; }
        .pulse-wave { display: flex; gap: 6px; align-items: center; height: 20px; }
        .pulse-wave span { width: 4px; height: 100%; background: #60a5fa; border-radius: 4px; animation: wave 1.2s ease-in-out infinite; box-shadow: 0 0 8px #60a5fa; }
        .pulse-wave span:nth-child(2) { animation-delay: 0.2s; background: #a855f7; box-shadow: 0 0 8px #a855f7; }
        .pulse-wave span:nth-child(3) { animation-delay: 0.4s; background: #ec4899; box-shadow: 0 0 8px #ec4899; }
        @keyframes wave { 0%, 100% { transform: scaleY(0.3); } 50% { transform: scaleY(1); } }
        
        .input-area { padding: 12px; background: #111827; border-top: 1px solid #1f2937; display: flex; gap: 10px; }
        input { flex: 1; padding: 12px 16px; border-radius: 24px; border: 1px solid #374151; background: #1f2937; color: #fff; outline: none; font-size: 0.95rem; }
        input:focus { border-color: #2563eb; }
        button { padding: 12px 20px; border-radius: 24px; border: none; background: #2563eb; color: #fff; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">AI Assistant</div>
    <div id="chatbox"></div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type a message..." onkeydown="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatbox = document.getElementById('chatbox');
            const msg = input.value.trim();
            if (!msg) return;

            chatbox.innerHTML += `<div class="msg user">${msg}</div>`;
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
                    body: JSON.stringify({ message: msg })
                });
                const data = await res.json();
                document.getElementById(loaderId).remove();
                chatbox.innerHTML += `<div class="msg bot">${data.response || data.error}</div>`;
            } catch (err) {
                document.getElementById(loaderId).remove();
                chatbox.innerHTML += `<div class="msg bot" style="color:#ef4444;">Error getting response</div>`;
            }
            chatbox.scrollTop = chatbox.scrollHeight;
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
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
        
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": user_message}]
        )
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
