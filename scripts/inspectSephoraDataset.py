from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
SEPHORA_RAW_DIR = ROOT_DIR / "data" / "raw" / "sephora"

def inspect_csv(file_path: Path) -> None:
    print("=" * 80)
    print(f"File: {file_path.name}")

    try:
        df = pd.read_csv(file_path, nrows=5)
    except Exception as error:
        print(f"Could not read file: {error}")
        return

    print(f"Columns ({len(df.columns)}):")
    for column in df.columns:
        print(f"  - {column}")

    print("\nPreview:")
    print(df.head())

def main() -> None:
    if not SEPHORA_RAW_DIR.exists():
        raise FileNotFoundError(f"Sephora raw data folder not found: {SEPHORA_RAW_DIR}")

    csv_files = sorted(SEPHORA_RAW_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {SEPHORA_RAW_DIR}.")

    print(f"Found {len(csv_files)} CSV file(s) in {SEPHORA_RAW_DIR}")

    for csv_file in csv_files:
        inspect_csv(csv_file)

if __name__ == "__main__":
    main()