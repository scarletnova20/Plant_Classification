"""Small CNN baseline for the source-linked plant dataset."""

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "Plant_Dataset"
MANIFEST = ROOT / "dataset_manifest.csv"
IMAGE_SIZE = (128, 128)
SEED = 42
VALIDATION_FRACTION = 0.20


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
    folder_images = {path.resolve() for path in DATASET.rglob("*")
                     if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}}
    manifest_images = {Path(row["path"]) for row in active}
    if folder_images != manifest_images:
        raise ValueError("Dataset images and manifest differ. Add or correct manifest rows first.")
    if len({row["image_id"] for row in active}) != len(active):
        raise ValueError("Duplicate image IDs in manifest.")
    counts = Counter(row["folder"] for row in active)
    for name in class_names:
        if counts[name] < 2:
            raise ValueError(f"Class {name} has fewer than two images.")

    # A source must never be assigned to different collection groups.
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
        print(f"  {name}: {len(subset)} ({original} original, {synthetic} synthetic; "
              f"{collections} collection group)")
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

        # Keep one reproducible group selection for every attainable image count.
        options = {0: ()}
        for key in keys:
            size = len(groups[key])
            for count, selected in list(options.items())[::-1]:
                options.setdefault(count + size, selected + (key,))
        total = len(subset)
        options_by_class[name] = {
            count: selected for count, selected in options.items()
            if 0 < count < total
        }

    # Select one attainable holdout size per class. The first objective is an
    # overall 20% holdout; the second keeps individual class ratios near 20%.
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
    """Prefer independent collection groups; otherwise use a labeled diagnostic holdout."""
    usable = [row for row in rows if "VISIBLE_SIGN" not in row["qc_note"]]
    print(f"Training-eligible images after sign exclusion: {len(usable)}")
    by_class = {name: [row for row in usable if row["folder"] == name]
                for name in class_names}
    independent = all(len({row["collection_group"] for row in subset}) >= 3
                      for subset in by_class.values())

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
                target = val_rows if key == val_key else test_rows if key == test_key else train_rows
                target.extend(groups[key])
    else:
        train_rows, val_rows = source_group_80_20_split(by_class, rng)

    mode = "independent_collection_split" if independent else "diagnostic_source_group_80_20"
    print(f"Split: {mode}; train={len(train_rows)}, validation={len(val_rows)}, "
          f"test={len(test_rows)}")
    if not independent:
        total = len(train_rows) + len(val_rows)
        print(f"Diagnostic ratio: training={len(train_rows) / total:.1%}, "
              f"validation={len(val_rows) / total:.1%}")
        print("LIMITATION: These photos lack independent collection groups. "
              "Validation is diagnostic only; no trustworthy test accuracy is available.")
    return train_rows, val_rows, test_rows, mode


def image_arrays(rows, class_names):
    import numpy as np

    class_index = {name: index for index, name in enumerate(class_names)}
    images, labels = [], []
    for row in rows:
        with Image.open(row["path"]) as image:
            image = image.convert("RGB").resize(IMAGE_SIZE)
            images.append(np.asarray(image, dtype=np.float32) / 255.0)
        labels.append(class_index[row["folder"]])
    return np.stack(images), np.asarray(labels, dtype=np.int32)


def build_model(num_classes):
    from tensorflow import keras

    model = keras.Sequential([
        keras.Input(shape=(128, 128, 3)),
        # Keras applies these random changes during training, not evaluation.
        keras.layers.RandomFlip("horizontal"),
        keras.layers.RandomRotation(0.05),
        keras.layers.RandomZoom(0.10),
        keras.layers.RandomTranslation(0.08, 0.08),
        keras.layers.Conv2D(8, 3, activation="relu", padding="same"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(16, 3, activation="relu", padding="same"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(32, activation="relu"),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(num_classes, activation="softmax"),
    ])
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def train_model(train_rows, val_rows, test_rows, mode, class_names, epochs):
    import matplotlib.pyplot as plt
    import tensorflow as tf

    tf.keras.utils.set_random_seed(SEED)
    print(f"GPU devices: {tf.config.list_physical_devices('GPU')}")
    train_images, train_labels = image_arrays(train_rows, class_names)
    val_images, val_labels = image_arrays(val_rows, class_names)
    model = build_model(len(class_names))
    model.summary()

    models_dir = ROOT / "models"
    results_dir = ROOT / "results"
    models_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)
    model_path = models_dir / "plant_classifier.keras"
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5,
                                         restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(model_path, monitor="val_loss",
                                           save_best_only=True),
    ]
    history = model.fit(train_images, train_labels, validation_data=(val_images, val_labels),
                        epochs=epochs, batch_size=8, callbacks=callbacks, verbose=2)

    (models_dir / "class_names.json").write_text(
        json.dumps(class_names, indent=2), encoding="utf-8")
    split = {"mode": mode, "seed": SEED, "image_size": list(IMAGE_SIZE),
             "excluded_signed_originals": True,
             "requested_validation_fraction": (
                 VALIDATION_FRACTION if mode == "diagnostic_source_group_80_20" else None
             ),
             "actual_validation_fraction": len(val_rows) / (len(train_rows) + len(val_rows)),
             "train": [row["dataset_path"] for row in train_rows],
             "validation": [row["dataset_path"] for row in val_rows],
             "test": [row["dataset_path"] for row in test_rows]}
    (models_dir / "split.json").write_text(json.dumps(split, indent=2), encoding="utf-8")

    for metric in ("accuracy", "loss"):
        plt.figure()
        plt.plot(history.history[metric], label="Training")
        plt.plot(history.history[f"val_{metric}"], label="Validation")
        plt.xlabel("Epoch")
        plt.ylabel(metric.title())
        plt.legend()
        plt.tight_layout()
        plt.savefig(results_dir / f"{metric}.png")
        plt.close()
    print(f"Best model saved: {model_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-data", action="store_true", help="Check images without TensorFlow")
    parser.add_argument("--diagnostic", action="store_true",
                        help="Allow a source-group 80/20 split despite collection-site overlap")
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
        train_rows, val_rows, test_rows, mode = make_split(rows, class_names, args.diagnostic)
    except ValueError as error:
        parser.exit(1, f"Dataset error: {error}\n")
    train_model(train_rows, val_rows, test_rows, mode, class_names, args.epochs)


if __name__ == "__main__":
    main()
