"""Small PyTorch CNN baseline for the source-linked plant dataset."""

import argparse
import csv
import json
import os
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms


ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "Plant_Dataset"
MANIFEST = ROOT / "dataset_manifest.csv"
IMAGE_SIZE = (128, 128)
SEED = 42
VALIDATION_FRACTION = 0.20
BATCH_SIZE = 8
LEARNING_RATE = 0.001
EARLY_STOPPING_PATIENCE = 5


def load_dataset():
    """Read active class folders and their matching manifest rows."""
    if not DATASET.is_dir():
        raise ValueError(f"Dataset folder not found: {DATASET}")
    if not MANIFEST.is_file():
        raise ValueError(f"Manifest not found: {MANIFEST}")

    class_names = sorted(folder.name for folder in DATASET.iterdir() if folder.is_dir())
    if len(class_names) < 2:
        raise ValueError("At least two class folders are required.")

    with MANIFEST.open(newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    active = []
    for row in rows:
        if row["status"] in {"Rejected", "Review"}:
            continue
        path = (ROOT / row["dataset_path"]).resolve()
        if not path.is_relative_to(DATASET.resolve()):
            continue
        if not path.is_file():
            raise ValueError(f"Missing image: {path}")
        if path.parent.parent.name not in class_names:
            raise ValueError(f"Image has no matching class folder: {path}")
        if not row["source_group"] or not row["collection_group"]:
            raise ValueError(f"Missing group metadata for {row['image_id']}")
        try:
            with Image.open(path) as image:
                image.verify()
        except Exception as error:
            raise ValueError(f"Cannot read image {path}: {error}") from error
        row["path"] = str(path)
        row["folder"] = path.parent.parent.name
        active.append(row)

    if not active:
        raise ValueError("No active images found in Plant_Dataset.")
    folder_images = {
        path.resolve()
        for path in DATASET.rglob("*")
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    }
    manifest_images = {Path(row["path"]) for row in active}
    if folder_images != manifest_images:
        raise ValueError("Dataset images and manifest differ. Add or correct manifest rows first.")
    if len({row["image_id"] for row in active}) != len(active):
        raise ValueError("Duplicate image IDs in manifest.")

    counts = Counter(row["folder"] for row in active)
    for name in class_names:
        if counts[name] < 2:
            raise ValueError(f"Class {name} has fewer than two images.")

    source_to_collection = defaultdict(set)
    for row in active:
        source_to_collection[row["source_group"]].add(row["collection_group"])
    if any(len(groups) != 1 for groups in source_to_collection.values()):
        raise ValueError("A source group has conflicting collection groups.")

    return active, class_names


def print_dataset_summary(rows, class_names):
    print(f"Classes detected: {len(class_names)}")
    print(f"Total images: {len(rows)}")
    print("Class distribution:")
    for name in class_names:
        subset = [row for row in rows if row["folder"] == name]
        original = sum(row["type"] == "Original" for row in subset)
        synthetic = len(subset) - original
        collections = len({row["collection_group"] for row in subset})
        print(
            f"  {name}: {len(subset)} ({original} original, {synthetic} synthetic; "
            f"{collections} collection group)"
        )
    signed = [row for row in rows if "VISIBLE_SIGN" in row["qc_note"]]
    print(f"Original images flagged for readable signs: {len(signed)}")
    for row in signed:
        print(f"  {row['image_id']}")


def source_group_80_20_split(by_class, rng):
    """Find a class-stratified split close to 80/20 without separating sources."""
    options_by_class = {}
    for name, subset in by_class.items():
        groups = defaultdict(list)
        for row in subset:
            groups[row["source_group"]].append(row)
        keys = sorted(groups)
        rng.shuffle(keys)
        if len(keys) < 2:
            raise ValueError(f"Class {name} needs at least two source groups for a diagnostic split.")

        options = {0: ()}
        for key in keys:
            size = len(groups[key])
            for count, selected in list(options.items())[::-1]:
                options.setdefault(count + size, selected + (key,))
        total = len(subset)
        options_by_class[name] = {
            count: selected for count, selected in options.items() if 0 < count < total
        }

    plans = {0: (0.0, {})}
    for name in by_class:
        class_total = len(by_class[name])
        next_plans = {}
        for running_total, (penalty, selections) in plans.items():
            for count, selected in options_by_class[name].items():
                new_total = running_total + count
                new_penalty = penalty + ((count / class_total) - VALIDATION_FRACTION) ** 2
                current = next_plans.get(new_total)
                if current is None or new_penalty < current[0]:
                    next_plans[new_total] = (
                        new_penalty,
                        {**selections, name: set(selected)},
                    )
        plans = next_plans

    target = round(sum(map(len, by_class.values())) * VALIDATION_FRACTION)
    chosen_total = min(plans, key=lambda total: (abs(total - target), plans[total][0]))
    validation_groups = plans[chosen_total][1]
    train_rows, val_rows = [], []
    for name, subset in by_class.items():
        held_out = validation_groups[name]
        for row in subset:
            (val_rows if row["source_group"] in held_out else train_rows).append(row)
    return train_rows, val_rows


def make_split(rows, class_names, allow_diagnostic):
    """Prefer independent collections; otherwise use a labeled source-group holdout."""
    usable = [row for row in rows if "VISIBLE_SIGN" not in row["qc_note"]]
    print(f"Training-eligible images after sign exclusion: {len(usable)}")
    by_class = {
        name: [row for row in usable if row["folder"] == name] for name in class_names
    }
    independent = all(
        len({row["collection_group"] for row in subset}) >= 3
        for subset in by_class.values()
    )

    if not independent and not allow_diagnostic:
        raise ValueError(
            "Independent train/validation/test groups are unavailable. "
            "Each current class has only one collection group. Add independent plant "
            "photos, or run 'py train.py --diagnostic' for a source-group holdout "
            "that does not estimate real-world performance."
        )

    rng = random.Random(SEED)
    train_rows, val_rows, test_rows = [], [], []
    if independent:
        for name, subset in by_class.items():
            groups = defaultdict(list)
            for row in subset:
                groups[row["collection_group"]].append(row)
            keys = sorted(groups)
            rng.shuffle(keys)
            val_key, test_key = keys[:2]
            for key in keys:
                target = (
                    val_rows
                    if key == val_key
                    else test_rows
                    if key == test_key
                    else train_rows
                )
                target.extend(groups[key])
    else:
        train_rows, val_rows = source_group_80_20_split(by_class, rng)

    mode = (
        "independent_collection_split"
        if independent
        else "diagnostic_source_group_80_20"
    )
    print(
        f"Split: {mode}; train={len(train_rows)}, validation={len(val_rows)}, "
        f"test={len(test_rows)}"
    )
    if not independent:
        total = len(train_rows) + len(val_rows)
        print(
            f"Diagnostic ratio: training={len(train_rows) / total:.1%}, "
            f"validation={len(val_rows) / total:.1%}"
        )
        print(
            "LIMITATION: These photos lack independent collection groups. "
            "Validation is diagnostic only; no trustworthy test accuracy is available."
        )
    return train_rows, val_rows, test_rows, mode


def build_train_transform():
    """Return stochastic augmentation followed by conversion to a float tensor."""
    return transforms.Compose(
        [
            transforms.Resize(IMAGE_SIZE),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(degrees=18),
            transforms.RandomAffine(
                degrees=0,
                translate=(0.08, 0.08),
                scale=(0.90, 1.10),
            ),
            transforms.ToTensor(),
        ]
    )


def build_eval_transform():
    """Return deterministic preprocessing for validation and prediction."""
    return transforms.Compose([transforms.Resize(IMAGE_SIZE), transforms.ToTensor()])


class PlantImageDataset(Dataset):
    """Load manifest rows as RGB image tensors and integer class labels."""

    def __init__(self, rows, class_names, transform):
        self.rows = list(rows)
        self.class_index = {name: index for index, name in enumerate(class_names)}
        self.transform = transform

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        with Image.open(row["path"]) as image:
            image = image.convert("RGB")
            tensor = self.transform(image)
        return tensor, self.class_index[row["folder"]]


class PlantCNN(nn.Module):
    """CNN matching the original three-convolution baseline."""

    def __init__(self, num_classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(8, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 16 * 16, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, num_classes),
        )

    def forward(self, images):
        return self.classifier(self.features(images))


def set_reproducible_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


def build_loader(rows, class_names, training):
    dataset = PlantImageDataset(
        rows,
        class_names,
        build_train_transform() if training else build_eval_transform(),
    )
    generator = torch.Generator().manual_seed(SEED)
    return DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=training,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
        generator=generator,
    )


