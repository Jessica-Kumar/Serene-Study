import pandas as pd
import numpy as np
import random

def convert_to_binary(val):
    if isinstance(val, str):
        if val.lower() == 'yes': return 1
        if val.lower() == 'no': return 0
    return val

def assign_level(symptom_count, original_label):
    if original_label in ['Anxiety', 'Stress']:
        if symptom_count >= 12:
            return 'High'
        else:
            return 'Moderate'
    elif original_label in ['Depression', 'Loneliness']:
        if symptom_count >= 8:
            return 'Moderate'
        else:
            return 'Low'
    else:
        return 'Low'

symptom_phrases = {
    'feeling.nervous': "I feel incredibly nervous all the time.",
    'panic': "I keep having panic attacks when I think about it.",
    'breathing.rapidly': "My breathing gets rapid when I study.",
    'sweating': "I start sweating profusely during tests.",
    'trouble.in.concentration': "I have a lot of trouble concentrating.",
    'having.trouble.in.sleeping': "I'm having trouble sleeping at night.",
    'having.trouble.with.work': "I am struggling to get my work done.",
    'hopelessness': "I feel a sense of hopelessness.",
    'anger': "I get angry and irritable very easily.",
    'over.react': "I tend to overreact to small things.",
    'change.in.eating': "My eating habits have completely changed.",
    'suicidal.thought': "I've been having some really dark thoughts.",
    'feeling.tired': "I feel exhausted and tired all the time.",
    'close.friend': "I have a close friend I can talk to.",
    'social.media.addiction': "I can't stop checking social media.",
    'weight.gain': "I've noticed some weight gain recently.",
    'material.possessions': "I care too much about my things.",
    'introvert': "I prefer to keep to myself.",
    'popping.up.stressful.memory': "Stressful memories keep popping up.",
    'having.nightmares': "I've been having terrible nightmares.",
    'avoids.people.or.activities': "I avoid people and normal activities.",
    'feeling.negative': "I'm just feeling very negative lately.",
    'trouble.concentrating': "My mind constantly wanders.",
    'blamming.yourself': "I keep blaming myself for everything."
}

def generate_text(row):
    phrases = []
    # Identify present symptoms
    for col, phrase in symptom_phrases.items():
        if row.get(col) == 1:
            phrases.append(phrase)
    
    if not phrases:
        return "I'm actually feeling okay, not too stressed."
    
    # Shuffle and pick a random subset to make texts more natural and varied
    # If a person has 20 symptoms, joining 20 sentences looks robotic.
    # Let's pick up to 5 symptoms to form their "reflection"
    random.shuffle(phrases)
    selected_phrases = phrases[:min(5, len(phrases))]
    
    # Join into a paragraph
    text = " ".join(selected_phrases)
    
    # Add some natural variation
    intros = [
        "Lately, ",
        "To be honest, ",
        "When I think about the exams, ",
        "I've noticed that ",
        ""
    ]
    return random.choice(intros) + text

def prepare_dataset():
    print("Loading original dataset...")
    df = pd.read_csv('Mental_health_dset.csv')
    
    # Due to data size and for quicker BERT fine-tuning locally, let's take a sample of 2000 rows
    # maintaining the class distribution roughly if possible
    df = df.sample(n=2000, random_state=42).reset_index(drop=True)
    
    original_disorder = df['Disorder'] if 'Disorder' in df.columns else pd.Series(['Normal']*len(df))
    if 'Disorder' in df.columns:
        df = df.drop('Disorder', axis=1)

    for col in df.columns:
        df[col] = df[col].apply(convert_to_binary)
        
    df['Symptom_Count'] = df.sum(axis=1)
    df['Original_Disorder'] = original_disorder
    
    print("Assigning labels...")
    df['Exam_Anxiety_Level'] = df.apply(lambda row: assign_level(row['Symptom_Count'], row['Original_Disorder']), axis=1)
    
    print("Generating synthetic text reflections...")
    df['student_text'] = df.apply(generate_text, axis=1)
    
    # Keep only the required columns for BERT
    final_df = df[['student_text', 'Exam_Anxiety_Level']].copy()
    
    print("Label Distribution:")
    print(final_df['Exam_Anxiety_Level'].value_counts())
    
    final_df.to_csv('anxiety_text_dataset.csv', index=False)
    print("Created anxiety_text_dataset.csv successfully.")

if __name__ == "__main__":
    prepare_dataset()
