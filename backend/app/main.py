from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/recommendations")
def get_recommendations(profile: RecommendationRequest):
    try:
        recommendations = recommend_products(profile)

        return {
            "profile": profile,
            "recommendations": recommendations,
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error while generating recommendations",
        )