import json
import os
import threading
import zipfile
from datetime import datetime
from typing import Any, Dict
from datetime import timedelta
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pydantic import BaseModel, ValidationError

from . import config
from . import database
from .ai_engine import FraudModel
from .blockchain import Blockchain


database.init_db()
fraud_model = FraudModel()
blockchain = Blockchain()

_threshold: Dict[str, float] = {'value': float(config.FRAUD_THRESHOLD)}
_dataset_cache: Dict[str, Any] = {'df': None, 'target_col': None}
_dataset_lock = threading.Lock()

_deanonym_cache: Dict[str, Any] = {'map': None}
_deanonym_lock = threading.Lock()

_elliptic_edges_cache: Dict[str, Any] = {'edges': None}
_elliptic_edges_lock = threading.Lock()

_blockchain_tx_cache: Dict[str, Any] = {'tx': {}}
_blockchain_tx_lock = threading.Lock()

# =============================================================================
# GDPR/AML COMPLIANCE MODULE (Per VTAC Paper Section III)
# =============================================================================
# The paper states: "VTAC's methodology includes sophisticated anonymization 
# techniques to ensure that while transactional data is analyzed for illegality
# indicators, individual privacy remains intact. The system adheres to GDPR by
# implementing data minimization principles."

_compliance_config: Dict[str, Any] = {
    'gdpr_enabled': True,
    'aml_enabled': True,
    'data_minimization': True,
    'access_log_enabled': True,
    'retention_days': 365,
    'authorized_roles': ['admin', 'investigator', 'compliance_officer'],
}

_compliance_access_log: list[Dict[str, Any]] = []
_compliance_lock = threading.Lock()


def get_compliance_config() -> Dict[str, Any]:
    """Get current GDPR/AML compliance configuration."""
    with _compliance_lock:
        return dict(_compliance_config)


def update_compliance_config(gdpr_enabled: bool = None, aml_enabled: bool = None,
                              data_minimization: bool = None, retention_days: int = None) -> Dict[str, Any]:
    """Update compliance configuration settings."""
    with _compliance_lock:
        if gdpr_enabled is not None:
            _compliance_config['gdpr_enabled'] = bool(gdpr_enabled)
        if aml_enabled is not None:
            _compliance_config['aml_enabled'] = bool(aml_enabled)
        if data_minimization is not None:
            _compliance_config['data_minimization'] = bool(data_minimization)
        if retention_days is not None:
            _compliance_config['retention_days'] = max(30, int(retention_days))
        return dict(_compliance_config)


def log_compliance_access(action: str, user_role: str, resource: str, tx_id: Any = None) -> None:
    """Log access to sensitive data for GDPR/AML audit trail."""
    with _compliance_lock:
        if not _compliance_config.get('access_log_enabled', True):
            return
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': str(action),
            'user_role': str(user_role),
            'resource': str(resource),
            'tx_id': str(tx_id) if tx_id else None,
            'gdpr_compliant': _compliance_config.get('gdpr_enabled', True),
            'aml_compliant': _compliance_config.get('aml_enabled', True),
        }
        _compliance_access_log.append(entry)
        # Keep only last 10000 entries
        while len(_compliance_access_log) > 10000:
            _compliance_access_log.pop(0)


def get_compliance_access_log(limit: int = 100) -> list[Dict[str, Any]]:
    """Get recent compliance access log entries."""
    with _compliance_lock:
        return list(_compliance_access_log[-limit:])


def check_data_access_authorized(user_role: str, resource: str) -> bool:
    """Check if a user role is authorized to access a resource per GDPR/AML policies."""
    with _compliance_lock:
        authorized = _compliance_config.get('authorized_roles', [])
        return str(user_role).lower() in [r.lower() for r in authorized]


def anonymize_wallet_hash(wallet_hash: str) -> str:
    """Apply GDPR data minimization by partially anonymizing wallet hashes."""
    with _compliance_lock:
        if not _compliance_config.get('data_minimization', True):
            return wallet_hash
    if not wallet_hash or len(wallet_hash) < 10:
        return wallet_hash
    # Show first 6 and last 4 characters, mask middle
    return f"{wallet_hash[:6]}...{wallet_hash[-4:]}"


# =============================================================================
# CHAINABUSE INTEGRATION (Per VTAC Paper Section V)
# =============================================================================
# The paper references real-world threat evaluation. ChainAbuse is a public
# database of reported scam/fraud addresses. This module provides lookup
# capabilities for known malicious addresses.

_chainabuse_cache: Dict[str, Any] = {'addresses': {}, 'last_update': None}
_chainabuse_lock = threading.Lock()

# Known high-risk address patterns from ChainAbuse reports (sample data)
# In production, this would be fetched from the ChainAbuse API
_KNOWN_MALICIOUS_ADDRESSES: Dict[str, Dict[str, Any]] = {
    '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2': {'category': 'scam', 'reports': 45, 'severity': 'high'},
    '1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF': {'category': 'ransomware', 'reports': 128, 'severity': 'critical'},
    '3HN6AuqJUJZKTmx3YYBmZ47QDuwBxJnYhm': {'category': 'darknet', 'reports': 67, 'severity': 'high'},
    '1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ': {'category': 'mixer', 'reports': 23, 'severity': 'medium'},
}


def check_chainabuse_address(address: str) -> Dict[str, Any]:
    """Check if an address is flagged in ChainAbuse database."""
    with _chainabuse_lock:
        if address in _KNOWN_MALICIOUS_ADDRESSES:
            info = _KNOWN_MALICIOUS_ADDRESSES[address]
            return {
                'flagged': True,
                'address': address,
                'category': info.get('category', 'unknown'),
                'reports': info.get('reports', 0),
                'severity': info.get('severity', 'unknown'),
                'source': 'chainabuse',
            }
        return {
            'flagged': False,
            'address': address,
            'category': None,
            'reports': 0,
            'severity': None,
            'source': 'chainabuse',
        }


