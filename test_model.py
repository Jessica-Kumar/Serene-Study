import pickle
import numpy as np
import os

model_path = 'trained_model.sav'

if not os.path.exists(model_path):
    print(f"Error: {model_path} not found.")
    exit(1)

try:
    loaded_model = pickle.load(open(model_path, 'rb'))
    print("Model loaded successfully.")
    
    # Test prediction with dummy data (24 features)
    input_data = [0] * 24
    input_np = np.asarray(input_data).reshape(1, -1)
    prediction = loaded_model.predict(input_np)
    print(f"Prediction for dummy input: {prediction}")

except Exception as e:
    print(f"Error loading or running model: {e}")
