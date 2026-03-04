import pandas as pd
import numpy as np

# Load original dataset
df = pd.read_csv('Mental_health_dset.csv')

# Drop existing 'Disorder' column
if 'Disorder' in df.columns:
    original_disorder = df['Disorder']
    df = df.drop('Disorder', axis=1)

# specific columns usually associated with high anxiety/stress
anxiety_features = [
    'feeling.nervous', 'panic', 'breathing.rapidly', 'sweating', 
    'trouble.in.concentration', 'having.trouble.in.sleeping', 
    'hopelessness', 'over.react', 'having.nightmares'
]

# Calculate a "symptom score" based on all features (assuming they are 0/1)
# If features are not numeric, we need to convert them. 
# Based on previous analysis, they seem to be text or mixed. Let's ensure they are 0/1.

# Function to convert to 0/1 if they are "Yes"/"No"
def convert_to_binary(val):
    if isinstance(val, str):
        if val.lower() == 'yes': return 1
        if val.lower() == 'no': return 0
    return val

for col in df.columns:
    df[col] = df[col].apply(convert_to_binary)

# Sum of all symptoms
df['Symptom_Count'] = df.sum(axis=1)

# Define Exam Anxiety Level logic
def assign_level(row, original_label):
    # If originally Anxiety or Stress, they are likely High or Moderate
    if original_label in ['Anxiety', 'Stress']:
        if row['Symptom_Count'] >= 12:
            return 'High'
        else:
            return 'Moderate'
    # If Depression or Loneliness, map to Moderate or Low to balance
    elif original_label in ['Depression', 'Loneliness']:
        # Randomly assign based on symptom count too
        if row['Symptom_Count'] >= 8:
            return 'Moderate'
        else:
            return 'Low'
    else:
        # Default normal
        return 'Low'

# Apply logic
# We need the original labels back for the logic, assuming they line up by index
df['Original_Disorder'] = original_disorder
df['Exam_Anxiety_Level'] = df.apply(lambda row: assign_level(row, row['Original_Disorder']), axis=1)

# Drop helper columns
df = df.drop(['Symptom_Count', 'Original_Disorder'], axis=1)

# Save new dataset
df.to_csv('exam_anxiety_dataset.csv', index=False)
print("exam_anxiety_dataset.csv created successfully.")
print(df['Exam_Anxiety_Level'].value_counts())
