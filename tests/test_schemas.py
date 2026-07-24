"""
AgroPilot Schema Validation Tests
Ensures Pydantic models correctly validate and reject LLM outputs.
"""

import pytest
from pydantic import ValidationError
from schemas import CropRecommendation, PestAssessment, MarketIntelligence


class TestCropRecommendation:
    """Tests for CropRecommendation schema."""

    def test_valid_input(self):
        data = {
            "crop_name": "Rice (धान)",
            "reason": "Thrives in high rainfall monsoon conditions",
            "sowing_time": "Immediate",
            "harvest_time": "120-150 days",
            "water_needs": "high",
            "soil_type": "Clay loam",
        }
        model = CropRecommendation.model_validate(data)
        assert model.crop_name == "Rice (धान)"
        assert model.water_needs == "high"

    def test_water_needs_normalization(self):
        """Should normalize ' HIGH ' to 'high'."""
        data = {
            "crop_name": "Bajra (बाजरा)",
            "reason": "Drought-resistant millet for arid conditions",
            "sowing_time": "Next 7 days",
            "harvest_time": "60-65 days",
            "water_needs": " HIGH ",
            "soil_type": "Sandy",
        }
        model = CropRecommendation.model_validate(data)
        assert model.water_needs == "high"

    def test_invalid_water_needs_rejected(self):
        """Should reject invalid water_needs values."""
        data = {
            "crop_name": "Test Crop",
            "reason": "Some reason for this crop recommendation",
            "sowing_time": "Next week",
            "harvest_time": "90 days",
            "water_needs": "extreme",
            "soil_type": "Loam",
        }
        with pytest.raises(ValidationError):
            CropRecommendation.model_validate(data)

    def test_missing_required_field_rejected(self):
        """Should reject when required fields are missing."""
        data = {"crop_name": "Rice"}  # missing everything else
        with pytest.raises(ValidationError):
            CropRecommendation.model_validate(data)

    def test_empty_crop_name_rejected(self):
        """Should reject crop_name shorter than 2 characters."""
        data = {
            "crop_name": "X",
            "reason": "Some valid reason for recommending this",
            "sowing_time": "Next week",
            "harvest_time": "90 days",
            "water_needs": "low",
            "soil_type": "Loam",
        }
        with pytest.raises(ValidationError):
            CropRecommendation.model_validate(data)


class TestPestAssessment:
    """Tests for PestAssessment schema."""

    def test_valid_input(self):
        data = {
            "pest_name": "Aphids (माहू)",
            "severity": "medium",
            "symptoms": "Yellowing leaves and stunted growth observed",
            "organic_treatment": "Neem oil spray at 5ml/L water weekly",
            "chemical_treatment": "Imidacloprid 17.8% SL @ 0.3ml/L spray",
            "preventive_measures": "Crop rotation and yellow sticky traps",
            "action_by_date": "Within 7 days",
        }
        model = PestAssessment.model_validate(data)
        assert model.severity == "medium"

    def test_severity_normalization(self):
        """Should normalize 'HIGH' to 'high'."""
        data = {
            "pest_name": "Stem Borer (तना छेदक)",
            "severity": "HIGH",
            "symptoms": "Dead heart in vegetative stage whiteheads",
            "organic_treatment": "Release Trichogramma parasitoids at weekly intervals",
            "chemical_treatment": "Cartap hydrochloride 4G at 10 kg per acre",
            "preventive_measures": "Clip seedling tips before transplanting",
            "action_by_date": "Immediate action required",
        }
        model = PestAssessment.model_validate(data)
        assert model.severity == "high"

    def test_invalid_severity_rejected(self):
        """Should reject severity values not in low/medium/high."""
        data = {
            "pest_name": "Some Pest Name",
            "severity": "critical",
            "symptoms": "Some symptoms described here in detail",
            "organic_treatment": "Some organic treatment approach here",
            "chemical_treatment": "Some chemical treatment with dosage",
            "preventive_measures": "Some preventive measures listed here",
            "action_by_date": "Within 3 days",
        }
        with pytest.raises(ValidationError):
            PestAssessment.model_validate(data)


class TestMarketIntelligence:
    """Tests for MarketIntelligence schema."""

    def test_valid_input(self):
        data = {
            "price": 2800,
            "unit": "quintal",
            "trend": "up 12% this month",
            "best_market": "Azadpur Mandi, Delhi",
            "sell_timing": "Sell after 60 days when September demand peaks",
            "storage_tips": "Dry ventilated space with less than 12% moisture",
            "market_strategy": "Sell in bulk for 8-10% premium over local rates",
        }
        model = MarketIntelligence.model_validate(data)
        assert model.price == 2800

    def test_price_as_string_coerced(self):
        """Should coerce string price '₹2,800' to int 2800."""
        data = {
            "price": "₹2,800",
            "unit": "quintal",
            "trend": "stable this month",
            "best_market": "APMC Market, Pune",
            "sell_timing": "Hold for 2 months for better prices",
            "storage_tips": "Standard grain storage in dry location",
            "market_strategy": "Sell to local aggregators at market rate",
        }
        model = MarketIntelligence.model_validate(data)
        assert model.price == 2800

    def test_negative_price_rejected(self):
        """Should reject negative or zero prices."""
        data = {
            "price": -100,
            "unit": "quintal",
            "trend": "down sharply",
            "best_market": "Test Mandi",
            "sell_timing": "Some timing advice",
            "storage_tips": "Some storage tips here",
            "market_strategy": "Some market strategy here",
        }
        with pytest.raises(ValidationError):
            MarketIntelligence.model_validate(data)

    def test_absurd_price_rejected(self):
        """Should reject prices > 50000 (unrealistic)."""
        data = {
            "price": 999999,
            "unit": "quintal",
            "trend": "up trend",
            "best_market": "Test Mandi Name",
            "sell_timing": "Some timing advice",
            "storage_tips": "Some storage tips here",
            "market_strategy": "Some market strategy here",
        }
        with pytest.raises(ValidationError):
            MarketIntelligence.model_validate(data)
