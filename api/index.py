from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <!-- CACHE BYPASS TAGS -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    <title>Tringo AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        body { width: 100vw; height: 100vh; background: #000; color: #fff; font-family: sans-serif; overflow: hidden; display: flex; flex-direction: column; }
        
        .top-nav { display: flex; padding: 12px; gap: 10px; background: #000; }
        .nav-btn { flex: 1; padding: 10px; background: #141414; border: 1px solid #262626; border-radius: 20px; color: #888; font-weight: bold; cursor: pointer; text-align: center; }
        .nav-btn.active { color: #fff; background: #222; border-color: #d037fd; }

        .tab-content { flex: 1; display: none; flex-direction: column; align-items: center; justify-content: center; padding: 16px; }
        .tab-content.active-tab { display: flex; }

        .greeting { font-size: 1.4rem; font-weight: bold; margin-bottom: 6px; }
        .subtext { font-size: 0.85rem; color: #666; margin-bottom: 20px; text-align: center; }
        .chat-box { width: 100%; max-width: 400px; color: #ccc; text-align: center; margin-bottom: 20px; font-size: 0.9rem; }

        /* INPUT BAR FOR MOBILE */
        .bottom-bar { position: absolute; bottom: 15px; left: 0; width: 100%; padding: 0 10px; display: flex; align-items: center; gap: 6px; }
        .input-box { flex: 1; display: flex; align-items: center; background: #121212; border: 1px solid #282828; border-radius: 25px; padding: 2px 8px 2px 12px; gap: 6px; min-width: 0; }
        .input-box input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-size: 0.85rem; height: 38px; min-width: 0; }
        
        /* MIC BUTTON */
        .mic-btn { width: 30px; height: 30px; border-radius: 50%; background: #222; border: 1px solid #444; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; }
        .mic-btn svg { width: 16px; height: 16px; fill: #fff; }

        /* LIVE WAVE BUTTON */
        .wave-btn { width: 32px; height: 32px; border-radius: 50%; background: #a855f7; border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; }
        .wave-btn svg { width: 16px; height: 16px; stroke: #fff; }

        /* SMALL COMPACT SEND BUTTON */
        .send-btn { width: 38px; height: 38px; background: #222; border: 1px solid #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; cursor: pointer; }
        .send-btn svg { width: 16px; height: 16px; fill: #fff; margin-left: 2px; }
    </style>
</head>
<body>
    <div class="top-nav">
        <button class="nav-btn active" id="chatBtn" onclick="switchTab('chat')">AI Chat</button>
        <button class="nav-btn" id="studioBtn" onclick="switchTab('studio')">3D Video Studio</button>
    </div>

    <div class="tab-content active-tab" id="chatTab">
        <div class="greeting">Hi Jamshed,</div>
        <div class="subtext">Ask or speak anything to Tringo AI!</div>
        <div class="chat-box" id="chatDisplay">Type or speak your prompt...</div>

        <div class="bottom-bar">
            <div class="input-box">
                <input type="text" id="msgInput" placeholder="Message Tringo AI...">
                
                <!-- Mic Icon (Voice to Text) -->
                <button class="mic-btn" onclick="startDictation()" title="Voice to Text">
                    <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                </button>

                <!-- Live Voice Wave -->
                <button class="wave-btn" onclick="alert('Live Voice Active')" title="Live Voice">
                    <svg viewBox="0 0 24 24"><path d="M12 3v18M8 6v12M4 9v6M16 6v12M20 9v6" stroke-width="2.5" stroke-linecap="round"/></svg>
                </button>
            </div>

            <!-- Compact Send Button -->
            <button class="send-btn" onclick="sendMsg()">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </div>

    <div class="tab-content" id="studioTab">
        <div class="greeting">🎬 3D Video Studio</div>
        <div class="subtext">3D Animation Workspace Ready</div>
    </div>

    <script>
        function switchTab(t) {
            document.getElementById('chatTab').classList.toggle('active-tab', t === 'chat');
            document.getElementById('studioTab').classList.toggle('active-tab', t === 'studio');
            document.getElementById('chatBtn').classList.toggle('active', t === 'chat');
            document.getElementById('studioBtn').classList.toggle('active', t === 'studio');
        }

        function startDictation() {
            if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) return alert('Voice not supported');
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SR();
            rec.onresult = (e) => { document.getElementById('msgInput').value = e.results[0][0].transcript; };
            rec.start();
        }

        function sendMsg() {
            const val = document.getElementById('msgInput').value;
            if (val) document.getElementById('chatDisplay').textContent = "You: " + val;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
