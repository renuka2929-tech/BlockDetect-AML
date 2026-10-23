import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, 'fraud_system.db')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'fraud_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, 'models', 'features.json')
LEDGER_EXPORT_PATH = os.path.join(BASE_DIR, 'exports', 'ledger_export.json')
REPORT_EXPORT_PATH = os.path.join(BASE_DIR, 'exports', 'model_report.txt')

DATASET_PATH = os.path.join(BASE_DIR, 'Datasets', 'creditcard.csv')

ELLIPTIC_FEATURES_FILE = 'elliptic_txs_features.csv'
ELLIPTIC_CLASSES_FILE = 'elliptic_txs_classes.csv'
ELLIPTIC_EDGES_FILE = 'elliptic_txs_edgelist.csv'

_elliptic_dir_candidates = [
    os.path.join(BASE_DIR, 'Datasets', 'elliptic'),
    os.path.join(BASE_DIR, 'Datasets', 'elliptic_bitcoin_dataset'),
]

ELLIPTIC_DATASET_DIR = _elliptic_dir_candidates[0]
for _cand in _elliptic_dir_candidates:
    _features = os.path.join(_cand, ELLIPTIC_FEATURES_FILE)
    _classes = os.path.join(_cand, ELLIPTIC_CLASSES_FILE)
    if os.path.isdir(_cand) and os.path.exists(_features) and os.path.exists(_classes):
        ELLIPTIC_DATASET_DIR = _cand
        DATASET_PATH = _cand
        break

DEANONYM_MAPPING_PATH = os.path.join(BASE_DIR, 'Datasets', 'Result.csv')

ENABLE_BLOCKCHAIN_LOOKUP = True
BLOCKCHAIN_LOOKUP_BASE_URL = 'https://blockstream.info/api'

FRAUD_THRESHOLD = 0.6
ANOMALY_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'anomaly_model.pkl')
KEY_DIR = os.path.join(BASE_DIR, 'keys')
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, 'private_key.pem')
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, 'public_key.pem')
CHARTS_EXPORT_DIR = os.path.join(BASE_DIR, 'exports')
MODEL_COMPARISON_PATH = os.path.join(BASE_DIR, 'exports', 'model_comparison.json')

TRAIN_SAMPLE_SIZE = 50000
RF_N_ESTIMATORS = 120
RF_MAX_DEPTH = 8

MODEL_TYPE = 'xgboost'
USE_SMOTE = True
TEST_SIZE = 0.2
VAL_SIZE = 0.1
CV_FOLDS = 10
