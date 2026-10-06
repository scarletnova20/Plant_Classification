# Dataset expansion completion report

Date: 2026-10-06

## Google Drive

- Download status: complete and byte-size verified
- Downloaded files: 279
- JPEG photographs: 171
- DNG raw counterparts: 108
- Staged source size: 3.01 GiB

## Dataset

- Previous active image count: 65
- New original JPEGs integrated: 171
- New generated images: 16
- Rejected new originals: 0
- Final active dataset: 252 images across 13 classes
- Combined composition: 195 originals and 57 synthetic images

## Integrated distribution

| Class | Original | Generated | Rejected | Active total |
| --- | ---: | ---: | ---: | ---: |
| Plant_010 Rosa x damascene | 38 | 6 | 0 | 44 |
| Plant_011 Codiaeum variegatum | 24 | 2 | 0 | 26 |
| Plant_012 Globe Amaranth | 22 | 2 | 0 | 24 |
| Plant_013 Lantana camara | 33 | 2 | 0 | 35 |
| Plant_014 Pink Rain Lily (Zephyranthes) | 32 | 2 | 0 | 34 |
| Plant_015 Ocimum sanctum | 22 | 2 | 0 | 24 |
| **Expansion total** | **171** | **16** | **0** | **187** |

## Quality control

- Corrupted JPEGs: 0
- DNG size mismatches: 0
- Invalid DNG signatures: 0
- Exact duplicate JPEGs: 0
- Exact matches against the previous active dataset: 0
- Near-duplicate candidates: 4 pairs, retained as traceable original photographs
- Manifest and active folders: matched
- All 252 active images: readable

Each new class appears to contain repeated photographs of one potted specimen. The 16 source-linked generated images add controlled angle and background variation but do not count as independent biological specimens.

## Project files

- Active dataset: `Plant_Dataset/`
- Updated manifest: `dataset_manifest.csv`
- Updated audit: `DATASET_AUDIT.md`
- Updated report: `DATASET_REPORT.md`
- Source staging archive: `data_staging/google_drive_dataset/`
- Generated-image review log: `GENERATED_IMAGE_LOG.md`
- Generated candidates and contact sheet: `data_staging/generated_candidates/`
- Pre-expansion backup: `backups/pre_expansion_2026-10-05/`

## Expanded CNN baseline

- Framework: PyTorch 2.5.1, CPU
- Classes: 13
- Training-eligible images: 242 after excluding 10 sign-bearing originals
- Diagnostic train split: 194 (80.2%)
- Diagnostic validation split: 48 (19.8%)
- Independent test split: unavailable
- Epochs run: 25 of 25; best checkpoint from epoch 23
- Diagnostic validation loss: 1.4408
- Diagnostic validation accuracy: 26/48, or 54.17%

The validation result is a code and learning-behavior diagnostic. It is not an estimate of real-world generalization because no class has multiple independent collection groups.

## Status

- Dataset download: COMPLETE
- Dataset integration: COMPLETE
- Manifest validation: COMPLETE
- Expanded baseline training: COMPLETE
- Independent evaluation readiness: NO

