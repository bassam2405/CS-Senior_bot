#This is used to check the models available as gemini updates them regularly
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load the key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("------------------------------------------------")
print(f"Checking models for API Key ending in: ...{api_key[-5:]}")
print("------------------------------------------------")

try:
    # Ask Google for the list of available models
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ AVAILABLE: {m.name}")
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nTIP: If you see an error about 'version', try: pip install --upgrade google-generativeai")
