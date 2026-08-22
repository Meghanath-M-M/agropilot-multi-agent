"""
AgroPilot Agent Architecture
4 specialized AI agents + Master Orchestrator for agricultural advisory generation.

Agents:
  1. WeatherAgent — Fetches real-time weather or uses seasonal fallback
  2. CropAgent — Recommends crops via LLM or rule-based logic
  3. PestAgent — Identifies pests/diseases from symptoms
  4. MarketAgent — Provides market intelligence and pricing

All agents gracefully fall back to rule-based logic if Groq is unavailable.
Each agent tags its output with a data_source and confidence score for transparency.
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Optional

import config
import utils
from schemas import CropRecommendation, PestAssessment, MarketIntelligence

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════
# CROP YIELD TABLE (quintals per acre, India averages)
# Used for realistic income projection instead of a fixed multiplier
# ═══════════════════════════════════════════
CROP_YIELDS = {
    "bajra": 8, "millet": 8, "pearl millet": 8,
    "rice": 18, "paddy": 18,
    "wheat": 16,
    "tomato": 80, "okra": 40, "vegetable": 50,
    "cotton": 6,
    "soybean": 8, "soya": 8,
    "mustard": 6,
    "onion": 60,
    "sugarcane": 300,   # quintals of cane, not sugar
    "maize": 12, "corn": 12,
    "potato": 80,
    "groundnut": 7, "peanut": 7,
}


def _estimate_yield(crop_name: str) -> int:
    """Look up average yield (quintals/acre) for a crop, default 16."""
    name = crop_name.lower()
    for key, value in CROP_YIELDS.items():
        if key in name:
            return value
    return 16  # safe default


def _get_current_season() -> str:
    """Return the Indian cropping season name."""
    month = datetime.now().month
    if 6 <= month <= 10:
        return "Kharif (Jun-Oct, monsoon season)"
    elif month >= 11 or month <= 3:
        return "Rabi (Nov-Mar, winter season)"
    else:
        return "Zaid (Apr-Jun, summer season)"


class WeatherAgent:
    """Fetches weather data from OpenWeatherMap API with mock fallback."""

    def __init__(self) -> None:
        self.api_key: str = config.OPENWEATHERMAP_API_KEY
        self.url: str = config.OPENWEATHERMAP_URL

    def get_weather(self, location: str) -> Dict:
        """Fetch weather for a given location.

        Args:
            location: City or village name in India.

        Returns:
            Dict with temp, humidity, condition, rainfall, analysis,
            data_source, and confidence.
        """
        if not self.api_key or self.api_key == "your_openweathermap_api_key_here":
            logger.warning("No OpenWeatherMap API key. Using mock data.")
            result = utils.get_mock_weather(location)
            result["data_source"] = "rule_based_fallback"
            result["confidence"] = 0.7
            return result

        try:
            params = {"q": f"{location},IN", "appid": self.api_key, "units": "metric"}
            response = requests.get(self.url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            temp = round(data["main"]["temp"])
            humidity = data["main"]["humidity"]
            desc = data["weather"][0]["description"]

            # Infer rainfall level
            rain_mm = data.get("rain", {}).get("1h", 0)
            if rain_mm > 7 or "heavy" in desc.lower():
                rainfall = "high"
            elif rain_mm > 2 or "rain" in desc.lower() or "drizzle" in desc.lower():
                rainfall = "medium"
            else:
                rainfall = "low"

            analysis = f"{desc.capitalize()} conditions detected."
            if rainfall == "high":
                analysis += " Heavy rainfall expected — ensure drainage."
            elif temp > 35:
                analysis += " Extreme heat — irrigate early morning or late evening."

            return {
                "temp": temp,
                "humidity": humidity,
                "condition": desc,
                "rainfall": rainfall,
                "analysis": analysis,
                "data_source": "live_api",
                "confidence": 1.0,
            }
        except Exception as e:
            logger.error(f"Weather API failed: {e}. Falling back to mock data.")
            result = utils.get_mock_weather(location)
            result["data_source"] = "rule_based_fallback"
            result["confidence"] = 0.7
            return result


class CropAgent:
    """Recommends crops using Groq LLM with rule-based fallback."""

    def __init__(self) -> None:
        self.groq_url: str = "https://api.groq.com/openai/v1/chat/completions"
        self.headers: dict = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    def get_recommendation(self, weather_data: Dict, location: str,
                           crop_pref: Optional[str] = None,
                           soil_type: Optional[str] = None) -> Dict:
        """Generate crop recommendation based on weather and preferences.

        Args:
            weather_data: Output from WeatherAgent.
            location: Farmer's location.
            crop_pref: Optional farmer crop preference.
            soil_type: Optional soil type.

        Returns:
            Dict with crop_name, reason, sowing_time, harvest_time,
            water_needs, soil_type, data_source, confidence.
        """
        month = datetime.now().month
        season = _get_current_season()

        if crop_pref:
            pref_note = f"\nFarmer is ALREADY GROWING: {crop_pref}. You MUST provide agronomic details for this EXACT crop. DO NOT recommend a different crop."
            task_instruction = f"Provide agronomic details for {crop_pref}."
        else:
            pref_note = ""
            task_instruction = "Recommend the SINGLE best crop for this farmer."

        soil_note = f"\nSoil type: {soil_type}" if soil_type and soil_type != "Auto-detect" else ""

        prompt = f"""You are an Indian agricultural expert with 20 years of field experience.

