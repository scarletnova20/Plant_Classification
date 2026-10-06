"""Predict a plant class from one image."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from tensorflow import keras


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"Image not found: {args.image}")

    model_path = ROOT / "models" / "plant_classifier.keras"
    names_path = ROOT / "models" / "class_names.json"
    if not model_path.is_file() or not names_path.is_file():
        raise SystemExit("Trained model or class mapping missing. Run train.py first.")

    try:
        with Image.open(args.image) as image:
            image = image.convert("RGB").resize((128, 128))
            pixels = np.asarray(image, dtype=np.float32) / 255.0
    except Exception as error:
        raise SystemExit(f"Cannot open image: {error}") from error

    class_names = json.loads(names_path.read_text(encoding="utf-8"))
    model = keras.models.load_model(model_path)
    probabilities = model.predict(pixels[None, ...], verbose=0)[0]
    index = int(np.argmax(probabilities))
    folder_name = class_names[index]
    display_name = folder_name.split("_", 2)[-1].replace("_", " ")
    print(f"Predicted class: {display_name} ({folder_name})")
    print(f"Confidence: {probabilities[index] * 100:.1f}%")
    print("This baseline was trained on a small source-linked dataset; confidence is not calibrated.")


if __name__ == "__main__":
    main()
