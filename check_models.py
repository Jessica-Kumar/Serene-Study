import google.generativeai as genai
import streamlit as st
import os

# Try to load API key from secrets or environment
try:
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    api_key = secrets["GOOGLE_API_KEY"]
except:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("API Key not found in secrets or environment.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
