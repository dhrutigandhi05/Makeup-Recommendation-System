import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(ROOT_DIR / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

PRODUCT_DATA_PATH = ROOT_DIR / os.getenv(
    "PRODUCT_DATA_PATH",
    "data/processed/makeup_products.csv",
)

SEPHORA_PROCESSED_PATH = ROOT_DIR / os.getenv(
    "SEPHORA_PROCESSED_PATH",
    "data/processed/sephoraMlDataset.csv",
)

RECOMMENDER_RULES_PATH = ROOT_DIR / os.getenv(
    "RECOMMENDER_RULES_PATH",
    "config/recommenderRules.json",
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing")