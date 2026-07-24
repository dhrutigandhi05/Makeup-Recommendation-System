import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

sys.path.append(str(BACKEND_DIR))

from app.database import Base, engine
from app.dbModels import ProductProfileSuitability

MIN_REVIEW_COUNT = 5
SUITABLE_RECOMMENDATION_RATE = 0.70
UNSUITABLE_RECOMMENDATION_RATE = 0.40

def normalizeSkinType(value) -> str:
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()
    mapping = {
        "oily": "Oily",
        "dry": "Dry",
        "combination": "Combination",
        "normal": "Normal",
        "sensitive": "Sensitive",
    }

    return mapping.get(value, "")

def normalizeSkinTone(value) -> str:
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()
    lightValues = {"fair", "fairlight", "light", "porcelain"}
    mediumValues = {"medium", "olive", "tan", "mediumtan"}
    deepValues = {"deep", "dark", "rich", "deeprich"}
    cleanedValue = value.replace(" ", "").replace("-", "").replace("_", "")

    if cleanedValue in lightValues:
        return "Light"

    if cleanedValue in mediumValues:
        return "Medium"

    if cleanedValue in deepValues:
        return "Deep"

    return ""

def loadReviewProductData() -> pd.DataFrame:
    query = """
        SELECT
            pr.source_product_id,
            pr.skin_type,
            pr.skin_tone,
            pr.rating AS review_rating,
            pr.target_recommended,
            p.product_name,
            p.brand_name,
            p.price,
            p.category,
            p.product_type,
            p.description,
            p.ingredients,
            p.highlights,
            p.tags,
            p.rating AS product_rating
        FROM product_reviews pr
        JOIN products p
          ON pr.source_product_id = p.source_product_id
         AND p.source = 'sephora'
        WHERE pr.source = 'sephora'
          AND pr.target_recommended IS NOT NULL;
    """

    return pd.read_sql(query, engine)

def buildSuitabilityDataset(data: pd.DataFrame) -> pd.DataFrame:
    data["normalized_skin_type"] = data["skin_type"].apply(normalizeSkinType)
    data["normalized_skin_tone"] = data["skin_tone"].apply(normalizeSkinTone)
    data = data[
        (data["normalized_skin_type"] != "")
        & (data["normalized_skin_tone"] != "")
    ].copy()

    grouped = (
        data.groupby(
            [
                "source_product_id",
                "product_name",
                "brand_name",
                "normalized_skin_type",
                "normalized_skin_tone",
            ],
            dropna=False,
        )
        .agg(
            review_count=("target_recommended", "count"),
            average_rating=("review_rating", "mean"),
            recommendation_rate=("target_recommended", "mean"),
            category=("category", "first"),
            product_type=("product_type", "first"),
            description=("description", "first"),
            ingredients=("ingredients", "first"),
            highlights=("highlights", "first"),
            tags=("tags", "first"),
            product_rating=("product_rating", "first"),
        )
        .reset_index()
    )

    grouped = grouped[grouped["review_count"] >= MIN_REVIEW_COUNT].copy()
    grouped["target_suitable"] = grouped["recommendation_rate"].apply(
        lambda rate: 1
        if rate >= SUITABLE_RECOMMENDATION_RATE
        else 0
        if rate <= UNSUITABLE_RECOMMENDATION_RATE
        else None
    )

    grouped = grouped.dropna(subset=["target_suitable"]).copy()
    grouped["target_suitable"] = grouped["target_suitable"].astype(int)
    grouped["product_text"] = (
        grouped["product_name"].fillna("").astype(str)
        + " "
        + grouped["brand_name"].fillna("").astype(str)
        + " "
        + grouped["category"].fillna("").astype(str)
        + " "
        + grouped["product_type"].fillna("").astype(str)
        + " "
        + grouped["description"].fillna("").astype(str)
        + " "
        + grouped["ingredients"].fillna("").astype(str)
        + " "
        + grouped["highlights"].fillna("").astype(str)
        + " "
        + grouped["tags"].fillna("").astype(str)
    )

    grouped["profile_text"] = (
        "skin type "
        + grouped["normalized_skin_type"]
        + " skin tone "
        + grouped["normalized_skin_tone"]
    )

    grouped["training_text"] = grouped["product_text"] + " " + grouped["profile_text"]

    finalData = pd.DataFrame(
        {
            "source": "sephora",
            "source_product_id": grouped["source_product_id"].astype(str),
            "product_name": grouped["product_name"],
            "brand_name": grouped["brand_name"],
            "skin_type": grouped["normalized_skin_type"],
            "skin_tone": grouped["normalized_skin_tone"],
            "review_count": grouped["review_count"],
            "average_rating": grouped["average_rating"],
            "recommendation_rate": grouped["recommendation_rate"],
            "target_suitable": grouped["target_suitable"],
            "product_text": grouped["product_text"],
            "profile_text": grouped["profile_text"],
            "training_text": grouped["training_text"],
        }
    )

    return finalData.where(pd.notna(finalData), None)

def resetSuitabilityTable() -> None:
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE product_profile_suitability RESTART IDENTITY")
        )

def main() -> None:
    print("Loading Sephora review/product data from Postgres...")
    data = loadReviewProductData()
    print(f"Loaded rows: {len(data)}")
    print("Building product-profile suitability dataset...")
    suitabilityData = buildSuitabilityDataset(data)

    if suitabilityData.empty:
        raise ValueError("No suitability rows were created.")

    resetSuitabilityTable()
    suitabilityData.to_sql(
        ProductProfileSuitability.__tablename__,
        engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )

    print("Saved product-profile suitability data to Postgres.")
    print(f"Rows: {len(suitabilityData)}")
    print("Target distribution:")
    print(suitabilityData["target_suitable"].value_counts())
    print("Skin type distribution:")
    print(suitabilityData["skin_type"].value_counts())
    print("Skin tone distribution:")
    print(suitabilityData["skin_tone"].value_counts())

if __name__ == "__main__":
    main()