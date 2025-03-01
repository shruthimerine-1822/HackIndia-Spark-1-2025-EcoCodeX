from flask import Flask, request, jsonify, send_file
import torch
import io

app = Flask(__name__)

# Stores received model state_dicts
received_models = []  # List of received model state_dicts
client_sample_counts = []  # List of sample counts from clients

# Helper function: Serialize model
def serialize_model(state_dict):
    buffer = io.BytesIO()
    torch.save(state_dict, buffer)
    buffer.seek(0)  # Reset buffer position
    return buffer

# Helper function: Deserialize model
def deserialize_model(model_bytes):
    buffer = io.BytesIO(model_bytes)
    return torch.load(buffer)

# Route to receive model updates from local clients
@app.route('/update_model', methods=['POST'])
def update_model():
    global received_models, client_sample_counts

    try:
        if 'model' not in request.files or 'num_samples' not in request.form:
            return jsonify({"error": "Missing model file or sample count!"}), 400

        model_file = request.files['model'].read()
        num_samples = int(request.form['num_samples'])
        model_state_dict = deserialize_model(model_file)

        received_models.append(model_state_dict)
        client_sample_counts.append(num_samples)

        return jsonify({"message": "✅ Model update received!"})
    except Exception as e:
        return jsonify({"error": f"Failed to process model: {e}"}), 500

# Route to aggregate models using Weighted FedAvg
@app.route('/aggregate', methods=['POST'])
def aggregate():
    global received_models, client_sample_counts

    if len(received_models) == 0:
        return jsonify({"error": "No models received for aggregation!"}), 400

    total_samples = sum(client_sample_counts)

    if total_samples == 0:
        return jsonify({"error": "Total sample count is zero, cannot aggregate!"}), 400

    # Initialize an empty state_dict for aggregation
    aggregated_state_dict = {key: torch.zeros_like(param) for key, param in received_models[0].items()}

    # Perform weighted aggregation
    for model_state, num_samples in zip(received_models, client_sample_counts):
        weight = num_samples / total_samples  # Compute weight
        for key in model_state.keys():
            aggregated_state_dict[key] += model_state[key] * weight

    # Clear stored models after aggregation
    received_models.clear()
    client_sample_counts.clear()

    return jsonify({"message": "✅ Aggregation completed!"})

if __name__ == '__main__':  # Fixed '__name__' condition
    app.run(host='0.0.0.0', port=5000)
