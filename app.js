// Updated Chat Box Output Line in app.js
chatBox.innerHTML += `
    <div class="message ai-message">
        <div class="ai-text">${data.reply}</div>
        <div class="ai-actions">
            <button onclick="speakText('${data.reply.replace(/'/g, "\\'")}')">🔊 Listen</button>
        </div>
    </div>
`;
