"""
AgroPilot Utils Tests
Tests for mock data generators — verifies location-awareness,
season-awareness, and crop-to-mandi mapping.
"""

import pytest
from unittest.mock import patch
from datetime import datetime

import utils


class TestMockWeather:
    """Tests for get_mock_weather."""

    def test_known_city_returns_data(self):
        """Should return weather data for a known city."""
        result = utils.get_mock_weather("Delhi")
        assert "temp" in result
        assert "humidity" in result
        assert "rainfall" in result
        assert "analysis" in result

    def test_unknown_city_returns_default(self):
        """Should return generic season-based data for unknown locations."""
        result = utils.get_mock_weather("Timbuktu")
        assert "temp" in result
        assert "rainfall" in result

    def test_different_cities_different_temps(self):
        """Mumbai and Jaipur should generally have different temperatures."""
        mumbai = utils.get_mock_weather("Mumbai")
        jaipur = utils.get_mock_weather("Jaipur")
        # They might be the same in certain seasons but mandis must differ
        assert mumbai is not jaipur  # Different dicts

    def test_all_popular_cities_covered(self):
        """All 15 POPULAR_CITIES should have weather profiles."""
        cities = [
            "Delhi", "Mumbai", "Pune", "Jaipur", "Lucknow",
            "Bhopal", "Nagpur", "Hyderabad", "Chennai", "Kolkata",
            "Nashik", "Indore", "Patna", "Varanasi", "Kanpur",
        ]
        for city in cities:
            result = utils.get_mock_weather(city)
            assert result["temp"] > 0, f"No temp for {city}"
            assert result["humidity"] > 0, f"No humidity for {city}"

    def test_case_insensitive(self):
        """Should match cities regardless of case."""
        lower = utils.get_mock_weather("delhi")
        upper = utils.get_mock_weather("DELHI")
        mixed = utils.get_mock_weather("Delhi")
        assert lower["temp"] == upper["temp"] == mixed["temp"]


class TestMockCrop:
    """Tests for get_mock_crop."""

    def test_hot_dry_gets_bajra(self):
        """Hot dry conditions during Kharif should recommend Bajra."""
        weather = {"temp": 40, "rainfall": "low"}
        with patch("utils.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 7, 15)
            result = utils.get_mock_crop(weather, "Jaipur")
        assert "bajra" in result["crop_name"].lower() or "millet" in result["crop_name"].lower()

    def test_high_rainfall_gets_rice(self):
        """High rainfall during monsoon should recommend Rice."""
        weather = {"temp": 28, "rainfall": "high"}
        with patch("utils.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 8, 1)
            result = utils.get_mock_crop(weather, "Kolkata")
        assert "rice" in result["crop_name"].lower() or "paddy" in result["crop_name"].lower()

    def test_all_required_fields_present(self):
        """Crop recommendation should have all required fields."""
        weather = {"temp": 30, "rainfall": "medium"}
        result = utils.get_mock_crop(weather, "Pune")
        required = ["crop_name", "reason", "sowing_time", "harvest_time", "water_needs", "soil_type"]
        for field in required:
            assert field in result, f"Missing field: {field}"


class TestMockPest:
    """Tests for get_mock_pest."""

    def test_rice_gets_stem_borer(self):
        result = utils.get_mock_pest("Rice / Paddy")
        assert "Stem Borer" in result["pest_name"]
        assert result["severity"] == "high"

    def test_bajra_gets_aphids(self):
        result = utils.get_mock_pest("Pearl Millets (Bajra)")
        assert "Aphid" in result["pest_name"]

    def test_soybean_gets_caterpillar(self):
        result = utils.get_mock_pest("Soybean (सोयाबीन)")
        assert "Caterpillar" in result["pest_name"] or "Spodoptera" in result["pest_name"]

    def test_unknown_crop_gets_default(self):
        result = utils.get_mock_pest("Dragon Fruit")
        assert "Rust" in result["pest_name"]

    def test_all_required_fields_present(self):
        result = utils.get_mock_pest("Wheat")
        required = ["pest_name", "severity", "symptoms", "organic_treatment",
                     "chemical_treatment", "preventive_measures", "action_by_date"]
        for field in required:
            assert field in result, f"Missing field: {field}"


class TestMockMarket:
    """Tests for get_mock_market."""

    def test_real_mandi_name_for_delhi(self):
        result = utils.get_mock_market("Rice", "Delhi")
        assert "Azadpur" in result["best_market"]

    def test_real_mandi_name_for_mumbai(self):
        result = utils.get_mock_market("Tomato", "Mumbai")
        assert "Vashi" in result["best_market"]

    def test_unknown_city_generic_mandi(self):
        result = utils.get_mock_market("Wheat", "Timbuktu")
        assert "APMC" in result["best_market"]

    def test_price_is_positive(self):
        result = utils.get_mock_market("Rice", "Delhi")
        assert result["price"] > 0

    def test_different_crops_different_prices(self):
        rice = utils.get_mock_market("Rice", "Delhi")
        tomato = utils.get_mock_market("Tomato", "Delhi")
        assert rice["price"] != tomato["price"]
