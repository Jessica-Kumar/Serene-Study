# -------------------------------------------------------
# Dockerfile for HuggingFace Spaces (Docker runtime)
# FastAPI Backend — Exam Anxiety Detector
# -------------------------------------------------------

FROM python:3.11-slim

ENV PORT=7860

WORKDIR /app

# Install system deps including libgomp (required by PyTorch)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch (must be before transformers)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Verify torch works
RUN python -c "import torch; print('Torch OK:', torch.__version__)"

# Install remaining backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY api.py .
COPY bert_label_encoder.sav .

# Copy the trained BERT model directory
COPY bert_anxiety_model/ ./bert_anxiety_model/

# HuggingFace Spaces requires a non-root user
RUN useradd -m -u 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
