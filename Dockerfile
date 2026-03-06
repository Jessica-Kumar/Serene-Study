# -------------------------------------------------------
# Dockerfile for HuggingFace Spaces (Docker runtime)
# FastAPI Backend — Exam Anxiety Detector
# -------------------------------------------------------

FROM python:3.11-slim

# HuggingFace Spaces requires port 7860
ENV PORT=7860

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements_backend.txt .

# Install CPU-only PyTorch first (saves ~1.5GB vs full GPU version)
RUN pip install --no-cache-dir torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Install remaining backend dependencies
RUN pip install --no-cache-dir -r requirements_backend.txt

# Copy all backend files
COPY api.py .
COPY bert_label_encoder.sav .

# Copy the trained BERT model directory
COPY bert_anxiety_model/ ./bert_anxiety_model/

# HuggingFace Spaces requires a non-root user
RUN useradd -m -u 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port for HuggingFace Spaces
EXPOSE 7860

# Start the FastAPI server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
