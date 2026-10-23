# Smart Money Laundering System (VTAC Paper-Aligned)

**Machine Learning in Money Laundering Detection Over Blockchain Technology (VTAC) – End-to-End Demo**

This project aligns the application flow, outputs, and UI terminology with the VTAC paper:

1. **Detection (ML):** illegal/legal classification using the Elliptic dataset
2. **De-anonymization:** map Elliptic `txId` → real Bitcoin transaction hash (`Result.csv`)
3. **Identification & Advisory:** graph + blockchain enrichment with VTAC advisory fields

The UI and API use **illegal / legal** terminology.

---

## What the VTAC Paper Requires (and what this project implements)

### VTAC Phase Coverage

| VTAC phase | Paper intent | Implemented here | Where |
|---|---|---|---|
| Detection | Train ML model(s) to classify transactions | RandomForest, AdaBoost, XGBoost; 10-fold CV; inference returns score + illegal/legal | `app/ai_engine.py`, `app/services.py` |
| De-anonymization | Resolve anonymized Elliptic node to real blockchain transaction | `Result.csv` mapping (`txId` → `tx_hash`) used in API and UI | `Datasets/Result.csv`, `app/services.py` |
| Identification & Advisory | Produce advisory signals: value, frequency, time window, weight factor | Uses Elliptic edge list + optional Blockstream lookup to compute advisory fields + beneficiaries | `app/services.py` (`vtac_identification_from_elliptic`) |

### VTAC Advisory Fields (as returned by the API)

The endpoint returns these VTAC-aligned fields inside `identification`:

- `frequency`: incoming/outgoing edge counts (`incoming_edges`, `outgoing_edges`)
- `time_window`: derived from Elliptic `time_step` neighborhood
- `weight_factor`: neighborhood-based weight estimate
- `value`: totals for incoming/outgoing/fee BTC (when blockchain lookup enabled)

Optional real-blockchain enrichment (if enabled):

- `advisory.time_window_blockchain`: `{start, end, seconds}` computed from real block times
- `beneficiaries`: top output addresses by BTC received

---

## VTAC “Covered vs Approximated” Notes

The VTAC paper describes an end-to-end methodology (detection → deanonymization → identification/advisory). Some advisory signals are described conceptually. This project implements them in a practical, reproducible way using the Elliptic graph and (optionally) real Bitcoin transaction data.

### Covered (directly implemented)

- Elliptic dataset ingestion (features/classes/edgelist)
- Transaction classification to **illegal/legal** using ML
- `Result.csv`-based deanonymization (`txId → tx_hash`)
- Identification on the Elliptic transaction graph neighborhood (incoming/outgoing edges)
- Advisory fields surfaced in UI + API:
  - value
  - frequency
  - time window
  - weight factor

### Approximated (paper-consistent, implementation-defined)

- `weight_factor` is computed as a normalized neighborhood degree estimate.
- `time_window` is computed from Elliptic `time_step` spread in the selected neighborhood.
- When blockchain lookup is enabled, a real-chain time window is computed from observed block times.

If you want a stricter, alternative definition for any advisory metric (e.g., fixed hop count, fixed node cap, or time-step-only), adjust `vtac_identification_from_elliptic` in `app/services.py`.

---

## Quick Start

### 1) Install

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Windows

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Download datasets (Elliptic + deanonymization)

This project supports automatic download using Kaggle (requires Kaggle credentials).

```bash
python download_datasets.py
```

Kaggle credentials location:

- macOS/Linux: `~/.kaggle/kaggle.json`
- Windows: `%USERPROFILE%\.kaggle\kaggle.json`

This downloads into:

- `Datasets/elliptic/` (Elliptic dataset)
- `Datasets/elliptic_deanonymized/` (deanonymized mapping dataset)

Then ensure `Datasets/Result.csv` exists (your mapping file). The system uses:

- `app/config.py → DEANONYM_MAPPING_PATH`

---

## Dataset Layout Expectations

### Elliptic dataset

The system auto-detects an Elliptic dataset directory if it contains:

- `elliptic_txs_features.csv` (no header)
- `elliptic_txs_classes.csv`

Recommended directory:

- `Datasets/elliptic/`

To enable graph identification, ensure the same directory contains:

- `elliptic_txs_edgelist.csv`

### Deanonymization

The system expects:

- `Datasets/Result.csv`

