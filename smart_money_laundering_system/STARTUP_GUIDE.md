# Startup Guide (VTAC Paper-Aligned)

This guide helps you run the **Smart Money Laundering System** in a reproducible way aligned to the VTAC paper:

- **Detection (ML)** on the Elliptic dataset
- **De-anonymization** using `Result.csv` (`txId` → real Bitcoin tx hash)
- **Identification & advisory** (value, frequency, time window, weight factor) with optional blockchain enrichment

---

## 0) Prerequisites

- Python 3.8+
- macOS / Linux / Windows
- (Optional) Kaggle account to auto-download datasets

---

## 1) Create and activate a virtual environment

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2) Get the datasets

The system supports the **Elliptic Bitcoin Dataset** and a deanonymization mapping file.

### Option A: Download via Kaggle (recommended)

1) Put your Kaggle credentials file at:

- macOS/Linux: `~/.kaggle/kaggle.json`
- Windows: `%USERPROFILE%\.kaggle\kaggle.json`

2) Make sure permissions are correct (macOS/Linux):

```bash
chmod 600 ~/.kaggle/kaggle.json
```

3) Run the downloader:

```bash
python download_datasets.py
```

This downloads into:

- `Datasets/elliptic/`
- `Datasets/elliptic_deanonymized/`

### Option B: Manual download

Place the Elliptic files into one folder (any of the following are auto-detected):

- `Datasets/elliptic/`
- `Datasets/elliptic_bitcoin_dataset/`

Required files inside that folder:

- `elliptic_txs_features.csv`
- `elliptic_txs_classes.csv`
- `elliptic_txs_edgelist.csv`

---

## 3) Make sure `Result.csv` exists

The system expects the deanonymization mapping at:

- `Datasets/Result.csv`

If you downloaded a mapping dataset from Kaggle, you may need to **copy/rename** the correct mapping CSV to exactly:

- `Datasets/Result.csv`

This file is used to map:

- `Elliptic txId` → `real Bitcoin tx hash`

---

## 4) Configure the project

Open: `app/config.py`

Important settings:

- `MODEL_TYPE = 'xgboost'` (paper-aligned default)
- `CV_FOLDS = 10`
- `FRAUD_THRESHOLD = 0.6` (classification threshold)
- `ENABLE_BLOCKCHAIN_LOOKUP = True` (enables real blockchain enrichment)

### About `ENABLE_BLOCKCHAIN_LOOKUP`

- **True**:
  - Makes external requests to Blockstream
  - Adds BTC totals, beneficiaries, and blockchain time window
  - Can be slower (network-dependent)

- **False**:
  - No external requests
  - Still returns frequency/time window/weight factor from Elliptic graph

---

## 5) Train the ML model (recommended)

```bash
python retrain_model.py
```

Outputs:

- `exports/model_report.txt`
- `exports/model_comparison.json`
- `models/fraud_model.pkl`

---

## 6) Start the app

```bash
python main.py
```

Then open:

- `http://localhost:8080`

---

## 7) Verify VTAC pipeline in the UI

1) Login
2) Go to **Dashboard → Monitor**
3) Scroll to **Elliptic txId Lookup**
4) Enter a txId (example: `230325127`)
5) Click **Lookup Elliptic txId**

You should see:

- `score`
- `classification` (legal/illegal)
- `deanonymized_tx_hash`
- VTAC advisory fields:
  - **value** (BTC totals + fee)
  - **frequency** (incoming/outgoing edges)
  - **time window** (Elliptic steps + optional blockchain window)
  - **weight factor**
- Beneficiaries table (if blockchain lookup enabled)

---

## 8) Verify via API

Open in browser:

- `http://localhost:8080/api/predict_elliptic/230325127`

---

## Troubleshooting

### 1) Dataset not found

- Check `app/config.py → DATASET_PATH`
- For Elliptic: it should point to a **directory** containing the 3 Elliptic files

### 2) `Result.csv` not found / deanonymization missing

- Confirm file exists: `Datasets/Result.csv`
- Confirm it has a column mapping Elliptic txId to a real tx hash

### 3) Lookup works but is slow

- Set `ENABLE_BLOCKCHAIN_LOOKUP = False`
- Restart the app

### 4) Blockstream errors / timeouts

- This is expected if Blockstream is down or rate-limited
- Try again later or disable blockchain lookup

### 5) Kaggle auth failure

- Verify `~/.kaggle/kaggle.json` exists
- Verify permissions are `600` on macOS/Linux

---

## Recommended “paper reproduction” checklist

- Use Elliptic dataset directory as `DATASET_PATH`
- Train with `MODEL_TYPE='xgboost'`
- Keep `CV_FOLDS=10`
- Use UI lookup with a txId from `Result.csv`
- Confirm advisory fields appear in output
