import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
import os
import random
import string
from datetime import datetime

# Singleton pattern to prevent re-initialization error in Streamlit
if not firebase_admin._apps:
    # Try loading from secrets.toml first
    try:
        if "firebase" in st.secrets:
            # Reconstruct the dictionary from secrets
            key_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        # Else try looking for a local JSON file
        elif os.path.exists("firebase_key.json"):
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
    except Exception as e:
        # If initialization fails, we just don't set app, checking later
        print(f"Firebase init error: {e}")

def get_db():
    try:
        return firestore.client()
    except:
        return None

def generate_short_id(length=6):
    """Generate a random short code for retrieval."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def save_result(data):
    """
    Saves the user result to Firestore.
    Returns: (success_bool, message_or_id)
    """
    db = get_db()
    if not db:
        return False, "Firebase not configured. Please add 'firebase_key.json' or secrets."
    
    try:
        # Create a unique ID
        result_id = generate_short_id()
        # Ensure uniqueness (simple check)
        doc_ref = db.collection('exam_results').document(result_id)
        
        # Add timestamp
        data['timestamp'] = datetime.now()
        
        doc_ref.set(data)
        return True, result_id
    except Exception as e:
        return False, str(e)

def load_result(result_id):
    """
    Loads a result by ID.
    Returns: (success_bool, data_or_error)
    """
    db = get_db()
    if not db:
        return False, "Firebase not configured."
    
    try:
        doc_ref = db.collection('exam_results').document(result_id.strip().upper())
        doc = doc_ref.get()
        if doc.exists:
            return True, doc.to_dict()
        else:
            return False, "Result not found."
    except Exception as e:
        return False, str(e)
