import google.generativeai as genai
import time

class AI_Agent:
    def __init__(self, api_key):
        if api_key:
            genai.configure(api_key=api_key)
            # List of models to try in order of preference
            self.models_to_try = [
                'gemini-2.0-flash',
                'gemini-1.5-flash',
                'gemini-1.5-pro',
                'gemini-pro',
                'gemini-flash-latest'
            ]
            self.current_model_name = self.models_to_try[0]
            self.model = genai.GenerativeModel(self.current_model_name)
        else:
            self.model = None

    def _generate_with_retry(self, prompt):
        if not self.model:
            return "Please enter a valid Google API Key."

        # Try the current model first, then fallback through the list
        # We need to iterate starting from the current model index? 
        # Actually, let's just try to find *any* working model if the current one fails.
        
        errors = []
        
        for model_name in self.models_to_try:
            try:
                # Update model if we are switching
                if model_name != self.current_model_name:
                    self.current_model_name = model_name
                    self.model = genai.GenerativeModel(model_name)
                
                response = self.model.generate_content(prompt)
                return response.text
                
            except Exception as e:
                error_str = str(e)
                errors.append(f"{model_name}: {error_str}")
                # If it's a safety block, maybe we shouldn't retry? But 404 and 429 we definitely should.
                continue

        return f"Unable to generate report. Tried models: {', '.join(self.models_to_try)}. \nErrors: {'; '.join(errors)}"

    def generate_report(self, diagnosis, input_data_dict, mbti_type=None, personality_scores=None):
        if not self.model:
            return "Please enter a valid Google API Key in the sidebar to generate an AI report."
        
        # Build personality insights (Same as before)
        personality_insights = ""
        if mbti_type:
            ie = mbti_type[0] if len(mbti_type) >= 2 else '?'
            sn = mbti_type[1] if len(mbti_type) >= 3 else '?'
            tf = mbti_type[2] if len(mbti_type) >= 4 else '?'
            jp = mbti_type[3] if len(mbti_type) >= 5 else '?'
            identity = mbti_type[5] if len(mbti_type) >= 7 else '?'
            
            personality_insights += f"**Your Personality Type:** {mbti_type}\n\n"
            
            if ie == 'I': personality_insights += "• **Introvert (I):** You recharge by being alone. Solitude is not loneliness.\n"
            else: personality_insights += "• **Extravert (E):** You gain energy from interaction. Don't neglect quiet reflection.\n"
            if sn == 'S': personality_insights += "• **Sensing (S):** You focus on facts. Don't get lost in details; see the big picture.\n"
            else: personality_insights += "• **Intuitive (N):** You see possibilities. Ground your 'what ifs' with facts.\n"
            if tf == 'T': personality_insights += "• **Thinking (T):** You value logic. Use rational self-talk to counter anxiety.\n"
            else: personality_insights += "• **Feeling (F):** You value harmony. Your worth is not defined by grades.\n"
            if jp == 'J': personality_insights += "• **Judging (J):** You like structure. Make a plan to regain control.\n"
            else: personality_insights += "• **Perceiving (P):** You prefer flexibility. Avoid rigid schedules; use loose goals.\n"
            if identity == 'T': personality_insights += "• **Turbulent (-T):** Perfectionism fuels anxiety. Practice 'good enough'.\n"
            else: personality_insights += "• **Assertive (-A):** You are calm. Use your stability to help others.\n"
        else:
            personality_insights = "Personality type unknown."
        
        symptom_text = ""
        if input_data_dict:
            symptom_text = "**Symptoms:**\n" + "\n".join(f"- {k}" for k in input_data_dict.keys())
        else:
            symptom_text = "No specific symptoms reported."
        
        prompt = f"""
        Act as an expert academic stress coach with knowledge of MBTI personality types.
        A student has the following exam anxiety assessment:
        
        **Anxiety Level:** {diagnosis}
        {personality_insights}
        {symptom_text}
        
        Write a supportive, personalized report.
        1. Explain what this anxiety level means for their personality type.
        2. Give 3 specific coping strategies tailored to their MBTI (e.g. if Introvert, suggest solitary recharging; if Extrovert, study groups).
        3. Provide one quick relaxation technique.
        4. Remind them this is not a clinical diagnosis.
        
        Keep it concise (under 400 words) and warm.
        """
        
        return self._generate_with_retry(prompt)

    def chat_response(self, user_input, context, mbti_type=None):
        if not self.model:
            return "Please enter a valid Google API Key to chat."
        
        personality_context = f"The user's personality type is {mbti_type}." if mbti_type else ""
        
        prompt = f"""
        Context: User took an exam anxiety test. Result: {context}. {personality_context}
        User Question: {user_input}
        
        Answer empathetically and concisely.
        """
        return self._generate_with_retry(prompt)
