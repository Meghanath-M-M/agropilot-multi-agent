"""
AgroPilot Agent Tests
Unit tests with mocking for all 4 agents and the MasterOrchestrator.
Tests cover: live API success, API failure fallback, agent isolation,
Pydantic validation, and data source transparency.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from agents import (
    WeatherAgent, CropAgent, PestAgent, MarketAgent,
    MasterOrchestrator, _estimate_yield, _get_current_season,
)


# ═══════════════════════════════════════════
# WeatherAgent Tests
# ═══════════════════════════════════════════

class TestWeatherAgent:
    """Tests for the WeatherAgent."""

    def test_live_api_success(self):
        """Should return live data with data_source='live_api' when API works."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "main": {"temp": 32.6, "humidity": 45},
            "weather": [{"description": "clear sky"}],
            "rain": {},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("agents.requests.get", return_value=mock_response):
            agent = WeatherAgent()
            agent.api_key = "test_key_123"
            result = agent.get_weather("Delhi")

        assert result["temp"] == 33  # rounded
        assert result["humidity"] == 45
        assert result["data_source"] == "live_api"
        assert result["confidence"] == 1.0
        assert result["rainfall"] == "low"

    def test_api_failure_falls_back_to_mock(self):
        """Should gracefully fall back to mock data on API error."""
        with patch("agents.requests.get", side_effect=Exception("Connection timeout")):
            agent = WeatherAgent()
            agent.api_key = "test_key_123"
            result = agent.get_weather("Mumbai")

        assert result["data_source"] == "rule_based_fallback"
        assert result["confidence"] == 0.7
        assert "temp" in result
        assert "humidity" in result

    def test_missing_api_key_uses_mock(self):
        """Should use mock data when API key is not configured."""
        agent = WeatherAgent()
        agent.api_key = ""
        result = agent.get_weather("Delhi")

        assert result["data_source"] == "rule_based_fallback"
        assert result["confidence"] == 0.7

    def test_rainfall_detection_heavy(self):
        """Should detect high rainfall from API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "main": {"temp": 28, "humidity": 90},
            "weather": [{"description": "heavy rain"}],
            "rain": {"1h": 10},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("agents.requests.get", return_value=mock_response):
            agent = WeatherAgent()
            agent.api_key = "test_key"
            result = agent.get_weather("Mumbai")

        assert result["rainfall"] == "high"


# ═══════════════════════════════════════════
# CropAgent Tests
# ═══════════════════════════════════════════

class TestCropAgent:
    """Tests for the CropAgent."""

    def test_llm_success_with_valid_json(self):
        """Should return validated LLM data with data_source='llm_generated'."""
        llm_response = json.dumps({
            "crop_name": "Rice (धान)",
            "reason": "Thrives in high rainfall conditions during monsoon",
            "sowing_time": "Immediate",
            "harvest_time": "120-150 days",
            "water_needs": "high",
            "soil_type": "Clay loam",
        })

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": llm_response}}]}
        mock_response.raise_for_status = MagicMock()

        with patch("agents.requests.post", return_value=mock_response):
            agent = CropAgent()
            weather = {"temp": 30, "humidity": 85, "rainfall": "high"}
            result = agent.get_recommendation(weather, "Mumbai")

        assert result["crop_name"] == "Rice (धान)"
        assert result["data_source"] == "llm_generated"
        assert result["confidence"] == 0.85

    def test_llm_invalid_json_falls_back(self):
        """Should fall back to rule-based when LLM returns invalid JSON."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "not valid json at all"}
        mock_response.raise_for_status = MagicMock()

        with patch("agents.requests.post", return_value=mock_response):
            agent = CropAgent()
            weather = {"temp": 35, "humidity": 30, "rainfall": "low"}
            result = agent.get_recommendation(weather, "Jaipur")

        assert result["data_source"] == "rule_based_fallback"
        assert result["confidence"] == 0.7

    def test_llm_missing_required_field_falls_back(self):
        """Should fall back when LLM response missing required Pydantic fields."""
        incomplete = json.dumps({"crop_name": "X"})  # missing reason, sowing_time, etc.

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": incomplete}
        mock_response.raise_for_status = MagicMock()

        with patch("agents.requests.post", return_value=mock_response):
            agent = CropAgent()
            weather = {"temp": 28, "humidity": 60, "rainfall": "medium"}
            result = agent.get_recommendation(weather, "Pune")

        assert result["data_source"] == "rule_based_fallback"

    def test_ollama_down_falls_back(self):
        """Should fall back when Ollama server is unreachable."""
        with patch("agents.requests.post", side_effect=Exception("Connection refused")):
            agent = CropAgent()
            weather = {"temp": 30, "humidity": 50, "rainfall": "medium"}
            result = agent.get_recommendation(weather, "Hyderabad")

        assert result["data_source"] == "rule_based_fallback"
        assert "crop_name" in result


