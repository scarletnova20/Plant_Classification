"""Apply the user's species-level labels while preserving stable class IDs."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent

CLASS_MAP = {
    "Plant_010": ("Rosa_x_damascene", "Plant_010_Rosa_x_damascene"),
    "Plant_011": ("Codiaeum_variegatum", "Plant_011_Codiaeum_variegatum"),
    "Plant_012": ("Globe_Amaranth", "Plant_012_Globe_Amaranth"),
    "Plant_013": ("Lantana_camara", "Plant_013_Lantana_camara"),
    "Plant_014": ("Pink_Rain_Lily_Zephyranthes", "Plant_014_Pink_Rain_Lily_Zephyranthes"),
    "Plant_015": ("Ocimum_sanctum", "Plant_015_Ocimum_sanctum"),
}

GROUP_LABELS = {
    "Drive_Group_01": "Rosa_x_damascene",
    "Drive_Group_02": "Codiaeum_variegatum",
    "Drive_Group_03": "Globe_Amaranth",
    "Drive_Group_04": "Lantana_camara",
    "Drive_Group_05": "Pink_Rain_Lily_Zephyranthes",
    "Drive_Group_06": "Ocimum_sanctum",
}


def rewrite_csv(path: Path, transform) -> None:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        rows = [transform(row) for row in reader]
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def update_manifest(row: dict[str, str]) -> dict[str, str]:
    mapping = CLASS_MAP.get(row["class_id"])
    if not mapping:
        return row
    class_name, folder = mapping
    row["class_name"] = class_name
    parts = Path(row["dataset_path"]).parts
    if len(parts) >= 2 and parts[0] == "Plant_Dataset":
        row["dataset_path"] = (Path("Plant_Dataset") / folder / Path(*parts[2:])).as_posix()
    marker = "SPECIES_LABEL_CONFIRMED_BY_USER_2026-10-05"
    if marker not in row["qc_note"]:
        row["qc_note"] = f"{row['qc_note']};{marker}".strip(";")
    return row


def update_staging(row: dict[str, str]) -> dict[str, str]:
    if row["provisional_group"] in GROUP_LABELS:
        row["visual_label"] = GROUP_LABELS[row["provisional_group"]]
        row["label_status"] = "Species_confirmed_2026-10-05"
    return row


def main() -> None:
    rewrite_csv(ROOT / "dataset_manifest.csv", update_manifest)
    rewrite_csv(
        ROOT / "data_staging" / "google_drive_dataset" / "staging_groups.csv",
        update_staging,
    )


if __name__ == "__main__":
    main()
