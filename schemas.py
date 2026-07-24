"""
AgroPilot Pydantic Schemas
Validates structured outputs from each AI agent to catch LLM hallucinations
and malformed responses before they reach the farmer.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional


class CropRecommendation(BaseModel):
    """Schema for CropAgent output."""
    crop_name: str = Field(..., min_length=2, description="Crop name with Hindi name in parentheses")
    reason: str = Field(..., min_length=10, description="Why this crop is recommended")
    sowing_time: str = Field(..., min_length=3, description="When to sow")
    harvest_time: str = Field(..., min_length=3, description="Expected harvest timeline")
    water_needs: Literal["low", "medium", "high"] = Field(..., description="Irrigation requirement")
    soil_type: str = Field(..., min_length=2, description="Suitable soil type")

    @field_validator("water_needs", mode="before")
    @classmethod
    def normalize_water_needs(cls, v: str) -> str:
        return v.strip().lower()


class PestAssessment(BaseModel):
    """Schema for PestAgent output."""
    pest_name: str = Field(..., min_length=2, description="Pest/disease name with Hindi name")
    severity: Literal["low", "medium", "high"] = Field(..., description="Risk severity level")
    symptoms: str = Field(..., min_length=10, description="Observable symptoms")
    organic_treatment: str = Field(..., min_length=10, description="Organic/natural treatment")
    chemical_treatment: str = Field(..., min_length=10, description="Chemical treatment option")
    preventive_measures: str = Field(..., min_length=10, description="Prevention steps")
    action_by_date: str = Field(..., min_length=3, description="Deadline for action")
    identified_crop: Optional[str] = None

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v: str) -> str:
        return v.strip().lower()


class MarketIntelligence(BaseModel):
    """Schema for MarketAgent output."""
    price: int = Field(..., gt=0, le=50000, description="Price per unit in INR")
    unit: str = Field(default="quintal", description="Price unit")
    trend: str = Field(..., min_length=2, description="Price trend description")
    best_market: str = Field(..., min_length=3, description="Recommended mandi/market")
    sell_timing: str = Field(..., min_length=5, description="When to sell for best price")
    storage_tips: str = Field(..., min_length=5, description="Storage recommendations")
    market_strategy: str = Field(..., min_length=5, description="Selling strategy advice")

    @field_validator("price", mode="before")
    @classmethod
    def coerce_price(cls, v) -> int:
        """Handle LLM returning price as string or float."""
        if isinstance(v, str):
            v = v.replace(",", "").replace("₹", "").strip()
        return int(float(v))
