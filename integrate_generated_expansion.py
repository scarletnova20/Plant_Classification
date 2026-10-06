"""Integrate visually reviewed ImageGen candidates into the active dataset."""

import csv
import hashlib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CANDIDATES = ROOT / "data_staging" / "generated_candidates"
MANIFEST = ROOT / "dataset_manifest.csv"

CLASS_FOLDERS = {
    "Plant_010": "Plant_010_Rosa_x_damascene",
    "Plant_011": "Plant_011_Codiaeum_variegatum",
    "Plant_012": "Plant_012_Globe_Amaranth",
    "Plant_013": "Plant_013_Lantana_camara",
    "Plant_014": "Plant_014_Pink_Rain_Lily_Zephyranthes",
    "Plant_015": "Plant_015_Ocimum_sanctum",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    with MANIFEST.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        rows = list(reader)

    source_rows = {row["source_id"]: row for row in rows if row["type"] == "Original"}
    existing_ids = {row["image_id"] for row in rows}
    candidates = sorted(CANDIDATES.glob("Plant_*_AUG_*.png"))
    if len(candidates) != 16:
        raise SystemExit(f"Expected 16 generated candidates, found {len(candidates)}")

    new_rows = []
    for candidate in candidates:
        image_id = candidate.stem
        if image_id in existing_ids:
            raise SystemExit(f"Image ID already exists: {image_id}")
        source_id = image_id.rsplit("_AUG_", 1)[0]
        source = source_rows.get(source_id)
        if source is None:
            raise SystemExit(f"No original manifest row for {source_id}")
        class_id = source["class_id"]
        folder = CLASS_FOLDERS[class_id]
        destination_rel = Path("Plant_Dataset") / folder / "generated" / candidate.name
        destination = ROOT / destination_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise SystemExit(f"Destination already exists: {destination}")
        shutil.copy2(candidate, destination)
        variation = (
            "GENERATED_GARDEN_SIDE_ANGLE"
            if image_id.endswith("_AUG_001")
            else "GENERATED_NEUTRAL_BACKGROUND_VIEWPOINT"
        )
        new_rows.append({
            "image_id": image_id,
            "class_id": class_id,
            "class_name": source["class_name"],
            "source_id": source_id,
            "source_group": source["source_group"],
            "collection_group": source["collection_group"],
            "type": "Synthetic",
            "variation": variation,
            "status": "Keep",
            "qc_note": (
                "IMAGEGEN_BUILTIN;SOURCE_LINKED;VISUAL_QC_PASS_2026-10-05;"
                "SPECIES_LABEL_CONFIRMED_BY_USER_2026-10-05"
            ),
            "original_filename": source["original_filename"],
            "original_path": source["dataset_path"],
            "dataset_path": destination_rel.as_posix(),
            "sha256": sha256(destination),
        })

    rows.extend(new_rows)
    with MANIFEST.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Integrated {len(new_rows)} generated images.")


if __name__ == "__main__":
    main()
