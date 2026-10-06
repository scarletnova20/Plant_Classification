"""Predict a plant class from one image with the saved PyTorch model."""

import argparse
import json
from pathlib import Path

import torch
from PIL import Image

from train import PlantCNN, build_eval_transform, load_checkpoint


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"Image not found: {args.image}")

    model_path = ROOT / "models" / "plant_classifier.pth"
    names_path = ROOT / "models" / "class_names.json"
    if not model_path.is_file() or not names_path.is_file():
        raise SystemExit("Trained model or class mapping missing. Run train.py first.")

    class_names = json.loads(names_path.read_text(encoding="utf-8"))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = load_checkpoint(model_path, device)
    if checkpoint.get("class_names") != class_names:
        raise SystemExit("Checkpoint class mapping differs from class_names.json.")

    try:
        with Image.open(args.image) as image:
            image_tensor = build_eval_transform()(image.convert("RGB")).unsqueeze(0)
    except Exception as error:
        raise SystemExit(f"Cannot open image: {error}") from error

    model = PlantCNN(len(class_names)).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    with torch.no_grad():
        logits = model(image_tensor.to(device))
        probabilities = torch.softmax(logits, dim=1)[0].cpu()

    index = int(probabilities.argmax().item())
    folder_name = class_names[index]
    display_name = folder_name.split("_", 2)[-1].replace("_", " ")
    print(f"Predicted class: {display_name} ({folder_name})")
    print(f"Confidence: {probabilities[index].item() * 100:.1f}%")
    print("This baseline was trained on a small source-linked dataset; confidence is not calibrated.")


if __name__ == "__main__":
    main()
