from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Makeup Recommendation API")

class RecommendationRequest(BaseModel):
    age_range: str
    skin_type: str
    experience_level: str
    coverage: str
    max_price: float
    skin_tone: str
    skin_concerns: List[str]

@app.get("/")
def root():
    return {"message": "Makeup Recommendation API is running"}

@app.post("/api/recommendations")
def get_recommendations(profile: RecommendationRequest):
    return {
        "profile": profile,
        "recommendations": [
            {
                "category": "Foundation",
                "product_name": "Sample Foundation",
                "brand": "Sample Brand",
                "price": 19.99,
                "url": "https://example.com",
                "match_score": 0.92,
                "reason": "Recommended because it matches your skin type, coverage preference, and budget."
            },
            {
                "category": "Concealer",
                "product_name": "Sample Concealer",
                "brand": "Sample Brand",
                "price": 12.99,
                "url": "https://example.com",
                "match_score": 0.87,
                "reason": "Recommended because it fits your selected skin concerns and budget."
            }
        ]
    }