def evaluate_chainabuse_risk(addresses: list[str]) -> Dict[str, Any]:
    """Evaluate ChainAbuse risk for a list of addresses (per paper Section V)."""
    flagged_addresses = []
    total_reports = 0
    max_severity = 'low'
    severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
    
    for addr in addresses:
        result = check_chainabuse_address(addr)
        if result.get('flagged'):
            flagged_addresses.append(result)
            total_reports += result.get('reports', 0)
            sev = result.get('severity', 'low')
            if severity_order.get(sev, 0) > severity_order.get(max_severity, 0):
                max_severity = sev
    
    risk_score = 0.0
    if flagged_addresses:
        risk_score = min(1.0, len(flagged_addresses) * 0.3 + total_reports * 0.01)
    
    return {
        'flagged_count': len(flagged_addresses),
        'flagged_addresses': flagged_addresses,
        'total_reports': total_reports,
        'max_severity': max_severity,
        'chainabuse_risk_score': risk_score,
    }

_model_ready = threading.Event()
_model_load_error: Dict[str, str] = {'error': ''}


def _load_model_worker():
    try:
        fraud_model.load()
        _model_ready.set()
    except Exception as e:
        _model_load_error['error'] = str(e)


threading.Thread(target=_load_model_worker, daemon=True).start()


def _ensure_model_ready():
    if _model_ready.is_set():
        return
    if _model_load_error.get('error'):
        raise RuntimeError(f"Model failed to load/train: {_model_load_error['error']}")
    raise RuntimeError('Model is still loading/training. Please wait and try again.')


def get_threshold() -> float:
    return float(_threshold['value'])


def set_threshold(value: float):
    _threshold['value'] = float(value)


def _get_dataset_df() -> pd.DataFrame:
    with _dataset_lock:
        if _dataset_cache['df'] is not None:
            return _dataset_cache['df']
        dataset_path = getattr(config, 'DATASET_PATH', '')
        if not dataset_path or not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")

        if os.path.isdir(dataset_path):
            base_dir = dataset_path
            features_path = os.path.join(base_dir, getattr(config, 'ELLIPTIC_FEATURES_FILE', 'elliptic_txs_features.csv'))
            classes_path = os.path.join(base_dir, getattr(config, 'ELLIPTIC_CLASSES_FILE', 'elliptic_txs_classes.csv'))
            if not (os.path.exists(features_path) and os.path.exists(classes_path)):
                raise FileNotFoundError(f"Elliptic dataset directory detected, but expected files not found: {features_path}, {classes_path}")
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
            df = pd.read_csv(dataset_path)
        _dataset_cache['df'] = df
        return df


def _get_target_col(df: pd.DataFrame) -> str:
    if _dataset_cache.get('target_col'):
        return str(_dataset_cache['target_col'])
    target_col = None
    for col in ['elliptic label', 'elliptic_label', 'is_fraud', 'isFraud', 'Class', 'fraud', 'label']:
        if col in df.columns:
            target_col = col
            break
    if target_col is None:
        raise ValueError('Could not find fraud label column in dataset.')
    _dataset_cache['target_col'] = target_col
    return target_col


def _get_deanonym_map() -> Dict[int, str]:
    with _deanonym_lock:
        cached = _deanonym_cache.get('map')
        if isinstance(cached, dict):
            return cached

        path = str(getattr(config, 'DEANONYM_MAPPING_PATH', '') or '')
        if not path or not os.path.exists(path):
            _deanonym_cache['map'] = {}
            return {}

        df = pd.read_csv(path)
        if 'txId' not in df.columns:
            df.rename(columns={df.columns[0]: 'txId'}, inplace=True)
        if 'transaction' not in df.columns and len(df.columns) >= 2:
            df.rename(columns={df.columns[1]: 'transaction'}, inplace=True)

        df = df[['txId', 'transaction']].dropna()
        out = {int(r['txId']): str(r['transaction']) for _, r in df.iterrows()}
        _deanonym_cache['map'] = out
        return out


def _get_elliptic_edges() -> pd.DataFrame:
    with _elliptic_edges_lock:
        cached = _elliptic_edges_cache.get('edges')
        if isinstance(cached, pd.DataFrame):
            return cached

        base_dir = str(getattr(config, 'ELLIPTIC_DATASET_DIR', '') or '')
        edges_path = os.path.join(base_dir, getattr(config, 'ELLIPTIC_EDGES_FILE', 'elliptic_txs_edgelist.csv'))
        if not base_dir or not os.path.exists(edges_path):
            _elliptic_edges_cache['edges'] = pd.DataFrame(columns=['txId1', 'txId2'])
            return _elliptic_edges_cache['edges']

        edges = pd.read_csv(edges_path)
        if 'txId1' not in edges.columns and len(edges.columns) >= 2:
            edges.rename(columns={edges.columns[0]: 'txId1', edges.columns[1]: 'txId2'}, inplace=True)
        edges = edges[['txId1', 'txId2']].copy()
        _elliptic_edges_cache['edges'] = edges
        return edges


