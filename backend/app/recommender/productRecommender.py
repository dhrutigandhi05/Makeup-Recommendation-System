import json
from functools import lru_cache
from typing import Any
import pandas as pd
from app.config import PRODUCT_DATA_PATH, RECOMMENDER_RULES_PATH

@lru_cache(maxsize=1)
def load_rules() -> dict:
    if not RECOMMENDER_RULES_PATH.exists():
        raise FileNotFoundError(
            f"Recommender rules file not found at {RECOMMENDER_RULES_PATH}"
        )

    with open(RECOMMENDER_RULES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

@lru_cache(maxsize=1)
def load_products() -> pd.DataFrame:
    if not PRODUCT_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Product data file not found at {PRODUCT_DATA_PATH}. "
            "Run scripts/fetch_makeup_api.py first."
        )

    df = pd.read_csv(PRODUCT_DATA_PATH)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    df = df[df["price"] > 0]

    text_columns = [
        "brand",
        "name",
        "description",
        "category",
        "product_type",
        "tag_list",
        "product_link",
        "website_link",
        "image_link",
    ]

    for column in text_columns:
        if column not in df.columns:
            df[column] = ""
        df[column] = df[column].fillna("")

    return df

def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword.lower() in text for keyword in keywords)

def build_product_text(product: pd.Series) -> str:
    fields = [
        product.get("brand", ""),
        product.get("name", ""),
        product.get("description", ""),
        product.get("category", ""),
        product.get("product_type", ""),
        product.get("tag_list", ""),
    ]

    return " ".join(str(field) for field in fields).lower()

def score_product(product: pd.Series, profile: Any, rules: dict) -> tuple[float, list[str]]:
    weights = rules["weights"]
    skin_type_keywords = rules["skin_type_keywords"]
    concern_keywords = rules["concern_keywords"]
    coverage_keywords = rules["coverage_keywords"]
    experience_product_types = rules["experience_product_types"]
    text = build_product_text(product)
    score = weights["base_score"]
    reasons = []
    product_type = str(product.get("product_type", "")).lower()

    preferred_types = experience_product_types.get(
        profile.experience_level,
        experience_product_types["Beginner"],
    )

    if product_type in preferred_types:
        score += weights["experience_match"]
        reasons.append(f"fits a {profile.experience_level.lower()} makeup routine")

    skin_keywords = skin_type_keywords.get(profile.skin_type, [])

    if contains_any(text, skin_keywords):
        score += weights["skin_type_match"]
        reasons.append(f"matches {profile.skin_type.lower()} skin")

    selected_coverage_keywords = coverage_keywords.get(profile.coverage, [])

    if contains_any(text, selected_coverage_keywords):
        score += weights["coverage_match"]
        reasons.append(f"aligns with {profile.coverage.lower()} coverage")

    matched_concerns = []

    for concern in profile.skin_concerns:
        selected_concern_keywords = concern_keywords.get(concern, [])

        if contains_any(text, selected_concern_keywords):
            matched_concerns.append(concern)

    if matched_concerns:
        concern_score = min(
            weights["max_concern_score"],
            weights["concern_match_per_item"] * len(matched_concerns),
        )

        score += concern_score
        reasons.append("supports concerns like " + ", ".join(matched_concerns))

    price = float(product.get("price", 0))

    if price <= profile.max_price:
        price_score = max(0, 1 - price / profile.max_price)
        score += weights["price_score"] * price_score
        reasons.append(f"fits your ${profile.max_price:.0f} budget")

    score = min(score, 0.99)

    if not reasons:
        reasons.append("has relevant product information for your profile")

    return score, reasons

def recommend_products(profile: Any, limit: int = 8) -> list[dict]:
    rules = load_rules()
    df = load_products()

    filtered_df = df[df["price"] <= profile.max_price].copy()

    if filtered_df.empty:
        return []

    scored_products = []

    for _, product in filtered_df.iterrows():
        score, reasons = score_product(product, profile, rules)

        product_url = product.get("product_link") or product.get("website_link")

        if not product_url:
            continue

        scored_products.append(
            {
                "category": str(product.get("product_type", "")).title(),
                "product_name": str(product.get("name", "")),
                "brand": str(product.get("brand", "")).title()
                if product.get("brand")
                else "Unknown Brand",
                "price": float(product.get("price", 0)),
                "url": str(product_url),
                "image_link": str(product.get("image_link", "")),
                "match_score": round(score, 2),
                "reason": "Recommended because it "
                + ", ".join(reasons[:3])
                + ".",
            }
        )

    scored_products = sorted(
        scored_products,
        key=lambda item: item["match_score"],
        reverse=True,
    )

    return scored_products[:limit]