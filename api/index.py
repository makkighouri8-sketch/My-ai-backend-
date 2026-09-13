import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Single-page HTML + Integrated Rounded CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tringo AI Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #050505; color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 15px; }
        .container { width: 100%; max-width: 420px; background: #111111; border: 1px solid #222; border-radius: 24px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
        
        /* Navigation / Tabs */
        .nav-tabs { display: flex; justify-content: space-around; border-bottom: 1px solid #222; padding-bottom: 12px; margin-bottom: 20px; }
        .tab { color: #666; font-size: 0.9rem; font-weight: 600; text-decoration: none; padding: 6px 12px; }
        .tab.active { color: #ff2a5f; border-bottom: 2px solid #ff2a5f; }

        /* Rounded Mode Selector Controls */
        .mode-selector { display: flex; gap: 8px; background: #0a0a0a; padding: 6px; border-radius: 20px; border: 1px solid #222; margin-bottom: 20px; }
        .sub-mode-btn { flex: 1; padding: 12px; border: 1px solid transparent; background: transparent; color: #888; font-weight: bold; font-size: 0.85rem; border-radius: 14px; cursor: pointer; transition: 0.3s; display: flex; align-items: center; justify-content: center; gap: 6px; }
        .sub-mode-btn.active { background: #2563eb; color: #ffffff; }

        /* Card Container */
        .card { background: #0a0a0a; border: 1px solid #1e1e1e; border-radius: 18px; padding: 16px; }
        .card-title { color: #ff2a5f; font-size: 0.95rem; font-weight: bold; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }

        /* Rounded Textarea Input Box */
        .studio-input { width: 100%; height: 100px; background: #000000; border: 1px solid #333; color: #fff; padding: 14px; border-radius: 16px; resize: none; margin-bottom: 14px; outline: none; font-size: 0.9rem; }
        .studio-input:focus { border-color: #2563eb; }

        /* Rounded Action Button */
        .gen-btn { width: 100%; padding: 14px; background: #2563eb; border: none; color: #ffffff; font-weight: bold; border-radius: 25px; cursor: pointer; transition: 0.2s; font-size: 0.95rem; box-shadow: 0 0 12px rgba(37, 99, 235, 0.4); }
        .gen-btn:active { transform: scale(0.98); }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-tabs">
            <a href="#" class="tab">AI Chat</a>
            <a href="#" class="tab active">3D Video Studio</a>
        </div>

        <div class="mode-selector">
            <button class="sub-mode-btn active">Prompt to 3D</button>
            <button class="sub-mode-btn">Pic to Animation</button>
        </div>

        <div class="card">
            <div class="card-title">Generate 3D Animation Video</div>
            <textarea class="studio-input" placeholder="Describe your 3D animation scene (e.g., A funny 3D character talking about finance in space)..."></textarea>
            <button class="gen-btn">Render 3D Video</button>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
    
