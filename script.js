// ✅ Get Elements
const imageInput = document.getElementById("imageUpload");
const resultsContainer = document.getElementById("results");
const loader = document.getElementById("loader");
const previewContainer = document.getElementById("imagePreviews");
const historyContainer = document.getElementById("predictionHistory");
const progressBar = document.getElementById("confidenceBar");
// ✅ Initialize Speech Recognition



// ✅ Initialize Speech Recognition
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = false;
recognition.lang = "en-US";

// ✅ Handle Recognized Speech
recognition.onresult = function (event) {
    let transcript = event.results[0][0].transcript.toLowerCase();
    console.log("Voice Command:", transcript);

    if (transcript.includes("upload an image")) {
        speak("upload_confirm");
        setTimeout(() => {
            imageInput.click(); // ✅ Open file picker
        }, 1000);
    } else if (transcript.includes("predict now")) {
        speak("predict_success");
        predict();
    } else if (transcript.includes("clear history")) {
        speak("clear_history");
        clearHistory();
    } else {
        speak("voice_activation");
    }
};

// ✅ Start Voice Recognition
function startListening() {
    recognition.start();
    console.log("Listening for commands...");
}

let currentAudio = null; // Store the currently playing audio

// ✅ Fetch & Play AI-Generated Speech (Fix Overlapping Issue)
function speak(action) {
    fetch("/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: action }),
    })
    .then(response => response.blob())
    .then(blob => {
        // Stop the current audio if it's already playing
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0; // Reset audio position
        }

        // Play new audio
        const url = URL.createObjectURL(blob);
        currentAudio = new Audio(url);
        currentAudio.play();
    })
    .catch(error => console.error("Error:", error));
}

// ✅ Add Button to Activate Voice Control
document.addEventListener("DOMContentLoaded", () => {
    const voiceBtn = document.createElement("button");
    voiceBtn.textContent = "🎤 Activate Voice Control";
    voiceBtn.onclick = startListening;
    voiceBtn.style = "position: fixed; bottom: 20px; right: 20px; padding: 10px; background: blue; color: white; border: none; border-radius: 5px; cursor: pointer;";
    document.body.appendChild(voiceBtn);
});


// ✅ Save & Display Prediction History
function savePrediction(result, confidence) {
    let history = JSON.parse(localStorage.getItem("predictions")) || [];
    history.unshift({ result, confidence, timestamp: new Date().toLocaleString() });

    localStorage.setItem("predictions", JSON.stringify(history));
    displayHistory();
}

function displayHistory() {
    let history = JSON.parse(localStorage.getItem("predictions")) || [];
    historyContainer.innerHTML = history
        .map((entry) => `
            <div class="history-item">
                <p>${entry.timestamp}: <strong>${entry.result}</strong> (${entry.confidence}%)</p>
            </div>
        `)
        .join("");
}



// ✅ Show Previews for Multiple Images
imageInput.addEventListener("change", function () {
    previewContainer.innerHTML = ""; // Clear previous previews

    if (!imageInput.files.length) {
        previewContainer.innerHTML = "<p>No images selected.</p>";
        return;
    }

    Array.from(imageInput.files).forEach((file, index) => {
        if (file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const imgDiv = document.createElement("div");
                imgDiv.classList.add("preview-item");

                const img = document.createElement("img");
                img.src = e.target.result;
                img.style = "width: 100px; height: auto; margin: 5px; border-radius: 10px; border: 2px solid white;";

                const label = document.createElement("p");
                label.textContent = "Processing..."; // Placeholder for result

                // ✅ Add individual progress bar for each image
                

                const progressBarContainer = document.createElement("div");
                progressBarContainer.classList.add("progress-bar");
                const progressBar = document.createElement("div");
                progressBarContainer.appendChild(progressBar);
                progressBar.style.width = "0%";

                imgDiv.appendChild(img);
                imgDiv.appendChild(label);
                imgDiv.appendChild(progressBar);
                previewContainer.appendChild(imgDiv);
            };
            reader.readAsDataURL(file);
        }
    });
});
let voiceAction = null;  // Define a global variable for voice responses

// ✅ Prediction Function for Multiple Images
async function predict() {
    if (!imageInput.files.length) {
        alert("Please upload images first.");
        return;
    }
    document.querySelectorAll(".progress-bar").forEach(bar => {
        bar.style.width = "0%"; // Reset progress bars
    });
    

    loader.style.display = "block";
    resultsContainer.innerHTML = "";

    const formData = new FormData();
    for (const file of imageInput.files) {
        formData.append("files", file);
    }

    try {
        const response = await fetch("/predict", {

            method: "POST",
            body: formData,
        });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        loader.style.display = "none";  // ✅ Hide Loader
        resultsContainer.innerHTML = "";  // ✅ Clear Previous Results

if (data.error) {
    resultsContainer.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
} else {
    data.forEach((item, index) => {
        resultsContainer.innerHTML += `
            <div class="result-item">
                <p><strong>${item.filename}</strong>: ${item.result} (${(item.prediction * 100).toFixed(2)}%)</p>
                <img src="${item.gradcam}" alt="Grad-CAM Heatmap" style="width: 150px; border-radius: 8px;">
        
            </div>
        `;

        // ✅ Find the corresponding image preview and update the text
        const imgDiv = previewContainer.children[index];
        if (imgDiv) {
            imgDiv.querySelector("p").textContent = item.result;

            // ✅ Update Progress Bar
            const confidence = Math.round(item.prediction * 100);
            const progressBar = imgDiv.querySelector(".progress-bar");
            if (progressBar) {
                progressBar.style.width = `${confidence}%`;
                progressBar.style.backgroundColor = confidence > 50 ? "red" : "green";
            }
             
            // ✅ Save Prediction to History
            savePrediction(item.result, confidence);
            // ✅ Set voice action (ensure only one voice response)
            if (!voiceAction) {
                voiceAction = item.prediction > 0.5 ? "pneumonia_detected" : "predict_success";
            }
        }
    });
    // ✅ Speak the final decision (only one response)
    if (voiceAction) {
        speak(voiceAction);
    }
}

    } catch (error) {
        loader.style.display = "none";
        resultsContainer.innerHTML = `<p style="color: red;">Error connecting to server.</p>`;
        speak("voice_activation");
    }
}

// ✅ Reset Prediction History
function clearHistory() {
    localStorage.removeItem("predictions");
    historyContainer.innerHTML = "<p>History Cleared!</p>";
}
// Background Slider Logic
let currentImage = 1;
const images = document.querySelectorAll('.background-slider');

setInterval(() => {
    const current = document.querySelector(`.background-slider.image${currentImage}`);
    current.classList.remove('show');
    current.classList.add('slide-out-left');

    currentImage = (currentImage % 3) + 1;
    const next = document.querySelector(`.background-slider.image${currentImage}`);
    next.classList.add('show');
    next.classList.remove('slide-in-right', 'slide-out-left');

    // Reset classes after animation
    setTimeout(() => {
        current.classList.remove('slide-out-left');
        next.classList.remove('slide-in-right');
    }, 1000); // Match transition duration
}, 5000); // Change image every 5 seconds
    
