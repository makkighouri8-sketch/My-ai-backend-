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

        /* Top Nav */
        .top-nav { 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 10px 16px; 
            gap: 12px; 
            background: #000000; 
            flex-shrink: 0; 
        }
        .nav-btn { 
            flex: 1; 
            padding: 10px 16px; 
            background: #181818; 
            border: 1px solid #2a2a2a; 
            border-radius: 24px; 
            color: #888888; 
            font-weight: bold; 
            font-size: 0.9rem; 
            cursor: pointer; 
            text-align: center;
            transition: all 0.3s ease;
        }
        .nav-btn.active { 
            color: #ffffff; 
            background: #222222; 
            border-color: #d037fd; 
            box-shadow: 0 0 10px rgba(208, 55, 253, 0.25);
        }

        .main-content { flex: 1; position: relative; width: 100%; height: calc(100vh - 65px); overflow: hidden; }
        .panel { display: none; width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
        .panel.active { display: flex; flex-direction: column; }

        /* Live Voice Chat Panel */
        #chatPanel { position: relative; background: #050505; align-items: center; justify-content: center; }

        .voice-orb-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }

        .voice-orb {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            background: radial-gradient(circle, #d037fd 0%, #7000ff 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 35px rgba(208, 55, 253, 0.4);
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .voice-orb svg {
            width: 50px;
            height: 50px;
            fill: #ffffff;
        }

        .voice-orb.listening {
            animation: pulse-ring 1.5s infinite;
            background: radial-gradient(circle, #2563eb 0%, #00d4ff 100%);
            box-shadow: 0 0 45px rgba(37, 99, 235, 0.6);
        }

        .voice-orb.speaking {
            animation: speak-wave 0.8s infinite alternate;
            background: radial-gradient(circle, #ff007f 0%, #d037fd 100%);
            box-shadow: 0 0 50px rgba(255, 0, 127, 0.7);
        }

        @keyframes pulse-ring {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 25px rgba(37, 99, 235, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
        }

        @keyframes speak-wave {
            0% { transform: scale(0.95); }
            100% { transform: scale(1.15); }
        }

        .status-tag {
            margin-top: 18px;
            font-size: 0.95rem;
            color: #aaaaaa;
            font-weight: 500;
        }

        .live-transcript-box {
            width: 90%;
            max-width: 450px;
            min-height: 70px;
            background: rgba(20, 20, 20, 0.8);
            border: 1px solid #2a2a2a;
            border-radius: 16px;
            padding: 14px 18px;
            text-align: center;
            font-size: 0.95rem;
            color: #e0e0e0;
            line-height: 1.4;
            margin-bottom: 20px;
        }

        .chat-bar { position: absolute; bottom: 20px; left: 4%; width: 92%; display: flex; gap: 8px; z-index: 5; }
        .chat-bar input { flex: 1; height: 48px; background: #151515; border: 1px solid #333; border-radius: 24px; padding: 0 16px; color: #fff; outline: none; font-size: 0.95rem; }
        .chat-bar input:focus { border-color: #d037fd; }
        .chat-bar button { padding: 0 20px; height: 48px; background: #d037fd; border: none; border-radius: 24px; color: #fff; font-weight: bold; cursor: pointer; }

        /* 3D Studio Panel */
        #studioPanel { overflow-y: auto; padding: 16px; background: #050505; z-index: 10; }
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
        <!-- Top Nav Bar -->
        <div class="top-nav">
            <button class="nav-btn active" id="tabChat" onclick="changeTab('chat')">Live Voice Chat</button>
            <button class="nav-btn" id="tabStudio" onclick="changeTab('studio')">3D Video Studio</button>
        </div>

        <div class="main-content">
            <!-- Voice Chat Panel -->
            <div id="chatPanel" class="panel active">
                
                <div class="voice-orb-container">
                    <div class="voice-orb" id="voiceOrb" onclick="toggleVoiceLive()">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                        </svg>
                    </div>
                    <div class="status-tag" id="statusTag">Tap mic button to talk live</div>
                </div>

                <div class="live-transcript-box" id="transcriptBox">
                    Tap the mic button and speak...
                </div>

                <div class="chat-bar">
                    <input type="text" id="msgInput" placeholder="Message Tringo AI..." onkeypress="onKey(event)">
                    <button onclick="sendTextChat()">Send</button>
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
        let isListening = false;
        let recognition = null;
        let synthesis = window.speechSynthesis;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                isListening = true;
                const orb = document.getElementById('voiceOrb');
                orb.className = 'voice-orb listening';
                document.getElementById('statusTag').textContent = 'Listening... Speak now';
            };

            recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                if (interimTranscript) {
                    document.getElementById('transcriptBox').textContent = "You: " + interimTranscript;
                }
                if (finalTranscript) {
                    document.getElementById('transcriptBox').textContent = "You: " + finalTranscript;
                    processVoiceInput(finalTranscript);
                }
            };

            recognition.onerror = () => {
                stopVoiceState();
                document.getElementById('statusTag').textContent = 'Error listening. Tap to try again.';
            };

            recognition.onend = () => {
                if (isListening) stopVoiceState();
            };
        } else {
            document.getElementById('statusTag').textContent = 'Voice recognition not supported in browser.';
        }

        function toggleVoiceLive() {
            if (!recognition) return alert('Speech recognition not supported in this browser.');
            if (isListening) {
                recognition.stop();
                stopVoiceState();
            } else {
                synthesis.cancel();
                recognition.start();
            }
        }

        function stopVoiceState() {
            isListening = false;
            const orb = document.getElementById('voiceOrb');
            orb.className = 'voice-orb';
            document.getElementById('statusTag').textContent = 'Tap mic button to talk live';
        }

        async function processVoiceInput(userText) {
            stopVoiceState();
            document.getElementById('statusTag').textContent = 'Thinking...';

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userText })
                });
                const data = await res.json();
                const reply = data.response || "I didn't catch that.";

                document.getElementById('transcriptBox').textContent = "Tringo: " + reply;
                speakResponse(reply);
            } catch (err) {
                document.getElementById('statusTag').textContent = 'Server error!';
            }
        }

        function speakResponse(text) {
            if (!synthesis) return;
            synthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            const orb = document.getElementById('voiceOrb');

            utterance.onstart = () => {
                orb.className = 'voice-orb speaking';
                document.getElementById('statusTag').textContent = 'Tringo AI Speaking...';
            };

            utterance.onend = () => {
                orb.className = 'voice-orb';
                document.getElementById('statusTag').textContent = 'Tap mic button to talk live';
            };

            synthesis.speak(utterance);
        }

        async function sendTextChat() {
            const inp = document.getElementById('msgInput');
            const val = inp.value.trim();
            if (!val) return;

            document.getElementById('transcriptBox').textContent = "You: " + val;
            inp.value = '';
            document.getElementById('statusTag').textContent = 'Thinking...';

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: val })
                });
                const data = await res.json();
                const reply = data.response || "No response";

                document.getElementById('transcriptBox').textContent = "Tringo: " + reply;
                speakResponse(reply);
            } catch (e) {
                document.getElementById('statusTag').textContent = 'Connection error!';
            }
        }

        function changeTab(tab) {
            const chatPanel = document.getElementById('chatPanel');
            const studioPanel = document.getElementById('studioPanel');
            const tabChat = document.getElementById('tabChat');
            const tabStudio = document.getElementById('tabStudio');

            if (tab === 'chat') {
                tabChat.classList.add('active');
                tabStudio.classList.remove('active');
                chatPanel.style.display = 'flex';
                studioPanel.style.display = 'none';
            } else {
                tabStudio.classList.add('active');
                tabChat.classList.remove('active');
                chatPanel.style.display = 'none';
                studioPanel.style.display = 'block';
                if(synthesis) synthesis.cancel();
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

        let uploadedImgBase64 = null;

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
                statusTxt.textContent = 'Animating image into 3D... Please w
