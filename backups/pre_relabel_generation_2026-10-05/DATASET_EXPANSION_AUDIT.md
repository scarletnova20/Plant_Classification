# Google Drive dataset expansion audit

Audit date: 2026-10-04; labels confirmed and integrated 2026-10-05

Source: Google Drive folder `179s4vO3epi0S5Jlm04IcvtvcH_iVTRSA`

## Download inventory

The folder is accessible through the connected Google Drive account. It is a flat folder with no class subfolders or label file.

| File type | Drive files | Purpose |
| --- | ---: | --- |
| JPEG | 171 | Training candidate and visual audit copy |
| DNG | 108 | Raw camera counterpart/source archive |
| **Total** | **279** | |

The JPEG files are staged under `data_staging/google_drive_dataset/jpeg/`. DNG files are staged separately under `data_staging/google_drive_dataset/dng/`. `drive_inventory.csv` records the Drive file IDs and metadata.

## JPEG validation

- Readable images: 171 of 171
- Corrupted or unreadable images: 0
- Exact duplicates within the staged JPEGs: 0
- Exact duplicates against the existing active dataset: 0
- Perceptual near-duplicate candidates: 4 pairs
- Image format: JPEG
- Dimensions: 30 at 3072 x 4096, 10 at 4096 x 3072, 109 at 3072 x 4080, and 22 at 4080 x 3072
- Contact sheets: 6 in `data_staging/google_drive_dataset/contact_sheets/`

The four near-duplicate pairs remain in staging for review. They have not been rejected automatically because a perceptual hash is only a screening signal.

## Provisional visual groups

The Drive folder supplied no labels. Contact-sheet review found six coherent groups, and the user confirmed the labels on 2026-10-05.

| Provisional group | Visual label | JPEG count | Label status |
| --- | --- | ---: | --- |
| Drive_Group_01 / Plant_010 | Rose | 38 | Confirmed and integrated |
| Drive_Group_02 / Plant_011 | Croton | 24 | Confirmed and integrated |
| Drive_Group_03 / Plant_012 | Globe Amaranth | 22 | Confirmed and integrated |
| Drive_Group_04 / Plant_013 | Lantana | 33 | Confirmed and integrated |
| Drive_Group_05 / Plant_014 | Rain Lily | 32 | Confirmed and integrated |
| Drive_Group_06 / Plant_015 | Basil/Tulsi | 22 | Confirmed and integrated |

The mapping of every JPEG to a provisional group is in `data_staging/google_drive_dataset/staging_groups.csv`.

## Existing class comparison

None of the six visual groups clearly matches an existing active class. In particular, the croton-like group is visually distinct from the existing Purple Cordyline class. No new stable `Plant_###` IDs have been assigned because the folder lacks authoritative labels.

## Diversity and source independence

The new JPEGs contain useful changes in angle, distance, crop, orientation, and background. Each group nevertheless appears to show one potted specimen, first in a nursery setting and then against a light wall. Multiple photographs of one specimen are related observations and must stay in one conservative collection group.

Synthetic generation is not appropriate at this point. Each provisional group already has 22-38 real photographs, while the missing evidence is independent specimens and confirmed labels. Synthetic images cannot supply either.

## Integration status

The 171 JPEGs were copied into six new active class folders and appended to `dataset_manifest.csv`. No original image was deleted or overwritten. The previous manifest, model, and results were backed up under `backups/pre_expansion_2026-10-05/` before integration and retraining.

## Required decision

The labels are confirmed. The related photographs still share one conservative collection group per class, so the current validation is diagnostic and cannot estimate independent real-world performance.
