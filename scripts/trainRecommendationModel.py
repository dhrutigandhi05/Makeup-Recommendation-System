import json
import sys
from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

sys.path.append(str(BACKEND_DIR))

from app.config import ML_METRICS_PATH, ML_MODEL_PATH
from app.database import engine

def loadTrainingData() -> pd.DataFrame:
    query = """
        SELECT
            combined_text,
            target_recommended
        FROM product_reviews
        WHERE combined_text IS NOT NULL
          AND TRIM(combined_text) <> ''
          AND target_recommended IS NOT NULL;
    """

    dataset = pd.read_sql(query, engine)
    dataset["combined_text"] = dataset["combined_text"].fillna("").astype(str)
    dataset["target_recommended"] = dataset["target_recommended"].astype(int)

    return dataset

def trainModel(dataset: pd.DataFrame):
    x = dataset["combined_text"]
    y = dataset["target_recommended"]

    xTrain, xTest, yTrain, yTest = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    max_features=50000,
                    ngram_range=(1, 2),
                    min_df=3,
                ),
            ),
            (
                "classifier",
                LinearSVC(
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    model.fit(xTrain, yTrain)

    predictions = model.predict(xTest)

    metrics = {
        "rows": int(len(dataset)),
        "train_rows": int(len(xTrain)),
        "test_rows": int(len(xTest)),
        "accuracy": float(accuracy_score(yTest, predictions)),
        "f1_score": float(f1_score(yTest, predictions)),
        "classification_report": classification_report(
            yTest,
            predictions,
            output_dict=True,
        ),
        "target_distribution": {
            str(label): int(count)
            for label, count in y.value_counts().to_dict().items()
        },
    }

    return model, metrics

def saveArtifacts(model, metrics: dict) -> None:
    ML_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    ML_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, ML_MODEL_PATH)

    with open(ML_METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    print(f"Saved model to: {ML_MODEL_PATH}")
    print(f"Saved metrics to: {ML_METRICS_PATH}")

def main() -> None:
    print("Loading training data")
    dataset = loadTrainingData()

    if dataset.empty:
        raise ValueError("No training data found in Postgres.")

    print(f"Loaded rows: {len(dataset)}")
    print("Target distribution:")
    print(dataset["target_recommended"].value_counts())
    print("Training TF-IDF + LinearSVC model...")
    model, metrics = trainModel(dataset)
    print("Model performance:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1 score: {metrics['f1_score']:.4f}")
    saveArtifacts(model, metrics)

if __name__ == "__main__":
    main()