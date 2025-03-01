import os
import tensorflow as tf
import numpy as np
import cv2
import matplotlib.cm as cm
from flask import Flask, request, jsonify, render_template,send_file
from werkzeug.utils import secure_filename
from gtts import gTTS

# Load the trained model
MODEL_PATH = r"C:\Users\merin\OneDrive\Desktop\pneumonia_detection_model\pneumonia_detection_model.h5"

model = tf.keras.models.load_model(MODEL_PATH)

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Define Upload Folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    """Check if the file is an allowed image type."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Image Preprocessing Function
def preprocess_xray(image_path):
    """Load and preprocess the X-ray image."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None  
    img = cv2.resize(img, (150, 150))
    img = img / 255.0  
    img = np.expand_dims(img, axis=-1)  
    img = np.repeat(img, 3, axis=-1)  
    img = np.expand_dims(img, axis=0)  
    return img
def get_grad_cam(model, img_array, layer_name="conv2d"):
    """Generate Grad-CAM heatmap for the given image."""
    try:
        grad_model = tf.keras.models.Model(
            [model.inputs], [model.get_layer(layer_name).output, model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            loss = predictions[:, 0]  # Target class probability

        grads = tape.gradient(loss, conv_outputs)

        if grads is None:
            print("🚨 Gradients could not be computed! Check the layer name.")
            return None

        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs.numpy()[0]
        pooled_grads = pooled_grads.numpy()

        for i in range(pooled_grads.shape[-1]):
            conv_outputs[:, :, i] *= pooled_grads[i]

        heatmap = np.mean(conv_outputs, axis=-1)
        heatmap = np.maximum(heatmap, 0)  # ReLU
        heatmap /= np.max(heatmap) if np.max(heatmap) != 0 else 1  # Normalize

        return heatmap

    except Exception as e:
        print(f"🚨 Error in get_grad_cam: {e}")
        return None

def overlay_heatmap(img_path, heatmap):
    """Overlay Grad-CAM heatmap onto the original image."""
    try:
        img = cv2.imread(img_path)
        if img is None:
            print(f"🚨 Could not load image: {img_path}")
            return None

        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap = np.uint8(255 * heatmap)  
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        superimposed_img = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
        output_path = img_path.replace(".png", "_gradcam.png").replace(".jpg", "_gradcam.jpg")
        cv2.imwrite(output_path, superimposed_img)

        print(f"✅ Grad-CAM saved at: {output_path}")
        return output_path

    except Exception as e:
        print(f"🚨 Error in overlay_heatmap: {e}")
        return None



# ✅ Serve HTML Pages
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hospitals")
def hospitals():
    return render_template("hospitals.html")

@app.route("/server")
def server():
    return render_template("server.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")




@app.route("/predict", methods=["POST"])
def predict():
    print("✅ Received request at /predict")

    if "files" not in request.files:
        print("🚨 No files received")
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    print(f"📸 Received {len(files)} files")  # Log the number of files

    predictions = []

    for file in files:
        if file.filename == "" or not allowed_file(file.filename):
            print(f"🚨 Skipping invalid file: {file.filename}")
            continue  

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        print(f"✅ File saved: {file_path}")

        input_image = preprocess_xray(file_path)
        if input_image is None:
            print(f"🚨 Error processing image: {filename}")
            continue  

        # 🔹 Make Prediction
        prediction = model.predict(input_image)[0][0]
        threshold = 0.5
        result = "Pneumonia Detected 🚨" if prediction > threshold else "No Pneumonia ✅"

        # 🔹 Generate Grad-CAM Heatmap
        heatmap = get_grad_cam(model, input_image, layer_name="conv2d")  
        gradcam_path = None
        if heatmap is not None:
            gradcam_path = overlay_heatmap(file_path, heatmap)  # Save Grad-CAM image

        predictions.append({
            "filename": filename,
            "prediction": float(prediction),
            "result": result,
            "gradcam": gradcam_path  # 🔹 Include Grad-CAM image in response
        })

    print("✅ Returning predictions:", predictions)
    return jsonify(predictions)


@app.route("/speak", methods=["POST"])
def speak():
    data = request.json
    action = data.get("action", "").strip().lower()

    responses = {
        "predict_success": "The prediction is complete. The X-ray analysis shows no pneumonia.",
        "pneumonia_detected": "Warning! Pneumonia detected in the X-ray scan. Please consult a doctor.",
        "upload_confirm": "pleas upload image from the files",
        "clear_history": "Prediction history cleared. You can start a new analysis.",
        "voice_activation": "Voice command activated. Say 'upload an image' or 'predict now' or 'clear histroy' to proceed."
    }

    text = responses.get(action, "Sorry, I didn't understand the request.")

    # Save the speech file inside the "static" folder
    output_file = os.path.join("static", "speech.mp3")
    tts = gTTS(text=text, lang="en")
    tts.save(output_file)

    return send_file(output_file, as_attachment=True)


# ✅ Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
