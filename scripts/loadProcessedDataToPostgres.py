import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

sys.path.append(str(BACKEND_DIR))

from app.config import PRODUCT_DATA_PATH, SEPHORA_PROCESSED_PATH
from app.database import Base, engine
from app.dbModels import Product, ProductReview

def cleanFrame(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.where(pd.notna(frame), None)

def getColumn(frame: pd.DataFrame, columnName: str, defaultValue=None):
    if columnName in frame.columns:
        return frame[columnName]

    return defaultValue

def loadMakeupProducts() -> pd.DataFrame:
    if not PRODUCT_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing Makeup API processed file: {PRODUCT_DATA_PATH}"
        )

    makeup = pd.read_csv(PRODUCT_DATA_PATH)

    products = pd.DataFrame(
        {
            "source": "makeupApi",
            "source_product_id": makeup["id"].astype(str),
            "product_name": makeup["name"],
            "brand_name": makeup.get("brand"),
            "price": pd.to_numeric(makeup.get("price"), errors="coerce"),
            "currency": makeup.get("currency"),
            "image_link": makeup.get("image_link"),
            "product_url": makeup.get("product_link"),
            "website_url": makeup.get("website_link"),
            "description": makeup.get("description"),
            "ingredients": None,
            "highlights": None,
            "tags": makeup.get("tag_list"),
            "rating": pd.to_numeric(makeup.get("rating"), errors="coerce"),
            "category": makeup.get("category"),
            "product_type": makeup.get("product_type"),
        }
    )

    products = products.dropna(subset=["product_name"])
    products = cleanFrame(products)

    return products

def loadSephoraProductsAndReviews() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not SEPHORA_PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"Missing Sephora processed file: {SEPHORA_PROCESSED_PATH}"
        )

    sephora = pd.read_csv(SEPHORA_PROCESSED_PATH)
    productRows = sephora.drop_duplicates(subset=["product_id"]).copy()

    if "price_usd_product" in productRows.columns:
        priceColumn = productRows["price_usd_product"]
    elif "price_usd_review" in productRows.columns:
        priceColumn = productRows["price_usd_review"]
    else:
        priceColumn = None

    if "rating_product" in productRows.columns:
        ratingColumn = productRows["rating_product"]
    elif "rating_review" in productRows.columns:
        ratingColumn = productRows["rating_review"]
    else:
        ratingColumn = None

    primaryCategory = getColumn(productRows, "primary_category", "")
    secondaryCategory = getColumn(productRows, "secondary_category", "")
    tertiaryCategory = getColumn(productRows, "tertiary_category", "")

    tags = (
        primaryCategory.fillna("").astype(str)
        + " "
        + secondaryCategory.fillna("").astype(str)
        + " "
        + tertiaryCategory.fillna("").astype(str)
    )

    products = pd.DataFrame(
        {
            "source": "sephora",
            "source_product_id": productRows["product_id"].astype(str),
            "product_name": productRows["product_name"],
            "brand_name": productRows.get("brand_name"),
            "price": pd.to_numeric(priceColumn, errors="coerce")
            if priceColumn is not None
            else None,
            "currency": "USD",
            "image_link": None,
            "product_url": None,
            "website_url": None,
            "description": None,
            "ingredients": productRows.get("ingredients"),
            "highlights": productRows.get("highlights"),
            "tags": tags,
            "rating": pd.to_numeric(ratingColumn, errors="coerce")
            if ratingColumn is not None
            else None,
            "category": productRows.get("primary_category"),
            "product_type": productRows.get("secondary_category"),
        }
    )

    reviews = pd.DataFrame(
        {
            "source": "sephora",
            "source_product_id": sephora["product_id"].astype(str),
            "rating": pd.to_numeric(sephora.get("rating_review"), errors="coerce"),
            "is_recommended": sephora.get("is_recommended"),
            "target_recommended": sephora.get("target_recommended"),
            "skin_type": sephora.get("skin_type"),
            "skin_tone": sephora.get("skin_tone"),
            "review_title": sephora.get("review_title"),
            "review_text": sephora.get("review_text"),
            "combined_text": sephora.get("combined_text"),
        }
    )

    if "is_recommended" in reviews.columns:
        reviews["is_recommended"] = reviews["is_recommended"].apply(
            lambda value: None if pd.isna(value) else bool(int(value))
        )

    products = products.dropna(subset=["product_name"])

    products = cleanFrame(products)
    reviews = cleanFrame(reviews)

    return products, reviews

def resetTables() -> None:
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE product_reviews, products RESTART IDENTITY CASCADE")
        )

def insertFrame(frame: pd.DataFrame, tableName: str) -> None:
    frame.to_sql(
        tableName,
        engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )

def main() -> None:
    resetTables()
    makeupProducts = loadMakeupProducts()
    insertFrame(makeupProducts, Product.__tablename__)
    print(f"Inserted Makeup API products: {len(makeupProducts)}")
    sephoraProducts, sephoraReviews = loadSephoraProductsAndReviews()
    insertFrame(sephoraProducts, Product.__tablename__)
    print(f"Inserted Sephora products: {len(sephoraProducts)}")
    insertFrame(sephoraReviews, ProductReview.__tablename__)
    print(f"Inserted Sephora reviews: {len(sephoraReviews)}")

    with engine.connect() as connection:
        productCount = connection.execute(
            text("SELECT COUNT(*) FROM products")
        ).scalar_one()

        reviewCount = connection.execute(
            text("SELECT COUNT(*) FROM product_reviews")
        ).scalar_one()

    print("Database load complete")
    print(f"Total products: {productCount}")
    print(f"Total reviews: {reviewCount}")

if __name__ == "__main__":
    main()