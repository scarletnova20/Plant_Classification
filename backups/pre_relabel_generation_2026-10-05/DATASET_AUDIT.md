# Plant image dataset audit

> Expansion update (2026-10-05): the user confirmed the six Google Drive labels. All 171 JPEG originals were integrated as Plant_010 through Plant_015. The active dataset now contains 236 images across 13 classes. The 108 DNG counterparts remain in the source staging archive. See `DATASET_EXPANSION_AUDIT.md`.

This is the pre-generation audit. For the current dataset, counts, exclusions, and usage notes, see `DATASET_REPORT.md`.

Source folder: `Images_plants/` (28 JPEGs, each 720 × 1280). Audited 2026-09-21. No images have been generated or moved.

Class names below are working labels based on visible morphology. Only the `Mimusops elengi` and `Mangifera indica` names are directly supported by readable signs in the photos. Confirm the remaining botanical identifications before treating them as species labels.

| Class ID | Working class name | Originals | Existing visual characteristics | Missing variation / concern | Target additional | Status |
| --- | --- | ---: | --- | --- | ---: | --- |
| Plant_001 | Variegated_Dracaena | 3 | Tall striped, narrow leaves; outdoor ornamental planting; medium and closer views | Similar site/light; image 11 may be a different cultivar, so confirm grouping | Up to 7 | Pending identification |
| Plant_002 | Fern_Unidentified | 1 | Ferns in a mixed garden scene; broad view | Target fern is partly obscured by other plants; needs a clear, independently identified source | 0 for now | Review source |
| Plant_003 | Variegated_Umbrella_Plant | 2 | Cream-and-green palmate leaves; medium and closer framing | Same specimen, background and light; other specimen or setting | Up to 8 | Pending identification |
| Plant_004 | Purple_Cordyline | 2 | Purple strap leaves; close and medium views | Same planting/background; whole plant and other setting | Up to 8 | Pending identification |
| Plant_005 | Lobed_Leaf_Shrub_Unidentified | 3 | Deeply lobed leaves; close and medium views; garden | Species uncertain; busy background; whole plant and independent specimen | Up to 7 | Pending identification |
| Plant_006 | White_Flowering_Shrub_Unidentified | 5 | Green leaves and small white/pink flowers; close and wider views | Verify that both garden locations are the same species; other angles and light | Up to 5 | Pending identification |
| Plant_007 | Mimusops_elengi | 7 | Several young trees; full tree and closer views; signs visible | Similar institutional garden setting, portrait framing, and lighting; backgrounds may leak class | Up to 3 | Pending generation |
| Plant_008 | Mangifera_indica | 3 | Young mango tree; full plant and closer view; sign visible | All photos likely the same sapling/site; independent tree photos preferred | Up to 7 | Pending generation |
| Plant_009 | Dragon_Tree_Dracaena_sp | 2 | Spiky rosettes on woody branches; two views of same planting | Exact taxon uncertain; same site/light; clear individual plant and other settings | Up to 8 | Pending identification |

**Totals:** 9 provisional classes; 28 original photos; 0 generated photos; 0 rejected photos. The additional-image counts are upper planning bounds toward about 10 per class, not a commitment to synthesize weak variants. The fern image is not currently a sound class source, so the usable class count may be 8 until a clearer original is provided.

## Source ID mapping

Originals stay in `Images_plants/`. Each row below maps a permanent source ID to the unchanged filename. The same IDs are recorded in `dataset_manifest.csv`.

| Source ID | Original filename |
| --- | --- |
| Plant_001_SRC_001 | WhatsApp Image 2026-09-21 at 5.50.17 PM (1).jpeg |
| Plant_001_SRC_002 | WhatsApp Image 2026-09-21 at 5.50.18 PM.jpeg |
| Plant_001_SRC_003 | WhatsApp Image 2026-09-21 at 5.51.07 PM.jpeg |
| Plant_002_SRC_001 | WhatsApp Image 2026-09-21 at 5.50.17 PM.jpeg |
| Plant_003_SRC_001 | WhatsApp Image 2026-09-21 at 5.50.18 PM (1).jpeg |
| Plant_003_SRC_002 | WhatsApp Image 2026-09-21 at 5.50.18 PM (2).jpeg |
| Plant_004_SRC_001 | WhatsApp Image 2026-09-21 at 5.50.19 PM (1).jpeg |
| Plant_004_SRC_002 | WhatsApp Image 2026-09-21 at 5.50.51 PM.jpeg |
| Plant_005_SRC_001 | WhatsApp Image 2026-09-21 at 5.50.19 PM.jpeg |
| Plant_005_SRC_002 | WhatsApp Image 2026-09-21 at 5.50.52 PM.jpeg |
| Plant_005_SRC_003 | WhatsApp Image 2026-09-21 at 5.50.56 PM.jpeg |
| Plant_006_SRC_001 | WhatsApp Image 2026-09-21 at 5.51.09 PM.jpeg |
| Plant_006_SRC_002 | WhatsApp Image 2026-09-21 at 5.51.10 PM (1).jpeg |
| Plant_006_SRC_003 | WhatsApp Image 2026-09-21 at 5.51.10 PM.jpeg |
| Plant_006_SRC_004 | WhatsApp Image 2026-09-21 at 5.51.12 PM (1).jpeg |
| Plant_006_SRC_005 | WhatsApp Image 2026-09-21 at 5.51.18 PM (2).jpeg |
| Plant_007_SRC_001 | WhatsApp Image 2026-09-21 at 5.51.12 PM (2).jpeg |
| Plant_007_SRC_002 | WhatsApp Image 2026-09-21 at 5.51.12 PM.jpeg |
| Plant_007_SRC_003 | WhatsApp Image 2026-09-21 at 5.51.13 PM (1).jpeg |
| Plant_007_SRC_004 | WhatsApp Image 2026-09-21 at 5.51.13 PM.jpeg |
| Plant_007_SRC_005 | WhatsApp Image 2026-09-21 at 5.51.14 PM (1).jpeg |
| Plant_007_SRC_006 | WhatsApp Image 2026-09-21 at 5.51.16 PM.jpeg |
| Plant_007_SRC_007 | WhatsApp Image 2026-09-21 at 5.51.18 PM (1).jpeg |
| Plant_008_SRC_001 | WhatsApp Image 2026-09-21 at 5.51.14 PM.jpeg |
| Plant_008_SRC_002 | WhatsApp Image 2026-09-21 at 5.51.15 PM (1).jpeg |
| Plant_008_SRC_003 | WhatsApp Image 2026-09-21 at 5.51.17 PM.jpeg |
| Plant_009_SRC_001 | WhatsApp Image 2026-09-21 at 5.51.15 PM.jpeg |
| Plant_009_SRC_002 | WhatsApp Image 2026-09-21 at 5.51.18 PM.jpeg |

## Split and generation cautions

- Different photos of one physical plant, or of the same garden scene, are not independent test examples. Group those together in addition to keeping each original and its future derivatives together.
- Readable signs create label leakage. Exclude signs from model inputs or collect sign-free photos, while retaining unedited originals in the source archive.
- Synthetic viewpoint or background changes cannot establish new biological evidence. Prefer additional independently photographed plants for validation and test sets.
- No generation should start until provisional class groupings are confirmed, especially Plant_001, Plant_002, Plant_005, Plant_006, and Plant_009.
