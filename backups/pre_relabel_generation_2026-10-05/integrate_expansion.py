"""Integrate the user-confirmed Google Drive plant groups into Plant_Dataset."""

import csv
import hashlib
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STAGING = ROOT / "data_staging" / "google_drive_dataset"
STAGING_IMAGES = STAGING / "jpeg"
GROUPS_CSV = STAGING / "staging_groups.csv"
DATASET = ROOT / "Plant_Dataset"
MANIFEST = ROOT / "dataset_manifest.csv"

CLASS_MAP = {
    "Drive_Group_01": ("Plant_010", "Rose", "Plant_010_Rose"),
    "Drive_Group_02": ("Plant_011", "Croton", "Plant_011_Croton"),
    "Drive_Group_03": ("Plant_012", "Globe_Amaranth", "Plant_012_Globe_Amaranth"),
    "Drive_Group_04": ("Plant_013", "Lantana", "Plant_013_Lantana"),
    "Drive_Group_05": ("Plant_014", "Rain_Lily", "Plant_014_Rain_Lily"),
    "Drive_Group_06": ("Plant_015", "Basil_Tulsi", "Plant_015_Basil_Tulsi"),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main():
    with GROUPS_CSV.open(newline="", encoding="utf-8-sig") as file:
        staged = list(csv.DictReader(file))
    with MANIFEST.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        existing = list(reader)

    expected_fields = [
        "image_id", "class_id", "class_name", "source_id", "source_group",
        "collection_group", "type", "variation", "status", "qc_note",
        "original_filename", "original_path", "dataset_path", "sha256",
    ]
    if fields != expected_fields:
        raise SystemExit("Manifest schema changed; integration stopped.")
    if len(staged) != 171:
        raise SystemExit(f"Expected 171 staged JPEGs, found {len(staged)}.")

    existing_ids = {row["image_id"] for row in existing}
    existing_paths = {row["dataset_path"] for row in existing}
    counters = Counter()
    new_rows = []

    for row in staged:
        group = row["provisional_group"]
        if group not in CLASS_MAP:
            raise SystemExit(f"Unexpected group: {group}")
        class_id, class_name, folder_name = CLASS_MAP[group]
        counters[group] += 1
        number = counters[group]
        source_id = f"{class_id}_SRC_{number:03d}"
        image_id = f"{source_id}_ORG"
        destination_rel = Path("Plant_Dataset") / folder_name / "original" / f"{image_id}.jpg"
        destination = ROOT / destination_rel
        source = STAGING_IMAGES / row["drive_filename"]
        if not source.is_file():
            raise SystemExit(f"Missing staged image: {source}")
        if sha256(source) != row["sha256"]:
            raise SystemExit(f"Hash changed in staging: {source.name}")
        if image_id in existing_ids or destination_rel.as_posix() in existing_paths:
            raise SystemExit(f"Manifest collision: {image_id}")
        if destination.exists():
            raise SystemExit(f"Destination already exists: {destination}")

        destination.parent.mkdir(parents=True, exist_ok=True)
        (DATASET / folder_name / "generated").mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied_hash = sha256(destination)
        if copied_hash != row["sha256"]:
            raise SystemExit(f"Copied hash mismatch: {destination}")

        new_rows.append({
            "image_id": image_id,
            "class_id": class_id,
            "class_name": class_name,
            "source_id": source_id,
            "source_group": source_id,
            "collection_group": f"{class_id}_COLLECTION_001",
            "type": "Original",
            "variation": "None",
            "status": "Keep",
            "qc_note": "LABEL_CONFIRMED_2026-10-05;GOOGLE_DRIVE_SOURCE;SAME_SPECIMEN_COLLECTION",
            "original_filename": row["drive_filename"],
            "original_path": f"data_staging/google_drive_dataset/jpeg/{row['drive_filename']}",
            "dataset_path": destination_rel.as_posix(),
            "sha256": copied_hash,
        })

    with MANIFEST.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(existing + new_rows)

    print(f"Integrated {len(new_rows)} original JPEGs.")
    for group, count in counters.items():
        print(f"  {CLASS_MAP[group][2]}: {count}")
    print(f"Manifest rows: {len(existing) + len(new_rows)}")


if __name__ == "__main__":
    main()
