from flask import Flask, request, jsonify
import g4f

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Server is running online!"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": user_message}]
        )
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
  
