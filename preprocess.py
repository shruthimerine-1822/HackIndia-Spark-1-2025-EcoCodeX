import tensorflow as tf
import numpy as np

# Load the model
model = tf.keras.models.load_model("your_model.h5")

# Example: Creating a random input (Modify this based on your actual input shape)
input_shape = model.input_shape[1:]  # Exclude batch size
sample_input = np.random.rand(1, *input_shape)  # Create a sample input

# Make prediction
prediction = model.predict(sample_input)

# Print prediction
print("Prediction:", prediction)


