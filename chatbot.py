from flask import Flask, request, jsonify, render_template, send_file
from gtts import gTTS
import os
import tensorflow as tf
import numpy as np
import cv2
from werkzeug.utils import secure_filename
import random
# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load model
MODEL_PATH = r"C:\Users\merin\OneDrive\Desktop\pneumonia_detection_model\pneumonia_detection_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to preprocess image
def preprocess_xray(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None  
    img = cv2.resize(img, (150, 150)) / 255.0
    img = np.expand_dims(img, axis=-1)
    img = np.repeat(img, 3, axis=-1)
    img = np.expand_dims(img, axis=0)
    return img

# ✅ Route to display chatbot page
@app.route("/chatbot", methods=["GET"])
def chatbot_ui():
    return render_template("chatbot.html")
# ✅ Allowed File Extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    """Check if the file has a valid image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Route for chatbot prediction (must allow POST)
@app.route("/chatbot/predict", methods=["POST"])
def predict():
    print("✅ Received request at /predict")

    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    print(f"📸 Received {len(files)} files")  

    predictions = []

    for file in files:
        if file.filename == "" or not allowed_file(file.filename):
            print(f"🚨 Skipping invalid file: {file.filename}")
            continue  

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        print(f"✅ File saved: {file_path}")

        # ✅ Simulate a random prediction
        prediction = random.random()  # Generates a random number between 0 and 1
        result = "Pneumonia Detected 🚨" if prediction > 0.5 else "No Pneumonia ✅"

        # ✅ Add suggestions for the patient
        suggestions = {
            "Pneumonia Detected 🚨": [
                "Consult a doctor immediately.",
                "Get a chest X-ray for confirmation.",
                "Start prescribed antibiotics if confirmed.",
                "Rest and stay hydrated.",
                "Monitor for breathing difficulties."
            ],
            "No Pneumonia ✅": [
                "Maintain a healthy diet.",
                "Stay active and exercise regularly.",
                "Avoid smoking and polluted areas.",
                "If symptoms persist, consult a doctor.",
                "Get regular check-ups for lung health."
            ]
        }
        
        suggestion = random.choice(suggestions[result])  # Pick a random suggestion

        predictions.append({
            "filename": filename,
            "prediction": float(prediction),
            "result": result,
            "suggestion": suggestion
        })

    print("✅ Returning predictions:", predictions)
    return jsonify(predictions)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

