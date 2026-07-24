from functools import lru_cache
from typing import Any
import joblib
from app.config import PROFILE_SUITABILITY_MODEL_PATH
from app.dbModels import Product

@lru_cache(maxsize=1)
def loadRecommendationModel():
    if not PROFILE_SUITABILITY_MODEL_PATH.exists():
        return None

    return joblib.load(PROFILE_SUITABILITY_MODEL_PATH)

def buildModelText(product: Product, profile: Any) -> str:
    productText = " ".join(
        str(field or "")
        for field in [
            product.product_name,
            product.brand_name,
            product.category,
            product.product_type,
            product.tags,
            product.description,
            product.ingredients,
            product.highlights,
        ]
    )

    profileText = (
        f"skin type {profile.skin_type} "
        f"skin tone {profile.skin_tone}"
    )

    return f"{productText} {profileText}"

def predictSuitabilityScore(product: Product, profile: Any) -> float | None:
    model = loadRecommendationModel()

    if model is None:
        return None

    modelText = buildModelText(product, profile)

    if hasattr(model, "predict_proba"):
        probability = model.predict_proba([modelText])[0][1]
        return round(float(probability), 4)

    prediction = model.predict([modelText])[0]
    return float(prediction)