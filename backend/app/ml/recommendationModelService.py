import math
from functools import lru_cache
from typing import Any
import joblib
from app.config import ML_MODEL_PATH
from app.dbModels import Product

@lru_cache(maxsize=1)
def loadRecommendationModel():
    if not ML_MODEL_PATH.exists():
        return None

    return joblib.load(ML_MODEL_PATH)

def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)

    z = math.exp(value)
    return z / (1 + z)

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

    userProfileText = (
        f"skin type {profile.skin_type} "
        f"skin tone {profile.skin_tone} "
        f"coverage preference {profile.coverage} "
        f"experience level {profile.experience_level} "
        f"age range {profile.age_range} "
        f"skin concerns {' '.join(profile.skin_concerns)}"
    )

    return f"{productText} {userProfileText}"

def predictSuitabilityScore(product: Product, profile: Any) -> float | None:
    model = loadRecommendationModel()

    if model is None:
        return None

    modelText = buildModelText(product, profile)

    if hasattr(model, "decision_function"):
        decisionScore = model.decision_function([modelText])[0]
        return round(sigmoid(float(decisionScore)), 4)

    prediction = model.predict([modelText])[0]
    return float(prediction)