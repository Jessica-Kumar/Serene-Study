# 📘 AI Exam Anxiety & Personality Detector

**Understand your exam stress through the lens of your personality.**

This application combines a **Machine Learning Exam Anxiety Predictor** with an **MBTI Personality Quiz** and **Google Gemini AI** to provide deeply personalised insights and coping strategies.

## ✨ Features

-   **🧠 Rapid Personality Quiz**: Determines your 4-letter personality type (MBTI) + Turbulent/Assertive trait in just 9 questions.
-   **📊 Exam Anxiety Assessment**: Analyzes 24 physical, emotional, and social symptoms related to exams.
-   **🤖 AI Personalised Reports**: Uses Google Gemini to generate a custom report explaining how *your specific personality type* experiences stress, with tailored advice (e.g., specific tips for Introverts vs. Extroverts).
-   **💬 AI Chat Assistant**: Ask follow-up questions to an AI coach aware of your anxiety level and personality.

## 🚀 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Hafeez-UrRehman/Mental-Health-Analyzer.git
    cd Mental-Health-Analyzer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up API Key:**
    -   Get a [Google Gemini API Key](https://aistudio.google.com/app/apikey).
    -   The app will ask for it in the sidebar, or you can add it to `.streamlit/secrets.toml`:
        ```toml
        GOOGLE_API_KEY = "your_key_here"
        ```

4.  **Run the App:**
    ```bash
    streamlit run Web_File.py
    ```

## 🛠️ Retraining the Model

If you want to modify the logic or retrain the anxiety predictor:
1.  Open `Mental_Health_Analyzer_Exam_Edition.ipynb` in Jupyter.
2.  Run all cells to regenerate `exam_anxiety_model.sav` and `label_encoder.sav`.
3.  Alternatively, run the script:
    ```bash
    python train_exam_model.py
    ```

## ⚠️ Disclaimer

This tool is for educational and self-reflection purposes only. It is **not** a clinical diagnostic tool. If you are experiencing severe distress, please seek professional support.
