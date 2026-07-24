import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

sys.path.append(str(BACKEND_DIR))

from app.database import engine

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
    cleanedValue = value.replace(" ", "").replace("-", "").replace("_", "")
    lightValues = {"fair", "fairlight", "light", "porcelain"}
    mediumValues = {"medium", "olive", "tan", "mediumtan"}
    deepValues = {"deep", "dark", "rich", "deeprich"}

    if cleanedValue in lightValues:
        return "Light"

    if cleanedValue in mediumValues:
        return "Medium"

    if cleanedValue in deepValues:
        return "Deep"

    return ""

def loadReviewData() -> pd.DataFrame:
    query = """
        SELECT
            pr.source_product_id,
            pr.skin_type,
            pr.skin_tone,
            pr.rating AS review_rating,
            pr.target_recommended,
            p.product_name,
            p.brand_name
        FROM product_reviews pr
        JOIN products p
          ON pr.source_product_id = p.source_product_id
         AND p.source = 'sephora'
        WHERE pr.source = 'sephora'
          AND pr.target_recommended IS NOT NULL;
    """

    return pd.read_sql(query, engine)

def buildGroupedData(data: pd.DataFrame) -> pd.DataFrame:
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
        )
        .reset_index()
    )

    return grouped

def printDistribution(grouped: pd.DataFrame) -> None:
    print("Grouped data summary")
    print(f"Rows before min review filter: {len(grouped)}")
    print("Recommendation rate quantiles:")
    print(grouped["recommendation_rate"].quantile([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]))
    print("Average rating quantiles:")
    print(grouped["average_rating"].quantile([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]))

def printThresholdOptions(grouped: pd.DataFrame) -> None:
    minReviewCounts = [5, 10, 20]
    unsuitableThresholds = [0.50, 0.60, 0.65, 0.70, 0.75]
    suitableThresholds = [0.80, 0.85, 0.90, 0.95]

    print("Threshold candidate counts")
    print("=" * 80)

    for minReviews in minReviewCounts:
        filtered = grouped[grouped["review_count"] >= minReviews].copy()

        print(f"Minimum reviews per product-profile group: {minReviews}")
        print(f"Groups available: {len(filtered)}")
        print("-" * 80)

        for unsuitableThreshold in unsuitableThresholds:
            for suitableThreshold in suitableThresholds:
                if unsuitableThreshold >= suitableThreshold:
                    continue

                positiveCount = len(
                    filtered[filtered["recommendation_rate"] >= suitableThreshold]
                )

                negativeCount = len(
                    filtered[filtered["recommendation_rate"] <= unsuitableThreshold]
                )

                total = positiveCount + negativeCount

                if negativeCount == 0:
                    ratio = "no negatives"
                else:
                    ratio = f"{positiveCount / negativeCount:.1f}:1"

                print(
                    f"negative <= {unsuitableThreshold:.2f}, "
                    f"positive >= {suitableThreshold:.2f} | "
                    f"positive: {positiveCount:5d}, "
                    f"negative: {negativeCount:5d}, "
                    f"total: {total:5d}, "
                    f"pos:neg = {ratio}"
                )

def main() -> None:
    print("Loading review data from Postgres...")
    data = loadReviewData()
    print(f"Loaded review rows: {len(data)}")
    print("Grouping by product + skin type + skin tone...")
    grouped = buildGroupedData(data)
    printDistribution(grouped)
    printThresholdOptions(grouped)

if __name__ == "__main__":
    main()