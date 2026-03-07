# 🌿 Serene-Study: AI-Based Exam Anxiety Detector

**Understand your exam stress through the lens of your personality.**

Serene-Study is an end-to-end AI application designed to support students at **KIET Group of Institutions** by detecting exam-related anxiety and providing personalized coping strategies.

It combines a **fine-tuned BERT NLP model**, an **MBTI personality quiz**, and **Google Gemini AI** to offer deeply personalized insights.

---

## ✨ Features

### 🧠 BERT-Powered Analysis
Classifies student thoughts into **three distinct anxiety levels**:
- Low Anxiety
- Moderate Anxiety
- High Anxiety

Using a **custom-trained Transformer model**.

### 📊 Exam Anxiety Dashboard (Institutional Mode)
Analyzes **aggregate, anonymized student data** to track wellness trends across the campus.

### 🧩 Rapid Personality Quiz
Determines your **4-letter personality type (MBTI)** + **Turbulent/Assertive trait** in just **9 questions**.

### 🤖 AI Personalised Reports
Uses **Google Gemini AI** to generate a **Deep Report** explaining how your specific personality type experiences stress, with tailored advice.

### 💬 AI Chat Assistant
Ask follow-up questions to an **AI coach** aware of your anxiety level and personality.

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Jessica-Kumar/Serene-Study.git
cd Serene-Study
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up API Key

Get a **Google Gemini API Key**.

The app will ask for it in the **Streamlit sidebar**, or you can add it to:

```
.streamlit/secrets.toml
```

Example:

```toml
GOOGLE_API_KEY = "your_key_here"
BACKEND_URL = "http://localhost:8000"
```

---

### 4. Run the System

#### Start the Backend (Terminal 1)

```bash
uvicorn api:app --reload
```

#### Start the Frontend (Terminal 2)

```bash
streamlit run Web_File.py
```

---

## 🛠️ Retraining the Model

If you want to modify the logic or retrain the anxiety predictor:

### Notebook Training

Open:

```
Mental_Health_Analyzer_Exam_Edition.ipynb
```

Run all cells in **Google Colab or Jupyter Notebook** to regenerate:
- `bert_anxiety_model.pt`
- label mapping

### Local Training Script

```bash
python train_exam_model.py
```

---

## 🤝 The Team (KIET Group of Institutions)

- **Falak Khan** — Team Leader & Final Documentation  
- **Jessica Kumar** — Lead Developer & Technical Architect  
- **Kriti Gupta** — Testing & Validation  
- **Ishanya Singh** — Environment & Data Setup  

---

## ⚠️ Disclaimer

This tool is for **educational and self-reflection purposes only**. It is **not a clinical diagnostic tool**.

If you are experiencing severe distress, please seek professional support from **campus counseling services or qualified mental health professionals**.

---

Developed at **KIET Group of Institutions**.