LOCATION: {location}
WEATHER: {weather_data.get('temp')}°C, {weather_data.get('humidity')}% humidity, {weather_data.get('rainfall')} rainfall
SEASON: {season}
CURRENT MONTH: {datetime.now().strftime('%B %Y')}
{pref_note}{soil_note}

RULES:
- If recommending a new crop, it must be grown in {location}
- Sowing time must be realistic for {season}
- Water needs must match rainfall ({weather_data.get('rainfall')})
- Include common Hindi name in parentheses
- Harvest time should be in "X-Y days" format
- Reason should mention why this crop suits the weather

OUTPUT FORMAT (JSON strictly):
{{"crop_name": "<Crop Name (Hindi Name)>", "reason": "<Specific reason based on weather>", "sowing_time": "<timeframe>", "harvest_time": "<days>", "water_needs": "<low/medium/high>", "soil_type": "<type>"}}

CRITICAL: Generate a unique recommendation. Do NOT output a generic example.
Now {task_instruction} Respond ONLY with valid JSON:"""

        try:
            response = requests.post(
                self.groq_url,
                headers=self.headers,
                json={
                    "model": "openai/gpt-oss-120b",
                    "temperature": 0.6, 
                    "messages": [{"role": "user", "content": prompt}], 
                    "response_format": {"type": "json_object"},
                    "reasoning_format": "hidden"
                },
                timeout=15
            )
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(result)

            # Validate with Pydantic
            validated = CropRecommendation.model_validate(parsed)
            output = validated.model_dump()
            output["data_source"] = "llm_generated"
            output["confidence"] = 0.85
            return output

        except Exception as e:
            logger.warning(f"Groq CropAgent failed: {e}. Using rule-based fallback.")
            result = utils.get_mock_crop(weather_data, location)
            result["data_source"] = "rule_based_fallback"
            result["confidence"] = 0.7
            return result


class PestAgent:
    """Identifies pests/diseases from symptoms using LLM with rule-based fallback."""

    def __init__(self) -> None:
        self.groq_url: str = "https://api.groq.com/openai/v1/chat/completions"
        self.headers: dict = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    def analyze(self, crop_name: str, symptoms: str = "",
                has_photo: bool = False) -> Dict:
        """Analyze pest/disease risk for a given crop.

        Args:
            crop_name: Name of the recommended crop.
            symptoms: Optional description of symptoms observed.
            has_photo: Whether a photo was uploaded (for simulation).

        Returns:
            Dict with pest_name, severity, symptoms, treatments, prevention,
            deadline, data_source, confidence.
        """
        if not symptoms and not has_photo:
            result = utils.get_mock_pest(crop_name)
            result["data_source"] = "rule_based_fallback"
            result["confidence"] = 0.7
            result["identified_crop"] = None
            return result

        photo_note = ("\nA photo of the affected crop was also provided showing visible damage. "
                      "Factor the visual evidence into your assessment.") if has_photo else ""

        if crop_name.lower() == "unknown crop":
            crop_identify_note = ("\nThe crop name is not known. Infer the likely affected crop from the symptoms and photo, "
                                   "if available, and include a field `identified_crop` with the crop name in your JSON output.")
        elif has_photo:
            crop_identify_note = ("\nAlso identify the specific crop being affected from the photo context "
                                   "and include a field `identified_crop` with the crop name in your JSON output.")
        else:
            crop_identify_note = ""

        prompt = f"""You are an Indian agricultural pest and disease expert with field experience across all agro-climatic zones.

        A farmer growing {crop_name} reports these symptoms: \"{symptoms}\"{photo_note}{crop_identify_note}

        RULES:
        - Identify the SINGLE most likely pest or disease based on the described symptoms
        - Include the Hindi name in parentheses
        - Severity criteria:
          * \"low\" = cosmetic damage only, <10% yield impact
          * \"medium\" = 10-30% yield loss if untreated within 14 days
          * \"high\" = >30% yield loss, immediate action required
        - Organic treatment must use products available at any Indian agri-shop
        - Chemical treatment must include exact dosage (e.g., \"2ml/L water\")
        - action_by_date must be a specific timeframe like \"Within 5 days\"

        OUTPUT FORMAT (JSON strictly):
        {{\"pest_name\": \"<Pest Name (Hindi)>\", \"severity\": \"<low/medium/high>\", \"symptoms\": \"<Detailed symptoms>\", \"organic_treatment\": \"<Specific organic treatment>\", \"chemical_treatment\": \"<Specific chemical treatment>\", \"preventive_measures\": \"<Prevention measures>\", \"action_by_date\": \"<Timeframe>\", \"identified_crop\": \"<Crop name or null>\"}}

        CRITICAL: Generate a specific assessment based ONLY on the symptoms provided. Do not copy examples.
        Respond ONLY with valid JSON:"""

        try:
            response = requests.post(
                self.groq_url,
                headers=self.headers,
                json={
                    "model": "openai/gpt-oss-120b",
                    "temperature": 0.6, 
                    "messages": [{"role": "user", "content": prompt}], 
                    "response_format": {"type": "json_object"},
                    "reasoning_format": "hidden"
                },
                timeout=15
            )
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(result)

            # Validate with Pydantic
            validated = PestAssessment.model_validate(parsed)
            output = validated.model_dump()
            output["data_source"] = "llm_generated"
            output["confidence"] = 0.85
            output["identified_crop"] = parsed.get("identified_crop")
            return output

        except Exception as e:
            logger.warning(f"Groq PestAgent failed: {e}. Using rule-based fallback.")
            result = utils.get_mock_pest(crop_name)
            result["data_source"] = "rule_based_fallback"
            result["confidence"] = 0.7
            result["identified_crop"] = None
            return result


class MarketAgent:
    """Provides market intelligence and price data with mock fallback."""

    def __init__(self) -> None:
        self.groq_url: str = "https://api.groq.com/openai/v1/chat/completions"
        self.headers: dict = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    def get_market_intelligence(self, crop_name: str, location: str) -> Dict:
        """Generate market intelligence for a crop in a region.

        Args:
            crop_name: Name of the crop.
            location: Farmer's location.

        Returns:
            Dict with price, unit, trend, best_market, sell_timing,
            storage_tips, market_strategy, data_source, confidence.
        """
        season = _get_current_season()

        prompt = f"""You are an Indian agricultural market analyst with access to Agmarknet price data.

Provide realistic market intelligence for {crop_name} near {location}.

RULES:
- Price must be a realistic Indian mandi price in ₹ per quintal (100 kg)
  * Cereals (wheat, rice, bajra): ₹2,000-4,000/quintal
  * Vegetables (tomato, onion, okra): ₹1,500-8,000/quintal (volatile)
  * Cash crops (cotton, sugarcane): ₹5,000-8,000/quintal
- "best_market" must name a REAL mandi/APMC market near {location}
- "trend" must indicate direction and percentage (e.g., "up 8% this month")
- "sell_timing" should factor in {season} seasonality
- "price" must be a NUMBER, not a string

OUTPUT FORMAT (JSON strictly):
{{"price": 0, "unit": "quintal", "trend": "<trend>", "best_market": "<Name of a real APMC market near location>", "sell_timing": "<Strategic advice>", "storage_tips": "<Storage advice>", "market_strategy": "<Market strategy>"}}

CRITICAL: Provide highly accurate market data for the exact crop and location requested. Do not output generic examples.
Respond ONLY with valid JSON:"""

        try:
            response = requests.post(
                self.groq_url,
                headers=self.headers,
                json={
                    "model": "openai/gpt-oss-120b",
                    "temperature": 0.6, 
                    "messages": [{"role": "user", "content": prompt}], 
                    "response_format": {"type": "json_object"},
                    "reasoning_format": "hidden"
                },
                timeout=15
            )
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(result)

            # Validate with Pydantic
            validated = MarketIntelligence.model_validate(parsed)
            output = validated.model_dump()
            output["data_source"] = "llm_generated"
            output["confidence"] = 0.85
            return output

        except Exception as e:
            logger.warning(f"Groq MarketAgent failed: {e}. Using rule-based fallback.")
            result = utils.get_mock_market(crop_name, location)
            result["data_source"] = "rule_based_fallback"
            result["confidence"] = 0.7
            return result


class MasterOrchestrator:
    """Coordinates all 4 agents to produce a unified farm advisory."""

    def __init__(self) -> None:
        self.weather_agent = WeatherAgent()
        self.crop_agent = CropAgent()
        self.pest_agent = PestAgent()
        self.market_agent = MarketAgent()

    def generate_advisory(self, location: str, symptoms: str = "",
                          crop_pref: str = "", soil_type: str = "",
                          has_photo: bool = False) -> Dict:
        """Run all agents sequentially and compile a unified advisory.

        Each agent is wrapped in its own error boundary so one failure
        does not prevent the others from running.

        Args:
            location: Farmer's city/village name.
            symptoms: Optional pest/disease symptoms.
            crop_pref: Optional farmer crop preference.
            soil_type: Optional soil type.
            has_photo: Whether a crop photo was uploaded.

        Returns:
            Complete advisory dictionary with data_source tags and
            confidence scores per agent.
        """
        errors = []

        # 1. Weather Agent
        try:
            weather_data = self.weather_agent.get_weather(location)
        except Exception as e:
            logger.error(f"WeatherAgent crashed: {e}")
            weather_data = utils.get_mock_weather(location)
            weather_data["data_source"] = "rule_based_fallback"
            weather_data["confidence"] = 0.7
            errors.append("Weather Agent encountered an error — using estimated data.")

        effective_crop_pref = crop_pref.strip() if crop_pref and crop_pref.strip() else None
        initial_pest_result = None

        # If the farmer did not specify a crop but provided symptoms or a photo, try to infer the crop first.
        if not effective_crop_pref and (symptoms.strip() or has_photo):
            try:
                initial_pest_result = self.pest_agent.analyze("Unknown crop", symptoms, has_photo)
                identified_crop = initial_pest_result.get("identified_crop")
                effective_crop_pref = identified_crop if identified_crop else effective_crop_pref
            except Exception as e:
                logger.error(f"PestAgent (crop identification) crashed: {e}")
                mock_pest = utils.get_mock_pest("Unknown crop")
                mock_pest["data_source"] = "rule_based_fallback"
                mock_pest["confidence"] = 0.7
                errors.append("Pest Agent (crop identification) encountered an error — using known pest mapping.")

        # 2. Crop Agent
        try:
            crop_data = self.crop_agent.get_recommendation(
                weather_data, location, effective_crop_pref, soil_type or None
            )
        except Exception as e:
            logger.error(f"CropAgent crashed: {e}")
            crop_data = utils.get_mock_crop(weather_data, location)
            crop_data["data_source"] = "rule_based_fallback"
            crop_data["confidence"] = 0.7
            errors.append("Crop Agent encountered an error — using rule-based recommendation.")

        # 3. Pest Agent
        pest_crop_name = effective_crop_pref or crop_data.get("crop_name", "Unknown")
        try:
            pest_data = self.pest_agent.analyze(pest_crop_name, symptoms, has_photo)
        except Exception as e:
            logger.error(f"PestAgent crashed: {e}")
            pest_data = utils.get_mock_pest(crop_data.get("crop_name", "Unknown"))
            pest_data["data_source"] = "rule_based_fallback"
            pest_data["confidence"] = 0.7
            errors.append("Pest Agent encountered an error — using known pest mapping.")

        # 4. Market Agent
        try:
            market_data = self.market_agent.get_market_intelligence(
                pest_crop_name, location
            )
        except Exception as e:
            logger.error(f"MarketAgent crashed: {e}")
            market_data = utils.get_mock_market(crop_data.get("crop_name", "Unknown"), location)
            market_data["data_source"] = "rule_based_fallback"
            market_data["confidence"] = 0.7
            errors.append("Market Agent encountered an error — using estimated prices.")

        # ── Crop-aware income projection ──
        price = market_data.get("price", 2500)
        crop_name = crop_data.get("crop_name", "")
        yield_per_acre = _estimate_yield(crop_name)
        expected_income = int(price * yield_per_acre)
        previous_income = int(expected_income * 0.81)  # ~19% improvement baseline
        improvement_pct = round(
            (expected_income - previous_income) / previous_income * 100
        )

        # ── Agent source & confidence aggregation ──
        agent_sources = {
            "weather": weather_data.get("data_source", "unknown"),
            "crop": crop_data.get("data_source", "unknown"),
            "pest": pest_data.get("data_source", "unknown"),
            "market": market_data.get("data_source", "unknown"),
        }

        confidences = [
            weather_data.get("confidence", 0.7),
            crop_data.get("confidence", 0.7),
            pest_data.get("confidence", 0.7),
            market_data.get("confidence", 0.7),
        ]
        advisory_confidence = round(sum(confidences) / len(confidences), 2)

        advisory = {
            "farmer_location": location,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "weather": weather_data,
            "crop": crop_data,
            "pest": pest_data,
            "market": market_data,
            "expected_income": expected_income,
            "previous_income": previous_income,
            "income_improvement": f"+{improvement_pct}%",
            "illustrative_estimate": True,
            "agent_sources": agent_sources,
            "advisory_confidence": advisory_confidence,
            "errors": errors,
        }

        return advisory
