let isWaveActive = false;

function switchTab(t) {
    document.getElementById('chatTab').classList.toggle('active-tab', t === 'chat');
    document.getElementById('studioTab').classList.toggle('active-tab', t === 'studio');
    document.getElementById('chatBtn').classList.toggle('active', t === 'chat');
    document.getElementById('studioBtn').classList.toggle('active', t === 'studio');
}

function autoResize(textarea) {
    textarea.style.height = '24px';
    textarea.style.height = (textarea.scrollHeight > 120 ? 120 : textarea.scrollHeight) + 'px';
}

function startDictation(event) {
    if (event) event.preventDefault();
    const input = document.getElementById('msgInput');
    const micBtn = document.getElementById('micBtn');

    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        return alert('Voice recognition not supported on this browser.');
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SR();

    rec.onstart = () => micBtn.classList.add('active');
    rec.onresult = (e) => { input.value = e.results[0][0].transcript; autoResize(input); };
    rec.onend = () => { micBtn.classList.remove('active'); input.focus(); };

    rec.start();
    input.focus();
}

function toggleLiveWave() {
    const waveBtn = document.getElementById('waveBtn');
    const liveOverlay = document.getElementById('liveOverlay');
    
    isWaveActive = !isWaveActive;
    waveBtn.classList.toggle('listening', isWaveActive);
    liveOverlay.classList.toggle('active', isWaveActive);
}

function triggerUpload(e) {
    if (e.target.classList.contains('remove-btn')) return;
    document.getElementById('imgUpload').click();
}

function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.getElementById('imgPreview');
            img.src = e.target.result;
            document.getElementById('previewWrapper').style.display = 'flex';
            document.getElementById('uploadIcon').style.display = 'none';
            document.getElementById('uploadText').style.display = 'none';
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function removeImage(e) {
    e.stopPropagation();
    const fileInput = document.getElementById('imgUpload');
    fileInput.value = '';
    document.getElementById('imgPreview').src = '';
    document.getElementById('previewWrapper').style.display = 'none';
    document.getElementById('uploadIcon').style.display = 'block';
    document.getElementById('uploadText').style.display = 'block';
}
