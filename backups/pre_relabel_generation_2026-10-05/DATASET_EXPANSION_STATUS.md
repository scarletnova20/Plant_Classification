# Dataset expansion completion report

Date: 2026-10-05

## Google Drive

- Download status: complete and byte-size verified
- Downloaded files: 279
- JPEG photographs: 171
- DNG raw counterparts: 108
- Staged source size: 3.01 GiB

## Dataset

- Previous active image count: 65
- New original JPEGs integrated: 171
- New generated images: 0
- Rejected new originals: 0
- Final active dataset: 236 images across 13 classes
- Combined composition: 195 originals and 41 synthetic images

## Integrated distribution

| Class | Original | Generated | Rejected | Active total |
| --- | ---: | ---: | ---: | ---: |
| Plant_010 Rose | 38 | 0 | 0 | 38 |
| Plant_011 Croton | 24 | 0 | 0 | 24 |
| Plant_012 Globe Amaranth | 22 | 0 | 0 | 22 |
| Plant_013 Lantana | 33 | 0 | 0 | 33 |
| Plant_014 Rain Lily | 32 | 0 | 0 | 32 |
| Plant_015 Basil/Tulsi | 22 | 0 | 0 | 22 |
| **Expansion total** | **171** | **0** | **0** | **171** |

## Quality control

- Corrupted JPEGs: 0
- DNG size mismatches: 0
- Invalid DNG signatures: 0
- Exact duplicate JPEGs: 0
- Exact matches against the previous active dataset: 0
- Near-duplicate candidates: 4 pairs, retained as traceable original photographs
- Manifest and active folders: matched
- All 236 active images: readable

Each new class appears to contain repeated photographs of one potted specimen. These photographs add angle, crop, and background variation but do not count as independent biological specimens. No synthetic expansion was added because every confirmed class already contains 22-38 real photographs.

## Project files

- Active dataset: `Plant_Dataset/`
- Updated manifest: `dataset_manifest.csv`
- Updated audit: `DATASET_AUDIT.md`
- Updated report: `DATASET_REPORT.md`
- Source staging archive: `data_staging/google_drive_dataset/`
- Pre-expansion backup: `backups/pre_expansion_2026-10-05/`

## Expanded CNN baseline

- Framework: TensorFlow/Keras 2.17.1, CPU
- Classes: 13
- Training-eligible images: 226 after excluding 10 sign-bearing originals
- Diagnostic train split: 203
- Diagnostic validation split: 23
- Independent test split: unavailable
- Epochs run: 6 of 25; early stopping restored epoch 1
- Diagnostic validation loss: 2.6707
- Diagnostic validation accuracy: 3/23, or 13.04%

The validation result is a code and learning-behavior diagnostic. It is not an estimate of real-world generalization because no class has multiple independent collection groups.

## Status

- Dataset download: COMPLETE
- Dataset integration: COMPLETE
- Manifest validation: COMPLETE
- Expanded baseline training: COMPLETE
- Independent evaluation readiness: NO
