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
    <title>Tringo AI - Live Voice</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        html, body { width: 100%; height: 100%; background: #050505; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }

        .app-container { display: flex; flex-direction: column; width: 100vw; height: 100vh; background: #050505; position: relative; }

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
        .nav-btn.active { 
            color: #ffffff; 
            background: #222222; 
            border-color: #d037fd; 
        }

        .main-content { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; padding: 20px; }

        /* Main Logo */
        .logo-container { margin-bottom: 24px; }
        .logo-container svg { width: 90px; height: 90px; }

        .greeting-text { font-size: 1.5rem; font-weight: bold; color: #ffffff; margin-bottom: 6px; text-align: center; }
        .sub-text { font-size: 0.9rem; color: #666666; margin-bottom: 30px; text-align: center; }

        .chat-display { width: 100%; max-width: 500px; min-height: 50px; max-height: 160px; overflow-y: auto; text-align: center; font-size: 0.95rem; color: #cccccc; line-height: 1.4; padding: 0 10px; margin-bottom: 20px; }

        /* Bottom Input Bar */
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

        /* Live Wave Mic Icon in Input Box */
        .live-wave-trigger {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #d037fd, #7000ff);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 12px rgba(208, 55, 253, 0.4);
            transition: transform 0.2s ease;
        }
        .live-wave-trigger:active { transform: scale(0.92); }
        .live-wave-trigger svg { width: 22px; height: 22px; fill: #ffffff; }

        .send-btn { padding: 0 16px; height: 38px; background: #222222; border: 1px solid #333; border-radius: 20px; color: #ffffff; font-weight: bold; font-size: 0.85rem; cursor: pointer; }

        /* FULLSCREEN LIVE NEON VOICE OVERLAY */
        .live-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #030308;
            z-index: 100;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 40px 20px 60px 20px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s ease;
        }
        .live-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        .overlay-header { display: flex; align-items: center; justify-content: space-between; width: 100%; max-width: 500px; }
        .live-badge { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: bold; color: #d037fd; text-transform: uppercase; letter-spacing: 1px; }
        .live-dot { width: 8px; height: 8px; border-radius: 50%; background: #d037fd; box-shadow: 0 0 8px #d037fd; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.3; } }

        .close-overlay-btn { background: #1a1a1a; border: 1px solid #333; color: #fff; width: 36px; height: 36px; border-radius: 50%; font-size: 1.2rem; cursor: pointer; }

        /* NEON WAVE ANIMATION CENTER */
        .wave-container {
            position: relative;
            width: 260px;
            height: 260px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .neon-orb {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            background: radial-gradient(circle, #d037fd 0%, #7000ff 70%, #000000 100%);
            box-shadow: 0 0 40px rgba(208, 55, 253, 0.8), inset 0 0 20px rgba(255, 255, 255, 0.5);
            position: relative;
            z-index: 2;
            transition: all 0.3s ease;
        }

        .neon-wave {
            position: absolute;
            width: 130px;
            height: 130px;
            border-radius: 50%;
            border: 2px solid rgba(208, 55, 253, 0.6);
            box-shadow: 0 0 20px rgba(208, 55, 253, 0.4);
            animation: wave-expand 2s infinite linear;
            z-index: 1;
        }
        .neon-wave:nth-child(2) { animation-delay: 0.6s; border-color: rgba(112, 0, 255, 0.6); }
        .neon-wave:nth-child(3) { animation-delay: 1.2s; border-color: rgba(0, 212, 255, 0.6); }

        @keyframes wave-expand {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(2.2); opacity: 0; }
        }

        /* Active Voice State Styles */
        .live-overlay.listening .neon-orb {
            animation: orb-user-pulse 0.8s infinite alternate;
            background: radial-gradient(circle, #00d4ff 0%, #0051ff 70%, #000000 100%);
            box-shadow: 0 0 50px rgba(0, 212, 255, 0.9);
        }

        .live-overlay.speaking .neon-orb {
            animation: orb-ai-speak 0.6s infinite alternate;
            background: radial-gradient(circle, #ff007f 0%, #d037fd 70%, #000000 100%);
            box-shadow: 0 0 60px rgba(255, 0, 127, 0.9);
        }

        @keyframes orb-user-pulse {
            0% { transform: scale(0.95); }
            100% { transform: scale(1.18); }
        }

        @keyframes orb-ai-speak {
            0% { transform: scale(1.0); }
            100% { transform: scale(1.3); }
        }

        .live-status-text {
            font-size: 1.1rem;
            color: #ffffff;
            font-weight: 500;
            text-align: center;
            max-width: 90%;
            min-height: 60px;
        }

        .end-call-btn {
            width: 65px;
            height: 65px;
            border-radius: 50%;
            background: #ff2a5f;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 20px rgba(255, 42, 95, 0.5);
        }
        .end-call-btn svg { width: 30px; height: 30px; fill: #ffffff; }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- Top Nav Bar -->
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
                Tap the gradient wave icon in the input bar for Live Voice Chat!
            </div>

            <!-- Input Bar with Live Wave Button Inside -->
            <div class="input-wrapper">
                <input type="text" id="msgInput" placeholder="Message Tringo AI..." onkeypress="onKey(event)">
                <div class="input-actions">
                    <!-- Live Voice Wave Button -->
                    <button class="live-wave-trigger" onclick="openLiveVoiceMode()" title="Live Voice Chat">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 3v18M8 6v12M4 9v6M16 6v12M20 9v6" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
                        </svg>
                    </button>
                    <button class="send-btn" onclick="sendTextChat()">Send</button>
                </div>
            </div>
        </div>

        <!-- FULLSCREEN LIVE NEON VOICE OVERLAY -->
        <div class="live-overlay" id="liveOverlay">
            <div class="overlay-header">
                <div class="live-badge">
                    <div class="live-dot"></div>
                    <span>Tringo Live Voice</span>
                </div>
                <button class="close-overlay-btn" onclick="closeLiveVoiceMode()">✕</button>
            </div>

            <!-- Neon Waves & Orb Center -->
            <div class="wave-container">
                <div class="neon-wave"></div>
                <div class="neon-wave"></div>
                <div class="neon-wave"></div>
                <div class="neon-orb" id="neonOrb"></div>
            </div>

            <div class="live-status-text" id="liveStatusText">
                Listening... Speak now!
            </div>

            <button class="end-call-btn" onclick="closeLiveVoiceMode()" title="End Live Voice">
                <svg viewBox="0 0 24 24">
                    <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08c-.18-.17-.29-.42-.29-.7 0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.67c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.11-.7-.28-.79-.74-1.69-1.36-2.67-1.85-.33-.16-.56-.5-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
                </svg>
            </button>
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
                const overlay = document.getElementById('liveOverlay');
                overlay.className = 'live-overlay active listening';
                document.getElementById('liveStatusText').textContent = "Listening to you...";
            };

            recognition.onresult = (event) => {
                let interim = '';
                let final = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) final += event.results[i][0].transcript;
                    else interim += event.results[i][0].transcript;
                }

                if (interim) document.getElementById('liveStatusText').textContent = interim;
                if (final) {
                    document.getElementById('liveStatusText').textContent = final;
                    sendVoiceToAI(final);
                }
            };

            recognition.onerror = () => {
                if(isLiveActive) {
                    document.getElementById('liveStatusText').textContent = "Didn't catch that. Speaking again?";
                    setTimeout(() => { if(isLiveActive) recognition.start(); }, 1500);
                }
            };

            recognition.onend = () => {
                // Keep listening loop active while live mode is open
            };
        }

        function openLiveVoiceMode() {
            if (!recognition) return alert('Speech recognition is not supported in this browser.');
            isLiveActive = true;
            document.getElementById('liveOverlay').classList.add('active');
            synthesis.cancel();
            recognition.start();
        }

        function closeLiveVoiceMode() {
            isLiveActive = false;
            if (recognition) recognition.stop();
            if (synthesis) synthesis.cancel();
            document.getElementById('liveOverlay').className = 'live-overlay';
        }

        async function sendVoiceToAI(text) {
            const overlay = document.getElementById('liveOverlay');
            overlay.className = 'live-overlay active';
            document.getElementById('liveStatusText').textContent = "Thinking...";

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                const reply = data.response || "I didn't hear anything.";

                document.getElementById('liveStatusText').textContent = reply;
                speakAIResponse(reply);
            } catch (err) {
                document.getElementById('liveStatusText').textContent = "Connection error!";
            }
        }

        function speakAIResponse(text) {
            if (!synthesis) return;
            synthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            const overlay = document.getElementById('liveOverlay');

            utterance.onstart = () => {
                overlay.className = 'live-overlay active speaking';
            };

            utterance.onend = () => {
                if (isLiveActive) {
                    overlay.className = 'live-overlay active listening';
                    document.getElementById('liveStatusText').textContent = "Listening again...";
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
    
