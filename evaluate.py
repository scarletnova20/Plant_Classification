"""Evaluate the saved PyTorch model on its held-out split."""

import json
import textwrap

import matplotlib.pyplot as plt
import torch
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader

from train import (
    BATCH_SIZE,
    ROOT,
    PlantCNN,
    PlantImageDataset,
    build_eval_transform,
    load_checkpoint,
    load_dataset,
)


def main():
    models_dir = ROOT / "models"
    model_path = models_dir / "plant_classifier.pth"
    names_path = models_dir / "class_names.json"
    split_path = models_dir / "split.json"
    for path in (model_path, names_path, split_path):
        if not path.is_file():
            raise SystemExit(f"Missing {path}. Train the PyTorch model first.")

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
        print("DIAGNOSTIC VALIDATION ONLY - no independent test set is available.")
        print("These results do not estimate real-world generalization.")
    else:
        print("Held-out collection-group test results on this dataset.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = load_checkpoint(model_path, device)
    if checkpoint.get("framework") != "pytorch":
        raise SystemExit("The checkpoint is not a supported PyTorch checkpoint.")
    if checkpoint.get("class_names") != class_names:
        raise SystemExit("Checkpoint class mapping differs from class_names.json.")
    if checkpoint.get("num_classes") != len(class_names):
        raise SystemExit("Checkpoint output size differs from the dataset classes.")

    dataset = PlantImageDataset(held_out, class_names, build_eval_transform())
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    model = PlantCNN(len(class_names)).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0
    labels = []
    predictions = []
    with torch.no_grad():
        for images, batch_labels in loader:
            images = images.to(device)
            batch_labels = batch_labels.to(device)
            logits = model(images)
            total_loss += criterion(logits, batch_labels).item() * batch_labels.size(0)
            labels.extend(batch_labels.cpu().tolist())
            predictions.extend(logits.argmax(dim=1).cpu().tolist())

    loss = total_loss / len(dataset)
    correct = sum(prediction == label for prediction, label in zip(predictions, labels))
    accuracy = correct / len(dataset)
    print(f"Evaluation device: {device}")
    print(f"Checkpoint epoch: {checkpoint['epoch']}")
    print(f"{subset_name.title()} loss: {loss:.4f}")
    print(f"{subset_name.title()} accuracy: {accuracy:.4f} ({correct}/{len(dataset)})")
    report = classification_report(
        labels,
        predictions,
        labels=range(len(class_names)),
        target_names=class_names,
        zero_division=0,
    )
    print(report)

    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / "classification_report.txt").write_text(
        f"Framework: PyTorch\nSplit: {subset_name}; mode: {split['mode']}\n"
        "Baseline results on this dataset; not a real-world performance estimate.\n\n"
        f"Checkpoint epoch: {checkpoint['epoch']}\n"
        f"Loss: {loss:.4f}\nAccuracy: {accuracy:.4f} ({correct}/{len(dataset)})\n\n"
        f"{report}",
        encoding="utf-8",
    )
    matrix = confusion_matrix(labels, predictions, labels=range(len(class_names)))
    display_names = [
        "\n".join(textwrap.wrap(name.split("_", 2)[-1].replace("_", " "), 18))
        for name in class_names
    ]
    figure, axis = plt.subplots(figsize=(13, 11))
    ConfusionMatrixDisplay(matrix, display_labels=display_names).plot(
        ax=axis, xticks_rotation=45, colorbar=False, values_format="d"
    )
    axis.tick_params(axis="both", labelsize=8)
    figure.tight_layout()
    figure.savefig(results_dir / "confusion_matrix.png", dpi=150)
    plt.close(figure)
    print(f"Report and confusion matrix saved in {results_dir}")


if __name__ == "__main__":
    main()
