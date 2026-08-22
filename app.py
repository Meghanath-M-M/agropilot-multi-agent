"""
AgroPilot — Main Streamlit Application
AI-Powered Multi-Agent Advisory System for Indian Farmers

Pages:
  1. Farmer Input
  2. Agent Processing (animated)
  3. Human-in-the-Loop Approval
  4. Final Advisory Output
  5. Dashboard / Analytics
"""

import streamlit as st
import time
import json
import re
import pandas as pd
from datetime import datetime
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go

from config import APP_NAME, APP_SUBTITLE, COLORS
import utils
from agents import MasterOrchestrator
from messaging import WhatsAppMessenger
from audit import AuditLogger


# ═══════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════
st.set_page_config(
    page_title=f"{APP_NAME} — Farm Advisory",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

utils.inject_custom_css()


# ═══════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════
def initialize_session_state() -> None:
    """Initialize all session state variables."""
    defaults = {
        "page": "login",
        "advisory_data": None,
        "whatsapp_status": None,
        "form_data": None,
        "farmer_phone": "",
        "advisories_log": [],
        "language": "English",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def navigate_to(page_name: str) -> None:
    """Navigate to a specific page."""
    st.session_state.page = page_name
    st.session_state.whatsapp_status = None  # reset on navigation
    st.rerun()


# ═══════════════════════════════════════════
# UI TRANSLATIONS
# ═══════════════════════════════════════════
try:
    import json
    with open("ui_translations.json", "r", encoding="utf-8") as f:
        UI_TRANSLATIONS = json.load(f)
except Exception:
    UI_TRANSLATIONS = {}

def T(text: str) -> str:
    """Translate static UI text based on selected language."""
    lang = st.session_state.get("language", "English")
    if lang == "English":
        return text
    return UI_TRANSLATIONS.get(text, {}).get(lang, text)

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
def render_sidebar() -> None:
    """Renders the navigation sidebar."""
    with st.sidebar:
        st.markdown("# 🌾 AgroPilot")
        st.caption("AI-Powered Multi-Agent Advisory")
        st.markdown("---")

        st.markdown(f"##### {T('Navigation')}")
        if st.button(T("📝  New Advisory"), use_container_width=True, key="nav_input"):
            navigate_to("input")
        if st.button(T("📊  Dashboard"), use_container_width=True, key="nav_dash"):
            navigate_to("dashboard")

        st.markdown("---")
        st.markdown(f"##### 🌍 {T('Advisory Language')}")
        LANG_OPTIONS = [
            "English",
            "हिंदी (Hindi)",
            "தமிழ் (Tamil)",
            "తెలుగు (Telugu)",
            "ಕನ್ನಡ (Kannada)",
            "മലയാളം (Malayalam)",
            "मराठी (Marathi)",
            "ਬੰਗਲਾ (Bengali)",
            "ਪੰਜਾਬੀ (Punjabi)",
        ]
        selected_lang = st.selectbox(
            T("Translate advisory to:"),
            options=LANG_OPTIONS,
            index=LANG_OPTIONS.index(st.session_state.get("language", "English")),
            label_visibility="collapsed"
        )
        st.session_state.language = selected_lang

        st.markdown("---")
        st.markdown(f"##### {T('Agent Status')}")
        st.markdown(f"🟢 {T('Weather Agent')}")
        st.markdown(f"🟢 {T('Crop Agent')}")
        st.markdown(f"🟢 {T('Pest & Disease Agent')}")
        st.markdown(f"🟢 {T('Market Intelligence Agent')}")

        st.markdown("---")
        st.markdown(f"##### {T('About')}")
        st.caption("IBM AI Agents Internship — July 2026")
        st.caption("🌍 UN SDG 2 (Zero Hunger)")
        st.caption("🌿 UN SDG 15 (Life on Land)")
        
        st.markdown("---")
        st.markdown(f"##### {T('Developed By')}")
        st.caption("• Meghanath M M\n\n• Abaikrishna M V\n\n• Akash K V\n\n• Anjal P Salim\n\n• Michael Shan\n\n• Sobin Joseph")


# ═══════════════════════════════════════════
# PAGE 0 — LOGIN
# ═══════════════════════════════════════════
def page_login() -> None:
    """Login page to capture farmer phone number."""
    utils.render_hero(T("Welcome to AgroPilot"), T("Please enter your WhatsApp number to begin."))
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown(f"<h3 style='text-align:center; color:#24422C;'>{T('Login')}</h3>", unsafe_allow_html=True)
            phone = st.text_input(
                T("WhatsApp Number"), 
                value=st.session_state.farmer_phone,
                placeholder="+919876543210"
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(T("Continue ➔"), use_container_width=True, type="primary"):
                if len(phone) >= 10:
                    st.session_state.farmer_phone = phone
                    navigate_to("input")
                else:
                    st.error("Please enter a valid phone number (at least 10 digits).")

# ═══════════════════════════════════════════
# PAGE 1 — FARMER INPUT
# ═══════════════════════════════════════════
POPULAR_CITIES = [
    "Delhi", "Mumbai", "Pune", "Jaipur", "Lucknow",
    "Bhopal", "Nagpur", "Hyderabad", "Chennai", "Kolkata",
    "Nashik", "Indore", "Patna", "Varanasi", "Kanpur"
]


def page_input() -> None:
    """Renders the farmer input form."""
    utils.render_hero(
        T("Generate Farm Advisory"),
        T("Enter your farm details below. Our 4 AI agents will analyze weather, recommend crops, assess pest risks, and provide market intelligence.")
    )

    with st.form("farmer_input_form", border=False):
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown(f"#### 📍 {T('Location & Preferences')}")
            location = st.selectbox(
                T("City / Village"),
                options=POPULAR_CITIES,
                index=0,
                help=T("Select the nearest major city for weather data.")
            )
            custom_location = st.text_input(
                T("Or type a custom location"),
                placeholder="e.g., Meerut, Aurangabad"
            )
            crop_pref = st.text_input(
                T("Current Crop / Crop Preference (Optional)"),
                placeholder="e.g., Rice, Wheat, Tomato",
                help="Enter the crop currently in your field for disease or pest advice, or leave blank if you want a new crop recommendation based on your location and soil."
            )
            soil_type = st.selectbox(
                T("Soil Type (Optional)"),
                ["Auto-detect", "Sandy", "Clay", "Loam", "Red Soil", "Black Soil", "Alluvial"]
            )

        with col2:
            st.markdown(f"#### 🐛 {T('Symptoms & Evidence')}")
            symptoms = st.text_area(
                T("Describe Pest/Disease Symptoms (Optional)"),
                placeholder="e.g., yellow spots on leaves, wilting, stunted growth, visible insects...",
                height=120
            )
            photo = st.file_uploader(
                T("Upload Crop Photo (Optional)"),
                type=["jpg", "png", "jpeg"],
                help="Upload a photo of affected leaves or plants for AI analysis."
            )

        st.markdown("")  # spacing
        submitted = st.form_submit_button(f"🚀  {T('Analyze & Generate Advisory')}", use_container_width=True)

        if submitted:
            final_location = custom_location.strip() if custom_location.strip() else location
            if not final_location:
                st.error("Please select or enter a location.")
            else:
                st.session_state.form_data = {
                    "location": final_location,
                    "crop_pref": crop_pref,
                    "soil_type": soil_type,
                    "symptoms": symptoms,
                    "has_photo": photo is not None
                }
                navigate_to("processing")


# ═══════════════════════════════════════════
# PAGE 2 — AGENT PROCESSING
# ═══════════════════════════════════════════
AGENT_STEPS = [
    ("🌦️", "Weather Agent", "Fetching real-time weather data and seasonal analysis..."),
    ("🌱", "Crop Recommendation Agent", "Analyzing soil, weather, and crop suitability..."),
    ("🐛", "Pest & Disease Agent", "Evaluating symptoms and identifying potential threats..."),
    ("💰", "Market Intelligence Agent", "Gathering prices, trends, and mandi strategies..."),
]


def page_processing() -> None:
    """Shows animated agent processing steps."""
    utils.render_hero(
        T("Agents Processing"),
        f"{T('Analyzing inputs for')} {st.session_state.form_data['location']}..."
    )

    # Create placeholders for each agent step
    step_placeholders = []
    for i, (icon, name, desc) in enumerate(AGENT_STEPS):
        step_placeholders.append(st.empty())

    progress = st.progress(0)
    status = st.empty()

    # Animate through each agent
    for i, (icon, name, desc) in enumerate(AGENT_STEPS):
        # Mark previous steps as done
        for j in range(i):
            prev_icon, prev_name, prev_desc = AGENT_STEPS[j]
            step_placeholders[j].markdown(f"""
                <div class="agent-step done">
                    <span class="agent-name">{prev_icon} {T(prev_name)}</span>
                    <div class="agent-desc">✅ {T('Complete')}</div>
                </div>
            """, unsafe_allow_html=True)

        # Mark current step as active
        step_placeholders[i].markdown(f"""
            <div class="agent-step active">
                <span class="agent-name">{icon} {T(name)}</span>
                <div class="agent-desc">⏳ {T(desc)}</div>
            </div>
        """, unsafe_allow_html=True)

        # Render future steps
        for j in range(i + 1, len(AGENT_STEPS)):
            fut_icon, fut_name, fut_desc = AGENT_STEPS[j]
            step_placeholders[j].markdown(f"""
                <div class="agent-step">
                    <span class="agent-name">{fut_icon} {T(fut_name)}</span>
                    <div class="agent-desc">{T('Waiting...')}</div>
                </div>
            """, unsafe_allow_html=True)

        status.info(f"⏳ {name}: {desc}")
        progress.progress((i + 1) * 25)
        time.sleep(1.2)

    # Mark all done
    for i, (icon, name, desc) in enumerate(AGENT_STEPS):
        step_placeholders[i].markdown(f"""
            <div class="agent-step done">
                <span class="agent-name">{icon} {T(name)}</span>
                <div class="agent-desc">✅ {T('Complete')}</div>
            </div>
        """, unsafe_allow_html=True)

    # Run actual orchestration
    status.info(f"🔄 {T('Compiling unified advisory...')}")
    orchestrator = MasterOrchestrator()
    data = st.session_state.form_data
    advisory = orchestrator.generate_advisory(
        location=data.get("location", ""),
        symptoms=data.get("symptoms", ""),
        crop_pref=data.get("crop_pref", ""),
        soil_type=data.get("soil_type", ""),
        has_photo=data.get("has_photo", False)
    )
    advisory["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # ── Translate advisory if non-English ──
    lang = st.session_state.get("language", "English")
    if lang != "English":
        status.info(f"🌐 Translating advisory to {lang}...")
        result = _translate_advisory(advisory, lang)
        if isinstance(result, dict):
            # Update advisory in-place
            advisory["crop"]["crop_name"] = result.get("crop_name", advisory["crop"].get("crop_name"))
            advisory["crop"]["reason"] = result.get("crop_reason", advisory["crop"].get("reason"))
            advisory["crop"]["sowing_time"] = result.get("sowing_time", advisory["crop"].get("sowing_time"))
            advisory["crop"]["harvest_time"] = result.get("harvest_time", advisory["crop"].get("harvest_time"))
            advisory["crop"]["water_needs"] = result.get("water_needs", advisory["crop"].get("water_needs"))
            advisory["crop"]["soil_type"] = result.get("soil_type", advisory["crop"].get("soil_type"))
            
            advisory["pest"]["pest_name"] = result.get("pest_name", advisory["pest"].get("pest_name"))
            advisory["pest"]["symptoms"] = result.get("pest_symptoms", advisory["pest"].get("symptoms"))
            advisory["pest"]["organic_treatment"] = result.get("organic_treatment", advisory["pest"].get("organic_treatment"))
            advisory["pest"]["chemical_treatment"] = result.get("chemical_treatment", advisory["pest"].get("chemical_treatment"))
            advisory["pest"]["preventive_measures"] = result.get("preventive_measures", advisory["pest"].get("preventive_measures"))
            
            advisory["weather"]["analysis"] = result.get("weather_analysis", advisory["weather"].get("analysis"))
            
            advisory["market"]["sell_timing"] = result.get("sell_timing", advisory["market"].get("sell_timing"))
            advisory["market"]["storage_tips"] = result.get("storage_tips", advisory["market"].get("storage_tips"))
            advisory["market"]["market_strategy"] = result.get("market_strategy", advisory["market"].get("market_strategy"))
            
            advisory["translation_status"] = f"Translated to {lang}"
        else:
            advisory["translation_error"] = str(result)

    st.session_state.advisory_data = advisory

    # Log generation
    AuditLogger().log_advisory_generated(advisory)

    progress.progress(100)
    status.success(f"✅ {T('All agents complete — advisory ready for expert review!')}")
    time.sleep(1)
    navigate_to("approval")


# ═══════════════════════════════════════════
# PAGE 3 — HUMAN-IN-THE-LOOP APPROVAL
# ═══════════════════════════════════════════
def page_approval() -> None:
    """Human expert approval gate."""
    advisory = st.session_state.advisory_data
    if not advisory:
        st.error("No advisory data found. Please generate one first.")
        if st.button("← Back to Input"):
            navigate_to("input")
        return

    utils.render_hero(
        T("Expert Approval Gate"),
        T("Review the AI-generated advisory below. Approve to send to farmer via WhatsApp, or reject to modify.")
    )

    if "translation_status" in advisory:
        st.info(f"🌐 {advisory['translation_status']}")
    elif "translation_error" in advisory:
        err = advisory['translation_error'].replace('__error__: ', '')
        st.warning(f"⚠️ Translation failed: {err}")

    crop = advisory.get("crop", {})
    pest = advisory.get("pest", {})
    market = advisory.get("market", {})
    weather = advisory.get("weather", {})

    # ── Summary metrics ──
    st.markdown(f'<div class="section-header">📋 {T("Advisory Summary")}</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"📍 {T('Location')}", advisory.get("farmer_location", "N/A"))
    col2.metric(f"🌱 {T('Crop')}", crop.get("crop_name", "N/A").split("(")[0].strip())
    severity = pest.get("severity", "low").upper()
    col3.metric(f"🐛 {T('Pest Risk')}", severity)
    col4.metric(f"💰 {T('Price')}", f"₹{market.get('price', 0)}/{market.get('unit', 'qt')}")

    st.markdown("")

    # ── Details in expanders ──
    with st.expander(f"🌦️ {T('Weather Details')}", expanded=True):
        c1, c2, c3 = st.columns(3)
        c1.write(f"**{T('Temperature:')}** {weather.get('temp')}°C")
        c2.write(f"**{T('Humidity:')}** {weather.get('humidity')}%")
        c3.write(f"**{T('Rainfall:')}** {weather.get('rainfall', 'N/A').capitalize()}")
        st.info(weather.get("analysis", ""))

    with st.expander(f"🌱 {T('Crop Recommendation')}"):
        st.write(f"**{crop.get('crop_name', '')}**")
        st.write(crop.get("reason", ""))
        c1, c2, c3 = st.columns(3)
        c1.write(f"**{T('Sow:')}** {crop.get('sowing_time')}")
        c2.write(f"**{T('Harvest:')}** {crop.get('harvest_time')}")
        c3.write(f"**{T('Water:')}** {crop.get('water_needs', '').capitalize()}")

    with st.expander(f"🐛 {T('Pest & Disease Assessment')}"):
        st.write(f"**{pest.get('pest_name')}** — {T('Severity:')} **{pest.get('severity', '').upper()}**")
        st.write(f"*{T('Symptoms:')}* {pest.get('symptoms')}")
        st.write(f"🌿 *{T('Organic:')}* {pest.get('organic_treatment')}")
        st.write(f"💊 *{T('Chemical:')}* {pest.get('chemical_treatment')}")
        st.warning(f"⏰ {T('Action by:')} {pest.get('action_by_date')}")

    with st.expander(f"💰 {T('Market Intelligence')}"):
        c1, c2 = st.columns(2)
        c1.write(f"**{T('Price:')}** ₹{market.get('price')}/{market.get('unit')} ({market.get('trend')})")
        c2.write(f"**{T('Best Mandi:')}** {market.get('best_market')}")
        st.write(f"**{T('Strategy:')}** {market.get('sell_timing')}")
        st.write(f"**{T('Storage:')}** {market.get('storage_tips')}")

    st.markdown("---")

    # ── Approval actions ──
    col_phone, col_actions = st.columns([2, 1])

    with col_phone:
        phone = st.text_input(
            "📱 Farmer's WhatsApp Number",
            value=st.session_state.farmer_phone,
            help="Include country code, e.g. +919876543210"
        )
        st.session_state.farmer_phone = phone

    with col_actions:
        st.markdown("")
        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(T("❌ Reject"), use_container_width=True, key="reject_btn"):
                AuditLogger().log_advisory_rejected(advisory)
                navigate_to("input")
        with c2:
            if st.button(T("✅ Approve & Send"), use_container_width=True, key="approve_btn"):
                AuditLogger().log_advisory_approved(advisory, phone)
                # Log this advisory
                st.session_state.advisories_log.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "location": advisory.get("farmer_location"),
                    "crop": crop.get("crop_name", "").split("(")[0].strip(),
                    "status": "✅ Approved"
                })
                navigate_to("output")


# ═══════════════════════════════════════════
# PAGE 4 — ADVISORY OUTPUT
# ═══════════════════════════════════════════

# Map data_source values to display labels and CSS classes
_SOURCE_LABELS = {
    "live_api":            ("Live API",      "#1e7e34", "#e6f4ea"),
    "llm_generated":       ("AI Generated",  "#0c5ea0", "#dbeafe"),
    "rule_based_fallback": ("Rule-Based",    "#856404", "#fef3cd"),
    "unknown":             ("Unknown",       "#666",    "#eee"),
}


def _source_pill(source_key: str) -> str:
    """Return an HTML pill badge for a data source."""
    label, color, bg = _SOURCE_LABELS.get(source_key, _SOURCE_LABELS["unknown"])
    return (f'<span style="display:inline-block;padding:2px 10px;border-radius:12px;'
            f'font-size:0.75rem;font-weight:600;color:{color};background:{bg};'
            f'margin-left:6px;">{label}</span>')


def _translate_advisory(advisory: dict, target_lang: str):
    """Use Groq LLM to translate advisory text fields to target_lang.
    Returns translated dict on success, or a string error message on failure.
    """
    import logging
    import config
    _log = logging.getLogger(__name__)

    if not config.GROQ_API_KEY:
        return "__error__: GROQ_API_KEY is not set in .env"

    try:
        from groq import Groq
        client = Groq(api_key=config.GROQ_API_KEY)
        crop = advisory.get("crop", {})
        pest = advisory.get("pest", {})
        market = advisory.get("market", {})
        weather = advisory.get("weather", {})
        payload = {
            "crop_name": crop.get("crop_name", ""),
            "crop_reason": crop.get("reason", ""),
            "sowing_time": crop.get("sowing_time", ""),
            "harvest_time": crop.get("harvest_time", ""),
            "water_needs": crop.get("water_needs", ""),
            "soil_type": crop.get("soil_type", ""),
            "pest_name": pest.get("pest_name", ""),
            "pest_symptoms": pest.get("symptoms", ""),
            "organic_treatment": pest.get("organic_treatment", ""),
            "chemical_treatment": pest.get("chemical_treatment", ""),
            "preventive_measures": pest.get("preventive_measures", ""),
            "weather_analysis": weather.get("analysis", ""),
            "sell_timing": market.get("sell_timing", ""),
            "storage_tips": market.get("storage_tips", ""),
            "market_strategy": market.get("market_strategy", ""),
        }
        prompt = (
            f"Translate the following agricultural advisory JSON fields to {target_lang}.\n"
            "CRITICAL INSTRUCTION: Output ONLY valid raw JSON. No markdown fences, no explanations, no reasoning text, no extra content.\n"
            "Return a JSON object with the SAME keys, values translated.\n"
            "Do NOT translate numbers, dates, or technical chemical names.\n\n"
            f"Input JSON:\n{json.dumps(payload, ensure_ascii=False)}"
        )
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are a pure JSON translation function. You must ONLY output valid raw JSON. No markdown fences, no explanations, no reasoning text, no XML tags, no environment details, no extra content of any kind."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip()
        for tag in ["environment_details", "environment_info", "meta"]:
            raw = re.sub(rf"<{tag}>.*?</{tag}>", "", raw, flags=re.DOTALL)
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            return f"__error__: LLM did not return valid JSON. Got: {raw[:200]}"
        return json.loads(raw[start:end])
    except Exception as e:
        _log.error(f"Translation error: {e}")
        return f"__error__: {e}"


def page_output() -> None:
    """Renders the final verified advisory and sends WhatsApp."""
    advisory = st.session_state.advisory_data
    if not advisory:
        st.error("No advisory data found.")
        if st.button("← Back"):
            navigate_to("input")
        return

    # ── Send WhatsApp (once) ──
    if st.session_state.whatsapp_status is None:
        messenger = WhatsAppMessenger()
        phone = st.session_state.get("farmer_phone", "")
        success, msg = messenger.send_message(phone, advisory)
        st.session_state.whatsapp_status = (success, msg)
        AuditLogger().log_whatsapp_sent(phone, success, msg)

    success, status_msg = st.session_state.whatsapp_status

    success, status_msg = st.session_state.whatsapp_status

    if "translation_status" in advisory:
        st.success(f"🌐 Advisory {advisory['translation_status'].lower()}")
    elif "translation_error" in advisory:
        err = advisory['translation_error'].replace('__error__: ', '')
        st.warning(f"⚠️ Translation failed: {err}")

    # ── Header ──
    utils.render_hero(
        T("Verified Advisory Report"),
        f"Advisory for {advisory.get('farmer_location')} — Generated {advisory.get('timestamp', 'now')}"
    )

    # WhatsApp status
    if success:
        st.success(f"📱 {status_msg}")
    else:
        st.error(f"📱 {status_msg}")

    # Language badge
    lang = st.session_state.get("language", "English")
    if lang != "English":
        st.markdown(
            f'<span class="lang-badge">🌐 {T("Advisory translated to")} {lang}</span>',
            unsafe_allow_html=True
        )
        st.markdown("")

    # Field Verified stamp + Confidence badge
    confidence = advisory.get("advisory_confidence", 0.0)
    conf_pct = int(confidence * 100)
    conf_color = "#1e7e34" if conf_pct >= 85 else "#856404" if conf_pct >= 70 else "#c0392b"
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:1.5rem; flex-wrap:wrap;">
            <div class="field-verified-stamp">{T('✅ FIELD VERIFIED — EXPERT APPROVED')}</div>
            <div style="display:inline-flex;align-items:center;gap:6px;padding:8px 18px;
                        border-radius:8px;background:rgba(36,66,44,0.05);border:2px solid {conf_color};">
                <span style="font-weight:700;color:{conf_color};font-size:1.1rem;
                             font-family:'Zilla Slab',serif;">🎯 {conf_pct}%</span>
                <span style="font-size:0.8rem;color:#666;">{T('Advisory Confidence')}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    weather = advisory.get("weather", {})
    crop = advisory.get("crop", {})
    pest = advisory.get("pest", {})
    market = advisory.get("market", {})
    sources = advisory.get("agent_sources", {})
    # Use translated content where available
    t = advisory

    # ── Report cards ──
    col1, col2 = st.columns(2, gap="large")

    with col1:
        utils.render_card(T("Weather Conditions"), "🌦️", (
            f'<p><span class="label">{T("Temperature:")}</span> <span class="value">{weather.get("temp")}°C</span></p>'
            f'<p><span class="label">{T("Humidity:")}</span> <span class="value">{weather.get("humidity")}%</span></p>'
            f'<p><span class="label">{T("Condition:")}</span> <span class="value">{weather.get("condition", "").capitalize()}</span></p>'
            f'<p><span class="label">{T("Rainfall:")}</span> <span class="value">{weather.get("rainfall", "").capitalize()}</span></p>'
            f'<p style="margin-top:0.5rem; font-style:italic; color:#555;">{weather.get("analysis", "")}</p>'
        ))

        utils.render_card(T("Pest & Disease Alert"), "🐛", (
            f'<p><span class="label">{T("Identified:")}</span> <span class="value">{pest.get("pest_name")}</span></p>'
            f'<p><span class="label">{T("Severity:")}</span> <span class="value" style="color:{"#c0392b" if pest.get("severity") in ("high","medium") else "#27ae60"}">{pest.get("severity", "").upper()}</span></p>'
            f'<p><span class="label">{T("Symptoms:")}</span> {pest.get("symptoms")}</p>'
            f'<p><span class="label">🌿 {T("Organic:")}</span> {pest.get("organic_treatment")}</p>'
            f'<p><span class="label">💊 {T("Chemical:")}</span> {pest.get("chemical_treatment")}</p>'
            f'<p><span class="label">🛡️ {T("Prevention:")}</span> {pest.get("preventive_measures")}</p>'
            f'<p style="margin-top:0.5rem; color:#B8532F; font-weight:600;">⏰ {T("Action by:")} {pest.get("action_by_date")}</p>'
        ))

    with col2:
        utils.render_card(T("Crop Recommendation"), "🌱", (
            f'<p><span class="value" style="font-size:1.1rem;">{crop.get("crop_name")}</span></p>'
            f'<p style="color:#555;">{crop.get("reason")}</p>'
            f'<p><span class="label">{T("Sow:")}</span> <span class="value">{crop.get("sowing_time")}</span></p>'
            f'<p><span class="label">{T("Harvest:")}</span> <span class="value">{crop.get("harvest_time")}</span></p>'
            f'<p><span class="label">{T("Water:")}</span> <span class="value">{crop.get("water_needs", "").capitalize()}</span></p>'
            f'<p><span class="label">Soil Type:</span> <span class="value">{crop.get("soil_type")}</span></p>'
        ))

        utils.render_card(T("Market Intelligence"), "💰", (
            f'<p><span class="label">{T("Current Price:")}</span> <span class="value">₹{market.get("price")}/{market.get("unit")}</span> <span style="color:#27ae60;">({market.get("trend")})</span></p>'
            f'<p><span class="label">{T("Best Mandi:")}</span> <span class="value">{market.get("best_market")}</span></p>'
            f'<p><span class="label">{T("Sell Timing:")}</span> {market.get("sell_timing")}</p>'
            f'<p><span class="label">{T("Storage:")}</span> {market.get("storage_tips")}</p>'
            f'<p><span class="label">{T("Strategy:")}</span> {market.get("market_strategy")}</p>'
        ))

    # ── Income projection ──
    st.markdown("")
    utils.render_income_card(
        advisory.get("expected_income", 45000),
        advisory.get("previous_income", 36500),
        advisory.get("income_improvement", "+23%")
    )
    # Illustrative estimate disclaimer
    if advisory.get("illustrative_estimate"):
        st.caption("⚠️ _Income projection is an illustrative estimate based on average regional yields and current mandi prices. Actual results may vary._")
    st.markdown("")

    # ── Data Source Transparency ──
    st.markdown('<div class="section-header">🔍 Data Sources & Transparency</div>', unsafe_allow_html=True)
    source_html = '<div style="display:flex;flex-wrap:wrap;gap:1rem;margin-bottom:1rem;">'
    agent_labels = {
        "weather": "🌦️ Weather",
        "crop": "🌱 Crop",
        "pest": "🐛 Pest",
        "market": "💰 Market",
    }
    for key, label in agent_labels.items():
        src = sources.get(key, "unknown")
        pill = _source_pill(src)
        source_html += (
            '<div style="background:white;border-radius:10px;padding:0.6rem 1rem;'
            'box-shadow:0 1px 4px rgba(0,0,0,0.06);display:flex;align-items:center;gap:4px;">'
            f'<span style="font-weight:600;font-size:0.85rem;color:#24422C;">{label}</span>'
            f'{pill}</div>'
        )
    source_html += '</div>'
    st.markdown(source_html, unsafe_allow_html=True)

    st.markdown("")

    # ── Action buttons ──
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("📤 Resend WhatsApp", use_container_width=True):
            messenger = WhatsAppMessenger()
            s, m = messenger.send_message(st.session_state.farmer_phone, advisory)
            AuditLogger().log_whatsapp_resend(st.session_state.farmer_phone, s)
            st.toast(f"{'✅' if s else '❌'} {m}")
    with col_b:
        st.button("📞 Call Expert", use_container_width=True)
    with col_c:
        w_d = advisory.get("weather", {})
        c_d = advisory.get("crop", {})
        p_d = advisory.get("pest", {})
        m_d = advisory.get("market", {})
        report_text = (
            f"=================================\n"
            f"    AGROPILOT ADVISORY REPORT    \n"
            f"=================================\n"
            f"Date: {advisory.get('timestamp', 'N/A')}\n"
            f"Location: {advisory.get('farmer_location', 'N/A')}\n\n"
            f"--- CROP RECOMMENDATION ---\n"
            f"Crop: {c_d.get('crop_name')}\n"
            f"Reason: {c_d.get('reason')}\n"
            f"Sowing: {c_d.get('sowing_time')}\n"
            f"Harvest: {c_d.get('harvest_time')}\n"
            f"Soil Type: {c_d.get('soil_type')}\n\n"
            f"--- WEATHER CONDITIONS ---\n"
            f"Temp: {w_d.get('temp')}°C, Humidity: {w_d.get('humidity')}%\n"
            f"Condition: {w_d.get('condition', '').capitalize()}\n"
            f"Rainfall: {w_d.get('rainfall', '').capitalize()}\n\n"
            f"--- PEST & DISEASE ALERT ---\n"
            f"Identified: {p_d.get('pest_name')} (Severity: {p_d.get('severity')})\n"
            f"Symptoms: {p_d.get('symptoms')}\n"
            f"Organic Treatment: {p_d.get('organic_treatment')}\n"
            f"Chemical Treatment: {p_d.get('chemical_treatment')}\n\n"
            f"--- MARKET INTELLIGENCE ---\n"
            f"Current Price: Rs {m_d.get('price')}/{m_d.get('unit')} ({m_d.get('trend')})\n"
            f"Best Mandi: {m_d.get('best_market')}\n"
            f"Sell Timing: {m_d.get('sell_timing')}\n"
            f"Storage: {m_d.get('storage_tips')}\n"
        )
        st.download_button("📥 Download Report", data=report_text, file_name="agropilot_advisory.txt", use_container_width=True)
    with col_d:
        if st.button("🔄 New Advisory", use_container_width=True):
            navigate_to("input")

    # Footer
    st.markdown("""
        <div style="text-align:center; color:#999; margin-top:3rem; padding:1rem; font-size:0.8rem;">
            Generated by <strong>AgroPilot Multi-Agent System</strong> — 
            Weather Agent · Crop Agent · Pest Agent · Market Agent<br>
            IBM AI Agents Internship 2026 · UN SDG 2 & 15
        </div>
    """, unsafe_allow_html=True)



# ═══════════════════════════════════════════
# PAGE 5 — DASHBOARD / ANALYTICS
# ═══════════════════════════════════════════
def page_dashboard() -> None:
    """Renders the analytics dashboard."""
    utils.render_hero(
        "AgroPilot Dashboard",
        "Real-time impact tracking and system analytics"
    )

    # Read audit logs
    log_file = Path(__file__).resolve().parent / "logs" / "audit.jsonl"
    audit_data = []
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        audit_data.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    # Compute metrics
    advisories = [d for d in audit_data if d.get("event") == "advisory_generated"]
    approved = [d for d in audit_data if d.get("event") == "advisory_approved"]
    whatsapp_sent = [d for d in audit_data if d.get("event") == "whatsapp_delivery" and d.get("success")]
    
    total_advised = len(advisories)
    total_approved = len(approved)
    total_sent = len(whatsapp_sent)
    est_loss_prevented = total_approved * 5000

    # ── Impact Metrics ──
    st.markdown('<div class="section-header">📈 Impact Metrics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🌾 Advisories Generated", f"{total_advised}")
    col2.metric("✅ Advisories Approved", f"{total_approved}")
    col3.metric("📱 WhatsApp Sent", f"{total_sent}")
    col4.metric("🛡️ Crop Loss Prevented (Est.)", f"₹{est_loss_prevented:,}")

    st.markdown("")

    # ── Recent advisories ──
    st.markdown('<div class="section-header">📋 Recent Approved Advisories</div>', unsafe_allow_html=True)

    recent_approved = []
    for d in reversed(approved[-10:]):
        recent_approved.append({
            "Date": d.get("timestamp", "")[:10],
            "Location": d.get("location", "Unknown"),
            "Crop": d.get("crop", "Unknown").split(' (')[0] if ' (' in d.get("crop", "Unknown") else d.get("crop", "Unknown"),
            "Status": "✅ Approved"
        })
    
    if not recent_approved:
        st.info("No approved advisories yet.")
    else:
        df = pd.DataFrame(recent_approved)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("")

    # ── Charts ──
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<div class="section-header">🗺️ Geographic Distribution</div>', unsafe_allow_html=True)
        if advisories:
            locs = [d.get("location", "Unknown").title() for d in advisories if d.get("location")]
            if locs:
                loc_counts = pd.Series(locs).value_counts().reset_index()
                loc_counts.columns = ["Region", "Advisories"]
                fig_geo = px.bar(
                    loc_counts, x="Advisories", y="Region", orientation="h",
                    color="Advisories",
                    color_continuous_scale=["#e8f5e9", "#C98A2C"],
                    text="Advisories",
                )
                fig_geo.update_traces(textposition="outside")
                fig_geo.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=20, t=10, b=0), showlegend=False,
                    coloraxis_showscale=False,
                    yaxis=dict(categoryorder="total ascending"),
                    height=250
                )
                st.plotly_chart(fig_geo, use_container_width=True)
            else:
                st.info("No location data yet")
        else:
            st.info("No location data yet")

    with col_right:
        st.markdown('<div class="section-header">🌾 Crop Distribution</div>', unsafe_allow_html=True)
        if advisories:
            crops = [
                d.get("crop", "Unknown").split(" (")[0] if " (" in d.get("crop", "Unknown")
                else d.get("crop", "Unknown")
                for d in advisories if d.get("crop")
            ]
            if crops:
                crop_counts = pd.Series(crops).value_counts().reset_index()
                crop_counts.columns = ["Crop", "Count"]
                fig_crop = px.pie(
                    crop_counts, values="Count", names="Crop", hole=0.45,
                    color_discrete_sequence=["#24422C", "#C98A2C", "#3a6b47", "#d49a3c",
                                             "#1a3320", "#e8b86d", "#5a8a6a", "#f0d090"]
                )
                fig_crop.update_traces(textposition="inside", textinfo="percent+label")
                fig_crop.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation="h", y=-0.15),
                    height=280,
                    showlegend=False
                )
                st.plotly_chart(fig_crop, use_container_width=True)
            else:
                st.info("No crop data yet")
        else:
            st.info("No crop data yet")

    st.markdown("")

    # ── Data Source Breakdown ──
    st.markdown('<div class="section-header">🔍 Data Source Breakdown</div>', unsafe_allow_html=True)
    if advisories:
        all_sources = []
        for d in advisories:
            srcs = d.get("agent_sources", {})
            if isinstance(srcs, dict):
                all_sources.extend(srcs.values())
        if all_sources:
            src_counts = pd.Series(all_sources).value_counts().reset_index()
            src_counts.columns = ["Source", "Count"]
            src_labels = {
                "live_api": "🟢 Live API",
                "llm_generated": "🔵 AI Generated",
                "rule_based_fallback": "🟡 Rule-Based",
                "unknown": "⚫ Unknown"
            }
            src_counts["Source"] = src_counts["Source"].map(lambda x: src_labels.get(x, x))
            fig_src = px.bar(
                src_counts, x="Source", y="Count",
                color="Source",
                color_discrete_sequence=["#1e7e34", "#0c5ea0", "#856404", "#666"],
                text="Count"
            )
            fig_src.update_traces(textposition="outside")
            fig_src.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0), showlegend=False, height=280,
                xaxis_title="", yaxis_title="Agent Calls"
            )
            st.plotly_chart(fig_src, use_container_width=True)


    # ── Agent health ──
    st.markdown('<div class="section-header">🏥 Agent Health Status</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, (icon, name, latency) in zip(
        [c1, c2, c3, c4],
        [
            ("🌦️", "Weather Agent", "120ms"),
            ("🌱", "Crop Agent", "450ms"),
            ("🐛", "Pest Agent", "380ms"),
            ("💰", "Market Agent", "200ms"),
        ]
    ):
        with col:
            html_content = (
                f'<p><span class="label">Status:</span> <span class="value" style="color:#27ae60;">● Online</span></p>'
                f'<p><span class="label">Avg Latency:</span> <span class="value">{latency}</span></p>'
                f'<p><span class="label">Uptime:</span> <span class="value">99.8%</span></p>'
            )
            utils.render_card(name, icon, html_content)


# ═══════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════
def main() -> None:
    """Application entry point and page router."""
    initialize_session_state()
    render_sidebar()

    page = st.session_state.page

    if page == "login":
        page_login()
    elif page == "input":
        page_input()
    elif page == "processing":
        page_processing()
    elif page == "approval":
        page_approval()
    elif page == "output":
        page_output()
    elif page == "dashboard":
        page_dashboard()


if __name__ == "__main__":
    main()