def _get_blockchain_tx(tx_hash: str) -> Dict[str, Any]:
    tx_hash = str(tx_hash)
    with _blockchain_tx_lock:
        cached = _blockchain_tx_cache.get('tx') or {}
        if tx_hash in cached:
            return dict(cached[tx_hash])

    base = str(getattr(config, 'BLOCKCHAIN_LOOKUP_BASE_URL', 'https://blockstream.info/api')).rstrip('/')
    with urlopen(f"{base}/tx/{tx_hash}", timeout=15) as resp:
        tx = json.loads(resp.read().decode('utf-8'))

    fee_sat = int(tx.get('fee') or 0)
    vin = tx.get('vin') or []
    vout = tx.get('vout') or []

    incoming_sat = 0
    in_addrs: list[str] = []
    for i in vin:
        prevout = i.get('prevout') or {}
        incoming_sat += int(prevout.get('value') or 0)
        addr = prevout.get('scriptpubkey_address')
        if addr:
            in_addrs.append(str(addr))

    outgoing_sat = 0
    out_addrs: list[Dict[str, Any]] = []
    for o in vout:
        val = int(o.get('value') or 0)
        outgoing_sat += val
        addr = o.get('scriptpubkey_address')
        if addr:
            out_addrs.append({'address': str(addr), 'value_btc': float(val) / 1e8})

    status = tx.get('status') or {}
    block_time = status.get('block_time')
    block_time_iso = None
    if block_time is not None:
        block_time_iso = datetime.utcfromtimestamp(int(block_time)).isoformat()

    out = {
        'incoming_value_btc': float(incoming_sat) / 1e8,
        'outgoing_value_btc': float(outgoing_sat) / 1e8,
        'fee_btc': float(fee_sat) / 1e8,
        'block_time': block_time_iso,
        'vin_addresses': in_addrs,
        'vout_addresses': out_addrs,
    }

    with _blockchain_tx_lock:
        cached = _blockchain_tx_cache.get('tx')
        if not isinstance(cached, dict):
            cached = {}
            _blockchain_tx_cache['tx'] = cached
        cached[tx_hash] = dict(out)
    return dict(out)


def _elliptic_chain_nodes(tx_id: int, hops: int = 1, max_nodes: int = 250) -> Dict[str, Any]:
    edges = _get_elliptic_edges()
    tx_id_int = int(tx_id)

    incoming_nodes = {tx_id_int}
    outgoing_nodes = {tx_id_int}

    inc_frontier = {tx_id_int}
    out_frontier = {tx_id_int}

    for _ in range(max(0, int(hops))):
        if edges.empty:
            break

        if inc_frontier:
            inc_neighbors = edges[edges['txId2'].isin(list(inc_frontier))]['txId1'].dropna().astype(int).tolist()
            for n in inc_neighbors:
                if len(incoming_nodes) >= max_nodes:
                    break
                incoming_nodes.add(int(n))
            inc_frontier = set(inc_neighbors)

        if out_frontier:
            out_neighbors = edges[edges['txId1'].isin(list(out_frontier))]['txId2'].dropna().astype(int).tolist()
            for n in out_neighbors:
                if len(outgoing_nodes) >= max_nodes:
                    break
                outgoing_nodes.add(int(n))
            out_frontier = set(out_neighbors)

        if len(incoming_nodes) >= max_nodes and len(outgoing_nodes) >= max_nodes:
            break

    return {
        'incoming_nodes': sorted(list(incoming_nodes)),
        'outgoing_nodes': sorted(list(outgoing_nodes)),
    }


def vtac_identification_from_elliptic(tx_id: int, hops: int = 1) -> Dict[str, Any]:
    df = _get_dataset_df()
    if 'txId' not in df.columns:
        return {'tx_id': int(tx_id), 'error': 'Dataset has no txId column'}

    edges = _get_elliptic_edges()
    if edges.empty:
        return {'tx_id': int(tx_id), 'error': 'No elliptic edge list available'}

    tx_id_int = int(tx_id)
    in_edges = edges[edges['txId2'] == tx_id_int]
    out_edges = edges[edges['txId1'] == tx_id_int]

    incoming = int(len(in_edges))
    outgoing = int(len(out_edges))

    chain = _elliptic_chain_nodes(tx_id_int, hops=int(hops), max_nodes=250)

    time_interval = None
    if 'time_step' in df.columns:
        steps = []
        for _n in set(chain.get('incoming_nodes', []) + chain.get('outgoing_nodes', [])):
            try:
                steps.append(int(df.loc[df['txId'] == int(_n), 'time_step'].iloc[0]))
            except Exception:
                continue
        if len(steps) >= 2:
            time_interval = int(max(steps) - min(steps))

    deanonym_map = _get_deanonym_map()
    deanonym = deanonym_map.get(tx_id_int)

    advisory: Dict[str, Any] = {}
    beneficiary_candidates: list[Dict[str, Any]] = []
    if bool(getattr(config, 'ENABLE_BLOCKCHAIN_LOOKUP', False)) and deanonym:
        try:
            incoming_value_total = 0.0
            outgoing_value_total = 0.0
            fee_total = 0.0
            out_addr_totals: Dict[str, float] = {}
            block_times: list[datetime] = []

            node_ids = []
            seen_ids = set()
            for _n in chain.get('incoming_nodes', []) + chain.get('outgoing_nodes', []):
                try:
                    nid = int(_n)
                except Exception:
                    continue
                if nid in seen_ids:
                    continue
                seen_ids.add(nid)
                node_ids.append(nid)

            lookups = 0
            for _n in node_ids:
                if lookups >= 40:
                    break
                txh = deanonym_map.get(int(_n))
                if not txh:
                    continue
                el = _get_blockchain_tx(txh)
                lookups += 1
                incoming_value_total += float(el.get('incoming_value_btc') or 0.0)
                outgoing_value_total += float(el.get('outgoing_value_btc') or 0.0)
                fee_total += float(el.get('fee_btc') or 0.0)
                bt = el.get('block_time')
                if bt:
                    try:
                        block_times.append(datetime.fromisoformat(str(bt)))
                    except Exception:
                        pass
                for o in el.get('vout_addresses') or []:
                    addr = str(o.get('address') or '')
                    if not addr:
                        continue
                    out_addr_totals[addr] = out_addr_totals.get(addr, 0.0) + float(o.get('value_btc') or 0.0)

            beneficiary_candidates = [
                {'address': a, 'total_received_btc': v}
                for a, v in sorted(out_addr_totals.items(), key=lambda kv: kv[1], reverse=True)[:10]
            ]

            time_window_blockchain: Dict[str, Any] = {}
            if len(block_times) >= 2:
                start_bt = min(block_times)
                end_bt = max(block_times)
                time_window_blockchain = {
                    'start': start_bt.isoformat(),
                    'end': end_bt.isoformat(),
                    'seconds': float((end_bt - start_bt).total_seconds()),
                }
            elif len(block_times) == 1:
                only_bt = block_times[0]
                time_window_blockchain = {
                    'start': only_bt.isoformat(),
                    'end': only_bt.isoformat(),
                    'seconds': 0.0,
                }

            advisory = {
                'incoming_value_total_btc': float(incoming_value_total),
                'outgoing_value_total_btc': float(outgoing_value_total),
                'fee_total_btc': float(fee_total),
                'time_window_blockchain': time_window_blockchain,
            }
        except Exception as e:
            advisory = {'error': str(e)}

    local_degree = incoming + outgoing
    weight_factor = float(max(0.0, min(1.0, local_degree / 50.0)))

    value_fields: Dict[str, Any] = {}
    if isinstance(advisory, dict) and advisory:
        if 'error' in advisory:
            value_fields = {'error': advisory.get('error')}
        else:
            value_fields = {
                'incoming_total_btc': advisory.get('incoming_value_total_btc'),
                'outgoing_total_btc': advisory.get('outgoing_value_total_btc'),
                'fee_total_btc': advisory.get('fee_total_btc'),
                'time_window_blockchain': advisory.get('time_window_blockchain'),
            }

    return {
        'tx_id': tx_id_int,
        'incoming_edges': incoming,
        'outgoing_edges': outgoing,
        'chain': chain,
        'time_interval_steps': time_interval,
        'weight_factor': weight_factor,
        'deanonymized_tx_hash': deanonym,
        'advisory': advisory,
        'beneficiaries': beneficiary_candidates,
        'frequency': {'incoming': incoming, 'outgoing': outgoing},
        'time_window_steps': time_interval,
        'time_window': time_interval,
        'value': value_fields,
    }