# ═══════════════════════════════════════════
# PestAgent Tests
# ═══════════════════════════════════════════

class TestPestAgent:
    """Tests for the PestAgent."""

    def test_no_symptoms_uses_rule_based(self):
        """Should use rule-based mapping when no symptoms provided."""
        agent = PestAgent()
        result = agent.analyze("Rice / Paddy (धान)")

        assert result["data_source"] == "rule_based_fallback"
        assert "Stem Borer" in result["pest_name"]

    def test_with_symptoms_attempts_llm(self):
        """Should attempt LLM when symptoms are provided."""
        llm_response = json.dumps({
            "pest_name": "Leaf Blight (पत्ता झुलसा)",
            "severity": "high",
            "symptoms": "Brown spots on leaves spreading rapidly",
            "organic_treatment": "Bordeaux mixture spray at 1% concentration weekly",
            "chemical_treatment": "Mancozeb 75 WP @ 2.5g/L spray at 7-day intervals",
            "preventive_measures": "Remove infected debris, improve air circulation",
            "action_by_date": "Within 3 days",
        })

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": llm_response}}]}
        mock_response.raise_for_status = MagicMock()

        with patch("agents.requests.post", return_value=mock_response):
            agent = PestAgent()
            result = agent.analyze("Rice", symptoms="brown spots on leaves")

        assert result["data_source"] == "llm_generated"
        assert result["severity"] == "high"

    def test_photo_returns_identified_crop(self):
        """Should return identified_crop when has_photo=True."""
        llm_response = json.dumps({
            "pest_name": "Stem Borer (पुंगी)",
            "severity": "medium",
            "symptoms": "Holes in leaves with visible damage",
            "organic_treatment": "Neem oil spray",
            "chemical_treatment": "Chlorpyrifos 20% EC @ 2ml/L",
            "preventive_measures": "Remove infected leaves",
            "action_by_date": "Within 5 days",
            "identified_crop": "Rice",
        })

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": llm_response}}]}
        mock_response.raise_for_status = MagicMock()

        with patch("agents.requests.post", return_value=mock_response):
            agent = PestAgent()
            result = agent.analyze("Rice", has_photo=True)

        assert "identified_crop" in result
        assert result["identified_crop"] is not None


# ═══════════════════════════════════════════
# MarketAgent Tests
# ═══════════════════════════════════════════

class TestMarketAgent:
    """Tests for the MarketAgent."""

    def test_ollama_down_falls_back(self):
        """Should return rule-based market data when Ollama is down."""
        with patch("agents.requests.post", side_effect=Exception("Connection refused")):
            agent = MarketAgent()
            result = agent.get_market_intelligence("Rice", "Delhi")

        assert result["data_source"] == "rule_based_fallback"
        assert result["price"] > 0
        assert "best_market" in result


# ═══════════════════════════════════════════
# MasterOrchestrator Tests
# ═══════════════════════════════════════════

