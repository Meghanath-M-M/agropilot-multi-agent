# 🌾 AgroPilot: AI-Powered Multi-Agent Advisory

**AgroPilot** is an intelligent, multi-agent advisory system designed to provide actionable, localized, and multi-lingual farm advisories to Indian farmers.

Developed during the **IBM AI Agents Internship — July 2026**, this project aligns directly with the United Nations Sustainable Development Goals:
- 🌍 **UN SDG 2**: Zero Hunger
- 🌿 **UN SDG 15**: Life on Land

---

## 🌐 Live Demo
You can try out the live deployed application here: 
**[https://agropilot-multi-agent.streamlit.app/](https://agropilot-multi-agent.streamlit.app/)**

---

## 👥 Development Team
- Meghanath M M
- Abaikrishna M V
- Akash K V
- Anjal P Salim
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

## 📱 Testing WhatsApp Delivery (Twilio Sandbox)
Because this project uses the Twilio WhatsApp Sandbox for development, **any phone number you want to send a message to must first join the sandbox.**

**How to join and receive messages:**
1. Open WhatsApp on the phone that will receive the advisory.
2. Send a message to the Twilio Sandbox Number (e.g. `+14155238886`).
3. Send the exact join code assigned to your Twilio account (for example: `join smooth-apple`).
4. Once Twilio replies with *"You are all set!"*, you can enter that phone number into AgroPilot and successfully receive WhatsApp advisories.

*(Note: If you do not configure Twilio API keys in the `.env` file, AgroPilot will gracefully fallback to "Demo Mode" and simulate a successful send in the UI without requiring sandbox access).*

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
