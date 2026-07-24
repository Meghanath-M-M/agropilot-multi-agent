"""
AgroPilot Utility Functions
Helper functions for CSS injection, mock data generation, and formatting.
"""

import streamlit as st
import config
from datetime import datetime
from typing import Dict


def inject_custom_css() -> None:
    """Injects the AgroPilot design system CSS into the Streamlit app."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Zilla+Slab:wght@400;500;600;700&display=swap');

        /* ── Global Typography ── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            font-family: 'Zilla Slab', serif !important;
            color: #24422C !important;
            letter-spacing: -0.02em;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a3320 0%, #24422C 40%, #2d5236 100%);
        }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] h4, section[data-testid="stSidebar"] .stMarkdown h4,
        section[data-testid="stSidebar"] h5, section[data-testid="stSidebar"] .stMarkdown h5,
        section[data-testid="stSidebar"] h6, section[data-testid="stSidebar"] .stMarkdown h6,
        section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] .stMarkdown span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stMarkdown {
            color: #F7F1E1 !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: rgba(247,241,225,0.2);
        }

        /* ── Buttons ── */
        .stButton > button, .stDownloadButton > button {
            background: linear-gradient(135deg, #C98A2C 0%, #d49a3c 100%);
            color: white !important;
            border-radius: 10px;
            border: none;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 8px rgba(201,138,44,0.3);
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #B8532F 0%, #c96340 100%);
            color: white !important;
            box-shadow: 0 4px 16px rgba(184,83,47,0.4);
            transform: translateY(-1px);
            border: none;
        }
        .stButton > button:active, .stDownloadButton > button:active {
            transform: translateY(0px);
        }

        /* ── Form submit button ── */
        .stFormSubmitButton > button {
            background: linear-gradient(135deg, #24422C 0%, #2d5236 100%) !important;
            color: white !important;
            font-size: 1rem;
            padding: 0.75rem 2rem;
            box-shadow: 0 4px 12px rgba(36,66,44,0.3);
        }
        .stFormSubmitButton > button:hover {
            background: linear-gradient(135deg, #1a3320 0%, #24422C 100%) !important;
            box-shadow: 0 6px 20px rgba(36,66,44,0.5);
        }

        /* ── Cards via custom class ── */
        .agri-card {
            background: white;
            border-radius: 14px;
            padding: 1.5rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid rgba(36,66,44,0.08);
            margin-bottom: 1rem;
            transition: box-shadow 0.3s ease;
        }
        .agri-card:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .agri-card h4 {
            margin-top: 0 !important;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #C98A2C;
            margin-bottom: 0.75rem !important;
        }
        .agri-card p {
            margin: 0.3rem 0;
            line-height: 1.6;
            color: #333;
        }
        .agri-card .label {
            color: #666;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .agri-card .value {
            color: #24422C;
            font-weight: 600;
        }

        /* ── Metrics ── */
        div[data-testid="stMetric"] {
            background: white;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid #C98A2C;
        }
        div[data-testid="stMetric"] label {
            color: #666 !important;
            font-weight: 500;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #24422C !important;
            font-family: 'Zilla Slab', serif !important;
        }

        /* ── Progress bar ── */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #24422C, #C98A2C) !important;
            border-radius: 8px;
        }

        /* ── Field Verified Stamp ── */
        .field-verified-stamp {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #24422C;
            border: 3px solid #24422C;
            padding: 8px 20px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 1.1rem;
            text-transform: uppercase;
            font-family: 'Zilla Slab', serif;
            transform: rotate(-3deg);
            letter-spacing: 0.05em;
            background: rgba(36,66,44,0.05);
        }

        /* ── Hero banner ── */
        .hero-banner {
            background: linear-gradient(135deg, #24422C 0%, #2d5236 60%, #3a6b47 100%);
            color: #F7F1E1;
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(36,66,44,0.25);
        }
        .hero-banner h1 {
            color: #F7F1E1 !important;
            font-size: 2rem;
            margin: 0 0 0.25rem 0 !important;
        }
        .hero-banner p {
            color: rgba(247,241,225,0.85);
            font-size: 1.05rem;
            margin: 0;
        }

        /* ── Status pills ── */
        .status-pill {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-approved {
            background: #e6f4ea;
            color: #1e7e34;
        }
        .status-rejected {
            background: #fde8e8;
            color: #c0392b;
        }
        .status-pending {
            background: #fef3cd;
            color: #856404;
        }

        /* ── Agent step cards ── */
        .agent-step {
            background: white;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid #ddd;
            box-shadow: 0 1px 6px rgba(0,0,0,0.04);
            transition: all 0.4s ease;
        }
        .agent-step.active {
            border-left-color: #C98A2C;
            box-shadow: 0 2px 12px rgba(201,138,44,0.15);
        }
        .agent-step.done {
            border-left-color: #24422C;
        }
        .agent-step .agent-name {
            font-weight: 600;
            color: #24422C;
            font-family: 'Zilla Slab', serif;
            font-size: 1.05rem;
        }
        .agent-step .agent-desc {
            color: #666;
            font-size: 0.85rem;
        }

        /* ── Section header ── */
        .section-header {
            font-family: 'Zilla Slab', serif;
            color: #24422C;
            font-size: 1.4rem;
            font-weight: 600;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #C98A2C;
            margin-bottom: 1rem;
            display: inline-block;
        }

        /* ── Income card ── */
        .income-card {
            background: linear-gradient(135deg, #24422C, #2d5236);
            color: #F7F1E1;
            border-radius: 14px;
            padding: 1.5rem 2rem;
            text-align: center;
            box-shadow: 0 4px 16px rgba(36,66,44,0.3);
        }
        .income-card .big-number {
            font-size: 2.5rem;
            font-weight: 700;
            font-family: 'Zilla Slab', serif;
            color: #C98A2C;
        }
        .income-card .improvement {
            font-size: 1.3rem;
            color: #7fdb8a;
            font-weight: 600;
        }

        /* ── Dataframe styling ── */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
        }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            font-family: 'Zilla Slab', serif !important;
            font-weight: 600;
            color: #24422C;
        }

        /* ── Tab styling ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: white;
        }

        /* ── Animations ── */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(18px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeInLeft {
            from { opacity: 0; transform: translateX(-18px); }
            to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulseBadge {
            0%, 100% { box-shadow: 0 0 0 0 rgba(201,138,44,0.4); }
            50%       { box-shadow: 0 0 0 8px rgba(201,138,44,0); }
        }
        @keyframes shimmer {
            0%   { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .agri-card {
            animation: fadeInUp 0.4s ease both;
        }
        .hero-banner {
            animation: fadeInUp 0.5s ease both;
        }
        div[data-testid="stMetric"] {
            animation: fadeInUp 0.45s ease both;
        }
        .field-verified-stamp {
            animation: pulseBadge 2s ease-in-out infinite;
        }
        .agent-step {
            animation: fadeInLeft 0.35s ease both;
        }

        /* ── Section headers ── */
        .section-header {
            font-family: 'Zilla Slab', serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: #24422C;
            padding-bottom: 0.4rem;
            border-bottom: 3px solid #C98A2C;
            margin: 1.2rem 0 0.8rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ── Language badge ── */
        .lang-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(201,138,44,0.12);
            border: 1.5px solid #C98A2C;
            color: #C98A2C;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* ── Mobile responsiveness ── */
        @media (max-width: 768px) {
            .hero-banner h1 { font-size: 1.4rem !important; }
            .hero-banner p  { font-size: 0.9rem; }
            .agri-card      { padding: 1rem; }
            div[data-testid="stMetric"] { padding: 0.75rem 1rem; }
        }

        </style>
    """, unsafe_allow_html=True)


