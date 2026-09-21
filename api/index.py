from flask import Flask, render_template_string, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__, static_folder="../", static_url_path="")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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

    <!-- Gemini Capsule Floating Dock -->
    <div class="dock-wrapper" id="dockWrapper">
        <div class="gemini-dock">
            <button class="icon-btn" title="Upload Media">
                <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            </button>
            <input type="text" class="dock-input" id="msgInput" placeholder="Ask Tringo AI..." oninput="handleInputToggle()" onkeypress="handleKeyPress(event)">
            
            <div class="voice-group" id="voiceGroup">
                <button class="icon-btn" onclick="toggleVoiceInput()" title="Voice Input">
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
                <div class="orb-energy-ring
