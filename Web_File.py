import streamlit as st
import os
import requests
import json
import pandas as pd
import plotly.express as px
from ai_agent import AI_Agent
import firebase_config as fb

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Serene Study: Exam Anxiety Detector",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="collapsed"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #2D3E40; }
    
    .block-container { max-width: 960px; padding-top: 2rem; padding-bottom: 2rem; }
    
    h1 { font-weight: 700; color: #1A2E30; font-size: 2.2rem; }
    h2 { font-weight: 600; color: #2D3E40; font-size: 1.5rem; margin-top: 1.5rem; margin-bottom: 0.75rem; }
    h3 { font-weight: 600; color: #2D3E40; font-size: 1.2rem; }
    
    div[data-testid="stExpander"], div.stForm {
        background-color: #FFFFFF; border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06); border: none;
        padding: 1rem; margin-bottom: 1.5rem;
    }
    
    div.stButton > button {
        background-color: #6B9080; color: white; border-radius: 10px;
        padding: 0.55rem 1.2rem; border: none; font-weight: 600;
        width: 100%; transition: all 0.25s ease;
    }
    div.stButton > button:hover {
        background-color: #5A7A6B; box-shadow: 0 4px 12px rgba(107,144,128,0.35); color: white;
    }
    
    div[data-testid="stNotification"] { border-radius: 12px; padding: 1rem; }
    
    .personality-badge {
        background: linear-gradient(135deg, #CBB3A6, #B09080);
        color: white; border-radius: 40px; padding: 0.35rem 1.1rem;
        font-weight: 700; font-size: 0.95rem; letter-spacing: 1.5px;
        display: inline-block; margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    
    .ai-report {
        background-color: #F8FCF9; padding: 2rem; border-radius: 16px;
        border-left: 5px solid #6B9080; line-height: 1.7; font-size: 1.05rem; margin-top: 1rem;
    }
    
    .tips-box {
        background: linear-gradient(135deg, #EAF4EF, #F0F7EC);
        border-left: 5px solid #6B9080; border-radius: 12px;
        padding: 1rem 1.5rem; margin-top: 0.75rem;
    }
    
    .alert-high {
        background-color: #FFF0F0; border-left: 5px solid #FF6B6B;
        border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .soft-text { color: #5E7C7C; font-size: 0.95rem; }
    
    [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# -------------------- API KEY --------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = st.text_input("Enter Google Gemini API Key", type="password")

# -------------------- BACKEND URL --------------------
# On Streamlit Cloud, set BACKEND_URL in secrets to your HF Space URL
# e.g. https://jessica-kumar-serene-study-api.hf.space
try:
    BACKEND_URL = st.secrets["BACKEND_URL"].rstrip("/")
except:
    BACKEND_URL = "http://localhost:8000"

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/leaf.png", width=60)
    st.markdown("### 🌿 Serene Study")
    st.markdown("*Your mental wellness companion*")
    st.markdown("---")
    st.header("📂 Load Past Result")
    result_id_input = st.text_input("Enter Result ID (e.g., A1B2)")
    if st.button("Load Report"):
        found, data = fb.load_result(result_id_input)
        if found:
            st.session_state['anxiety_level'] = data.get('anxiety_level')
            st.session_state['mbti'] = data.get('mbti')
            st.session_state['student_text'] = data.get('student_text', '')
            st.session_state['ai_report'] = data.get('ai_report')
            st.session_state['loaded_report_date'] = data.get('timestamp')
            st.session_state['backend_tips'] = ''
            st.success("Report loaded successfully!")
            st.rerun()
        else:
            st.error(data)
    st.markdown("---")
    st.caption("⚠️ This is a supportive tool, not a clinical diagnosis.")
    st.caption("🔒 All submissions are anonymized.")

ai_agent = AI_Agent(api_key)

# -------------------- MAIN UI --------------------
st.title("🌿 Serene Study: Exam Anxiety Detector")
st.markdown("<p class='soft-text'>Understand your exam stress through the lens of your personality. A calm space for self-reflection and institutional care.</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎓 Student Reflection Portal", "📊 Institutional Dashboard"])

# -------------------------------------------------------------------------------------
# TAB 1: SCENARIO 1 (Student View)
# -------------------------------------------------------------------------------------
with tab1:
    # ---- MBTI Quiz ----
    with st.expander("🧠 Step 1: Quick Personality Snapshot", expanded=True):
        st.markdown("Answer intuitively – no right or wrong answers. Helps tailor advice to **how you naturally think and feel**.")
        scores = {'I':0,'E':0,'S':0,'N':0,'T':0,'F':0,'J':0,'P':0,'Turbulent':0,'Assertive':0}
        col1, col2 = st.columns(2)
        with col1:
            q1 = st.radio("1. After a busy week, you prefer to:", ["Spend time alone to recharge", "Be around people to recharge"], key='q1')
            scores['I'] += 1 if "alone" in q1 else 0; scores['E'] += 1 if "people" in q1 else 0
            q2 = st.radio("2. In a group project, you usually:", ["Listen and contribute occasionally", "Speak up and lead discussions"], key='q2')
            scores['I'] += 1 if "Listen" in q2 else 0; scores['E'] += 1 if "lead" in q2 else 0
            q3 = st.radio("3. When learning something new, you prefer:", ["Step‑by‑step instructions", "Understanding the big picture first"], key='q3')
            scores['S'] += 1 if "step" in q3.lower() else 0; scores['N'] += 1 if "big" in q3 else 0
            q4 = st.radio("4. You trust more:", ["Facts and experience", "Hunches and possibilities"], key='q4')
            scores['S'] += 1 if "Facts" in q4 else 0; scores['N'] += 1 if "Hunches" in q4 else 0
        with col2:
            q5 = st.radio("5. When making a decision, you weigh:", ["Logic and consistency", "Impact on people and harmony"], key='q5')
            scores['T'] += 1 if "Logic" in q5 else 0; scores['F'] += 1 if "Impact" in q5 else 0
            q6 = st.radio("6. You are more persuaded by:", ["Solid arguments", "Personal stories"], key='q6')
            scores['T'] += 1 if "Solid" in q6 else 0; scores['F'] += 1 if "Personal" in q6 else 0
            q7 = st.radio("7. You prefer to work:", ["With a clear plan and deadlines", "As inspiration strikes, flexible"], key='q7')
            scores['J'] += 1 if "clear" in q7 else 0; scores['P'] += 1 if "flexible" in q7 else 0
            q8 = st.radio("8. Your workspace is usually:", ["Neat and organised", "Looks messy but I know where things are"], key='q8')
            scores['J'] += 1 if "Neat" in q8 else 0; scores['P'] += 1 if "messy" in q8 else 0
        st.markdown("---")
        q9 = st.radio("9. When facing a challenge, you tend to:", ["Worry about possible mistakes", "Stay confident and calm"], key='q9')
        scores['Turbulent'] += 1 if "Worry" in q9 else 0; scores['Assertive'] += 1 if "confident" in q9 else 0

        ie = 'I' if scores['I'] >= scores['E'] else 'E'
        sn = 'S' if scores['S'] >= scores['N'] else 'N'
        tf = 'T' if scores['T'] >= scores['F'] else 'F'
        jp = 'J' if scores['J'] >= scores['P'] else 'P'
        identity = 'T' if scores['Turbulent'] >= scores['Assertive'] else 'A'
        mbti = f"{ie}{sn}{tf}{jp}-{identity}"
        st.session_state['mbti'] = mbti
        st.session_state['personality_scores'] = scores
        st.markdown(f"<div style='text-align:center;margin-top:1rem;'><span class='personality-badge'>{mbti}</span></div>", unsafe_allow_html=True)

    # ---- Text Input ----
    st.markdown("---")
    st.header("📝 Step 2: Share Your Exam Feelings")
    st.markdown("<p class='soft-text'>Express your thoughts freely. The AI reads your words, not checkboxes.</p>", unsafe_allow_html=True)

    with st.form("exam_form"):
        student_text = st.text_area(
            "Your Thoughts & Feelings",
            height=160,
            placeholder="E.g., I feel incredibly overwhelmed. Every time I think about the exam my heart races and I can't sleep..."
        )
        submitted = st.form_submit_button("🔍 Analyze My Reflections", use_container_width=True)

    if submitted:
        if not student_text.strip():
            st.warning("Please write something to analyze.")
        else:
            st.session_state['student_text'] = student_text
            with st.spinner("🤖 Reading your reflections via BERT model..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/predict",
                        json={"text": student_text, "mbti_type": st.session_state['mbti']},
                        timeout=15
                    )
                    if response.status_code == 200:
                        data = response.json()
                        raw = data.get('anxiety_level', 0)
                        level_map = {0: 'Low', 1: 'Moderate', 2: 'High'}
                        st.session_state['anxiety_level'] = level_map.get(raw, 'Low') if isinstance(raw, int) else str(raw)
                        st.session_state['backend_tips'] = data.get('tips', '')
                    else:
                        st.error(f"Backend error: {response.text}")
                        st.stop()
                except Exception as e:
                    st.error(f"⚠️ Could not connect to backend. Is `uvicorn api:app` running? ({e})")
                    st.stop()

    # ---- Results ----
    if 'anxiety_level' in st.session_state:
        st.markdown("---")
        st.header("📊 Your Result")
        anxiety_level = st.session_state.get('anxiety_level', 'Low')

        col_r, col_m = st.columns([3, 1])
        with col_r:
            if anxiety_level == "Low":
                st.success(f"✅ **{anxiety_level} Anxiety** – You're managing well. Keep up good habits!")
                st.progress(0.2)
            elif anxiety_level == "Moderate":
                st.info(f"🟡 **{anxiety_level} Anxiety** – Some stress is normal, but let's work on coping.")
                st.progress(0.6)
            else:
                st.warning(f"🔴 **{anxiety_level} Anxiety** – Your anxiety is significant. Please be gentle with yourself.")
                st.progress(0.95)
        with col_m:
            if 'loaded_report_date' in st.session_state:
                st.caption(f"📅 From: {st.session_state['loaded_report_date']}")

        # Instant tips from backend
        tips = st.session_state.get('backend_tips', '')
        if tips:
            st.markdown("<div class='tips-box'><b>💡 Immediate Coping Tips</b>", unsafe_allow_html=True)
            for line in tips.strip().split('\n'):
                if line.strip():
                    st.markdown(f"&nbsp;&nbsp;• {line.strip()}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ---- AI Deep Report ----
        st.markdown("---")
        st.header("🤖 Step 3: Personalized AI Guide")
        st.markdown(f"<p class='soft-text'>Based on your <b>{st.session_state.get('mbti','Unknown')}</b> personality and <b>{anxiety_level}</b> anxiety level.</p>", unsafe_allow_html=True)

        if st.button("✨ Generate Deep Report", use_container_width=True):
            if not api_key:
                st.error("Please enter your Google Gemini API Key (sidebar or input at top).")
            else:
                with st.spinner("Crafting your personalized wellness guide..."):
                    reflection_text = st.session_state.get('student_text', 'No reflection provided.')
                    report = ai_agent.generate_report(
                        diagnosis=st.session_state['anxiety_level'],
                        input_data_dict={"Student Reflection": reflection_text},
                        mbti_type=st.session_state.get('mbti', 'Unknown'),
                        personality_scores=st.session_state.get('personality_scores', {})
                    )
                    st.session_state['ai_report'] = report

        if 'ai_report' in st.session_state:
            st.markdown(f"<div class='ai-report'>{st.session_state['ai_report']}</div>", unsafe_allow_html=True)

            col_s, _ = st.columns([1, 1])
            with col_s:
                if st.button("💾 Save Result Anonymously"):
                    data_to_save = {
                        'anxiety_level': st.session_state['anxiety_level'],
                        'mbti': st.session_state.get('mbti', 'Unknown'),
                        'student_text': st.session_state.get('student_text', ''),
                        'ai_report': st.session_state['ai_report']
                    }
                    success, msg = fb.save_result(data_to_save)
                    if success:
                        st.success(f"✅ Saved! Your Result ID: **{msg}** — note it down to reload later.")
                    else:
                        st.error(f"Save failed: {msg}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("💬 Chat with Your AI Coach")
            user_q = st.text_input("Ask a follow-up question...")
            if user_q:
                with st.spinner("Thinking..."):
                    answer = ai_agent.chat_response(user_q, st.session_state['anxiety_level'], st.session_state.get('mbti', 'Unknown'))
                    st.markdown(f"<div style='background:#F0F7F4;padding:1rem;border-radius:10px;'><b>AI:</b> {answer}</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------------------------
# TAB 2: SCENARIO 2 (Institutional Dashboard — auto-loads)
# -------------------------------------------------------------------------------------
with tab2:
    st.header("🏫 Academic Wellness Monitoring")
    st.markdown("Track aggregated, anonymized student anxiety trends to support timely counseling and institutional action.")

    # Auto-load on tab open
    if 'dashboard_history' not in st.session_state:
        try:
            resp = requests.get(f"{BACKEND_URL}/history", timeout=6)
            if resp.status_code == 200:
                st.session_state['dashboard_history'] = resp.json()
        except:
            pass

    col_ref, _ = st.columns([1, 3])
    with col_ref:
        if st.button("🔄 Refresh Data"):
            with st.spinner("Refreshing..."):
                try:
                    resp = requests.get(f"{BACKEND_URL}/history", timeout=10)
                    if resp.status_code == 200:
                        st.session_state['dashboard_history'] = resp.json()
                    else:
                        st.error("Failed to refresh.")
                except Exception as e:
                    st.error(f"Backend not responding: {e}")

    history = st.session_state.get('dashboard_history', [])
    total = len(history)

    if total > 0:
        level_map = {0: 'Low', 1: 'Moderate', 2: 'High'}
        df = pd.DataFrame(history)
        df['Level'] = df['anxiety_level'].map(level_map)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Counts per level
        counts = df['Level'].value_counts()
        high_count = counts.get('High', 0)
        mod_count = counts.get('Moderate', 0)
        low_count = counts.get('Low', 0)
        high_pct = round((high_count / total) * 100)

        # Alert banner if High > 30%
        if high_pct > 30:
            st.markdown(
                f"<div class='alert-high'>🚨 <b>Counselor Alert:</b> {high_pct}% of students are reporting <b>High Anxiety</b>. "
                f"Consider scheduling a wellness workshop or counseling session immediately.</div>",
                unsafe_allow_html=True
            )

        # Metric row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Assessments", total)
        m2.metric("🔴 High Anxiety", high_count, f"{high_pct}%")
        m3.metric("🟡 Moderate", mod_count, f"{round((mod_count/total)*100)}%")
        m4.metric("🟢 Low Anxiety", low_count, f"{round((low_count/total)*100)}%")

        st.markdown("---")

        # Pie chart
        col_pie, col_bar = st.columns(2)
        with col_pie:
            st.markdown("### 📊 Distribution")
            dist = df['Level'].value_counts().reset_index()
            dist.columns = ['Level', 'Count']
            fig = px.pie(dist, values='Count', names='Level',
                         color='Level',
                         color_discrete_map={'High':'#FF6B6B','Moderate':'#FCA311','Low':'#6B9080'},
                         hole=0.4)
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

        with col_bar:
            st.markdown("### 📈 Timeline")
            df_sorted = df.sort_values('timestamp')
            df_sorted = df_sorted.copy()
            df_sorted['date'] = df_sorted['timestamp'].dt.date
            timeline = df_sorted.groupby(['date', 'Level']).size().reset_index(name='Count')
            fig2 = px.bar(timeline, x='date', y='Count', color='Level',
                          color_discrete_map={'High':'#FF6B6B','Moderate':'#FCA311','Low':'#6B9080'},
                          barmode='stack')
            fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title="Level")
            st.plotly_chart(fig2, use_container_width=True)

        st.caption("🔒 All data is fully anonymized. No personally identifiable information is stored or displayed.")
    else:
        st.info("No assessments recorded yet. Students need to complete Step 2 in the Student Portal first.")
