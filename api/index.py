from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI - Gemini Live</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        html, body { width: 100%; height: 100%; background: #000000; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }

        .app-container { display: flex; flex-direction: column; width: 100vw; height: 100vh; background: #000000; position: relative; }

        /* Top Nav */
        .top-nav { 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 12px 16px; 
            gap: 12px; 
            background: #000000; 
            flex-shrink: 0; 
            z-index: 2;
        }
        .nav-btn { 
            flex: 1; 
            padding: 10px 16px; 
            background: #141414; 
            border: 1px solid #262626; 
            border-radius: 24px; 
            color: #888888; 
            font-weight: bold; 
            font-size: 0.9rem; 
            cursor: pointer; 
            text-align: center;
        }
        .nav-btn.active { color: #ffffff; background: #222222; border-color: #d037fd; }

        .main-content { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; padding: 20px; }

        .logo-container { margin-bottom: 20px; }
        .logo-container svg { width: 85px; height: 85px; }

        .greeting-text { font-size: 1.5rem; font-weight: bold; color: #ffffff; margin-bottom: 6px; text-align: center; }
        .sub-text { font-size: 0.9rem; color: #666666; margin-bottom: 30px; text-align: center; }

        .chat-display { width: 100%; max-width: 500px; min-height: 50px; max-height: 160px; overflow-y: auto; text-align: center; font-size: 0.95rem; color: #cccccc; line-height: 1.4; padding: 0 10px; margin-bottom: 20px; }

        /* Input Bar */
        .input-wrapper {
            position: absolute;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            width: 92%;
            max-width: 500px;
            display: flex;
            align-items: center;
            background: #121212;
            border: 1px solid #282828;
            border-radius: 30px;
            padding: 4px 6px 4px 18px;
            z-index: 5;
        }
        .input-wrapper input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #ffffff;
            font-size: 0.95rem;
            height: 44px;
        }
        .input-wrapper input::placeholder { color: #555555; }

        .input-actions { display: flex; align-items: center; gap: 8px; }

        /* Live Wave Trigger Button */
        .live-wave-trigger {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #a855f7, #6366f1);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 12px rgba(168, 85, 247, 0.4);
        }
        .live-wave-trigger svg { width: 20px; height: 20px; fill: #ffffff; }

        .send-btn { padding: 0 16px; height: 38px; background: #222222; border: 1px solid #333; border-radius: 20px; color: #ffffff; font-weight: bold; font-size: 0.85rem; cursor: pointer; }

        /* FULLSCREEN GEMINI STYLE LIVE OVERLAY */
        .gemini-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #000000;
            z-index: 100;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 40px 20px 40px 20px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        .gemini-overlay.active { opacity: 1; pointer-events: auto; }

        .overlay-top { display: flex; align-items: center; justify-content: space-between; width: 100%; max-width: 500px; }
        .brand-tag { font-size: 0.9rem; font-weight: 700; color: #a855f7; letter-spacing: 1px; text-transform: uppercase; }
        .close-btn { background: #1a1a1a; border: 1px solid #333; color: #fff; width: 36px; height: 36px; border-radius: 50%; font-size: 1.1rem; cursor: pointer; }

        /* CENTER GEMINI FLUID NEON BLOB */
        .gemini-blob-container {
            position: relative;
            width: 220px;
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .gemini-blob {
            width: 120px;
            height: 120px;
            border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
            background: linear-gradient(45deg, #00f2fe, #4facfe, #6b11ff, #d037fd);
            background-size: 200% 200%;
            filter: blur(8px);
            box-shadow: 0 0 60px rgba(79, 172, 254, 0.6), 0 0 80px rgba(208, 55, 253, 0.4);
            animation: morph-blob 6s ease-in-out infinite alternate, gradient-shift 4s ease infinite;
            transition: all 0.3s ease;
        }

        @keyframes morph-blob {
            0% { border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%; transform: scale(1) rotate(0deg); }
            50% { border-radius: 60% 40% 30% 70% / 50% 30% 70% 40%; transform: scale(1.1) rotate(180deg); }
            100% { border-radius: 50% 50% 40% 60% / 30% 60% 40% 70%; transform: scale(0.95) rotate(360deg); }
        }

        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .gemini-overlay.listening .gemini-blob {
            animation: morph-blob 2s ease-in-out infinite alternate, gradient-shift 2s ease infinite;
            transform: scale(1.25);
            box-shadow: 0 0 80px rgba(0, 242, 254, 0.8);
        }

        .gemini-overlay.speaking .gemini-blob {
            animation: morph-blob 1.2s ease-in-out infinite alternate, gradient-shift 1.5s ease infinite;
            transform: scale(1.4);
            box-shadow: 0 0 90px rgba(208, 55, 253, 0.9);
        }

        .live-status { font-size: 1.1rem; color: #ffffff; text-align: center; max-width: 90%; min-height: 50px; font-weight: 500; }

        /* GEMINI BOTTOM GLOW BAR WITH SOUND WAVES */
        .bottom-glow-bar {
            width: 92%;
            max-width: 450px;
            height: 64px;
            background: rgba(20, 20, 28, 0.9);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-radius: 35px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px 0 24px;
            box-shadow: 0 0 25px rgba(99, 102, 241, 0.25), inset 0 0 15px rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
        }

        /* SOUND WAVE BARS ANIMATION */
        .wave-bars {
            display: flex;
            align-items: center;
            gap: 5px;
            height: 30px;
        }

        .bar {
            width: 4px;
            height: 8px;
            background: linear-gradient(180deg, #00f2fe, #a855f7);
            border-radius: 4px;
            transition: height 0.2s ease;
        }

        .gemini-overlay.listening .bar {
            animation: sound-wave 1s ease-in-out infinite alternate;
        }

        .gemini-overlay.speaking .bar {
            background: linear-gradient(180deg, #ff007f, #a855f7);
            animation: sound-wave-fast 0.6s ease-in-out infinite alternate;
        }

        .bar:nth-child(1) { animation-delay: 0.1s; }
        .bar:nth-child(2) { animation-delay: 0.3s; }
        .bar:nth-child(3) { animation-delay: 0.2s; }
        .bar:nth-child(4) { animation-delay: 0.4s; }
        .bar:nth-child(5) { animation-delay: 0.15s; }

        @keyframes sound-wave {
            0% { height: 6px; }
            100% { height: 26px; }
        }

        @keyframes sound-wave-fast {
            0% { height: 10px; }
            100% { height: 32px; }
        }

        .end-btn {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: #262626;
            border: 1px solid #333;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .end-btn svg { width: 20px; height: 20px; fill: #ff4757; }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- Top Nav -->
        <div class="top-nav">
            <button class="nav-btn active">AI Chat</button>
            <button class="nav-btn">3D Video Studio</button>
        </div>

        <div class="main-content">
            <div class="logo-container">
                <svg viewBox="0 0 100 100">
                    <path fill="#d037fd" d="M50,15 C65,15 78,28 78,43 C78,65 50,85 50,85 C50,85 22,65 22,43 C22,28 35,15 50,15 Z" />
                </svg>
            </div>

            <div class="greeting-text">Hi Jamshed,</div>
            <div class="sub-text">Ask or speak anything to Tringo AI!</div>

            <div class="chat-display" id="chatDisplay">
                Tap the wave button in the input bar to start Gemini-style Live Voice Chat!
            </div>

            <!-- Input Bar -->
            <div class="input-wrapper">
                <input type="text" id="msgInput" placeholder="Message Tringo AI..." onkeypress="onKey(event)">
                <div class="input-actions">
                    <button class="live-wave-trigger" onclick="openLiveVoiceMode()" title="Live Voice Chat">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 3v18M8 6v12M4 9v6M16 6v12M20 9v6" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
                        </svg>
                    </button>
                    <button class="send-btn" onclick="sendTextChat()">Send</button>
                </div>
            </div>
        </div>

        <!-- FULLSCREEN GEMINI STYLE LIVE OVERLAY -->
        <div class="gemini-overlay" id="geminiOverlay">
            <div class="overlay-top">
                <span class="brand-tag">Tringo Live AI</span>
                <button class="close-btn" onclick="closeLiveVoiceMode()">✕</button>
            </div>

            <!-- Fluid Morphing Neon Blob -->
            <div class="gemini-blob-container">
                <div class="gemini-blob" id="geminiBlob"></div>
            </div>

            <div class="live-status" id="liveStatus">Listening... Speak now!</div>

            <!-- GEMINI BOTTOM CAPSULE SOUND WAVES -->
            <div class="bottom-glow-bar">
                <div class="wave-bars">
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                </div>

                <button class="end-btn" onclick="closeLiveVoiceMode()" title="Close Live Voice">
                    <svg viewBox="0 0 24 24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        let isLiveActive = false;
        let recognition = null;
        let synthesis = window.speechSynthesis;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                const overlay = document.getElementById('geminiOverlay');
                overlay.className = 'gemini-overlay active listening';
                document.getElementById('liveStatus').textContent = "Listening to you...";
            };

            recognition.onresult = (event) => {
                let interim = '';
                let final = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) final += event.results[i][0].transcript;
                    else interim += event.results[i][0].transcript;
                }

                if (interim) document.getElementById('liveStatus').textContent = interim;
                if (final) {
                    document.getElementById('liveStatus').textContent = final;
                    sendVoiceToAI(final);
                }
            };

            recognition.onerror = () => {
                if(isLiveActive) {
                    document.getElementById('liveStatus').textContent = "Didn't catch that. Try speaking again.";
                }
            };

            recognition.onend = () => {};
        }

        function openLiveVoiceMode() {
            if (!recognition) return alert('Speech recognition is not supported in this browser.');
            isLiveActive = true;
            document.getElementById('geminiOverlay').classList.add('active');
            synthesis.cancel();
            recognition.start();
        }

        function closeLiveVoiceMode() {
            isLiveActive = false;
            if (recognition) recognition.stop();
            if (synthesis) synthesis.cancel();
            document.getElementById('geminiOverlay').className = 'gemini-overlay';
        }

        async function sendVoiceToAI(text) {
            const overlay = document.getElementById('geminiOverlay');
            overlay.className = 'gemini-overlay active';
            document.getElementById('liveStatus').textContent = "Thinking...";

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                const reply = data.response || "No response received.";

                document.getElementById('liveStatus').textContent = reply;
                speakAIResponse(reply);
            } catch (err) {
                document.getElementById('liveStatus').textContent = "Connection error!";
            }
        }

        function speakAIResponse(text) {
            if (!synthesis) return;
            synthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            const overlay = document.getElementById('geminiOverlay');

            utterance.onstart = () => {
                overlay.className = 'gemini-overlay active speaking';
            };

            utterance.onend = () => {
                if (isLiveActive) {
                    overlay.className = 'gemini-overlay active listening';
                    document.getElementById('liveStatus').textContent = "Listening again...";
                    recognition.start();
                }
            };

            synthesis.speak(utterance);
        }

        async function sendTextChat() {
            const inp = document.getElementById('msgInput');
            const val = inp.value.trim();
            if (!val) return;

            document.getElementById('chatDisplay').textContent = "You: " + val;
            inp.value = '';

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: val })
                });
                const data = await res.json();
                document.getElementById('chatDisplay').textContent = "Tringo: " + (data.response || "No response");
            } catch (e) {
                document.getElementById('chatDisplay').textContent = "Error!";
            }
        }

        function onKey(e) { if (e.key === 'Enter') sendTextChat(); }
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
        return jsonify({"response": "Gemini API key missing."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": user_msg}]}]}
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        res_data = r.json()
        if 'candidates' in res_data:
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"response": reply})
        else:
            return jsonify({"response": "API Key Error."})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
    
