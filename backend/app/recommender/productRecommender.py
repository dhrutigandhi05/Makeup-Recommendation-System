import json
from functools import lru_cache
from typing import Any
from sqlalchemy.orm import Session
from app.config import RECOMMENDER_RULES_PATH
from app.dbModels import Product
from app.repositories.productRepository import getAvailableProducts

@lru_cache(maxsize=1)
def loadRules() -> dict:
    if not RECOMMENDER_RULES_PATH.exists():
        raise FileNotFoundError(
            f"Recommender rules file not found at {RECOMMENDER_RULES_PATH}"
        )

    with open(RECOMMENDER_RULES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def containsAny(text: str, keywords: list[str]) -> bool:
    return any(keyword.lower() in text for keyword in keywords)

def buildProductText(product: Product) -> str:
    fields = [
        product.brand_name,
        product.product_name,
        product.description,
        product.ingredients,
        product.highlights,
        product.category,
        product.product_type,
        product.tags,
    ]

    return " ".join(str(field or "") for field in fields).lower()

def scoreProduct(product: Product, profile: Any, rules: dict) -> tuple[float, list[str]]:
    weights = rules["weights"]
    skinTypeKeywords = rules["skin_type_keywords"]
    concernKeywords = rules["concern_keywords"]
    coverageKeywords = rules["coverage_keywords"]
    experienceProductTypes = rules["experience_product_types"]
    text = buildProductText(product)
    score = weights["base_score"]
    reasons = []
    productType = str(product.product_type or "").lower()

    preferredTypes = experienceProductTypes.get(
        profile.experience_level,
        experienceProductTypes["Beginner"],
    )

    normalizedPreferredTypes = [
        item.lower().replace("_", " ") for item in preferredTypes
    ]

    if productType in normalizedPreferredTypes:
        score += weights["experience_match"]
        reasons.append(f"fits a {profile.experience_level.lower()} makeup routine")

    selectedSkinKeywords = skinTypeKeywords.get(profile.skin_type, [])

    if containsAny(text, selectedSkinKeywords):
        score += weights["skin_type_match"]
        reasons.append(f"matches {profile.skin_type.lower()} skin")

    selectedCoverageKeywords = coverageKeywords.get(profile.coverage, [])

    if containsAny(text, selectedCoverageKeywords):
        score += weights["coverage_match"]
        reasons.append(f"aligns with {profile.coverage.lower()} coverage")

    matchedConcerns = []

    for concern in profile.skin_concerns:
        selectedConcernKeywords = concernKeywords.get(concern, [])

        if containsAny(text, selectedConcernKeywords):
            matchedConcerns.append(concern)

    if matchedConcerns:
        concernScore = min(
            weights["max_concern_score"],
            weights["concern_match_per_item"] * len(matchedConcerns),
        )

        score += concernScore
        reasons.append("supports concerns like " + ", ".join(matchedConcerns))

    if product.price and product.price <= profile.max_price:
        priceScore = max(0, 1 - float(product.price) / profile.max_price)
        score += weights["price_score"] * priceScore
        reasons.append(f"fits your ${profile.max_price:.0f} budget")

    if product.rating:
        ratingScore = min(float(product.rating) / 5, 1)
        score += 0.05 * ratingScore
        reasons.append("has positive product rating data")

    score = min(score, 0.99)

    if not reasons:
        reasons.append("has relevant product information for your profile")

    return score, reasons

def formatProductRecommendation(
    product: Product,
    score: float,
    reasons: list[str],
) -> dict:
    productUrl = product.product_url or product.website_url or ""

    return {
        "category": str(product.product_type or product.category or "Product").title(),
        "product_name": product.product_name,
        "brand": product.brand_name.title() if product.brand_name else "Unknown Brand",
        "price": float(product.price or 0),
        "url": productUrl,
        "image_link": product.image_link or "",
        "match_score": round(score, 2),
        "reason": "Recommended because it " + ", ".join(reasons[:3]) + ".",
    }

def recommendProducts(db: Session, profile: Any, limit: int = 8) -> list[dict]:
    rules = loadRules()
    products = getAvailableProducts(db, profile.max_price)

    if not products:
        return []

    scoredProducts = []

    for product in products:
        score, reasons = scoreProduct(product, profile, rules)

        if not product.product_url and not product.website_url:
            continue

        scoredProducts.append(
            formatProductRecommendation(product, score, reasons)
        )

    scoredProducts = sorted(
        scoredProducts,
        key=lambda item: item["match_score"],
        reverse=True,
    )

    return scoredProducts[:limit]