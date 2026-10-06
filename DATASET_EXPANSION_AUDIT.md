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
| Drive_Group_01 / Plant_010 | Rosa x damascene | 38 | Confirmed and integrated |
| Drive_Group_02 / Plant_011 | Codiaeum variegatum | 24 | Confirmed and integrated |
| Drive_Group_03 / Plant_012 | Globe Amaranth | 22 | Confirmed and integrated |
| Drive_Group_04 / Plant_013 | Lantana camara | 33 | Confirmed and integrated |
| Drive_Group_05 / Plant_014 | Pink Rain Lily (Zephyranthes) | 32 | Confirmed and integrated |
| Drive_Group_06 / Plant_015 | Ocimum sanctum | 22 | Confirmed and integrated |

The mapping of every JPEG to a provisional group is in `data_staging/google_drive_dataset/staging_groups.csv`.

## Existing class comparison

None of the six visual groups clearly matches an existing active class. In particular, the Codiaeum variegatum group is visually distinct from the existing Purple Cordyline class. After the user's label confirmation, stable IDs `Plant_010` through `Plant_015` were assigned.

## Diversity and source independence

The new JPEGs contain useful changes in angle, distance, crop, orientation, and background. Each group nevertheless appears to show one potted specimen, first in a nursery setting and then against a light wall. Multiple photographs of one specimen are related observations and must stay in one conservative collection group.

At the user's request, two source-linked variants were generated for each of the eight named representative photographs. All 16 passed visual review and were integrated. They add controlled viewpoint and background variation but do not add independent specimens or evaluation evidence. Prompt and source details are in `GENERATED_IMAGE_LOG.md`.

## Integration status

The 171 JPEGs and 16 reviewed generated variants were copied into six active class folders and recorded in `dataset_manifest.csv`. No original image was deleted or overwritten. Backups exist under `backups/pre_expansion_2026-10-05/` and `backups/pre_relabel_generation_2026-10-05/`.

## Evaluation status

The labels are confirmed. The related photographs still share one conservative collection group per class, so the current validation is diagnostic and cannot estimate independent real-world performance.

