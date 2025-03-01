# HackIndia-Spark-1-2025-EcoCodeX
PneumoAI is a Federated Learning-powered medical AI system for pneumonia detection using chest X-ray images. It features secure training across hospitals, voice-controlled predictions, and an AI chatbot for diagnosis and recommendations. 🏥🔬

🤖 AI Diagnosis Disease with Federated Learning

This project implements Federated Learning for AI-based disease diagnosis, currently focusing on pneumonia detection from chest X-ray images. In the future, it will be expanded to detect multiple diseases, ensuring data privacy while leveraging collaborative model training.

🚀 Features

Federated Learning: Enables hospitals to train models collaboratively without sharing raw patient data.

Pneumonia Detection: Uses deep learning to analyze chest X-ray images for pneumonia.

Voice Command Support: Allows users to upload images, request predictions, and clear history using voice commands.

AI Chatbot (Future Integration): Will accept X-ray images and provide AI-powered diagnostic assistance.

Central Server (Future Integration): A dashboard for hospitals to coordinate model training.

Flask API: Facilitates secure predictions and chatbot interactions.

📂 Project Structure

📂 federated-medical-ai
│── 📂 static                 # Static files (CSS, JS, images, uploads)
│   │── 📂 uploads            # Stores uploaded X-ray images
│   │── style.css             # Main CSS file
│   │── script.js             # Main JavaScript file
│── 📂 templates              # HTML pages for Flask
│   │── index.html            # Home page (Main interface)
│   │── hospitals.html        # Hospital interface
│   │── server.html           # Server status (Future Integration)
│   │── upload.html           # Upload page
│   │── chatbot.html          # Chatbot interface (Future Integration)
│── api.py                    # Flask backend (Handles predictions)
│── chatbot.py                # AI chatbot logic (Future Integration)
│── requirements.txt           # Python dependencies
│── run.py                     # Runs the Flask app
│── README.md                  # Documentation

🖼 Usage

1.Upload Chest X-ray Images:

Navigate to the Upload page and select an X-ray image.

Click Predict to analyze the image.

2.Use Voice Commands:

Say "Upload an image", "Predict now", or "Clear history" to interact hands-free.

3.Chatbot Assistance (Future Integration):

The chatbot will soon assist with medical queries and predictions.

🔥 Future Enhancements

Multi-disease Detection: Extend support for Tuberculosis, COVID-19, and more.

EHR Integration: Link AI diagnostics with electronic health records.

Enhanced Chatbot: Implement an AI assistant for real-time medical advice.

🤝 Contributing

Feel free to fork, improve, and submit pull requests!

📜 License

This project is open-source under the MIT License.
