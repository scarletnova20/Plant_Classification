"""Evaluate a saved model on its held-out split."""

import json

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from tensorflow import keras

from train import ROOT, image_arrays, load_dataset


def main():
    models_dir = ROOT / "models"
    model_path = models_dir / "plant_classifier.keras"
    names_path = models_dir / "class_names.json"
    split_path = models_dir / "split.json"
    for path in (model_path, names_path, split_path):
        if not path.is_file():
            raise SystemExit(f"Missing {path}. Train the model first.")

    class_names = json.loads(names_path.read_text(encoding="utf-8"))
    split = json.loads(split_path.read_text(encoding="utf-8"))
    rows, detected_names = load_dataset()
    if class_names != detected_names:
        raise SystemExit("Dataset class folders changed since training; retrain the model.")

    subset_name = "test" if split["test"] else "validation"
    paths = set(split[subset_name])
    held_out = [row for row in rows if row["dataset_path"] in paths]
    if len(held_out) != len(paths):
        raise SystemExit("Saved split contains missing images; retrain or restore the dataset.")
    if subset_name == "validation":
        print("DIAGNOSTIC VALIDATION ONLY — no independent test set is available.")
        print("These results do not estimate real-world generalization.")
    else:
        print("Held-out collection-group test results on this dataset.")

    images, labels = image_arrays(held_out, class_names)
    model = keras.models.load_model(model_path)
    loss, accuracy = model.evaluate(images, labels, verbose=0)
    predictions = np.argmax(model.predict(images, verbose=0), axis=1)
    print(f"{subset_name.title()} loss: {loss:.4f}")
    print(f"{subset_name.title()} accuracy: {accuracy:.4f}")
    report = classification_report(labels, predictions, labels=range(len(class_names)),
                                   target_names=class_names, zero_division=0)
    print(report)

    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / "classification_report.txt").write_text(
        f"Split: {subset_name}; mode: {split['mode']}\n"
        "Baseline results on this dataset; not a real-world performance estimate.\n\n"
        f"Loss: {loss:.4f}\nAccuracy: {accuracy:.4f}\n\n{report}", encoding="utf-8")
    matrix = confusion_matrix(labels, predictions, labels=range(len(class_names)))
    figure, axis = plt.subplots(figsize=(9, 8))
    ConfusionMatrixDisplay(matrix, display_labels=class_names).plot(
        ax=axis, xticks_rotation=45, colorbar=False)
    figure.tight_layout()
    figure.savefig(results_dir / "confusion_matrix.png")
    plt.close(figure)
    print(f"Report and confusion matrix saved in {results_dir}")


if __name__ == "__main__":
    main()
