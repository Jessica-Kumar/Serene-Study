"""
data_preprocessing.py
Prepares the Kaggle Mental Health dataset for BERT fine-tuning.

Dataset source:
  https://www.kaggle.com/datasets/infamouscoder/mental-health-social-media
  (or the CSV file: mental_health.csv / Combined Data.csv)

Expected CSV columns:
  'statement' (or 'text') — the text
  'status'               — label (Normal, Anxiety, Stress, Depression, Suicidal, Bipolar, Personality Disorder)

Label Mapping → Exam Anxiety Level:
  Normal                              → Low
  Anxiety, Stress                     → Moderate
  Depression, Suicidal, Bipolar,
  Personality Disorder                → High
"""

import pandas as pd
from pathlib import Path

# ---- Label Mapping ----
LABEL_MAP = {
    'Normal':               'Low',
    'Anxiety':              'Moderate',
    'Stress':               'Moderate',
    'Depression':           'High',
    'Suicidal':             'High',
    'Bipolar':              'High',
    'Personality Disorder': 'High',
}

LEVEL_TO_INT = {'Low': 0, 'Moderate': 1, 'High': 2}


def find_dataset_file():
    """Try common filenames the Kaggle dataset might be saved as."""
    candidates = [
        'mental_health.csv',
        'Combined Data.csv',
        'combined_data.csv',
        'kaggle_mental_health.csv',
        'mental_health_dataset.csv',
    ]
    for name in candidates:
        if Path(name).exists():
            return name
    return None


def prepare_dataset():
    print("=" * 50)
    print("Kaggle Mental Health Dataset Preprocessor")
    print("=" * 50)

    # ---- Load Dataset ----
    dataset_file = find_dataset_file()
    if not dataset_file:
        print("\n[ERROR] Could not find the Kaggle dataset CSV file.")
        print("Please download it from:")
        print("  https://www.kaggle.com/datasets/infamouscoder/mental-health-social-media")
        print("And save it as 'mental_health.csv' in this folder.\n")
        return False

    print(f"Loading dataset: {dataset_file}")
    df = pd.read_csv(dataset_file)
    print(f"  Loaded {len(df)} rows, columns: {list(df.columns)}")

    # ---- Find text and label columns ----
    text_col = next((c for c in df.columns if c.lower() in ['statement', 'text', 'content', 'post']), None)
    label_col = next((c for c in df.columns if c.lower() in ['status', 'label', 'category', 'class']), None)

    if not text_col or not label_col:
        print(f"[ERROR] Could not find text/label columns in: {list(df.columns)}")
        print("Expected a column named 'statement' or 'text', and 'status' or 'label'.")
        return False

    print(f"  Using text column: '{text_col}', label column: '{label_col}'")

    # ---- Clean ----
    df = df[[text_col, label_col]].dropna()
    df.columns = ['student_text', 'Original_Label']
    df['student_text'] = df['student_text'].astype(str).str.strip()
    df = df[df['student_text'].str.len() > 10]

    # ---- Map Labels ----
    print(f"\nOriginal label distribution:")
    print(df['Original_Label'].value_counts().to_string())

    df['Original_Label_Clean'] = df['Original_Label'].str.strip().str.title()
    df['Exam_Anxiety_Level'] = df['Original_Label_Clean'].map(LABEL_MAP)

    unmapped = df[df['Exam_Anxiety_Level'].isna()]['Original_Label_Clean'].unique()
    if len(unmapped) > 0:
        print(f"\n  [WARNING] Unmapped labels (will be dropped): {unmapped}")
    df = df.dropna(subset=['Exam_Anxiety_Level'])

    # ---- Balance classes (cap at 3000 per class) ----
    MAX_PER_CLASS = 3000
    balanced = df.groupby('Exam_Anxiety_Level', group_keys=False).apply(
        lambda x: x.sample(min(len(x), MAX_PER_CLASS), random_state=42)
    ).reset_index(drop=True)

    print(f"\nFinal label distribution (after balancing):")
    print(balanced['Exam_Anxiety_Level'].value_counts().to_string())
    print(f"Total samples: {len(balanced)}")

    # ---- Save ----
    final_df = balanced[['student_text', 'Exam_Anxiety_Level']].copy()
    final_df.to_csv('anxiety_text_dataset.csv', index=False)
    print(f"\n✅ Saved: anxiety_text_dataset.csv ({len(final_df)} rows)")
    return True


if __name__ == "__main__":
    prepare_dataset()
