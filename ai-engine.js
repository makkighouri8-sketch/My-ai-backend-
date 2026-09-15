async function sendMsg() {
    const input = document.getElementById('msgInput');
    const val = input.value.trim();
    if (!val) return;

    document.getElementById('chatDisplay').textContent = "You: " + val;
    input.value = '';
    input.style.height = '24px';

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: val })
        });
        const data = await res.json();
        document.getElementById('chatDisplay').textContent = "Tringo: " + (data.response || "No response received.");
    } catch (e) {
        document.getElementById('chatDisplay').textContent = "Tringo: Connection Error.";
    }
}

async function generate3DVideo(type) {
    alert("Triggering " + type + " 3D Generation Engine...");
}
