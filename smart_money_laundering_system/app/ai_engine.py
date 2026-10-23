import os
import json
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier, IsolationForest, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import classification_report
import joblib
import shap
import matplotlib.pyplot as plt

from . import config


class FraudModel:
    def __init__(self):
        self.model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.shap_explainer = None
        self.feature_medians: Optional[List[float]] = None
        self.anomaly_model: Optional[IsolationForest] = None

    def _load_dataset(self) -> pd.DataFrame:
        dataset_path = getattr(config, 'DATASET_PATH', '')
        if not dataset_path or not os.path.exists(dataset_path):
            raise FileNotFoundError(
                f"Dataset not found at {dataset_path}. "
                f"Place a dataset there and update DATASET_PATH."
            )

        if os.path.isdir(dataset_path):
            base_dir = dataset_path
            features_path = os.path.join(base_dir, getattr(config, 'ELLIPTIC_FEATURES_FILE', 'elliptic_txs_features.csv'))
            classes_path = os.path.join(base_dir, getattr(config, 'ELLIPTIC_CLASSES_FILE', 'elliptic_txs_classes.csv'))
            if os.path.exists(features_path) and os.path.exists(classes_path):
                feats = pd.read_csv(features_path, header=None)
                if feats.shape[1] >= 2:
                    cols = ['txId', 'time_step'] + [f'feature_{i}' for i in range(int(feats.shape[1]) - 2)]
                    feats.columns = cols
                classes = pd.read_csv(classes_path)
                if 'txId' not in classes.columns:
                    classes.rename(columns={classes.columns[0]: 'txId'}, inplace=True)
                if 'class' in classes.columns and 'elliptic label' not in classes.columns:
                    classes.rename(columns={'class': 'elliptic label'}, inplace=True)
                df = feats.merge(classes[['txId', 'elliptic label']], on='txId', how='left')
            else:
                raise FileNotFoundError(
                    f"Elliptic dataset directory detected, but expected files not found: {features_path}, {classes_path}"
                )
        else:
            df = pd.read_csv(dataset_path)
            base_dir = os.path.dirname(dataset_path)
            name = os.path.basename(dataset_path).lower()
            if 'elliptic' in name and name.endswith('.csv'):
                features_path = os.path.join(base_dir, getattr(config, 'ELLIPTIC_FEATURES_FILE', 'elliptic_txs_features.csv'))
                classes_path = os.path.join(base_dir, getattr(config, 'ELLIPTIC_CLASSES_FILE', 'elliptic_txs_classes.csv'))
                if os.path.exists(features_path) and os.path.exists(classes_path):
                    feats = pd.read_csv(features_path, header=None)
                    if feats.shape[1] >= 2:
                        cols = ['txId', 'time_step'] + [f'feature_{i}' for i in range(int(feats.shape[1]) - 2)]
                        feats.columns = cols
                    classes = pd.read_csv(classes_path)
                    if 'txId' not in classes.columns:
                        classes.rename(columns={classes.columns[0]: 'txId'}, inplace=True)
                    if 'class' in classes.columns and 'elliptic label' not in classes.columns:
                        classes.rename(columns={'class': 'elliptic label'}, inplace=True)
                    df = feats.merge(classes[['txId', 'elliptic label']], on='txId', how='left')

        if getattr(config, 'TRAIN_SAMPLE_SIZE', 0) and len(df) > int(config.TRAIN_SAMPLE_SIZE):
            df = df.sample(n=int(config.TRAIN_SAMPLE_SIZE), random_state=42)
        return df

    def _prepare_features(self, df: pd.DataFrame):
        target_col = None
        for col in ['elliptic label', 'elliptic_label', 'is_fraud', 'isFraud', 'Class', 'fraud', 'label']:
            if col in df.columns:
                target_col = col
                break
        if target_col is None:
            raise ValueError('Could not find fraud label column in dataset.')

        y_raw = df[target_col]
        if target_col in {'elliptic label', 'elliptic_label'}:
            if pd.api.types.is_numeric_dtype(y_raw):
                y_num = y_raw.astype('Int64')
                known_mask = ~y_num.isna()
                known_mask &= ~y_num.isin([3])
                df = df.loc[known_mask].copy()
                y_num = y_num.loc[known_mask]
                uniq = set([int(v) for v in y_num.dropna().unique().tolist()])
                if uniq <= {0, 1}:
                    y = y_num.astype(int)
                elif uniq <= {1, 2}:
                    y = (y_num == 1).astype(int)
                else:
                    y = (y_num == 1).astype(int)
            else:
                y_str = y_raw.astype(str).str.strip().str.lower()
                known_mask = ~y_str.isin(['unknown', 'nan', 'none', ''])
                df = df.loc[known_mask].copy()
                y_str = y_str.loc[known_mask]
                y = y_str.map({
                    '1': 1,
                    '2': 0,
                    'illegal': 1,
                    'illicit': 1,
                    'legal': 0,
                    'licit': 0,
                }).astype('Int64')
                known_mask_2 = ~y.isna()
                df = df.loc[known_mask_2].copy()
                y = y.loc[known_mask_2].astype(int)
        else:
            y = y_raw.astype(int)

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numeric_cols:
            numeric_cols.remove(target_col)
        if 'txId' in numeric_cols:
            numeric_cols.remove('txId')
        if not numeric_cols:
            raise ValueError('No numeric features available for training.')

        X = df[numeric_cols].fillna(df[numeric_cols].median())
        self.feature_names = numeric_cols
        self.feature_medians = [float(m) for m in df[numeric_cols].median().reindex(self.feature_names)]
        return X, y

    def train_and_save(self):
        df = self._load_dataset()
        X, y = self._prepare_features(df)

        test_size = float(getattr(config, 'TEST_SIZE', 0.2))
        val_size = float(getattr(config, 'VAL_SIZE', 0.1))
        X_trainval, X_test, y_trainval, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        val_ratio = val_size / max(1e-9, (1.0 - test_size))
        X_train, X_val, y_train, y_val = train_test_split(
            X_trainval, y_trainval, test_size=val_ratio, random_state=42, stratify=y_trainval
        )

        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)

        X_train_final = X_train_scaled
        y_train_final = y_train
        if bool(getattr(config, 'USE_SMOTE', True)):
            smote = SMOTE(random_state=42)
            X_train_final, y_train_final = smote.fit_resample(X_train_scaled, y_train)

        model_type = str(getattr(config, 'MODEL_TYPE', 'random_forest')).strip().lower()
        if model_type == 'adaboost':
            self.model = AdaBoostClassifier(random_state=42)
        elif model_type == 'xgboost':
            try:
                from xgboost import XGBClassifier
            except Exception as e:
                raise RuntimeError('xgboost is required for MODEL_TYPE="xgboost". Install it via requirements.txt.') from e
            self.model = XGBClassifier(
                n_estimators=400,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                reg_lambda=1.0,
                random_state=42,
                n_jobs=-1,
                eval_metric='logloss',
            )
        else:
            self.model = RandomForestClassifier(
                n_estimators=getattr(config, 'RF_N_ESTIMATORS', 200),
                max_depth=getattr(config, 'RF_MAX_DEPTH', 10),
                class_weight='balanced',
                random_state=42,
            )

        self.model.fit(X_train_final, y_train_final)

        baseline_model = LogisticRegression(max_iter=1000, n_jobs=-1)
        baseline_model.fit(X_train_final, y_train_final)

        y_pred_model = self.model.predict(X_test_scaled)
        y_pred_lr = baseline_model.predict(X_test_scaled)

        report_rf = classification_report(y_test, y_pred_model)
        os.makedirs(os.path.dirname(config.REPORT_EXPORT_PATH), exist_ok=True)
        with open(config.REPORT_EXPORT_PATH, 'w', encoding='utf-8') as f:
            f.write(report_rf)

        report_dict_rf = classification_report(y_test, y_pred_model, output_dict=True)
        report_dict_lr = classification_report(y_test, y_pred_lr, output_dict=True)

        cv_folds = int(getattr(config, 'CV_FOLDS', 10))
        cv_folds = max(2, cv_folds)
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        cv_metrics: Dict[str, Dict[str, float]] = {}
        for name, est in {
            'random_forest': RandomForestClassifier(
                n_estimators=getattr(config, 'RF_N_ESTIMATORS', 200),
                max_depth=getattr(config, 'RF_MAX_DEPTH', 10),
                class_weight='balanced',
                random_state=42,
            ),
            'adaboost': AdaBoostClassifier(random_state=42),
        }.items():
            scores = {'accuracy': [], 'precision': [], 'recall': [], 'f1': []}
            for train_idx, test_idx in cv.split(X, y):
                X_tr = X.iloc[train_idx]
                y_tr = y.iloc[train_idx] if hasattr(y, 'iloc') else y[train_idx]
                X_te = X.iloc[test_idx]
                y_te = y.iloc[test_idx] if hasattr(y, 'iloc') else y[test_idx]
                scaler = StandardScaler()
                X_tr_s = scaler.fit_transform(X_tr)
                X_te_s = scaler.transform(X_te)
                X_tr_final = X_tr_s
                y_tr_final = y_tr
                if bool(getattr(config, 'USE_SMOTE', True)):
                    sm = SMOTE(random_state=42)
                    X_tr_final, y_tr_final = sm.fit_resample(X_tr_s, y_tr)
                est.fit(X_tr_final, y_tr_final)
                y_hat = est.predict(X_te_s)
                rep = classification_report(y_te, y_hat, output_dict=True, zero_division=0)
                scores['accuracy'].append(float(rep.get('accuracy', 0.0)))
                scores['precision'].append(float(rep.get('weighted avg', {}).get('precision', 0.0)))
                scores['recall'].append(float(rep.get('weighted avg', {}).get('recall', 0.0)))
                scores['f1'].append(float(rep.get('weighted avg', {}).get('f1-score', 0.0)))
            cv_metrics[name] = {k: float(np.mean(v)) for k, v in scores.items()}

        try:
            from xgboost import XGBClassifier
            xgb_scores = {'accuracy': [], 'precision': [], 'recall': [], 'f1': []}
            est_xgb = XGBClassifier(
                n_estimators=400,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                reg_lambda=1.0,
                random_state=42,
                n_jobs=-1,
                eval_metric='logloss',
            )
            for train_idx, test_idx in cv.split(X, y):
                X_tr = X.iloc[train_idx]
                y_tr = y.iloc[train_idx] if hasattr(y, 'iloc') else y[train_idx]
                X_te = X.iloc[test_idx]
                y_te = y.iloc[test_idx] if hasattr(y, 'iloc') else y[test_idx]
                scaler = StandardScaler()
                X_tr_s = scaler.fit_transform(X_tr)
                X_te_s = scaler.transform(X_te)
                X_tr_final = X_tr_s
                y_tr_final = y_tr
                if bool(getattr(config, 'USE_SMOTE', True)):
                    sm = SMOTE(random_state=42)
                    X_tr_final, y_tr_final = sm.fit_resample(X_tr_s, y_tr)
                est_xgb.fit(X_tr_final, y_tr_final)
                y_hat = est_xgb.predict(X_te_s)
                rep = classification_report(y_te, y_hat, output_dict=True, zero_division=0)
                xgb_scores['accuracy'].append(float(rep.get('accuracy', 0.0)))
                xgb_scores['precision'].append(float(rep.get('weighted avg', {}).get('precision', 0.0)))
                xgb_scores['recall'].append(float(rep.get('weighted avg', {}).get('recall', 0.0)))
                xgb_scores['f1'].append(float(rep.get('weighted avg', {}).get('f1-score', 0.0)))
            cv_metrics['xgboost'] = {k: float(np.mean(v)) for k, v in xgb_scores.items()}
        except Exception:
            pass

        os.makedirs(os.path.dirname(config.MODEL_COMPARISON_PATH), exist_ok=True)
        with open(config.MODEL_COMPARISON_PATH, 'w', encoding='utf-8') as f:
            json.dump({
                "selected_model": model_type,
                "holdout_test": {"selected": report_dict_rf, "logistic_regression": report_dict_lr},
                "cross_validation": cv_metrics,
            }, f)

        self.anomaly_model = IsolationForest(contamination=0.01, random_state=42)
        self.anomaly_model.fit(X_train_scaled[y_train == 0])

        os.makedirs(os.path.dirname(config.MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, config.MODEL_PATH)
        joblib.dump(self.scaler, config.SCALER_PATH)
        if self.anomaly_model is not None:
            joblib.dump(self.anomaly_model, config.ANOMALY_MODEL_PATH)
        with open(config.FEATURES_PATH, 'w', encoding='utf-8') as f:
            json.dump({"feature_names": self.feature_names, "medians": self.feature_medians}, f)

        self.shap_explainer = None

    def load(self):
        if not os.path.exists(config.MODEL_PATH):
            self.train_and_save()
        else:
            self.model = joblib.load(config.MODEL_PATH)
            self.scaler = joblib.load(config.SCALER_PATH)
            if os.path.exists(config.ANOMALY_MODEL_PATH):
                self.anomaly_model = joblib.load(config.ANOMALY_MODEL_PATH)
            with open(config.FEATURES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and "feature_names" in data:
                    self.feature_names = data["feature_names"]
                    self.feature_medians = data.get("medians")
                else:
                    self.feature_names = data
                    self.feature_medians = None
            self.shap_explainer = None

    def _ensure_shap_explainer(self):
        if self.shap_explainer is None:
            assert self.model is not None
            self.shap_explainer = shap.TreeExplainer(self.model)

    def _build_feature_vector(self, txn: Dict[str, Any]) -> np.ndarray:
        """Map available numeric fields from txn into the trained feature space.

        Start from feature-wise medians (if available) so missing values are
        realistic; then override with any numeric values present in txn.
        """
        if self.feature_medians and len(self.feature_medians) == len(self.feature_names):
            x = np.array(self.feature_medians, dtype=float)
        else:
            x = np.zeros(len(self.feature_names), dtype=float)
        feat_map = {f: i for i, f in enumerate(self.feature_names)}
        for key, value in txn.items():
            if key in feat_map:
                try:
                    x[feat_map[key]] = float(value)
                except (TypeError, ValueError):
                    continue
        return x

    def predict_proba(self, txn: Dict[str, Any]) -> float:
        assert self.model is not None and self.scaler is not None
        x = self._build_feature_vector(txn)
        x_scaled = self.scaler.transform([x])
        prob = self.model.predict_proba(x_scaled)[0, 1]
        if self.anomaly_model is not None:
            raw_score = self.anomaly_model.decision_function(x_scaled)[0]
            anomaly_prob = 1.0 / (1.0 + np.exp(-raw_score))
            combined = 0.7 * prob + 0.3 * anomaly_prob
            return float(combined)
        return float(prob)

    def explain(self, txn: Dict[str, Any]) -> str:
        assert self.model is not None and self.scaler is not None
        self._ensure_shap_explainer()
        x = self._build_feature_vector(txn)
        x_scaled = self.scaler.transform([x])
        sv = self.shap_explainer.shap_values(x_scaled)
        shap_values = None
        if isinstance(sv, list):
            idx = 1 if len(sv) > 1 else 0
            shap_values = np.asarray(sv[idx])[0]
        else:
            arr = np.asarray(sv)
            if arr.ndim == 3:
                class_idx = 1 if arr.shape[2] > 1 else 0
                shap_values = arr[0, :, class_idx]
            elif arr.ndim == 2:
                shap_values = arr[0]
            else:
                shap_values = arr.reshape(-1)
        idx_sorted = np.argsort(-np.abs(shap_values))[:3]
        parts = []
        for idx in idx_sorted:
            fname = self.feature_names[idx]
            contrib = shap_values[idx]
            direction = 'increased risk' if contrib > 0 else 'reduced risk'
            parts.append(f"{fname} ({direction})")
        if not parts:
            return 'Model flagging based on learned patterns.'
        return 'Flagged due to: ' + ', '.join(parts)

    def plot_global_importance(self) -> str:
        assert self.model is not None
        importances = self.model.feature_importances_
        idx = np.argsort(importances)[::-1]
        names = [self.feature_names[i] for i in idx]
        vals = importances[idx]
        plt.figure(figsize=(8, 4))
        plt.bar(names[:10], vals[:10])
        plt.xticks(rotation=45, ha='right')
        plt.title('Top Feature Importances')
        plt.tight_layout()
        os.makedirs(os.path.dirname(config.REPORT_EXPORT_PATH), exist_ok=True)
        out_path = os.path.join(os.path.dirname(config.REPORT_EXPORT_PATH), 'feature_importance.png')
        plt.savefig(out_path)
        plt.close()
        return out_path
