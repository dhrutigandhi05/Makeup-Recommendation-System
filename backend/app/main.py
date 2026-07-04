from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.recommender.productRecommender import recommendProducts

app = FastAPI(title="Makeup Recommendation API")

class RecommendationRequest(BaseModel):
    age_range: str
    skin_type: str
    experience_level: str
    coverage: str
    max_price: float
    skin_tone: str
    skin_concerns: List[str]

def getDb():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Makeup Recommendation API is running"}

@app.get("/api/health")
def healthCheck():
    return {"status": "ok"}

@app.post("/api/recommendations")
def getRecommendations(
    profile: RecommendationRequest,
    db: Session = Depends(getDb),
):
    try:
        recommendations = recommendProducts(db, profile)

        return {
            "profile": profile,
            "recommendations": recommendations,
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:
        print(error)

        raise HTTPException(
            status_code=500,
            detail="Unexpected error while finding recommendations.",
        )