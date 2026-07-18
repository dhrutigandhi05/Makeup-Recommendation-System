from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.recommender.productRecommender import recommendProducts
from app.schemas import RecommendationRequest, RecommendationResponse

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