class TestMasterOrchestrator:
    """Integration tests for the orchestrator."""

    def test_all_agents_produce_output(self):
        """Should return a complete advisory with all 4 agent sections."""
        orch = MasterOrchestrator()

        with patch("agents.requests.post", side_effect=Exception("Ollama down")):
            result = orch.generate_advisory("Delhi", symptoms="yellow leaves")

        assert "weather" in result
        assert "crop" in result
        assert "pest" in result
        assert "market" in result
        assert "agent_sources" in result
        assert "advisory_confidence" in result
        assert result["advisory_confidence"] > 0

    def test_agent_isolation_weather_crash(self):
        """One agent crashing should not prevent others from running."""
        orch = MasterOrchestrator()

        with patch.object(orch.weather_agent, "get_weather", side_effect=RuntimeError("Crash!")):
            with patch("agents.requests.post", side_effect=Exception("Ollama down")):
                result = orch.generate_advisory("Mumbai")

        # Weather should have fallback data
        assert "weather" in result
        assert result["weather"]["data_source"] == "rule_based_fallback"
        # Other agents should still work
        assert "crop" in result
        assert "pest" in result
        assert "market" in result
        assert len(result["errors"]) >= 1

    def test_data_sources_tracked(self):
        """Should track data sources for all agents."""
        orch = MasterOrchestrator()

        with patch("agents.requests.post", side_effect=Exception("Ollama down")):
            result = orch.generate_advisory("Pune")

        sources = result["agent_sources"]
        assert "weather" in sources
        assert "crop" in sources
        assert "pest" in sources
        assert "market" in sources
        # With real API key, weather should be live
        if orch.weather_agent.api_key:
            assert sources["weather"] in ("live_api", "rule_based_fallback")

    def test_confidence_score_in_range(self):
        """Advisory confidence should be between 0 and 1."""
        orch = MasterOrchestrator()

        with patch("agents.requests.post", side_effect=Exception("Ollama down")):
            result = orch.generate_advisory("Jaipur")

        assert 0.0 <= result["advisory_confidence"] <= 1.0

    def test_illustrative_estimate_flag(self):
        """Income projection should be marked as illustrative."""
        orch = MasterOrchestrator()

        with patch("agents.requests.post", side_effect=Exception("Ollama down")):
            result = orch.generate_advisory("Chennai")

        assert result["illustrative_estimate"] is True
        assert result["expected_income"] > 0
        assert result["previous_income"] > 0

    def test_different_cities_different_results(self):
        """Different cities should produce different weather data."""
        orch = MasterOrchestrator()

        with patch("agents.requests.post", side_effect=Exception("Ollama down")):
            delhi = orch.generate_advisory("Delhi")
            mumbai = orch.generate_advisory("Mumbai")

        # At minimum, mandis should differ
        assert delhi["market"]["best_market"] != mumbai["market"]["best_market"]

    def test_photo_without_crop_pref_uses_identified_crop(self):
        """When a photo is uploaded without a crop preference, the orchestrator
        should use the photo-identified crop for the report."""
        orch = MasterOrchestrator()

        pest_data = {
            "pest_name": "Stem Borer (पुंगी)",
            "severity": "medium",
            "symptoms": "Holes in leaves",
            "organic_treatment": "Neem oil spray",
            "chemical_treatment": "Chlorpyrifos 20% EC @ 2ml/L",
            "preventive_measures": "Remove infected leaves",
            "action_by_date": "Within 5 days",
            "identified_crop": "Rice",
            "data_source": "llm_generated",
            "confidence": 0.85,
        }

        mock_crop_data = {
            "crop_name": "Rice (धान)",
            "reason": "Thrives in monsoon conditions",
            "sowing_time": "Immediate",
            "harvest_time": "120-150 days",
            "water_needs": "high",
            "soil_type": "Clay loam",
            "data_source": "llm_generated",
            "confidence": 0.85,
        }

        mock_market_data = {
            "price": 3500,
            "unit": "quintal",
            "trend": "up 5% this month",
            "best_market": "Delhi Mandi",
            "sell_timing": "Within 2 weeks",
            "storage_tips": "Store in dry place",
            "market_strategy": "Sell at peak season",
            "data_source": "llm_generated",
            "confidence": 0.85,
        }

        with patch.object(orch.pest_agent, "analyze", side_effect=[pest_data, pest_data]) as mock_pest:
            with patch.object(orch.crop_agent, "get_recommendation", return_value=mock_crop_data) as mock_crop:
                with patch.object(orch.market_agent, "get_market_intelligence", return_value=mock_market_data) as mock_market:
                    result = orch.generate_advisory("Delhi", has_photo=True, crop_pref="")

        # Verify pest_agent was called twice:
        # First call with "Unknown crop" for identification
        # Second call with the identified crop for actual assessment
        assert mock_pest.call_count == 2
        assert mock_pest.call_args_list[0][0][0] == "Unknown crop"

        # Verify the second PestAgent call used the identified crop from photo
        assert mock_pest.call_args_list[1][0][0] == "Rice"

        # Verify CropAgent received the photo-identified crop
        crop_rec_args = mock_crop.call_args
        assert crop_rec_args[0][2] == "Rice"

        # Verify MarketAgent received the photo-identified crop
        market_args = mock_market.call_args
        assert "Rice" in market_args[0][0]

    def test_symptoms_without_crop_pref_uses_identified_crop(self):
        """When symptoms mention a crop and crop preference is blank, use the identified crop."""
        orch = MasterOrchestrator()

        initial_pest_data = {
            "pest_name": "Leaf Blight (पत्ता झुलसा)",
            "severity": "high",
            "symptoms": "Yellowing rice leaves with brown spots",
            "organic_treatment": "Neem oil spray",
            "chemical_treatment": "Mancozeb 75 WP @ 2.5g/L",
            "preventive_measures": "Remove infected debris and improve air circulation",
            "action_by_date": "Within 3 days",
            "identified_crop": "Rice",
            "data_source": "llm_generated",
            "confidence": 0.85,
        }

        final_pest_data = {
            "pest_name": "Leaf Blight (पत्ता झुलसा)",
            "severity": "high",
            "symptoms": "Yellowing rice leaves with brown spots",
            "organic_treatment": "Neem oil spray",
            "chemical_treatment": "Mancozeb 75 WP @ 2.5g/L",
            "preventive_measures": "Remove infected debris and improve air circulation",
            "action_by_date": "Within 3 days",
            "identified_crop": "Rice",
            "data_source": "llm_generated",
            "confidence": 0.85,
        }

        mock_crop_data = {
            "crop_name": "Rice (धान)",
            "reason": "Thrives in monsoon conditions",
            "sowing_time": "Immediate",
            "harvest_time": "120-150 days",
            "water_needs": "high",
            "soil_type": "Clay loam",
            "data_source": "llm_generated",
            "confidence": 0.85,
        }

        mock_market_data = {
            "price": 3500,
            "unit": "quintal",
            "trend": "up 5% this month",
            "best_market": "Azadpur Mandi, Delhi",
            "sell_timing": "Within 2 weeks",
            "storage_tips": "Store in dry place",
            "market_strategy": "Sell at peak season",
            "data_source": "llm_generated",
            "confidence": 0.85,
        }

        with patch.object(orch.pest_agent, "analyze", side_effect=[initial_pest_data, final_pest_data]) as mock_pest:
            with patch.object(orch.crop_agent, "get_recommendation", return_value=mock_crop_data) as mock_crop:
                with patch.object(orch.market_agent, "get_market_intelligence", return_value=mock_market_data) as mock_market:
                    result = orch.generate_advisory("Delhi", symptoms="Yellowing rice leaves with brown spots", crop_pref="")

        assert mock_pest.call_count == 2
        assert mock_pest.call_args_list[0][0][0] == "Unknown crop"
        assert mock_pest.call_args_list[1][0][0] == "Rice"

        crop_rec_args = mock_crop.call_args
        assert crop_rec_args[0][2] == "Rice"

        market_args = mock_market.call_args
        assert "Rice" in market_args[0][0]


# ═══════════════════════════════════════════
# Helper Function Tests
# ═══════════════════════════════════════════

class TestHelperFunctions:
    """Tests for agent helper functions."""

    def test_estimate_yield_known_crop(self):
        """Should return correct yield for known crops."""
        assert _estimate_yield("Pearl Millets (Bajra / बाजरा)") == 8
        assert _estimate_yield("Rice / Paddy (धान)") == 18
        assert _estimate_yield("Tomato") == 80

    def test_estimate_yield_unknown_crop(self):
        """Should return default 16 for unknown crops."""
        assert _estimate_yield("Dragon Fruit") == 16

    def test_get_current_season_format(self):
        """Should return a non-empty season string."""
        season = _get_current_season()
        assert len(season) > 5
        assert any(s in season for s in ["Kharif", "Rabi", "Zaid"])
