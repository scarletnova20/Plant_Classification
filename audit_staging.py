"""Audit staged Google Drive JPEGs and build contact sheets for visual review."""

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
STAGING = ROOT / "data_staging" / "google_drive_dataset"
JPEG_DIR = STAGING / "jpeg"
REPORT_DIR = STAGING / "contact_sheets"

# The Drive folder had no labels. The user confirmed these visual groups on
# 2026-10-05, after the contact-sheet review.
PROVISIONAL_GROUPS = [
    ("Drive_Group_01", "Rosa_x_damascene", "IMG_20260917_163957371.jpg"),
    ("Drive_Group_02", "Codiaeum_variegatum", "IMG_20260917_164357523.jpg"),
    ("Drive_Group_03", "Globe_Amaranth", "IMG_20260917_164851517.jpg"),
    ("Drive_Group_04", "Lantana_camara", "IMG_20260917_165828025.jpg"),
    ("Drive_Group_05", "Pink_Rain_Lily_Zephyranthes", "IMG_20260917_170307619.jpg"),
    ("Drive_Group_06", "Ocimum_sanctum", None),
]


def dhash(image, size=8):
    gray = image.convert("L").resize((size + 1, size))
    pixels = list(gray.get_flattened_data())
    value = 0
    for y in range(size):
        for x in range(size):
            value = (value << 1) | (pixels[y * (size + 1) + x] > pixels[y * (size + 1) + x + 1])
    return value


def hamming(left, right):
    return (left ^ right).bit_count()


def main():
    files = sorted(JPEG_DIR.glob("*"))
    if not files:
        raise SystemExit(f"No JPEGs found in {JPEG_DIR}")

    rows, bad = [], []
    exact = defaultdict(list)
    for path in files:
        try:
            data = path.read_bytes()
            with Image.open(path) as image:
                image.load()
                rows.append({
                    "filename": path.name,
                    "format": image.format,
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                    "size_bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest().upper(),
                    "dhash": f"{dhash(image):016X}",
                })
                exact[rows[-1]["sha256"]].append(path.name)
        except Exception as error:
            bad.append((path.name, str(error)))

    hashes = [(row["filename"], int(row["dhash"], 16)) for row in rows]
    near = []
    for index, (name_a, hash_a) in enumerate(hashes):
        for name_b, hash_b in hashes[index + 1:]:
            distance = hamming(hash_a, hash_b)
            if distance <= 4:
                near.append((name_a, name_b, distance))

    STAGING.mkdir(parents=True, exist_ok=True)
    with (STAGING / "jpeg_inventory.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    with (STAGING / "duplicate_candidates.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["candidate_type", "filename_a", "filename_b", "dhash_distance"])
        for names in exact.values():
            if len(names) > 1:
                for name in names[1:]:
                    writer.writerow(["exact", names[0], name, 0])
        for name_a, name_b, distance in near:
            writer.writerow(["near", name_a, name_b, distance])

    group_index = 0
    group_source_counts = Counter()
    grouped_rows = []
    for row in rows:
        while (PROVISIONAL_GROUPS[group_index][2] is not None
               and row["filename"] >= PROVISIONAL_GROUPS[group_index][2]):
            group_index += 1
        group_id, visual_label, _ = PROVISIONAL_GROUPS[group_index]
        group_source_counts[group_id] += 1
        grouped_rows.append({
            "drive_filename": row["filename"],
            "provisional_group": group_id,
            "visual_label": visual_label,
            "label_status": "Confirmed_2026-10-05",
            "provisional_source_id": f"{group_id}_SRC_{group_source_counts[group_id]:03d}",
            "collection_group": f"{group_id}_COLLECTION_001",
            "image_type": "Original_JPEG",
            "inclusion_status": "Integrated_Active",
            "sha256": row["sha256"],
        })
    with (STAGING / "staging_groups.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=grouped_rows[0].keys())
        writer.writeheader()
        writer.writerows(grouped_rows)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    page_size, cols = 30, 5
    cell_w, cell_h, label_h = 260, 210, 28
    for page, start in enumerate(range(0, len(rows), page_size), 1):
        subset = rows[start:start + page_size]
        sheet = Image.new("RGB", (cols * cell_w, 6 * (cell_h + label_h)), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, row in enumerate(subset):
            x = (offset % cols) * cell_w
            y = (offset // cols) * (cell_h + label_h)
            with Image.open(JPEG_DIR / row["filename"]) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((cell_w - 8, cell_h - 8))
                px = x + (cell_w - image.width) // 2
                py = y + (cell_h - image.height) // 2
                sheet.paste(image, (px, py))
            draw.text((x + 4, y + cell_h + 2), row["filename"], fill="black", font=font)
        sheet.save(REPORT_DIR / f"staging_contact_{page:02d}.jpg", quality=90)

    dimensions = Counter((row["width"], row["height"]) for row in rows)
    print(f"JPEG files: {len(files)}")
    print(f"Readable: {len(rows)}; unreadable: {len(bad)}")
    print(f"Formats: {dict(Counter(row['format'] for row in rows))}")
    print(f"Dimensions: {dict(dimensions)}")
    print(f"Exact duplicate groups: {sum(len(names) > 1 for names in exact.values())}")
    print(f"Near-duplicate candidates (dHash <= 4): {len(near)}")
    print(f"Contact sheets: {len(list(REPORT_DIR.glob('*.jpg')))}")


if __name__ == "__main__":
    main()