This file should map Elliptic txIds to real Bitcoin transaction hashes. If your downloaded mapping file has a different name, copy/rename it to `Datasets/Result.csv`.

### 3) Train the model

```bash
python retrain_model.py
```

Artifacts:

- `models/fraud_model.pkl`
- `models/scaler.pkl`
- `models/features.json`
- `exports/model_report.txt`
- `exports/model_comparison.json`

### 4) Run the app

#### macOS / Linux

```bash
python main.py
```

#### Windows

```bat
python main.py
```

Or use:

```bat
run.bat
```

Open:

`http://localhost:8080`

---

## How to Use (UI)

### VTAC lookup inside the dashboard

1. Open the app
2. Login
3. Go to **Dashboard → Monitor**
4. Scroll to **Elliptic txId Lookup**
5. Enter a `txId` (from `Result.csv`)
6. Click **Lookup Elliptic txId**

You will see:

- ML score + `legal/illegal`
- De-anonymized transaction hash (if present)
- VTAC advisory summary (frequency, time window, weight factor, value)
- Beneficiary addresses (if blockchain lookup enabled)

---

## API

### Predict Elliptic txId

`GET /api/predict_elliptic/{tx_id}`

Example:

`http://localhost:8080/api/predict_elliptic/230325127`

Returns:

- `score`
- `classification`: `legal` or `illegal`
- `deanonymized_tx_hash`
- `identification`: advisory fields + beneficiaries

### Predict crypto transaction (VTAC-style)

`POST /api/predict_crypto`

Body:

```json
{
  "sender_hash": "...",
  "receiver_hash": "...",
  "tx_hash": "...",
  "amount": 0.1,
  "tx_fee": 0.0001,
  "asset": "BTC",
  "network": "bitcoin"
}
```

---

## Configuration

File: `app/config.py`

- `MODEL_TYPE`: `random_forest`, `adaboost`, `xgboost`
- `CV_FOLDS`: default `10`
- `FRAUD_THRESHOLD`: score threshold for illegal/legal classification
- `ENABLE_BLOCKCHAIN_LOOKUP`: when `True`, the system makes external requests to Blockstream
- `BLOCKCHAIN_LOOKUP_BASE_URL`: default `https://blockstream.info/api`
- `DEANONYM_MAPPING_PATH`: path to `Result.csv`

### External requests toggle

`ENABLE_BLOCKCHAIN_LOOKUP`:

- `True`: makes external requests to `BLOCKCHAIN_LOOKUP_BASE_URL` to enrich advisory output with real BTC totals, beneficiaries, and blockchain time window.
- `False`: advisory output still includes frequency/time window/weight factor using Elliptic graph only.

---

## Data Sources

- **Elliptic Bitcoin Dataset**
  - `elliptic_txs_features.csv` (no header; first columns are `txId`, `time_step`)
  - `elliptic_txs_classes.csv`
  - `elliptic_txs_edgelist.csv`
- **De-anonymization mapping**
  - `Result.csv` (maps Elliptic `txId` → real Bitcoin tx hash)

---

## Known Implementation Notes

- `ENABLE_BLOCKCHAIN_LOOKUP=True` performs real network calls; results depend on external API availability.
- The VTAC paper describes advisory concepts at a high level. This implementation produces practical, evidence-friendly approximations using graph neighborhood metrics and real transaction fields.
- Internal variables may still use historical names (e.g., `fraud_score`, `is_fraud`) for backwards compatibility, but user-facing outputs use illegal/legal wording.

### Windows notes

- If `pip install xgboost` fails on your Windows machine, set `MODEL_TYPE = 'random_forest'` in `app/config.py`, then retrain via `python retrain_model.py`.
- If Kaggle download fails, confirm `%USERPROFILE%\.kaggle\kaggle.json` exists and contains a valid API token.

---

## Reproducibility Tips (Paper Demo)

- Ensure `DATASET_PATH` points to your Elliptic directory (auto-detected if present).
- Use `MODEL_TYPE='xgboost'` for a paper-aligned baseline.
- Use `CV_FOLDS=10`.
- Run `python retrain_model.py` to generate:
  - `exports/model_report.txt`
  - `exports/model_comparison.json`
- Verify end-to-end VTAC output on a known txId from `Result.csv`:
  - UI: Dashboard → Monitor → Elliptic txId Lookup
  - API: `GET /api/predict_elliptic/{tx_id}`

---

## Startup Guide

See: `STARTUP_GUIDE.md`
