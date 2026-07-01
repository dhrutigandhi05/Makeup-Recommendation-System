import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

PRODUCT_DATA_PATH = ROOT_DIR / os.getenv(
    "PRODUCT_DATA_PATH",
    "data/processed/makeup_products.csv",
)

RECOMMENDER_RULES_PATH = ROOT_DIR / os.getenv(
    "RECOMMENDER_RULES_PATH",
    "config/recommenderRules.json",
)