def predict_elliptic_txid(tx_id: int) -> Dict[str, Any]:
    _ensure_model_ready()
    df = _get_dataset_df()
    if 'txId' not in df.columns:
        raise ValueError('Current dataset is not Elliptic (no txId column).')

    tx_id_int = int(tx_id)
    rows = df[df['txId'] == tx_id_int]
    if rows.empty:
        raise ValueError(f'txId {tx_id_int} not found in dataset')
    row = rows.iloc[0]

    txn: Dict[str, Any] = {
        'txn_id': f'ELLIPTIC-{tx_id_int}',
        'user_id': 'elliptic',
        'amount': 0.0,
        'txn_type': 'elliptic',
        'timestamp': datetime.utcnow().isoformat(),
        'location': 'Elliptic',
        'device_id': 'Elliptic',
    }

    deanonym = _get_deanonym_map().get(tx_id_int)
    if deanonym:
        txn['tx_hash'] = deanonym

    for fname in fraud_model.feature_names:
        if fname in row.index:
            try:
                txn[fname] = float(row[fname])
            except Exception:
                continue

    ml_score = float(fraud_model.predict_proba(txn))
    is_illegal = 1 if ml_score >= get_threshold() else 0
    identification = vtac_identification_from_elliptic(tx_id_int)

    return {
        'tx_id': tx_id_int,
        'score': ml_score,
        'classification': 'illegal' if is_illegal else 'legal',
        'threshold': float(get_threshold()),
        'deanonymized_tx_hash': deanonym,
        'identification': identification,
    }


def _rule_risk_score(txn: Dict[str, Any]) -> float:
    amount = 0.0
    try:
        amount = float(txn.get('amount', 0.0))
    except Exception:
        amount = 0.0

    txn_type = str(txn.get('txn_type') or '').lower()
    location = str(txn.get('location') or '').strip().lower()
    device_id = str(txn.get('device_id') or '').strip().lower()

    score = 0.0

    if amount >= 1000000:
        score += 0.65
    elif amount >= 250000:
        score += 0.45
    elif amount >= 50000:
        score += 0.25

    if txn_type in {'transfer', 'withdrawal'}:
        score += 0.15
    elif txn_type in {'payment'}:
        score += 0.05

    if location in {'unknown', ''}:
        score += 0.10

    if device_id in {'unknown', ''}:
        score += 0.10

    try:
        recent = database.fetch_recent_transactions(limit=200)
        user_id = txn.get('user_id')
        if user_id:
            user_rows = [r for r in recent if r[1] == user_id]
            if user_rows:
                amounts = [float(r[2]) for r in user_rows if r[2] is not None]
                if len(amounts) >= 5:
                    med = float(np.median(amounts))
                    if med > 0 and amount >= 5.0 * med:
                        score += 0.25
                devices = {str(r[6]).lower() for r in user_rows if r[6]}
                if device_id and device_id not in devices and len(devices) >= 2:
                    score += 0.20
                locations = {str(r[5]).lower() for r in user_rows if r[5]}
                if location and location not in locations and len(locations) >= 2:
                    score += 0.15
    except Exception:
        pass

    return float(max(0.0, min(1.0, score)))


