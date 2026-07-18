from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class AgeRange(str, Enum):
    under20 = "Under 20"
    twentyToThirty = "20-30"
    thirtyToForty = "30-40"
    fortyPlus = "40+"

class SkinType(str, Enum):
    oily = "Oily"
    dry = "Dry"
    combination = "Combination"
    normal = "Normal"
    sensitive = "Sensitive"

class ExperienceLevel(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"

class CoveragePreference(str, Enum):
    light = "Light"
    medium = "Medium"
    full = "Full"

class SkinTone(str, Enum):
    light = "Light"
    medium = "Medium"
    deep = "Deep"

class SkinConcern(str, Enum):
    acne = "Acne"
    darkCircles = "Dark Circles"
    hyperpigmentation = "Hyperpigmentation"
    rednessRosacea = "Redness/Rosacea"
    wrinkles = "Wrinkles"
    sensitiveSkin = "Sensitive Skin"

class RecommendationRequest(BaseModel):
    age_range: AgeRange
    skin_type: SkinType
    experience_level: ExperienceLevel
    coverage: CoveragePreference
    max_price: float = Field(gt=0, le=500)
    skin_tone: SkinTone
    skin_concerns: List[SkinConcern] = []

class ProductRecommendation(BaseModel):
    category: str
    product_name: str
    brand: str
    price: float
    url: str
    image_link: Optional[str] = None
    match_score: float
    ml_score: Optional[float] = None
    routine_step: Optional[str] = None
    reason: str

class RecommendationResponse(BaseModel):
    profile: RecommendationRequest
    recommendations: List[ProductRecommendation]

class FormOptionsResponse(BaseModel):
    age_ranges: List[str]
    skin_types: List[str]
    experience_levels: List[str]
    coverage_preferences: List[str]
    skin_tones: List[str]
    skin_concerns: List[str]