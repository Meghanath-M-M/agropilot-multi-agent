import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the .env file next to this script
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)

# API Keys and Endpoints
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
OPENWEATHERMAP_URL = "http://api.openweathermap.org/data/2.5/weather"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# UI Constants - Design System
COLORS = {
    "deep_green": "#24422C",
    "harvest_gold": "#C98A2C",
    "soil_terracotta": "#B8532F",
    "warm_cream": "#F7F1E1"
}

# Typography
FONTS = {
    "heading": "'Zilla Slab', serif",
    "body": "'Inter', sans-serif"
}

# App Settings
APP_NAME = "AgroPilot"
APP_SUBTITLE = "AI-Powered Multi-Agent Advisory System"