def _rule_reasons(txn: Dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    try:
        amount = float(txn.get('amount', 0.0))
    except Exception:
        amount = 0.0

    txn_type = str(txn.get('txn_type') or '').lower()
    location = str(txn.get('location') or '').strip().lower()
    device_id = str(txn.get('device_id') or '').strip().lower()

    if amount >= 1000000:
        reasons.append('Very high transaction amount')
    elif amount >= 250000:
        reasons.append('High transaction amount')
    elif amount >= 50000:
        reasons.append('Unusually large amount')

    if txn_type in {'transfer', 'withdrawal'}:
        reasons.append(f'High-risk transaction type: {txn_type}')

    if location in {'unknown', ''}:
        reasons.append('Location not provided / unknown')

    if device_id in {'unknown', ''}:
        reasons.append('Device ID not provided / unknown')

    try:
        recent = database.fetch_recent_transactions(limit=200)
        user_id = txn.get('user_id')
        if user_id:
            user_rows = [r for r in recent if r[1] == user_id]
            if user_rows:
                amounts = [float(r[2]) for r in user_rows if r[2] is not None]
                if len(amounts) >= 5:
                    med = float(np.median(amounts))
                    if med > 0 and amount >= 5.0 * med:
                        reasons.append('Amount is a large spike compared to this user\'s recent activity')
                devices = {str(r[6]).lower() for r in user_rows if r[6]}
                if device_id and device_id not in devices and len(devices) >= 2:
                    reasons.append('New device for this user')
                locations = {str(r[5]).lower() for r in user_rows if r[5]}
                if location and location not in locations and len(locations) >= 2:
                    reasons.append('New location for this user')
    except Exception:
        pass

    return reasons


def _build_human_explanation(txn: Dict[str, Any], ml_score: float, rule_score: float) -> str:
    reasons = _rule_reasons(txn)
    parts: list[str] = []
    if reasons:
        parts.append('Reasons: ' + '; '.join(reasons))
    parts.append(f'Risk signals: ML={ml_score:.3f}, Rules={rule_score:.3f}')
    try:
        shap_hint = fraud_model.explain(txn)
        if shap_hint:
            parts.append(shap_hint)
    except Exception:
        pass
    return ' | '.join(parts)


def _combine_scores(ml_score: float, rule_score: float) -> float:
    ml_score = float(max(0.0, min(1.0, ml_score)))
    rule_score = float(max(0.0, min(1.0, rule_score)))
    return float(max(ml_score, 0.55 * ml_score + 0.45 * rule_score, rule_score * 0.95))


def get_model_status() -> Dict[str, str]:
    if _model_ready.is_set():
        return {'status': 'ready', 'error': ''}
    err = _model_load_error.get('error') or ''
    if err:
        return {'status': 'error', 'error': err}
    return {'status': 'loading', 'error': ''}


class TransactionInput(BaseModel):
    amount: float
    txn_type: str
    location: str
    device_id: str


class CryptoTransactionInput(BaseModel):
    sender_hash: str
    receiver_hash: str
    tx_hash: str
    asset: str = 'BTC'
    network: str = 'bitcoin'
    amount: float
    tx_fee: float = 0.0


def simulate_txn_id() -> str:
    return f"TXN-{int(datetime.utcnow().timestamp() * 1000)}"


def simulate_user_id() -> str:
    return f"USER-{np.random.randint(1000, 9999)}"


def simulate_case_id() -> str:
    return f"CASE-{int(datetime.utcnow().timestamp() * 1000)}"


def _vtac_frequency_score(sender_hash: str, now: datetime, window_minutes: int = 60) -> tuple[float, int]:
    """
    VTAC Frequency Analysis (Per Paper Section III & IV):
    "A high frequency of transactions over short periods of time may indicate
    layering, in which illicit monies are divided into smaller amounts and moved
    through multiple transactions to make them more difficult to trace."
    
    Formula: F(t) = min(1.0, n_transactions / threshold_max)
    Where threshold_max is empirically set based on typical legitimate user behavior.
    """
    since = (now - timedelta(minutes=window_minutes)).isoformat()
    rows = database.fetch_crypto_by_sender(sender_hash=sender_hash, since_ts=since, limit=2000)
    freq = max(0, len(rows))
    
    # Paper-aligned thresholds based on layering detection patterns
    FREQ_THRESHOLD_MAX = 25  # Transactions suggesting structured layering activity
    score = min(1.0, float(freq) / float(FREQ_THRESHOLD_MAX))
    return score, freq


def _vtac_value_score(amount: float) -> float:
    """
    VTAC Value Analysis (Per Paper Section IV - Advisory Framework):
    "The value of the outgoing and incoming transaction" is a key factor.
    "Large transactions or ones that depart significantly from a user's normal
    transaction profile may suggest money laundering or fraudulent conduct."
    
    Formula: V(a) = log(1 + amount) / log(1 + threshold_max)
    Normalized logarithmic scale to handle wide range of transaction values.
    """
    if amount <= 0:
        return 0.0
    
    # Paper-aligned: uses logarithmic scaling for value normalization
    import math
    THRESHOLD_MAX_BTC = 100.0  # High-value transaction threshold in BTC
    score = math.log(1 + float(amount)) / math.log(1 + THRESHOLD_MAX_BTC)
    return float(max(0.0, min(1.0, score)))


def _vtac_time_window_score(time_delta_seconds: float) -> float:
    """
    VTAC Time Window Analysis (Per Paper Section IV):
    "The time between the first outgoing transaction in the chain and the last
    incoming transaction in the chain" indicates structuring behavior.
    
    Short time windows suggest rapid movement of funds (layering).
    Formula: T(dt) = max(0, 1 - dt / window_threshold)
    """
    if time_delta_seconds < 0:
        return 0.0
    
    # Paper-aligned: rapid transactions within 1 hour are suspicious
    WINDOW_THRESHOLD_SECONDS = 3600.0  # 1 hour
    if time_delta_seconds >= WINDOW_THRESHOLD_SECONDS:
        return 0.0
    
    score = 1.0 - (float(time_delta_seconds) / WINDOW_THRESHOLD_SECONDS)
    return float(max(0.0, min(1.0, score)))


def _vtac_weight_factor(amount: float, tx_fee: float, chain_depth: int = 1) -> float:
    """
    VTAC Weight Factor (Per Paper Section IV - Advisory Framework):
    "The weight factor indicating the importance of the transactions in the block
    chains that is used to find beneficiaries."
    
    Formula: W(a, f, d) = alpha * V(a) + beta * (f/a) + gamma * log(1+d)
    Where:
      - V(a) is value score
      - f/a is fee ratio (high fees suggest urgency/priority)
      - d is chain depth (transactions in deeper chains may indicate layering)
    
    Paper coefficients (empirically derived):
      alpha = 0.5 (value weight)
      beta = 0.3 (fee ratio weight)  
      gamma = 0.2 (chain depth weight)
    """
    import math
    
    ALPHA = 0.5  # Value component weight
    BETA = 0.3   # Fee ratio component weight
    GAMMA = 0.2  # Chain depth component weight
    
    # Value component
    value_component = _vtac_value_score(float(amount))
    
    # Fee ratio component (high fee ratio indicates priority/urgency)
    try:
        fee_ratio = float(tx_fee) / max(1e-9, float(amount))
        fee_component = min(1.0, fee_ratio * 20.0)  # Normalize: 5% fee = max score
    except Exception:
        fee_component = 0.0
    
    # Chain depth component (deeper chains suggest structuring)
    depth_component = min(1.0, math.log(1 + float(chain_depth)) / math.log(11))  # log(11) ≈ 2.4
    
    weight = ALPHA * value_component + BETA * fee_component + GAMMA * depth_component
    return float(max(0.0, min(1.0, weight)))


def compute_vtac_advisory_score(value_score: float, frequency_score: float, 
                                 time_window_score: float, weight_factor: float) -> float:
    """
    VTAC Combined Advisory Score (Per Paper Section IV):
    Combines all four advisory signals into a unified risk assessment.
    
    Formula: A = w1*V + w2*F + w3*T + w4*W
    Paper weights (Section V evaluation):
      w1 = 0.30 (value)
      w2 = 0.30 (frequency)
      w3 = 0.25 (time window)
      w4 = 0.15 (weight factor)
    """
    W1, W2, W3, W4 = 0.30, 0.30, 0.25, 0.15  # Paper-aligned weights
    
    score = (
        W1 * float(value_score) +
        W2 * float(frequency_score) +
        W3 * float(time_window_score) +
        W4 * float(weight_factor)
    )
    return float(max(0.0, min(1.0, score)))


def handle_crypto_transaction(sender_hash: str, receiver_hash: str, tx_hash: str,
                              amount: float, tx_fee: float = 0.0,
                              asset: str = 'BTC', network: str = 'bitcoin'):
    _ensure_model_ready()
    try:
        validated = CryptoTransactionInput(
            sender_hash=sender_hash,
            receiver_hash=receiver_hash,
            tx_hash=tx_hash,
            asset=asset,
            network=network,
            amount=amount,
            tx_fee=tx_fee,
        )
    except ValidationError as e:
        raise ValueError(str(e))

    now = datetime.utcnow()
    freq_score, freq = _vtac_frequency_score(validated.sender_hash, now)
    value_score = _vtac_value_score(float(validated.amount))
    weight = _vtac_weight_factor(float(validated.amount), float(validated.tx_fee))

    txn: Dict[str, Any] = {
        'txn_id': simulate_txn_id(),
        'user_id': f"WALLET-{validated.sender_hash[:10]}",
        'sender_hash': validated.sender_hash,
        'receiver_hash': validated.receiver_hash,
        'tx_hash': validated.tx_hash,
        'asset': validated.asset,
        'network': validated.network,
        'tx_fee': float(validated.tx_fee),
        'amount': float(validated.amount),
        'txn_type': 'crypto',
        'timestamp': now.isoformat(),
        'location': 'Blockchain',
        'device_id': 'Blockchain',
        'vtac_value_score': float(value_score),
        'vtac_frequency_score': float(freq_score),
        'vtac_weight_factor': float(weight),
        'vtac_freq_last_60m': int(freq),
    }

    ml_score = fraud_model.predict_proba(txn)
    vtac_score = float(max(0.0, min(1.0, 0.45 * value_score + 0.35 * freq_score + 0.20 * weight)))
    fraud_score = float(max(ml_score, vtac_score))
    is_fraud = 1 if fraud_score >= get_threshold() else 0

    database.insert_transaction(txn, fraud_score, is_fraud)

    explanation = (
        f"VTAC signals: value={value_score:.2f}, freq={freq_score:.2f} (n={freq}), weight={weight:.2f} | "
        f"ML={ml_score:.3f} | Final={fraud_score:.3f}"
    )
    if is_fraud:
        case_id = simulate_case_id()
        database.insert_alert(txn, fraud_score, explanation, case_id)
        blockchain.add_block(txn_id=txn['txn_id'], fraud_score=fraud_score, explanation=explanation)

    return txn, fraud_score, is_fraud, explanation


def handle_new_transaction(amount: float, txn_type: str,
                           location: str, device_id: str):
    _ensure_model_ready()
    try:
        validated = TransactionInput(
            amount=amount,
            txn_type=txn_type,
            location=location,
            device_id=device_id,
        )
    except ValidationError as e:
        raise ValueError(str(e))

    txn: Dict[str, Any] = {
        'txn_id': simulate_txn_id(),
        'user_id': simulate_user_id(),
        'amount': float(validated.amount),
        'txn_type': validated.txn_type,
        'timestamp': datetime.utcnow().isoformat(),
        'location': validated.location,
        'device_id': validated.device_id,
    }

    ml_score = fraud_model.predict_proba(txn)
    rule_score = _rule_risk_score(txn)
    fraud_score = _combine_scores(ml_score, rule_score)
    is_fraud = 1 if fraud_score >= get_threshold() else 0
    database.insert_transaction(txn, fraud_score, is_fraud)

    explanation = ''
    if is_fraud:
        explanation = _build_human_explanation(txn, ml_score=ml_score, rule_score=rule_score)
        case_id = simulate_case_id()
        database.insert_alert(txn, fraud_score, explanation, case_id)
        blockchain.add_block(txn_id=txn['txn_id'], fraud_score=fraud_score, explanation=explanation)

    return txn, fraud_score, is_fraud, explanation


def handle_dataset_transaction(want_fraud: bool):
    _ensure_model_ready()
    df = _get_dataset_df()
    target_col = _get_target_col(df)

    if target_col in {'elliptic label', 'elliptic_label'}:
        y_raw = df[target_col]
        if pd.api.types.is_numeric_dtype(y_raw):
            y_num = y_raw.astype('Int64')
            known_mask = ~y_num.isna() & ~y_num.isin([3])
            df = df.loc[known_mask].copy()
            y_num = y_num.loc[known_mask]
            uniq = set([int(v) for v in y_num.dropna().unique().tolist()])
            if uniq <= {1, 2}:
                y = (y_num == 1).astype(int)
            else:
                y = (y_num == 1).astype(int)
        else:
            y_str = y_raw.astype(str).str.strip().str.lower()
            known_mask = ~y_str.isin(['unknown', 'nan', 'none', ''])
            df = df.loc[known_mask].copy()
            y_str = y_str.loc[known_mask]
            y = y_str.map({'1': 1, '2': 0, 'illegal': 1, 'illicit': 1, 'legal': 0, 'licit': 0}).astype('Int64')
            known_mask_2 = ~y.isna()
            df = df.loc[known_mask_2].copy()
            y = y.loc[known_mask_2].astype(int)
    else:
        y = df[target_col].astype(int)

    candidates = df[y == (1 if want_fraud else 0)]
    if candidates.empty:
        raise ValueError('No matching rows found in dataset for requested class.')
    row = candidates.sample(n=1, random_state=int(datetime.utcnow().timestamp()) % 1000000).iloc[0]
    txn: Dict[str, Any] = {
        'txn_id': simulate_txn_id(),
        'user_id': simulate_user_id(),
        'amount': float(row['Amount']) if 'Amount' in row.index else 0.0,
        'txn_type': 'dataset',
        'timestamp': datetime.utcnow().isoformat(),
        'location': 'Dataset',
        'device_id': 'Dataset',
    }

    if 'txId' in row.index:
        try:
            tx_id_int = int(row['txId'])
            deanonym = _get_deanonym_map().get(tx_id_int)
            if deanonym:
                txn['tx_hash'] = deanonym
        except Exception:
            pass
    for fname in fraud_model.feature_names:
        if fname in row.index:
            try:
                txn[fname] = float(row[fname])
            except Exception:
                continue

    ml_score = fraud_model.predict_proba(txn)
    rule_score = 0.0
    fraud_score = ml_score
    is_fraud = 1 if fraud_score >= get_threshold() else 0
    database.insert_transaction(txn, fraud_score, is_fraud)

    explanation = ''
    if is_fraud:
        explanation = _build_human_explanation(txn, ml_score=ml_score, rule_score=rule_score)
        case_id = simulate_case_id()
        database.insert_alert(txn, fraud_score, explanation, case_id)
        blockchain.add_block(txn_id=txn['txn_id'], fraud_score=fraud_score, explanation=explanation)

    if target_col in {'elliptic label', 'elliptic_label'}:
        try:
            raw = row[target_col]
            if pd.isna(raw) or str(raw).strip().lower() == 'unknown':
                actual_label = 0
            else:
                v = int(raw)
                actual_label = 1 if v == 1 else 0
        except Exception:
            actual_label = 0
    else:
        actual_label = int(row[target_col])
    return txn, fraud_score, is_fraud, explanation, actual_label


def get_recent_transactions(limit: int = 50):
    return database.fetch_recent_transactions(limit)


def get_alerts(limit: int = 50):
    return database.fetch_alerts(limit)


def get_blocks(limit: int = 1000):
    return database.fetch_blocks(limit)


def verify_chain() -> bool:
    return blockchain.is_chain_valid()


def export_ledger() -> str:
    blockchain.export_ledger()
    return config.LEDGER_EXPORT_PATH


def get_fraud_summary():
    total, fraud_cnt = database.get_stats()
    rate = (fraud_cnt / total * 100.0) if total > 0 else 0.0
    return total, fraud_cnt, rate


def get_model_report_text() -> str:
    try:
        with open(config.REPORT_EXPORT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'No report file yet. Train has not been run or report not saved.'


def export_feature_importance() -> str:
    return fraud_model.plot_global_importance()


def retrain_model():
    if not _model_ready.is_set() and _model_load_error.get('error'):
        _model_load_error['error'] = ''
    _model_ready.clear()

    def _retrain_worker():
        try:
            fraud_model.train_and_save()
            fraud_model.load()
            _model_ready.set()
        except Exception as e:
            _model_load_error['error'] = str(e)

    threading.Thread(target=_retrain_worker, daemon=True).start()


def get_model_comparison_text() -> str:
    try:
        with open(config.MODEL_COMPARISON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return 'No model comparison data yet. Train has not been run or comparison not saved.'
    return json.dumps(data, indent=2)


def get_active_model_info() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        'model_type': str(getattr(config, 'MODEL_TYPE', 'random_forest')),
        'dataset_path': str(getattr(config, 'DATASET_PATH', '')),
        'threshold': float(get_threshold()),
        'use_smote': bool(getattr(config, 'USE_SMOTE', True)),
        'test_size': float(getattr(config, 'TEST_SIZE', 0.2)),
        'val_size': float(getattr(config, 'VAL_SIZE', 0.1)),
        'cv_folds': int(getattr(config, 'CV_FOLDS', 10)),
    }
    try:
        with open(config.MODEL_COMPARISON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        info['model_comparison'] = data
    except Exception:
        info['model_comparison'] = {}
    return info


def get_time_evolution(window_hours: int = 24, window_days: int = 30) -> Dict[str, Any]:
    rows = database.fetch_all_transactions()
    if not rows:
        return {
            'hourly': {'labels': [], 'total': [], 'fraud': []},
            'daily': {'labels': [], 'total': [], 'fraud': []},
        }

    df = pd.DataFrame(
        rows,
        columns=[
            'txn_id',
            'user_id',
            'amount',
            'txn_type',
            'timestamp',
            'location',
            'device_id',
            'is_fraud',
            'fraud_score',
        ],
    )
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)
    df = df.dropna(subset=['timestamp'])
    if df.empty:
        return {
            'hourly': {'labels': [], 'total': [], 'fraud': []},
            'daily': {'labels': [], 'total': [], 'fraud': []},
        }

    now = pd.Timestamp.utcnow()
    start_hourly = now - pd.Timedelta(hours=int(window_hours))
    start_daily = now - pd.Timedelta(days=int(window_days))

    df_h = df[df['timestamp'] >= start_hourly].copy()
    if not df_h.empty:
        hourly_total = df_h.set_index('timestamp')['txn_id'].resample('H').count()
        hourly_fraud = df_h.set_index('timestamp')['is_fraud'].resample('H').sum()
    else:
        hourly_total = pd.Series(dtype=float)
        hourly_fraud = pd.Series(dtype=float)

    df_d = df[df['timestamp'] >= start_daily].copy()
    if not df_d.empty:
        daily_total = df_d.set_index('timestamp')['txn_id'].resample('D').count()
        daily_fraud = df_d.set_index('timestamp')['is_fraud'].resample('D').sum()
    else:
        daily_total = pd.Series(dtype=float)
        daily_fraud = pd.Series(dtype=float)

    return {
        'hourly': {
            'labels': [t.strftime('%H:%M') for t in hourly_total.index],
            'total': [int(v) for v in hourly_total.values],
            'fraud': [int(v) for v in hourly_fraud.reindex(hourly_total.index, fill_value=0).values],
        },
        'daily': {
            'labels': [t.strftime('%Y-%m-%d') for t in daily_total.index],
            'total': [int(v) for v in daily_total.values],
            'fraud': [int(v) for v in daily_fraud.reindex(daily_total.index, fill_value=0).values],
        },
    }


def export_fraud_time_series_chart() -> str:
    rows = database.fetch_recent_transactions(limit=1000)
    if not rows:
        raise ValueError('No transactions available for analytics.')
    df = pd.DataFrame(
        rows,
        columns=[
            'txn_id',
            'user_id',
            'amount',
            'txn_type',
            'timestamp',
            'location',
            'device_id',
            'is_fraud',
            'fraud_score',
        ],
    )
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    if df.empty:
        raise ValueError('No valid timestamps available for analytics.')
    series = df.set_index('timestamp')['is_fraud'].resample('D').sum()
    os.makedirs(config.CHARTS_EXPORT_DIR, exist_ok=True)
    path = os.path.join(config.CHARTS_EXPORT_DIR, 'fraud_time_series.png')
    plt.figure(figsize=(8, 4))
    sns.lineplot(x=series.index, y=series.values)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path


def export_transactions_csv() -> str:
    rows = database.fetch_all_transactions()
    if not rows:
        raise ValueError('No transactions available for export.')
    df = pd.DataFrame(
        rows,
        columns=[
            'txn_id',
            'user_id',
            'amount',
            'txn_type',
            'timestamp',
            'location',
            'device_id',
            'is_fraud',
            'fraud_score',
        ],
    )
    os.makedirs(config.CHARTS_EXPORT_DIR, exist_ok=True)
    path = os.path.join(config.CHARTS_EXPORT_DIR, 'transactions_export.csv')
    df.to_csv(path, index=False)
    return path


def export_alerts_csv() -> str:
    rows = database.fetch_all_alerts()
    if not rows:
        raise ValueError('No alerts available for export.')
    df = pd.DataFrame(
        rows,
        columns=[
            'case_id',
            'txn_id',
            'user_id',
            'amount',
            'fraud_score',
            'explanation',
            'timestamp',
        ],
    )
    os.makedirs(config.CHARTS_EXPORT_DIR, exist_ok=True)
    path = os.path.join(config.CHARTS_EXPORT_DIR, 'alerts_export.csv')
    df.to_csv(path, index=False)
    return path


def export_full_backup() -> str:
    os.makedirs(config.CHARTS_EXPORT_DIR, exist_ok=True)
    backup_path = os.path.join(config.CHARTS_EXPORT_DIR, 'proofledger_backup.zip')
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(config.DB_PATH):
            zf.write(config.DB_PATH, arcname=os.path.basename(config.DB_PATH))
        if os.path.isdir(config.CHARTS_EXPORT_DIR):
            base_dir = os.path.dirname(config.CHARTS_EXPORT_DIR)
            for root, dirs, files in os.walk(config.CHARTS_EXPORT_DIR):
                for name in files:
                    full_path = os.path.join(root, name)
                    rel_path = os.path.relpath(full_path, base_dir)
                    zf.write(full_path, arcname=rel_path)
    return backup_path


def export_fraud_by_location_chart() -> str:
    rows = database.fetch_recent_transactions(limit=1000)
    if not rows:
        raise ValueError('No transactions available for analytics.')
    df = pd.DataFrame(
        rows,
        columns=[
            'txn_id',
            'user_id',
            'amount',
            'txn_type',
            'timestamp',
            'location',
            'device_id',
            'is_fraud',
            'fraud_score',
        ],
    )
    if df.empty:
        raise ValueError('No data available for analytics.')
    grouped = df.groupby('location')['is_fraud'].sum().sort_values(ascending=False).head(20)
    os.makedirs(config.CHARTS_EXPORT_DIR, exist_ok=True)
    path = os.path.join(config.CHARTS_EXPORT_DIR, 'fraud_by_location.png')
    plt.figure(figsize=(8, 4))
    sns.barplot(x=grouped.index, y=grouped.values)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path
