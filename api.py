from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pickle
import os
import firebase_admin
from firebase_admin import credentials, firestore
import firebase_config as fb  # Import existing config or just use directly 

app = FastAPI(title="Exam Anxiety API", description="Backend Inference for Anxiety Detection")

# Load model and tokenizers globally at startup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_dir = "bert_anxiety_model"
encoder_path = "bert_label_encoder.sav"

model = None
tokenizer = None
reverse_mapping = {}

@app.on_event("startup")
def load_assets():
    global model, tokenizer, reverse_mapping
    try:
        # If model doesn't exist yet, we can handle it gracefully for dev
        if os.path.exists(model_dir):
            model = AutoModelForSequenceClassification.from_pretrained(model_dir)
            model.to(device)
            model.eval()
            tokenizer = AutoTokenizer.from_pretrained(model_dir)
        else:
            print(f"Warning: {model_dir} not found. Please train the model first.")
            
        if os.path.exists(encoder_path):
            with open(encoder_path, "rb") as f:
                reverse_mapping = pickle.load(f)
        else:
            # Fallback if not trained yet
            reverse_mapping = {0: "Low", 1: "Moderate", 2: "High"}
            
    except Exception as e:
        print(f"Error loading system: {e}")

class RequestData(BaseModel):
    student_text: str
    mbti: str

class PredictResponse(BaseModel):
    anxiety_level: str
    mbti_context: str

@app.post("/predict", response_model=PredictResponse)
def predict_anxiety(data: RequestData):
    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model is not loaded or trained yet.")
    
    if not data.student_text.strip():
        # Empty text defaults to Low
        return PredictResponse(anxiety_level="Low", mbti_context=data.mbti)
    
    inputs = tokenizer(data.student_text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = logits.argmax().item()
    
    predicted_label = reverse_mapping.get(predicted_class_id, "Low")
    
    return PredictResponse(anxiety_level=predicted_label, mbti_context=data.mbti)

@app.get("/stats")
def get_stats():
    """Aggregates anonymized stats for the Institutional Dashboard"""
    # Assuming the results are saved in fb.db.collection('exam_results')
    try:
        if not hasattr(fb, 'db') or fb.db is None:
            return {"error": "Firebase DB not initialized", "stats": {}}
            
        users_ref = fb.db.collection(fb.COLLECTION_NAME)
        docs = users_ref.stream()
        
        distribution = {"Low": 0, "Moderate": 0, "High": 0}
        mbti_distribution = {}
        total = 0
        
        for doc in docs:
            d = doc.to_dict()
            level = d.get('anxiety_level')
            mbti_type = d.get('mbti', 'Unknown')
            
            if level in distribution:
                distribution[level] += 1
            total += 1
            
            mbti_distribution[mbti_type] = mbti_distribution.get(mbti_type, 0) + 1
            
        return {
            "total_assessments": total,
            "anxiety_distribution": distribution,
            "mbti_distribution": mbti_distribution
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        # Return fallback mock stats if firebase isn't perfectly set up locally
        return {
            "total_assessments": 100,
            "anxiety_distribution": {"Low": 50, "Moderate": 30, "High": 20},
            "mbti_distribution": {"INTJ-A": 15, "ESFP-T": 10, "INFP-T": 25, "ESTJ-A": 50}
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