def run_epoch(model, loader, criterion, device, optimizer=None):
    """Run one training or evaluation epoch and return loss and accuracy."""
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    total_correct = 0
    total_images = 0

    context = torch.enable_grad() if training else torch.no_grad()
    with context:
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            if training:
                optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, labels)
            if training:
                loss.backward()
                optimizer.step()

            batch_size = labels.size(0)
            total_loss += loss.item() * batch_size
            total_correct += (logits.argmax(dim=1) == labels).sum().item()
            total_images += batch_size

    return total_loss / total_images, total_correct / total_images


def save_checkpoint(path, model, class_names, epoch, val_loss, val_accuracy):
    state = {name: tensor.detach().cpu() for name, tensor in model.state_dict().items()}
    torch.save(
        {
            "framework": "pytorch",
            "torch_version": str(torch.__version__),
            "architecture": "PlantCNN",
            "model_state_dict": state,
            "class_names": list(class_names),
            "num_classes": len(class_names),
            "image_size": list(IMAGE_SIZE),
            "seed": SEED,
            "epoch": epoch,
            "validation_loss": val_loss,
            "validation_accuracy": val_accuracy,
        },
        path,
    )


def load_checkpoint(path, device):
    """Load the portable state-dictionary checkpoint."""
    return torch.load(path, map_location=device, weights_only=True)


