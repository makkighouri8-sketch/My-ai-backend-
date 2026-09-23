from flask import Flask, render_template_string, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__, static_folder="../", static_url_path="")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tringo AI</title>
    <!-- Github CSS Files Link -->
    <link rel="stylesheet" href="/style.css">
    <link rel="stylesheet" href="/animations.css">

    <!-- Markdown Parser -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <!-- Syntax Highlighting for Code -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
</head>
<body>

    <!-- Top Navigation -->
    <div class="top-nav">
        <button class="nav-btn active" id="btnChat" onclick="switchTab('chatTab')">AI Chat</button>
        <button class="nav-btn" id="btnStudio" onclick="switchTab('studioTab')">3D Video Studio</button>
    </div>

    <!-- Main Content Body -->
    <div class="main-container">
        <!-- Chat Tab -->
        <div id="chatTab" class="tab-content active-tab">
            <h1 class="greeting">Hi Jamshed,</h1>
            <p class="subtext">How can I help you today?</p>
            <div class="chat-box" id="chatBox">
                <div class="message ai-message">Hello! I am Tringo AI. Ask me anything or start a Live Call.</div>
            </div>
        </div>

        <!-- 3D Studio Tab -->
        <div id="studioTab" class="tab-content">
            <h1 class="greeting">3D Studio</h1>
            <p class="subtext">Generate high quality 3D Videos & Animations</p>
            <div class="studio-card">
                <textarea class="studio-input" placeholder="Describe your 3D concept..."></textarea>
                <button class="gen-btn">⚡ Generate 3D Video</button>
            </div>
        </div>
    </div>

    <!-- Tringo Capsule Floating Dock -->
    <div class="dock-wrapper" id="dockWrapper">
        <div class="gemini-dock">
            <button class="icon-btn" title="Upload Media">
                <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            </button>
            <input type="text" class="dock-input" id="msgInput" placeholder="Ask Tringo AI..." oninput="handleInputToggle()" onkeypress="handleKeyPress(event)">

            <div class="voice-group" id="voiceGroup">
                <button class="icon-btn" id="voiceToggleBtn" onclick="toggleVoiceInput()" title="Voice Input">
                    <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                </button>
                <button class="live-btn" id="liveChatBtn" onclick="startLiveVoice()" title="Live AI Call Mode">
                    <svg viewBox="0 0 24 24"><path d="M12 3v18m-4-14v10m8-10v10m-12-6v2m16-2v2" stroke-width="2.2" stroke-linecap="round"/></svg>
                </button>
            </div>

            <button class="send-btn" id="sendBtn" onclick="sendMessage()" title="Send">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </div>

    <!-- Live Voice Call Fullscreen Screen -->
    <div class="live-overlay" id="liveOverlay">
        <div class="live-top-bar">
            <span class="live-status" id="liveStatus">Listening...</span>
        </div>

        <!-- Center Glowing Energy Orb -->
        <div class="orb-wrapper">
            <div class="energy-orb">
                <div class="orb-core"></div>
                <div class="orb-energy-ring ring-1"></div>
                <div class="orb-energy-ring ring-2"></div>
                <div class="orb-energy-ring ring-3"></div>
            </div>
        </div>

        <!-- Live Caption / Transcript -->
        <div class="live-caption" id="liveCaption">Tap the orb and start speaking...</div>

        <!-- Fixed Call Control Bar -->
        <div class="call-controls-bar">
            <button class="control-btn mute-btn" id="muteBtn" onclick="toggleMute()" title="Mute / Unmute">
                <svg id="micIcon" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                <svg id="muteIcon" style="display:none;" viewBox="0 0 24 24"><path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.53.53c0-.02.01-.04.01-.06V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.03 5.03c0 .09-.49.35-.56.35zM7.27 2.73L6 4l3 3v.5c0 1.66-1.34 3-3 3v2c.94 0 1.81-.28 2.55-.74l1.42 1.41C10.56 13.7 9.32 14 8 14v2c1.95 0 3.75-.7 5.13-1.85l2.59 2.6 1.27-1.27-9.72-9.75zM18 11c0 4.08-3.05 7.44-7 7.93v2.02c5.05-.5 9-4.76 9-9.95h-2z"/></svg>
            </button>

            <button class="control-btn end-call-btn" onclick="endLiveVoice()" title="End Call">
                <svg viewBox="0 0 24 24"><path d="M12 9c-1.6 0-3.15.25-4.6.7v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08c-.18-.17-.29-.42-.29-.7 0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.67c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28-.79-.73-1.68-1.36-2.66-1.85-.33-.16-.56-.5-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/></svg>
            </button>
        </div>
    </div>

    <!-- External Scripts -->
    <script src="/app.js"></script>
    <script src="/ai-engine.js"></script>
    <script src="/voice.js"></script>

    <!-- Live Call Overlay Logic -->
    <script>
        let isLiveActive = false;
        let isMuted = false;
        let liveRecognition = null;
        let liveIsRecognizing = false;

        function startLiveVoice() {
            const overlay = document.getElementById('liveOverlay');
            if (!overlay) return;
            overlay.classList.add('active');
            isLiveActive = true;
            isMuted = false;
            updateMuteUI();
            updateLiveStatus();
            startLiveRecognition();
        }

        function endLiveVoice() {
            const overlay = document.getElementById('liveOverlay');
            if (!overlay) return;
            overlay.classList.remove('active');
            isLiveActive = false;
            stopLiveRecognition();
            if (window.speechSynthesis) window.speechSynthesis.cancel();
        }

        function toggleMute() {
            if (!isLiveActive) return;
            isMuted = !isMuted;
            const overlay = document.getElementById('liveOverlay');
            if (overlay) overlay.classList.toggle('muted', isMuted);
            updateMuteUI();
            updateLiveStatus();
            if (isMuted) {
                stopLiveRecognition();
                if (window.speechSynthesis) window.speechSynthesis.cancel();
            } else {
                startLiveRecognition();
            }
        }

        function updateMuteUI() {
            const muteBtn = document.getElementById('muteBtn');
            const micIcon = document.getElementById('micIcon');
            const muteIcon = document.getElementById('muteIcon');
            const caption = document.getElementById('liveCaption');
            if (!muteBtn) return;

            if (isMuted) {
                muteBtn.classList.add('muted');
                if (micIcon) micIcon.style.display = 'none';
                if (muteIcon) muteIcon.style.display = 'block';
                if (caption) caption.textContent = 'Microphone is muted.';
            } else {
                muteBtn.classList.remove('muted');
                if (micIcon) micIcon.style.display = 'block';
                if (muteIcon) muteIcon.style.display = 'none';
                if (caption) caption.textContent = 'Listening... speak now.';
            }
        }

        function updateLiveStatus() {
            const status = document.getElementById('liveStatus');
            if (!status) return;
            status.textContent = isMuted ? 'Muted' : 'Listening...';
        }

        function startLiveRecognition() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition || isMuted) return;
            if (liveIsRecognizing) return;

            liveRecognition = new SpeechRecognition();
            liveRecognition.continuous = true;
            liveRecognition.interimResults = true;
            liveRecognition.lang = 'en-US';

            let finalTranscript = '';
            let silenceTimer = null;

            liveRecognition.onresult = (event) => {
                let interim = '';
                finalTranscript = '';
                for (let i = 0; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interim += event.results[i][0].transcript;
                    }
                }
                const caption = document.getElementById('liveCaption');
                if (caption) caption.textContent = interim || finalTranscript || 'Listening...';

                if (finalTranscript.trim()) {
                    if (silenceTimer) clearTimeout(silenceTimer);
                    silenceTimer = setTimeout(() => {
                        sendLiveMessage(finalTranscript.trim());
                        finalTranscript = '';
                    }, 800);
                }
            };

            liveRecognition.onend = () => {
                liveIsRecognizing = false;
                if (isLiveActive && !isMuted) {
                    try { liveRecognition.start(); liveIsRecognizing = true; } catch(e) {}
                }
            };

            liveRecognition.onerror = (event) => {
                liveIsRecognizing = false;
                if (event.error === 'not-allowed') {
                    const caption = document.getElementById('liveCaption');
                    if (caption) caption.textContent = 'Microphone access denied. Please allow mic permission.';
                }
            };

            try {
                liveRecognition.start();
                liveIsRecognizing = true;
            } catch(e) {
                console.error('Live recognition start error:', e);
            }
        }

        function stopLiveRecognition() {
            if (liveRecognition) {
                try { liveRecognition.stop(); } catch(e) {}
                liveRecognition = null;
            }
            liveIsRecognizing = false;
        }

        async function sendLiveMessage(text) {
            const caption = document.getElementById('liveCaption');
            if (caption) caption.textContent = 'Thinking...';
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, history: [] })
                });
                const data = await response.json();
                const reply = data.reply || 'No response received.';
                if (caption) caption.textContent = reply;
                speakText(reply);
            } catch (err) {
                if (caption) caption.textContent = 'Connection error. Try again.';
            }
        }

        function speakText(text) {
            if (!window.speechSynthesis) return;
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'en-US';
            utter.onend = () => {
                if (isLiveActive && !isMuted) {
                    const caption = document.getElementById('liveCaption');
                    if (caption) caption.textContent = 'Listening... speak now.';
                }
            };
            window.speechSynthesis.speak(utter);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    history = data.get("history", [])

    if not message:
        return jsonify({"reply": "Please send a message."})

    if not client:
        return jsonify({"reply": "OpenAI API key is not configured. Please set OPENAI_API_KEY."})

    try:
        messages = []
        for h in history:
            if "role" in h and "text" in h:
                role = "assistant" if h["role"] == "model" else h["role"]
                messages.append({"role": role, "content": h["text"]})
        messages.append({"role": "user", "content": message})

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        reply = completion.choices[0].message.content or "No response received."
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Tringo AI encountered an error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
