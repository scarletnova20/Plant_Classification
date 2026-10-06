# Plant image dataset report

> Expansion status (2026-10-05): 171 confirmed Google Drive JPEG originals were added as six new classes. The active dataset now contains 236 images across 13 classes. The table below preserves the first dataset release; the expansion table records the added classes. See `DATASET_EXPANSION_AUDIT.md`.

## Confirmed Google Drive expansion

| Class | Original | Generated | Rejected | Active total |
| --- | ---: | ---: | ---: | ---: |
| Plant_010 Rose | 38 | 0 | 0 | 38 |
| Plant_011 Croton | 24 | 0 | 0 | 24 |
| Plant_012 Globe_Amaranth | 22 | 0 | 0 | 22 |
| Plant_013 Lantana | 33 | 0 | 0 | 33 |
| Plant_014 Rain_Lily | 32 | 0 | 0 | 32 |
| Plant_015 Basil_Tulsi | 22 | 0 | 0 | 22 |
| **Expansion total** | **171** | **0** | **0** | **171** |
| **Combined active dataset** | **195** | **41** | **7 synthetic candidates** | **236** |

All new photographs are readable and have unique file hashes. Four visually near-duplicate pairs remain as original photographs and share their conservative class collection group. The new classes contain repeated views of one potted specimen each, so they do not provide independent collection groups for evaluation.

Generated 2026-09-21/22 from the 28 JPEGs in `Images_plants/`. The source archive was not changed. Synthetic images were made with the built-in image generation tool, one source-linked candidate at a time, then visually checked. Image IDs and SHA-256 hashes are in `dataset_manifest.csv`.

| Class | Original in dataset | Kept synthetic | Rejected synthetic | Final in dataset | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| Plant_001 Variegated_Dracaena | 3 | 7 | 0 | 10 | Provisional identity/cultivar grouping |
| Plant_002 Fern_Unidentified | 0 | 0 | 0 | 0 | Review only: target obscured |
| Plant_003 Variegated_Umbrella_Plant | 2 | 8 | 1 | 10 | Provisional botanical identity |
| Plant_004 Purple_Cordyline | 2 | 6 | 0 | 8 | Provisional botanical identity |
| Plant_005 Lobed_Leaf_Shrub_Unidentified | 0 | 0 | 4 | 0 | Review only: sources may contain more than one taxon |
| Plant_006 White_Flowering_Shrub_Unidentified | 5 | 5 | 1 | 10 | Provisional botanical identity/grouping |
| Plant_007 Mimusops_elengi | 7 | 3 | 0 | 10 | Sign identified; original signs need removal for training |
| Plant_008 Mangifera_indica | 3 | 6 | 1 | 9 | Sign identified; original signs need removal for training |
| Plant_009 Dragon_Tree_Dracaena_sp | 2 | 6 | 0 | 8 | Exact taxon unconfirmed |
| **Total** | **24** | **41** | **7** | **65** | **7 active classes** |

The full source archive contains **28 originals across 9 provisional IDs**. Four originals are in `Review_Only/` and do not count toward the 65-file dataset. The 7 rejected synthetic candidates are in `QC_Rejected/`, outside `Plant_Dataset/`. The image generator produced 48 candidates total; 41 passed this visual review.

There are **28 original source groups** in the manifest, of which **24** are in active class folders. The 7 active classes have one conservative collection-site group each.

## Folder layout

`Plant_Dataset/Plant_###_ClassName/original/` contains unchanged copies of accepted source photos. `generated/` contains source-linked synthetic PNGs. Filenames retain the class, original source ID, and `ORG` or `AUG_###` type. `dataset_manifest.csv` records the original filename, image path, image type, variation, QC status, source group, collection group, and hash.

`Review_Only/` contains the fern image and the three unresolved lobed-leaf images. They remain traceable in the manifest but are excluded from the active class folders. `QC_Contact_Sheets/` holds visual review sheets. No contact sheet is inside a class folder.

## Rejections

- Plant_003_SRC_002_AUG_003: near duplicate of another umbrella-plant view.
- Plant_005_SRC_001_AUG_001, Plant_005_SRC_002_AUG_001, Plant_005_SRC_003_AUG_001, Plant_005_SRC_001_AUG_002: class source photos may depict different taxa. No synthetic image from this class is admitted until identification is resolved.
- Plant_006_SRC_005_AUG_001: target plant too small in the frame.
- Plant_008_SRC_001_AUG_002: near duplicate of another mango sapling view.

## Use for model training

This is a **source-linked synthetic dataset**, not 65 independent field photographs. Keep `Original` and `Synthetic` distinct in analysis and reporting. The 41 kept synthetic images are 63% of the active dataset; 24 originals are 37%.

The `source_group` field binds each generated image to its original. The `collection_group` field is deliberately more conservative: all photos of a class appear to come from the same garden/site or physical planting. **There is no independent collection group per class for a trustworthy train/validation/test split.** Gather new, independently photographed plants for validation and test sets. Do not randomly split these 65 files.

Readable botanical or donor signs appear in original Plant_007 and Plant_008 photos. Crop or mask those signs in *separate derived training copies*, while retaining the originals for provenance. Do not let the model use the signs as class cues.

The active class names other than the two sign identified species remain provisional. Confirm their botanical identities and the grouping of Plant_001 and Plant_006 before training a species classifier. The 10-image target was not forced for Plant_004, Plant_008, or Plant_009 because additional synthetic views would add limited diversity.

## Generation prompt set

Each candidate used one original photo as an image reference and a photorealistic-natural prompt. The common constraints were: preserve the reference plant's leaf morphology, coloration, branch/rosette form, and growth habit; produce an ordinary garden photograph; vary viewpoint, scale, composition, background, crop, and mild natural light; exclude signs, text, invented flowers/fruit, malformed or duplicated structures, and conspicuous synthetic artifacts. The major variation for each accepted image is recorded in the manifest. Rejected images were retained separately for audit.
