from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.recommender.productRecommender import recommendProducts
from app.schemas import (
    AgeRange,
    CoveragePreference,
    ExperienceLevel,
    FormOptionsResponse,
    RecommendationRequest,
    RecommendationResponse,
    SkinConcern,
    SkinTone,
    SkinType,
)

app = FastAPI(title="Makeup Recommendation API")

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

@app.get("/api/form-options", response_model=FormOptionsResponse)
def getFormOptions():
    return {
        "age_ranges": [option.value for option in AgeRange],
        "skin_types": [option.value for option in SkinType],
        "experience_levels": [option.value for option in ExperienceLevel],
        "coverage_preferences": [option.value for option in CoveragePreference],
        "skin_tones": [option.value for option in SkinTone],
        "skin_concerns": [option.value for option in SkinConcern],
    }

@app.post("/api/recommendations", response_model=RecommendationResponse)
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
            detail="Unexpected error while generating recommendations.",
        )