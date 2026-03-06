from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pickle
import os
from datetime import datetime
from typing import List

app = FastAPI(title="Serene Study API", description="Exam Anxiety Detection Backend")

# ---- Config ----
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_dir = "bert_anxiety_model"
encoder_path = "bert_label_encoder.sav"

model = None
tokenizer = None
reverse_mapping = {0: "Low", 1: "Moderate", 2: "High"}

# In-memory history store (resets on restart — good enough for demo)
prediction_history: List[dict] = []

@app.on_event("startup")
def load_assets():
    global model, tokenizer, reverse_mapping
    try:
        if os.path.exists(model_dir):
            print(f"Loading model from {model_dir}...")
            model = AutoModelForSequenceClassification.from_pretrained(model_dir)
            model.to(device)
            model.eval()
            tokenizer = AutoTokenizer.from_pretrained(model_dir)
            print("Model loaded successfully.")
        else:
            print(f"Warning: {model_dir} not found. Predictions will be unavailable.")

        if os.path.exists(encoder_path):
            with open(encoder_path, "rb") as f:
                reverse_mapping = pickle.load(f)
    except Exception as e:
        print(f"Error loading model: {e}")


# ---- Schemas ----
class PredictRequest(BaseModel):
    text: str
    mbti_type: str = "Unknown"

class PredictResponse(BaseModel):
    status: str
    anxiety_level: int
    tips: str

class HistoryRecord(BaseModel):
    id: int
    timestamp: str
    anxiety_level: int


# ---- Endpoints ----
@app.post("/predict", response_model=PredictResponse)
def predict_anxiety(data: PredictRequest):
    if not model or not tokenizer:
        # Return a random result for demo when model isn't loaded
        import random
        level = random.randint(0, 2)
        tips_map = {
            0: "1. You're doing great!\n2. Keep your routine.\n3. Get enough sleep.",
            1: "1. Take deep breaths.\n2. Break study into chunks.\n3. Talk to a friend.",
            2: "1. Reach out to a counselor.\n2. Practice mindfulness.\n3. Remember: one step at a time."
        }
        return PredictResponse(status="demo", anxiety_level=level, tips=tips_map[level])

    if not data.text.strip():
        return PredictResponse(status="success", anxiety_level=0, tips="1. You seem calm!\n2. Keep it up.")

    inputs = tokenizer(
        data.text, return_tensors="pt",
        truncation=True, padding=True, max_length=128
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        predicted_class_id = int(outputs.logits.argmax().item())

    level_label = reverse_mapping.get(predicted_class_id, "Low")

    tips_map = {
        "Low":      "1. You're managing well!\n2. Keep your routine.\n3. Stay hydrated and sleep well.",
        "Moderate": "1. Take a 5-minute break every hour.\n2. Break tasks into smaller parts.\n3. Talk to someone you trust.",
        "High":     "1. Please speak to a counselor.\n2. Practice box breathing: inhale 4s, hold 4s, exhale 4s.\n3. You are not alone — reach out."
    }

    record = {
        "id": len(prediction_history) + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "anxiety_level": predicted_class_id
    }
    prediction_history.append(record)

    return PredictResponse(
        status="success",
        anxiety_level=predicted_class_id,
        tips=tips_map.get(level_label, "")
    )


@app.get("/history")
def get_history():
    """Returns all past predictions (anonymized, in-memory)."""
    return prediction_history


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
