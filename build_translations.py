import json
import os
import sys
import time

# Add current dir to path to import config
sys.path.append(os.path.dirname(__file__))
import config

from groq import Groq

client = Groq(api_key=config.GROQ_API_KEY)

STRINGS = [
    "Welcome to AgroPilot",
    "Please enter your WhatsApp number to begin.",
    "Login",
    "WhatsApp Number",
    "Continue ➔",
    "Generate Farm Advisory",
    "Enter your farm details below. Our 4 AI agents will analyze weather, recommend crops, assess pest risks, and provide market intelligence.",
    "📍 Location & Preferences",
    "City / Village",
    "Select the nearest major city for weather data.",
    "Or type a custom location",
    "Current Crop / Crop Preference (Optional)",
    "Soil Type (Optional)",
    "🐛 Symptoms & Evidence",
    "Describe Pest/Disease Symptoms (Optional)",
    "Upload Crop Photo (Optional)",
    "🚀 Analyze & Generate Advisory",
    "Navigation",
    "📝  New Advisory",
    "📊  Dashboard",
    "🌍 Advisory Language",
    "Translate advisory to:",
    "Agent Status",
    "🟢 Weather Agent",
    "🟢 Crop Agent",
    "🟢 Pest & Disease Agent",
    "🟢 Market Intelligence Agent",
    "About",
    "Agents Processing",
    "Waiting...",
    "Complete",
    "Compiling unified advisory...",
    "All agents complete — advisory ready for expert review!",
    "Expert Approval Gate",
    "Review the AI-generated advisory below. Approve to send to farmer via WhatsApp, or reject to modify.",
    "📋 Advisory Summary",
    "📍 Location",
    "🌱 Crop",
    "🐛 Pest Risk",
    "💰 Price",
    "🌦️ Weather Details",
    "Temperature:",
    "Humidity:",
    "Condition:",
    "Rainfall:",
    "🌱 Crop Recommendation",
    "Sow:",
    "Harvest:",
    "Water:",
    "🐛 Pest & Disease Assessment",
    "Severity:",
    "Symptoms:",
    "🌿 Organic:",
    "💊 Chemical:",
    "🛡️ Prevention:",
    "Action by:",
    "💰 Market Intelligence",
    "Best Mandi:",
    "Sell Timing:",
    "Storage:",
    "Strategy:",
    "❌ Reject",
    "✅ Approve & Send",
    "Verified Advisory Report",
    "✅ FIELD VERIFIED — EXPERT APPROVED",
    "Advisory Confidence",
    "Weather Conditions",
    "Pest & Disease Alert",
    "Identified:",
    "Current Price:"
]

LANGUAGES = [
    "हिंदी (Hindi)",
    "தமிழ் (Tamil)",
    "తెలుగు (Telugu)",
    "ಕನ್ನಡ (Kannada)",
    "മലയാളം (Malayalam)",
    "मराठी (Marathi)",
    "ਬੰਗਲਾ (Bengali)",
    "ਪੰਜਾਬੀ (Punjabi)"
]

translations = {}
for text in STRINGS:
    translations[text] = {}

print("Translating UI strings...")
try:
    for lang in LANGUAGES:
        print("Translating to next language...")
        prompt = f"Translate this JSON array of English UI strings to {lang}. Return ONLY a JSON dictionary where the keys are the English strings, and the values are the translated strings.\n\n{json.dumps(STRINGS)}"
        
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        
        for text in STRINGS:
            translations[text][lang] = data.get(text, text)
            
        time.sleep(30)
            
    with open("ui_translations.json", "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    print("Done! Saved to ui_translations.json")
except Exception as e:
    print(f"Failed: {e}")
