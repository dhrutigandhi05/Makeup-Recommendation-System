import json
import sys
from pathlib import Path
import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

sys.path.append(str(BACKEND_DIR))

from app.config import (PROFILE_SUITABILITY_METRICS_PATH, PROFILE_SUITABILITY_MODEL_PATH)
from app.database import engine

def loadTrainingData() -> pd.DataFrame:
    query = """
        SELECT
            training_text,
            target_suitable,
            review_count,
            average_rating,
            recommendation_rate
        FROM product_profile_suitability
        WHERE training_text IS NOT NULL
          AND TRIM(training_text) <> ''
          AND target_suitable IS NOT NULL;
    """

    dataset = pd.read_sql(query, engine)
    dataset["training_text"] = dataset["training_text"].fillna("").astype(str)
    dataset["target_suitable"] = dataset["target_suitable"].astype(int)

    return dataset

def trainModel(dataset: pd.DataFrame):
    x = dataset["training_text"]
    y = dataset["target_suitable"]

    xTrain, xTest, yTrain, yTest = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    baseClassifier = LinearSVC(
        class_weight="balanced",
        random_state=42,
    )

    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    max_features=30000,
                    ngram_range=(1, 2),
                    min_df=2,
                ),
            ),
            (
                "classifier",
                CalibratedClassifierCV(
                    estimator=baseClassifier,
                    method="sigmoid",
                    cv=3,
                ),
            ),
        ]
    )

    model.fit(xTrain, yTrain)
    predictions = model.predict(xTest)
    probabilities = model.predict_proba(xTest)[:, 1]

    metrics = {
        "rows": int(len(dataset)),
        "train_rows": int(len(xTrain)),
        "test_rows": int(len(xTest)),
        "accuracy": float(accuracy_score(yTest, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(yTest, predictions)),
        "f1_score": float(f1_score(yTest, predictions)),
        "roc_auc": float(roc_auc_score(yTest, probabilities)),
        "confusion_matrix": confusion_matrix(yTest, predictions).tolist(),
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
    PROFILE_SUITABILITY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_SUITABILITY_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, PROFILE_SUITABILITY_MODEL_PATH)

    with open(PROFILE_SUITABILITY_METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    print(f"Saved model to: {PROFILE_SUITABILITY_MODEL_PATH}")
    print(f"Saved metrics to: {PROFILE_SUITABILITY_METRICS_PATH}")

def main() -> None:
    print("Loading product-profile suitability data from Postgres...")
    dataset = loadTrainingData()

    if dataset.empty:
        raise ValueError("No training data found in product_profile_suitability.")

    print(f"Loaded rows: {len(dataset)}")
    print("Target distribution:")
    print(dataset["target_suitable"].value_counts())
    print("Training TF-IDF + calibrated LinearSVC model...")
    model, metrics = trainModel(dataset)
    print("Model performance:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Balanced accuracy: {metrics['balanced_accuracy']:.4f}")
    print(f"F1 score: {metrics['f1_score']:.4f}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print("Confusion matrix:")
    print(metrics["confusion_matrix"])

    saveArtifacts(model, metrics)

if __name__ == "__main__":
    main()