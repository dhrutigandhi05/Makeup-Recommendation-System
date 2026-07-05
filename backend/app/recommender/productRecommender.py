import json
from functools import lru_cache
from typing import Any
from sqlalchemy.orm import Session
from app.config import RECOMMENDER_RULES_PATH
from app.dbModels import Product
from app.ml.recommendationModelService import predictSuitabilityScore
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

def scoreProduct(
    product: Product,
    profile: Any,
    rules: dict,
) -> tuple[float, list[str], float | None]:
    weights = rules["weights"]
    skinTypeKeywords = rules["skin_type_keywords"]
    concernKeywords = rules["concern_keywords"]
    coverageKeywords = rules["coverage_keywords"]
    experienceProductTypes = rules["experience_product_types"]
    text = buildProductText(product)

    ruleScore = weights["base_score"]
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
        ruleScore += weights["experience_match"]
        reasons.append(f"fits a {profile.experience_level.lower()} makeup routine")

    selectedSkinKeywords = skinTypeKeywords.get(profile.skin_type, [])

    if containsAny(text, selectedSkinKeywords):
        ruleScore += weights["skin_type_match"]
        reasons.append(f"matches {profile.skin_type.lower()} skin")

    selectedCoverageKeywords = coverageKeywords.get(profile.coverage, [])

    if containsAny(text, selectedCoverageKeywords):
        ruleScore += weights["coverage_match"]
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

        ruleScore += concernScore
        reasons.append("supports concerns like " + ", ".join(matchedConcerns))

    if product.price and product.price <= profile.max_price:
        priceScore = max(0, 1 - float(product.price) / profile.max_price)
        ruleScore += weights["price_score"] * priceScore
        reasons.append(f"fits your ${profile.max_price:.0f} budget")

    if product.rating:
        ratingScore = min(float(product.rating) / 5, 1)
        ruleScore += 0.05 * ratingScore
        reasons.append("has positive product rating data")

    ruleScore = min(ruleScore, 0.99)

    mlScore = predictSuitabilityScore(product, profile)

    if mlScore is not None:
        finalScore = (0.7 * ruleScore) + (0.3 * mlScore)

        if mlScore >= 0.65:
            reasons.append("is supported by the trained ML suitability model")
    else:
        finalScore = ruleScore

    finalScore = min(finalScore, 0.99)

    if not reasons:
        reasons.append("has relevant product information for your profile")

    return finalScore, reasons, mlScore

def formatProductRecommendation(
    product: Product,
    score: float,
    reasons: list[str],
    mlScore: float | None,
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
        "ml_score": mlScore,
        "reason": "Recommended because it " + ", ".join(reasons[:3]) + ".",
    }

def isExcludedProduct(product: Product, rules: dict) -> bool:
    excludedKeywords = rules.get("excluded_keywords", [])
    text = buildProductText(product)

    return containsAny(text, excludedKeywords)

def getRoutineSlots(profile: Any, rules: dict) -> list[dict]:
    routineSlots = rules.get("routine_slots", {})

    return routineSlots.get(
        profile.experience_level,
        routineSlots.get("Beginner", []),
    )

def productMatchesSlot(product: Product, slot: dict) -> bool:
    productType = str(product.product_type or "").lower().replace("_", " ")
    category = str(product.category or "").lower().replace("_", " ")
    text = buildProductText(product)

    for slotProductType in slot.get("product_types", []):
        normalizedSlotType = slotProductType.lower().replace("_", " ")

        if normalizedSlotType == productType:
            return True

        if normalizedSlotType in category:
            return True

        if normalizedSlotType in text:
            return True

    return False

def recommendProducts(db: Session, profile: Any, limit: int = 8) -> list[dict]:
    rules = loadRules()
    products = getAvailableProducts(db, profile.max_price)

    if not products:
        return []

    routineSlots = getRoutineSlots(profile, rules)

    scoredProducts = []

    for product in products:
        if isExcludedProduct(product, rules):
            continue

        score, reasons, mlScore = scoreProduct(product, profile, rules)

        if not product.product_url and not product.website_url:
            continue

        scoredProducts.append(
            {
                "raw_product": product,
                "score": score,
                "reasons": reasons,
                "ml_score": mlScore,
            }
        )

    if not scoredProducts:
        return []

    finalRecommendations = []
    usedProductIds = set()

    for slot in routineSlots:
        slotMatches = [
            item
            for item in scoredProducts
            if productMatchesSlot(item["raw_product"], slot)
            and item["raw_product"].id not in usedProductIds
        ]

        if not slotMatches:
            continue

        bestMatch = sorted(
            slotMatches,
            key=lambda item: item["score"],
            reverse=True,
        )[0]

        usedProductIds.add(bestMatch["raw_product"].id)

        recommendation = formatProductRecommendation(
            bestMatch["raw_product"],
            bestMatch["score"],
            bestMatch["reasons"],
            bestMatch["ml_score"],
        )

        recommendation["routine_step"] = slot["slot"]
        finalRecommendations.append(recommendation)

        if len(finalRecommendations) >= limit:
            break

    if len(finalRecommendations) < limit:
        remainingProducts = [
            item
            for item in scoredProducts
            if item["raw_product"].id not in usedProductIds
        ]

        remainingProducts = sorted(
            remainingProducts,
            key=lambda item: item["score"],
            reverse=True,
        )

        for item in remainingProducts:
            recommendation = formatProductRecommendation(
                item["raw_product"],
                item["score"],
                item["reasons"],
                item["ml_score"],
            )

            recommendation["routine_step"] = "Additional Pick"
            finalRecommendations.append(recommendation)

            if len(finalRecommendations) >= limit:
                break

    return finalRecommendations