def render_card(title: str, icon: str, content_html: str) -> None:
    """Renders a styled card component."""
    st.markdown(f"""
        <div class="agri-card">
            <h4>{icon} {title}</h4>
            {content_html}
        </div>
    """, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str) -> None:
    """Renders the hero banner."""
    st.markdown(f"""
        <div class="hero-banner">
            <h1>🌾 {title}</h1>
            <p>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)


def render_agent_step(icon: str, name: str, desc: str, state: str = "") -> None:
    """Renders an agent processing step card."""
    st.markdown(f"""
        <div class="agent-step {state}">
            <span class="agent-name">{icon} {name}</span>
            <div class="agent-desc">{desc}</div>
        </div>
    """, unsafe_allow_html=True)


def render_income_card(expected: int, previous: int, improvement: str) -> None:
    """Renders the income projection card."""
    st.markdown(f"""
        <div class="income-card">
            <div style="font-size:0.9rem; opacity:0.8;">Expected Income per Acre</div>
            <div class="big-number">₹{expected:,}</div>
            <div style="font-size:0.85rem; opacity:0.7; margin:0.25rem 0;">vs Previous Season: ₹{previous:,}</div>
            <div class="improvement">▲ {improvement}</div>
        </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# FALLBACK MOCK DATA GENERATORS
# ═══════════════════════════════════════════

# Climate zone mapping for all POPULAR_CITIES
_CLIMATE_ZONES = {
    "hot_dry":  ["delhi", "jaipur", "lucknow", "kanpur", "varanasi", "jodhpur"],
    "humid":    ["mumbai", "kolkata", "chennai", "patna"],
    "moderate": ["pune", "nashik", "bhopal", "hyderabad", "nagpur", "indore"],
}

# Season × location weather profiles: (temp, desc, humidity, rainfall)
_WEATHER_PROFILES = {
    # ── Hot-dry zone ──
    "delhi":     {"summer": (42, "extreme heat",         25, "low"),
                  "monsoon": (34, "humid with thunderstorms", 75, "high"),
                  "winter":  (14, "cold and foggy",       55, "none")},
    "jaipur":    {"summer": (44, "scorching dry heat",    15, "none"),
                  "monsoon": (33, "intermittent showers",  60, "medium"),
                  "winter":  (12, "clear and cold",        30, "none")},
    "lucknow":   {"summer": (40, "hot and humid",         40, "low"),
                  "monsoon": (32, "heavy downpours",       80, "high"),
                  "winter":  (10, "dense fog",             65, "none")},
    "kanpur":    {"summer": (41, "dry heat",              35, "low"),
                  "monsoon": (33, "steady monsoon rain",   78, "high"),
                  "winter":  (11, "cold with fog",         60, "none")},
    "varanasi":  {"summer": (42, "oppressive heat",       38, "low"),
                  "monsoon": (31, "heavy monsoon",         85, "high"),
                  "winter":  (12, "chilly and misty",      58, "none")},
    # ── Humid zone ──
    "mumbai":    {"summer": (34, "hot and sticky",        70, "medium"),
                  "monsoon": (28, "heavy rainfall",        92, "high"),
                  "winter":  (24, "pleasant and dry",      55, "none")},
    "kolkata":   {"summer": (36, "hot and humid",         75, "medium"),
                  "monsoon": (30, "torrential rain",       90, "high"),
                  "winter":  (18, "mild and dry",          50, "none")},
    "chennai":   {"summer": (38, "hot and dry",           55, "low"),
                  "monsoon": (28, "northeast monsoon rain", 85, "high"),
                  "winter":  (25, "pleasant",              60, "low")},
    "patna":     {"summer": (40, "hot and dusty",         45, "low"),
                  "monsoon": (31, "flooding rains",        88, "high"),
                  "winter":  (12, "cold and foggy",        65, "none")},
    # ── Moderate zone ──
    "pune":      {"summer": (36, "hot but bearable",      35, "low"),
                  "monsoon": (26, "steady rain",           80, "high"),
                  "winter":  (15, "cool and pleasant",     40, "none")},
    "nashik":    {"summer": (38, "hot and dry",           30, "low"),
                  "monsoon": (25, "good monsoon rain",     78, "high"),
                  "winter":  (13, "cold nights, mild days", 35, "none")},
    "bhopal":    {"summer": (40, "dry heat",              28, "low"),
                  "monsoon": (28, "moderate to heavy rain", 75, "high"),
                  "winter":  (12, "cool and clear",        40, "none")},
    "hyderabad": {"summer": (39, "hot and dry",           30, "low"),
                  "monsoon": (28, "scattered showers",     70, "medium"),
                  "winter":  (18, "pleasant",              45, "low")},
    "nagpur":    {"summer": (44, "extreme heat, dry",     20, "none"),
                  "monsoon": (30, "heavy rain",            80, "high"),
                  "winter":  (14, "cool and clear",        35, "none")},
    "indore":    {"summer": (40, "hot and dry",           25, "low"),
                  "monsoon": (27, "good monsoon",          75, "high"),
                  "winter":  (13, "cool and pleasant",     38, "none")},
}


def _get_season_key() -> str:
    """Return season key for weather profile lookup."""
    month = datetime.now().month
    if 3 <= month <= 6:
        return "summer"
    elif 7 <= month <= 10:
        return "monsoon"
    else:
        return "winter"


def get_mock_weather(location: str) -> Dict:
    """Generates intelligent mock weather data based on location AND current season.

    Uses a season × location cross-reference table for realistic results.
    Falls back to generic season-based defaults for unknown locations.
    """
    loc = location.lower()
    season_key = _get_season_key()

    # Try exact city match from profiles
    for city, seasons in _WEATHER_PROFILES.items():
        if city in loc:
            temp, desc, humidity, rainfall = seasons[season_key]
            break
    else:
        # Generic season-based defaults for unknown locations
        defaults = {
            "summer":  (35, "hot and dry", 30, "low"),
            "monsoon": (28, "scattered thunderstorms", 85, "high"),
            "winter":  (18, "clear sky", 45, "none"),
        }
        temp, desc, humidity, rainfall = defaults[season_key]

    analysis = f"{desc.capitalize()} conditions detected."
    if rainfall in ("low", "none") and temp > 35:
        analysis += " Drought risk — prioritize drought-resistant crops."
    elif rainfall == "high":
        analysis += " Flood-prone — ensure drainage and select water-tolerant varieties."
    elif rainfall == "medium":
        analysis += " Moderate moisture levels — optimal for a wide range of crops."
    elif rainfall == "none" and temp < 15:
        analysis += " Cold conditions — protect seedlings from frost damage."

    return {
        "temp": temp,
        "humidity": humidity,
        "condition": desc,
        "rainfall": rainfall,
        "analysis": analysis,
    }


def get_mock_crop(weather_data: Dict, location: str) -> Dict:
    """Generates rule-based crop recommendation from weather conditions and season."""
    temp = weather_data.get("temp", 30)
    rainfall = weather_data.get("rainfall", "low")
    month = datetime.now().month

    # Kharif season (monsoon) crops
    if 6 <= month <= 10:
        if temp > 30 and rainfall in ("low", "none"):
            return {
                "crop_name": "Pearl Millets (Bajra / बाजरा)",
                "reason": "Extremely drought-resistant. Thrives in hot, dry conditions with minimal irrigation. Ideal for current weather.",
                "sowing_time": "Next 7-10 days",
                "harvest_time": "60-65 days",
                "water_needs": "low",
                "soil_type": "Sandy loam",
            }
        elif rainfall == "high":
            return {
                "crop_name": "Rice / Paddy (धान)",
                "reason": "Thrives in high-rainfall, waterlogged conditions. Current monsoon weather is ideal for paddy cultivation.",
                "sowing_time": "Immediate — monsoon window",
                "harvest_time": "120-150 days",
                "water_needs": "high",
                "soil_type": "Clay / Alluvial loam",
            }
        else:
            return {
                "crop_name": "Soybean (सोयाबीन)",
                "reason": "Excellent Kharif legume for moderate rainfall zones. Fixes nitrogen in soil, improving fertility for the next crop.",
                "sowing_time": "Within 5-7 days",
                "harvest_time": "90-100 days",
                "water_needs": "medium",
                "soil_type": "Loam / Black soil",
            }
    # Rabi season (winter) crops
    elif month >= 11 or month <= 2:
        if temp < 15:
            return {
                "crop_name": "Wheat (गेहूं)",
                "reason": "Ideal rabi crop for cool winter conditions. Well-suited for irrigated fields across North India.",
                "sowing_time": "Immediate — optimal rabi window",
                "harvest_time": "110-130 days",
                "water_needs": "medium",
                "soil_type": "Loam / Alluvial",
            }
        else:
            return {
                "crop_name": "Mustard (सरसों)",
                "reason": "Thrives in mild winter conditions with low water needs. Strong market demand for oil extraction.",
                "sowing_time": "Within 10 days",
                "harvest_time": "100-120 days",
                "water_needs": "low",
                "soil_type": "Sandy loam",
            }
    # Zaid season (summer) crops
    else:
        if rainfall in ("medium", "high"):
            return {
                "crop_name": "Vegetables — Tomato & Okra (टमाटर / भिंडी)",
                "reason": "Moderate rainfall with warm temperatures supports rapid vegetable growth. High market demand ensures profitability.",
                "sowing_time": "Within 5 days",
                "harvest_time": "45-60 days",
                "water_needs": "medium",
                "soil_type": "Loam / Red soil",
            }
        else:
            return {
                "crop_name": "Watermelon (तरबूज)",
                "reason": "High-value summer crop that thrives in hot, dry conditions. Excellent market demand during peak summer.",
                "sowing_time": "Next 7 days",
                "harvest_time": "70-90 days",
                "water_needs": "medium",
                "soil_type": "Sandy loam",
            }


def get_mock_pest(crop_name: str) -> Dict:
    """Maps common pests/diseases to crop types."""
    crop = crop_name.lower()

    if "millet" in crop or "bajra" in crop:
        return {
            "pest_name": "Aphids (माहू)",
            "severity": "medium",
            "symptoms": "Yellowing leaves, stunted growth, honeydew secretion, visible colonies on leaf undersides",
            "organic_treatment": "Neem oil spray (5ml/L water) + liquid soap every 7 days. Release ladybugs as biocontrol.",
            "chemical_treatment": "Imidacloprid 17.8% SL @ 0.3ml/L if infestation >50% leaf coverage",
            "preventive_measures": "Crop rotation, remove weeds, install yellow sticky traps, intercrop with marigold",
            "action_by_date": "Within 7 days of first sighting",
        }
    elif "rice" in crop or "paddy" in crop:
        return {
            "pest_name": "Stem Borer (तना छेदक)",
            "severity": "high",
            "symptoms": "Dead heart in vegetative stage, whiteheads during reproductive stage, bore holes in stems",
            "organic_treatment": "Release Trichogramma japonicum egg parasitoids @ 1 lakh/ha at weekly intervals",
            "chemical_treatment": "Cartap hydrochloride 4G @ 10 kg/acre applied in standing water",
            "preventive_measures": "Clip seedling tips before transplanting, avoid excessive nitrogen, harvest at ground level",
            "action_by_date": "Immediate action required — high damage potential",
        }
    elif "tomato" in crop or "vegetable" in crop or "okra" in crop:
        return {
            "pest_name": "Whitefly & Leaf Curl Virus (सफेद मक्खी)",
            "severity": "medium",
            "symptoms": "Upward curling of leaves, yellowing, stunted plants, whiteflies on leaf undersides",
            "organic_treatment": "Yellow sticky traps + Neem oil spray at 5ml/L. Remove and burn infected plants.",
            "chemical_treatment": "Thiamethoxam 25 WG @ 0.3g/L spray at 10-day intervals",
            "preventive_measures": "Use virus-resistant varieties, maintain field hygiene, border crop of maize",
            "action_by_date": "Within 5 days — virus spreads rapidly",
        }
    elif "soybean" in crop or "soya" in crop:
        return {
            "pest_name": "Tobacco Caterpillar (तम्बाकू की सुंडी / Spodoptera litura)",
            "severity": "high",
            "symptoms": "Irregular holes in leaves, skeletonized foliage, larvae visible on undersides at dawn/dusk",
            "organic_treatment": "NPV (Nuclear Polyhedrosis Virus) spray @ 250 LE/ha + neem seed kernel extract (5%)",
            "chemical_treatment": "Chlorantraniliprole 18.5% SC @ 0.3ml/L at early larval stage",
            "preventive_measures": "Pheromone traps (5/acre), bird perches, deep summer ploughing",
            "action_by_date": "Within 3 days — larvae defoliate crops rapidly",
        }
    elif "mustard" in crop or "sarson" in crop:
        return {
            "pest_name": "Mustard Aphid (सरसों का माहू / Lipaphis erysimi)",
            "severity": "high",
            "symptoms": "Curling and discolouration of leaves, honeydew on inflorescence, sooty mould, shrivelled pods",
            "organic_treatment": "Neem oil (5ml/L) + soft soap spray, conserve Coccinellid beetles as natural predators",
            "chemical_treatment": "Dimethoate 30% EC @ 1ml/L or Thiamethoxam 25 WG @ 0.2g/L",
            "preventive_measures": "Early sowing (before Oct 25), mustard + wheat intercropping, avoid excess nitrogen",
            "action_by_date": "Spray at first appearance — pods at risk within 10 days",
        }
    elif "watermelon" in crop or "melon" in crop:
        return {
            "pest_name": "Fruit Fly (फल मक्खी / Bactrocera cucurbitae)",
            "severity": "medium",
            "symptoms": "Tiny puncture marks on fruit skin, maggots inside fruit, premature fruit drop and rotting",
            "organic_treatment": "Cue-lure traps + methyl eugenol bait traps (10/acre). Bag developing fruits with cloth.",
            "chemical_treatment": "Malathion 50 EC @ 2ml/L bait spray with jaggery (10g/L) at weekly intervals",
            "preventive_measures": "Collect and destroy fallen fruits daily, plough field after harvest, field sanitation",
            "action_by_date": "Install traps before flowering — within 5 days",
        }
    else:
        return {
            "pest_name": "Rust (गेरुई)",
            "severity": "low",
            "symptoms": "Orange/brown powdery pustules on leaves and stems, premature leaf drop",
            "organic_treatment": "Garlic extract spray (10%) + Pseudomonas fluorescens foliar application",
            "chemical_treatment": "Propiconazole 25% EC @ 1ml/L at first sign of pustules",
            "preventive_measures": "Use resistant varieties (HD-2967), avoid late sowing, balanced fertilization",
            "action_by_date": "Monitor closely for next 14 days",
        }


# Real mandi names mapped by region
_MANDI_MAP = {
    "delhi":     "Azadpur Mandi, Delhi",
    "mumbai":    "Vashi APMC, Navi Mumbai",
    "pune":      "Market Yard APMC, Pune",
    "jaipur":    "Muhana Mandi, Jaipur",
    "lucknow":   "Alambagh Mandi, Lucknow",
    "bhopal":    "Karond Mandi, Bhopal",
    "nagpur":    "Kalamna Market, Nagpur",
    "hyderabad": "Bowenpally Market, Hyderabad",
    "chennai":   "Koyambedu Market, Chennai",
    "kolkata":   "Posta Bazar, Kolkata",
    "nashik":    "Pimpalgaon APMC, Nashik",
    "indore":    "Devi Ahilyabai Mandi, Indore",
    "patna":     "Mithapur Mandi, Patna",
    "varanasi":  "Sarnath Mandi, Varanasi",
    "kanpur":    "Naubasta Mandi, Kanpur",
}


def _get_mandi_name(location: str) -> str:
    """Look up a real mandi name for the location, or use a generic fallback."""
    loc = location.lower()
    for city, mandi in _MANDI_MAP.items():
        if city in loc:
            return mandi
    return f"APMC Market, {location}"


def get_mock_market(crop_name: str, location: str) -> Dict:
    """Generates realistic mock market intelligence data with real mandi names."""
    crop = crop_name.lower()
    mandi = _get_mandi_name(location)

    if "millet" in crop or "bajra" in crop:
        return {
            "price": 2800,
            "unit": "quintal",
            "trend": "up 12% this month",
            "best_market": mandi,
            "sell_timing": "After 60 days when prices peak in September",
            "storage_tips": "Dry, ventilated space with <12% moisture. Use neem leaves between layers.",
            "market_strategy": "Sell in bulk (>5 quintals) at APMC for 8-10% price premium over local mandis.",
        }
    elif "rice" in crop or "paddy" in crop:
        return {
            "price": 3200,
            "unit": "quintal",
            "trend": "stable (+2%)",
            "best_market": mandi,
            "sell_timing": "Hold 1 month post-harvest if storage available — prices rise 10-15%",
            "storage_tips": "Keep moisture below 14%. Use hermetic bags to prevent insect damage.",
            "market_strategy": "Sell directly to millers for ₹200-300/quintal premium over mandi rate.",
        }
    elif "tomato" in crop or "vegetable" in crop or "okra" in crop:
        return {
            "price": 4500,
            "unit": "quintal",
            "trend": "up 18% this month",
            "best_market": mandi,
            "sell_timing": "Sell fresh within 3 days of harvest for maximum price",
            "storage_tips": "Cold storage at 10-12°C extends shelf life to 2 weeks.",
            "market_strategy": "Grade by size (A/B/C). A-grade direct to restaurants for 2x mandi rate.",
        }
    elif "soybean" in crop or "soya" in crop:
        return {
            "price": 4600,
            "unit": "quintal",
            "trend": "up 8% this month",
            "best_market": mandi,
            "sell_timing": "Sell within 2 weeks post-harvest — soybean prices drop in late November",
            "storage_tips": "Store in dry godown at <10% moisture. Fumigate with aluminium phosphide.",
            "market_strategy": "Sell to oil mills directly for ₹200-400/quintal premium. Negotiate bulk rates.",
        }
    elif "mustard" in crop or "sarson" in crop:
        return {
            "price": 5650,
            "unit": "quintal",
            "trend": "up 6% (MSP supported)",
            "best_market": mandi,
            "sell_timing": "Sell in March-April when oil mills peak procurement",
            "storage_tips": "Dry to <8% moisture, store in jute bags in ventilated room.",
            "market_strategy": "Compare MSP vs mandi rate — sell at higher. Oil mill direct gives ₹300+ premium.",
        }
    elif "watermelon" in crop or "melon" in crop:
        return {
            "price": 1800,
            "unit": "quintal",
            "trend": "up 25% (peak summer demand)",
            "best_market": mandi,
            "sell_timing": "Sell immediately at harvest — perishable, no holding benefit",
            "storage_tips": "Keep in shade, transport early morning or late evening to prevent cracking.",
            "market_strategy": "Sell direct to retailers and juice shops for 30-50% premium over mandi.",
        }
    elif "wheat" in crop:
        return {
            "price": 2400,
            "unit": "quintal",
            "trend": "stable (MSP ₹2,275/qt)",
            "best_market": mandi,
            "sell_timing": "Sell to FCI/govt procurement centres at MSP, or hold 2 months for 5-8% rise",
            "storage_tips": "Dry to <12% moisture, store in metal bins. Fumigation every 3 months.",
            "market_strategy": "Apply for MSP procurement if available. Otherwise sell to flour mills directly.",
        }
    else:
        return {
            "price": 2400,
            "unit": "quintal",
            "trend": "stable",
            "best_market": mandi,
            "sell_timing": "Consider holding for 2 months — prices typically recover post-season",
            "storage_tips": "Standard grain storage in dry, pest-free godown.",
            "market_strategy": "Sell to local aggregators or apply for MSP procurement.",
        }

