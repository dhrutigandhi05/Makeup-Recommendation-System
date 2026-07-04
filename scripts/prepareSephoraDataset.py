import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

SEPHORA_RAW_DIR = ROOT_DIR / os.getenv(
    "SEPHORA_RAW_DIR",
    "data/raw/sephora",
)

SEPHORA_PROCESSED_PATH = ROOT_DIR / os.getenv(
    "SEPHORA_PROCESSED_PATH",
    "data/processed/sephoraMlDataset.csv",
)

def cleanText(value) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()

def loadProductInfo() -> pd.DataFrame:
    productInfoPath = SEPHORA_RAW_DIR / "product_info.csv"

    if not productInfoPath.exists():
        raise FileNotFoundError(f"Missing product info file: {productInfoPath}")

    productInfo = pd.read_csv(productInfoPath)
    selectedColumns = [
        "product_id",
        "product_name",
        "brand_name",
        "loves_count",
        "rating",
        "reviews",
        "ingredients",
        "price_usd",
        "highlights",
        "primary_category",
        "secondary_category",
        "tertiary_category",
    ]

    availableColumns = [
        column for column in selectedColumns if column in productInfo.columns
    ]

    productInfo = productInfo[availableColumns].copy()

    return productInfo

def loadReviews() -> pd.DataFrame:
    reviewFiles = sorted(SEPHORA_RAW_DIR.glob("reviews_*.csv"))

    if not reviewFiles:
        raise FileNotFoundError(
            f"No review CSV files found in {SEPHORA_RAW_DIR}"
        )

    reviewFrames = []

    for reviewFile in reviewFiles:
        print(f"Loading {reviewFile.name}")
        reviewFrame = pd.read_csv(reviewFile)

        if "Unnamed: 0" in reviewFrame.columns:
            reviewFrame = reviewFrame.drop(columns=["Unnamed: 0"])

        reviewFrames.append(reviewFrame)

    reviews = pd.concat(reviewFrames, ignore_index=True)

    return reviews

def createTargetLabel(row) -> int | None:
    isRecommended = row.get("is_recommended")

    if not pd.isna(isRecommended):
        try:
            return int(isRecommended)
        except ValueError:
            pass

    rating = row.get("rating")

    if pd.isna(rating):
        return None

    if rating >= 4:
        return 1

    if rating <= 2:
        return 0

    return None

def prepareDataset() -> pd.DataFrame:
    productInfo = loadProductInfo()
    reviews = loadReviews()

    print(f"Loaded {len(productInfo)} products")
    print(f"Loaded {len(reviews)} reviews")

    dataset = reviews.merge(
        productInfo,
        on="product_id",
        how="left",
        suffixes=("_review", "_product"),
    )

    dataset["target_recommended"] = dataset.apply(createTargetLabel, axis=1)

    dataset = dataset.dropna(subset=["target_recommended"])
    dataset["target_recommended"] = dataset["target_recommended"].astype(int)

    textColumns = [
        "product_name_review",
        "product_name_product",
        "brand_name_review",
        "brand_name_product",
        "review_title",
        "review_text",
        "skin_type",
        "skin_tone",
        "ingredients",
        "highlights",
        "primary_category",
        "secondary_category",
        "tertiary_category",
    ]

    for column in textColumns:
        if column not in dataset.columns:
            dataset[column] = ""

        dataset[column] = dataset[column].apply(cleanText)

    dataset["product_name"] = dataset["product_name_product"]

    dataset.loc[
        dataset["product_name"] == "",
        "product_name",
    ] = dataset["product_name_review"]

    dataset["brand_name"] = dataset["brand_name_product"]

    dataset.loc[
        dataset["brand_name"] == "",
        "brand_name",
    ] = dataset["brand_name_review"]

    dataset["combined_text"] = (
        dataset["product_name"]
        + " "
        + dataset["brand_name"]
        + " "
        + dataset["primary_category"]
        + " "
        + dataset["secondary_category"]
        + " "
        + dataset["tertiary_category"]
        + " "
        + dataset["highlights"]
        + " "
        + dataset["ingredients"]
        + " "
        + dataset["review_title"]
        + " "
        + dataset["review_text"]
        + " skin type "
        + dataset["skin_type"]
        + " skin tone "
        + dataset["skin_tone"]
    )

    finalColumns = [
        "product_id",
        "product_name",
        "brand_name",
        "price_usd_review",
        "price_usd_product",
        "rating_review",
        "rating_product",
        "is_recommended",
        "target_recommended",
        "skin_type",
        "skin_tone",
        "review_title",
        "review_text",
        "ingredients",
        "highlights",
        "primary_category",
        "secondary_category",
        "tertiary_category",
        "combined_text",
    ]

    availableFinalColumns = [
        column for column in finalColumns if column in dataset.columns
    ]

    dataset = dataset[availableFinalColumns].copy()

    dataset = dataset.dropna(subset=["combined_text"])
    dataset = dataset[dataset["combined_text"].str.strip() != ""]

    return dataset

def main() -> None:
    dataset = prepareDataset()

    SEPHORA_PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(SEPHORA_PROCESSED_PATH, index=False)

    print()
    print("Saved cleaned Sephora ML dataset")
    print(f"Path: {SEPHORA_PROCESSED_PATH}")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")
    print("Target distribution:")
    print(dataset["target_recommended"].value_counts())
    print("Skin type distribution:")
    print(dataset["skin_type"].value_counts(dropna=False).head(10))
    print("Skin tone distribution:")
    print(dataset["skin_tone"].value_counts(dropna=False).head(10))

if __name__ == "__main__":
    main()