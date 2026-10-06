# Plant classification CNN baseline

This project uses `Plant_Dataset/` to train a small 128 × 128 RGB CNN. Class folders are detected automatically. Each class has `original/` and `generated/` image folders; `dataset_manifest.csv` preserves source and collection groups.

The baseline is: moderate random transforms (training only) → Conv2D with 8 filters → pooling → Conv2D with 16 filters → pooling → Conv2D with 32 filters → pooling → flatten → 32-unit dense layer → dropout → class output. For the current 13 classes this is 268,637 trainable parameters. Pixels are converted to RGB, resized to 128 × 128, and divided by 255.

Training uses Adam (learning rate 0.001), sparse categorical cross-entropy, accuracy, batches of 8, up to 25 epochs, early stopping after 5 epochs without validation-loss improvement, and a best-model checkpoint.

## Install

Use 64-bit Python 3.12. This project was run with the installed Anaconda Python 3.12.4. From this folder in PowerShell:

```powershell
& 'C:\Users\hridd\anaconda3\python.exe' -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The project `.venv` has the required packages installed. TensorFlow 2.17.1 works on this computer; the newer 2.18.1 and 2.21.0 packages failed to initialize a Windows DLL here. The environment uses CPU training.

## Check and train

```powershell
python train.py --check-data
python train.py --diagnostic
python evaluate.py
python predict.py "path\to\new_plant.jpg"
```

`--check-data` validates the 252 active images and prints class counts without importing TensorFlow. Training prints the model summary, saves the best model and class mapping in `models/`, and saves accuracy/loss plots in `results/`. `evaluate.py` writes a classification report and confusion matrix to `results/`.

The expanded diagnostic run completed on October 5, 2026. It used 13 classes and 252 active images. After excluding ten originals with readable signs, the source-group split contained 194 training images (80.2%) and 48 validation images (19.8%). The best checkpoint was epoch 22. Diagnostic validation accuracy was **29/48 (60.42%)**, with loss **1.4004**. This diagnostic result does not estimate real-world plant-identification performance.

## Evaluation limit

Each class currently has only **one conservative collection group**. A separate test set cannot give a trustworthy generalization estimate. `train.py` therefore refuses ordinary training with a claimed independent split. `--diagnostic` makes an approximately 80/20 source-group train/validation split, keeps all images derived from one original in the same subset, and creates **no test subset**. Its validation results are for checking the code and learning behavior only; different photos may still show the same physical plant or site.

Ten original images with readable signs are flagged in the manifest and excluded from model input by default. The originals remain unchanged in `Plant_Dataset/`. The two unresolved classes remain in `Review_Only/` and are not loaded. See `DATASET_REPORT.md` for class counts and label uncertainties.