def train_model(train_rows, val_rows, test_rows, mode, class_names, epochs):
    import matplotlib.pyplot as plt

    set_reproducible_seed()
    torch.set_num_threads(max(1, min(8, os.cpu_count() or 1)))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Training device: {device}")

    train_loader = build_loader(train_rows, class_names, training=True)
    val_loader = build_loader(val_rows, class_names, training=False)
    model = PlantCNN(len(class_names)).to(device)
    trainable = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    print(model)
    print(f"Trainable parameters: {trainable:,}")

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    models_dir = ROOT / "models"
    results_dir = ROOT / "results"
    models_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)
    model_path = models_dir / "plant_classifier.pth"

    (models_dir / "class_names.json").write_text(
        json.dumps(class_names, indent=2), encoding="utf-8"
    )
    split = {
        "framework": "pytorch",
        "mode": mode,
        "seed": SEED,
        "image_size": list(IMAGE_SIZE),
        "excluded_signed_originals": True,
        "requested_validation_fraction": (
            VALIDATION_FRACTION if mode == "diagnostic_source_group_80_20" else None
        ),
        "actual_validation_fraction": len(val_rows) / (len(train_rows) + len(val_rows)),
        "train": [row["dataset_path"] for row in train_rows],
        "validation": [row["dataset_path"] for row in val_rows],
        "test": [row["dataset_path"] for row in test_rows],
    }
    (models_dir / "split.json").write_text(json.dumps(split, indent=2), encoding="utf-8")

    history = {"loss": [], "accuracy": [], "val_loss": [], "val_accuracy": []}
    best_loss = float("inf")
    stale_epochs = 0
    best_epoch = 0

    for epoch in range(1, epochs + 1):
        train_loss, train_accuracy = run_epoch(
            model, train_loader, criterion, device, optimizer
        )
        val_loss, val_accuracy = run_epoch(model, val_loader, criterion, device)
        history["loss"].append(train_loss)
        history["accuracy"].append(train_accuracy)
        history["val_loss"].append(val_loss)
        history["val_accuracy"].append(val_accuracy)
        print(
            f"Epoch {epoch}/{epochs} - loss: {train_loss:.4f} - "
            f"accuracy: {train_accuracy:.4f} - val_loss: {val_loss:.4f} - "
            f"val_accuracy: {val_accuracy:.4f}"
        )

        if val_loss < best_loss - 1e-6:
            best_loss = val_loss
            best_epoch = epoch
            stale_epochs = 0
            save_checkpoint(
                model_path, model, class_names, epoch, val_loss, val_accuracy
            )
        else:
            stale_epochs += 1
            if stale_epochs >= EARLY_STOPPING_PATIENCE:
                print(
                    f"Early stopping after {epoch} epochs; "
                    f"best checkpoint is epoch {best_epoch}."
                )
                break

    for metric in ("accuracy", "loss"):
        plt.figure()
        plt.plot(history[metric], label="Training")
        plt.plot(history[f"val_{metric}"], label="Validation")
        plt.xlabel("Epoch")
        plt.ylabel(metric.title())
        plt.legend()
        plt.tight_layout()
        plt.savefig(results_dir / f"{metric}.png")
        plt.close()

    print(f"Best PyTorch model saved: {model_path}")
    print(f"Best epoch: {best_epoch}; validation loss: {best_loss:.4f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-data", action="store_true", help="Check images without training")
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Allow a source-group 80/20 split despite collection-site overlap",
    )
    parser.add_argument("--epochs", type=int, default=25)
    args = parser.parse_args()
    if args.epochs < 1:
        parser.error("--epochs must be positive")

    try:
        rows, class_names = load_dataset()
        print_dataset_summary(rows, class_names)
        if args.check_data:
            print("All active images opened successfully.")
            return
        train_rows, val_rows, test_rows, mode = make_split(
            rows, class_names, args.diagnostic
        )
    except ValueError as error:
        parser.exit(1, f"Dataset error: {error}\n")
    train_model(train_rows, val_rows, test_rows, mode, class_names, args.epochs)


if __name__ == "__main__":
    main()
