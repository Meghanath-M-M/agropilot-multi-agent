# 🌾 AgroPilot: AI-Powered Multi-Agent Advisory

**AgroPilot** is an intelligent, multi-agent advisory system designed to provide actionable, localized, and multi-lingual farm advisories to Indian farmers.

Developed during the **IBM AI Agents Internship — July 2026**, this project aligns directly with the United Nations Sustainable Development Goals:
- 🌍 **UN SDG 2**: Zero Hunger
- 🌿 **UN SDG 15**: Life on Land

---

## 👥 Development Team
- Meghanath M M
- Abaikrishna M V
- Akash K V
- Michael Shan
- Sobin Joseph

---

## 🚀 Features
1. **Multi-Agent Architecture**: Separate intelligent agents handle Weather, Crop selection, Pest/Disease identification, and Market Intelligence concurrently.
2. **Multi-Lingual Support**: Automatically translates advisory output to 8 Indian regional languages instantly.
3. **WhatsApp Integration**: Dispatches verified advisories directly to the farmer's WhatsApp via Twilio.
4. **Human-in-the-Loop**: Includes a verification gate for a human expert to review and approve the AI's recommendations before dispatching.
5. **Analytics Dashboard**: Tracks sent advisories and geographical reach.

---

## 🛠️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ibm-project.git
cd ibm-project
```

### 2. Install Dependencies
Ensure you have Python 3.9+ installed, then run:
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or source venv/bin/activate # Mac/Linux

pip install -r requirements.txt
```

### 3. Environment Variables
Create a file named `.env` in the root directory (you can copy `.env.example`) and fill in your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here

# Twilio WhatsApp Sandbox (Optional - without these, it runs in Demo Mode)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### 4. Build Translation Cache
To pre-cache the multi-lingual UI elements, run the builder script:
```bash
python build_translations.py
```
*(Note: This takes a few minutes to respect rate limits).*

### 5. Run the Application
Start the Streamlit server:
```bash
python -m streamlit run app.py
```
The application will be accessible at `http://localhost:8501`.
