from flask import Flask, request, jsonify, send_file
import torch
import io
import requests

app = Flask(__name__)

CENTRAL_SERVER_URL = "http://192.168.72.183:5000"

# Helper functions for serialization
def serialize_model(state_dict):
    buffer = io.BytesIO()
    torch.save(state_dict, buffer)
    buffer.seek(0)  # Reset buffer position
    return buffer

def deserialize_model(model_bytes):
    buffer = io.BytesIO(model_bytes)
    return torch.load(buffer)

# Route to send model updates to central server
@app.route('/send_model', methods=['POST'])
def send_model():
    try:
        model_state = serialize_model({})  # Placeholder for model state
        files = {"model": ("model.pth", model_state, "application/octet-stream")}
        data = {"num_samples": "32"}  # Placeholder for sample count

        response = requests.post(f"{CENTRAL_SERVER_URL}/update_model", files=files, data=data)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to send model: {e}"}), 500

@app.route('/fetch_global_model', methods=['GET'])
def fetch_global_model():
    try:
        response = requests.get(f"{CENTRAL_SERVER_URL}/get_model")
        if response.status_code == 200:
            global_model_weights = deserialize_model(response.content)
            return jsonify({"message": "✅ Global model updated!"})
        else:
            return jsonify({"error": "Failed to fetch model"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to central server: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
