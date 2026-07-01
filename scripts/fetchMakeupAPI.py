import json
import os
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

MAKEUP_API_URL = os.getenv("MAKEUP_API_URL")
RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data/raw")
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "data/processed")

if not MAKEUP_API_URL:
    raise ValueError("MAKEUP_API_URL is missing. Add it to your .env file.")

RAW_DATA_PATH = ROOT_DIR / RAW_DATA_DIR / "makeup_api_products.json"
PROCESSED_DATA_PATH = ROOT_DIR / PROCESSED_DATA_DIR / "makeup_products.csv"

def fetch_products() -> list[dict]:
    response = requests.get(MAKEUP_API_URL, timeout=30)
    response.raise_for_status()
    return response.json()

def clean_price(price):
    if price in [None, ""]:
        return None

    try:
        return float(price)
    except ValueError:
        return None

def clean_products(products: list[dict]) -> pd.DataFrame:
    rows = []

    for product in products:
        rows.append(
            {
                "id": product.get("id"),
                "brand": product.get("brand"),
                "name": product.get("name"),
                "price": clean_price(product.get("price")),
                "currency": product.get("currency"),
                "image_link": product.get("image_link"),
                "product_link": product.get("product_link"),
                "website_link": product.get("website_link"),
                "description": product.get("description"),
                "rating": product.get("rating"),
                "category": product.get("category"),
                "product_type": product.get("product_type"),
                "tag_list": ", ".join(product.get("tag_list", [])),
            }
        )

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["name", "product_type"])
    df = df.drop_duplicates(subset=["id"])

    return df

def main():
    print("Fetching products from Makeup API...")

    products = fetch_products()

    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(RAW_DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(products, file, indent=2)

    df = clean_products(products)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"Fetched {len(products)} raw products.")
    print(f"Saved raw data to: {RAW_DATA_PATH}")
    print(f"Saved cleaned data to: {PROCESSED_DATA_PATH}")
    print("Product type counts:")
    print(df["product_type"].value_counts())

if __name__ == "__main__":
    main()