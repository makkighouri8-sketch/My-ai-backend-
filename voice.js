// Voice input using the Web Speech API (SpeechRecognition)
let recognition = null;
let isRecognizing = false;

function initVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn("SpeechRecognition not supported in this browser.");
        return;
    }
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const input = document.getElementById('msgInput');
        if (!input) return;
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        input.value = transcript;
        handleInputToggle();
    };

    recognition.onend = () => {
        isRecognizing = false;
        const btn = document.getElementById('voiceToggleBtn');
        if (btn) btn.classList.remove('listening');
    };

    recognition.onerror = (event) => {
        isRecognizing = false;
        const btn = document.getElementById('voiceToggleBtn');
        if (btn) btn.classList.remove('listening');
        console.error("Speech recognition error:", event.error);
    };
}

function toggleVoiceInput() {
    if (!recognition) {
        alert("Voice input is not supported in this browser. Try Chrome or Edge.");
        return;
    }
    if (isRecognizing) {
        recognition.stop();
        isRecognizing = false;
        const btn = document.getElementById('voiceToggleBtn');
        if (btn) btn.classList.remove('listening');
    } else {
        try {
            recognition.start();
            isRecognizing = true;
            const btn = document.getElementById('voiceToggleBtn');
            if (btn) btn.classList.add('listening');
        } catch (e) {
            console.error("Could not start recognition:", e);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initVoiceInput();
});
