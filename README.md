# Plant classification CNN baseline

This project trains a small PyTorch convolutional neural network on `Plant_Dataset/`. The dataset contains 252 active RGB images across 13 classes. `dataset_manifest.csv` records each image's class, source group, collection group, and quality-control status.

## Model and training

The model accepts 128 x 128 RGB tensors in PyTorch's `channels x height x width` layout. Its layers are:

1. `Conv2d(3, 8)` + ReLU + max pooling
2. `Conv2d(8, 16)` + ReLU + max pooling
3. `Conv2d(16, 32)` + ReLU + max pooling
4. Flatten + `Linear(8192, 32)` + ReLU + dropout
5. `Linear(32, 13)` output logits

The network has 268,637 trainable parameters. Training uses random horizontal flips, rotations, translations, and scaling. Validation and prediction only resize images and convert pixel values to tensors in the range 0 to 1.

The loss is `torch.nn.CrossEntropyLoss`, so the model returns raw logits during training. Adam updates the weights with a learning rate of 0.001. Training uses batches of 8 for up to 25 epochs and saves the checkpoint with the lowest validation loss. Early stopping ends training after five epochs without improvement.

## Install

Use 64-bit Python 3.12. From this folder in PowerShell:

```powershell
& 'C:\Users\hridd\anaconda3\python.exe' -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The supplied requirements install the CPU builds of PyTorch 2.5.1 and torchvision 0.20.1, which were verified on this Windows computer.

## Check, train, evaluate, and predict

```powershell
python train.py --check-data
python train.py --diagnostic
python evaluate.py
python predict.py "path\to\new_plant.jpg"
```

- `train.py --check-data` validates the manifest, class folders, and all active images without training.
- `train.py --diagnostic` creates the source-group-aware 80/20 split, trains the CNN, and writes the best checkpoint.
- `evaluate.py` reloads the checkpoint, evaluates its held-out subset, and writes a classification report and confusion matrix.
- `predict.py` applies the same evaluation preprocessing and prints one predicted class and confidence score.

## Outputs

- `models/plant_classifier.pth`: PyTorch state dictionary plus model metadata
- `models/class_names.json`: ordered output-class mapping
- `models/split.json`: exact training, validation, and test paths
- `results/accuracy.png`: training and validation accuracy by epoch
- `results/loss.png`: training and validation loss by epoch
- `results/classification_report.txt`: per-class validation metrics
- `results/confusion_matrix.png`: validation confusion matrix
- `docs/Plant_Classification_PyTorch_Training_Guide.docx`: updated project flow and framework guide

The pre-migration TensorFlow code, `.keras` model, and results are preserved under `backups/pre_pytorch_migration_2026-10-06/`.

## Current PyTorch result

The PyTorch diagnostic run completed on October 6, 2026. Ten sign-bearing originals were excluded before splitting, leaving 242 eligible images. The source-group split contains 194 training images (80.2%) and 48 validation images (19.8%), with no source group shared between the subsets.

The best checkpoint came from epoch 23:

- Validation loss: **1.4408**
- Validation accuracy: **26/48 (54.17%)**

## Evaluation limit

Every class currently has only one conservative collection group. The project therefore cannot create an independent test set that measures performance on new plants or collection sites. Ordinary training stops with an explanation. The `--diagnostic` option allows the source-group-aware 80/20 train/validation split and creates no test subset.

The reported validation result checks that the pipeline learns and runs correctly on the current dataset. It is not a reliable estimate of real-world plant-identification accuracy. Add independently photographed specimens for each class before treating evaluation metrics as evidence of generalization.

Ten original images with readable signs remain in `Plant_Dataset/` and are flagged in the manifest, but training excludes them. The two unresolved classes remain in `Review_Only/` and are not loaded. See `DATASET_REPORT.md` and `DATASET_AUDIT.md` for data details.
