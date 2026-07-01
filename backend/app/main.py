from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from app.recommender.productRecommender import recommend_products

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
    recommendations = recommend_products(profile)
    return {
        "profile": profile,
        "recommendations": recommendations,
    }