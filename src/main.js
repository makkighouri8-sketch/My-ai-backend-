import { marked } from "marked";
import "./style.css";
import "./animations.css";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;

let chatHistory = [];
let isLiveActive = false;
let isMuted = false;

// Tab switching logic
window.switchTab = function (tabId) {
  document.querySelectorAll(".tab-content").forEach((tab) => tab.classList.remove("active-tab"));
  document.querySelectorAll(".nav-btn").forEach((btn) => btn.classList.remove("active"));

  document.getElementById(tabId).classList.add("active-tab");

  if (tabId === "chatTab") {
    document.getElementById("btnChat").classList.add("active");
  } else {
    document.getElementById("btnStudio").classList.add("active");
  }
};

// Dynamic input toggle & Auto-height adjustment
window.handleInputToggle = function () {
  const input = document.getElementById("msgInput");
  const sendBtn = document.getElementById("sendBtn");
  const voiceGroup = document.getElementById("voiceGroup");

  if (!input || !sendBtn || !voiceGroup) return;

  input.style.height = "auto";
  input.style.height = input.scrollHeight + "px";

  if (input.value.trim().length > 0) {
    sendBtn.style.display = "flex";
    voiceGroup.style.display = "none";
  } else {
    sendBtn.style.display = "none";
    voiceGroup.style.display = "flex";
  }
};

window.handleKeyPress = function (event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage(event);
  }
};

window.toggleVoiceInput = function () {
  // Voice input placeholder
};

// AI Markdown rendering with syntax highlighting + copy buttons
async function renderMarkdown(element, text) {
  element.innerHTML = "";
  const formattedText = marked.parse(text);
  element.innerHTML = formattedText;

  if (window.hljs) {
    element.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });
  }

  element.querySelectorAll("pre").forEach((pre) => {
    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-code-btn";
    copyBtn.innerText = "Copy";
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(pre.querySelector("code").innerText);
      copyBtn.innerText = "Copied!";
      setTimeout(() => (copyBtn.innerText = "Copy"), 2000);
    };
    pre.appendChild(copyBtn);
  });
}

// Send Message logic
window.sendMessage = async function (event) {
  if (event) event.preventDefault();

  const input = document.getElementById("msgInput");
  const message = input.value.trim();
  if (!message) return;

  const chatBox = document.getElementById("chatBox");

  const userDiv = document.createElement("div");
  userDiv.className = "message user-message";
  userDiv.textContent = message;
  chatBox.appendChild(userDiv);

  input.value = "";
  handleInputToggle();
  input.focus();
  chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });

  const aiDiv = document.createElement("div");
  aiDiv.className = "message ai-message typing-indicator";
  aiDiv.innerHTML = "<span>.</span><span>.</span><span>.</span>";
  chatBox.appendChild(aiDiv);
  chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });

  try {
    const response = await fetch(`${SUPABASE_URL}/functions/v1/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
        apikey: SUPABASE_ANON_KEY,
      },
      body: JSON.stringify({ message, history: chatHistory }),
    });

    if (!response.ok) {
      throw new Error(`Request failed (${response.status})`);
    }

    const data = await response.json();
    const reply = data.reply || "No response received.";

    aiDiv.classList.remove("typing-indicator");
    await renderMarkdown(aiDiv, reply);

    chatHistory.push({ role: "user", text: message });
    chatHistory.push({ role: "model", text: reply });
  } catch (err) {
    aiDiv.classList.remove("typing-indicator");
    aiDiv.textContent = "Error connecting to server. Please try again.";
  }

  chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });
};

// Live Voice Call overlay
window.startLiveVoice = function () {
  const overlay = document.getElementById("liveOverlay");
  if (!overlay) return;
  overlay.classList.add("active");
  isLiveActive = true;
  isMuted = false;
  updateMuteUI();
  updateLiveStatus();
};

window.endLiveVoice = function () {
  const overlay = document.getElementById("liveOverlay");
  if (!overlay) return;
  overlay.classList.remove("active");
  isLiveActive = false;
};

window.toggleMute = function () {
  if (!isLiveActive) return;
  isMuted = !isMuted;
  const overlay = document.getElementById("liveOverlay");
  if (overlay) overlay.classList.toggle("muted", isMuted);
  updateMuteUI();
  updateLiveStatus();
};

function updateMuteUI() {
  const muteBtn = document.getElementById("muteBtn");
  const micIcon = document.getElementById("micIcon");
  const muteIcon = document.getElementById("muteIcon");
  const caption = document.getElementById("liveCaption");
  if (!muteBtn) return;

  if (isMuted) {
    muteBtn.classList.add("muted");
    if (micIcon) micIcon.style.display = "none";
    if (muteIcon) muteIcon.style.display = "block";
    if (caption) caption.textContent = "Microphone is muted.";
  } else {
    muteBtn.classList.remove("muted");
    if (micIcon) micIcon.style.display = "block";
    if (muteIcon) muteIcon.style.display = "none";
    if (caption) caption.textContent = "Listening... speak now.";
  }
}

function updateLiveStatus() {
  const status = document.getElementById("liveStatus");
  if (!status) return;
  status.textContent = isMuted ? "Muted" : "Listening...";
}

// Service worker registration
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}

document.addEventListener("DOMContentLoaded", () => {
  handleInputToggle();
  const input = document.getElementById("msgInput");
  if (input) {
    input.addEventListener("input", handleInputToggle);
  }
});
