import sqlite3
from typing import Any, Dict, List

from . import config


def get_conn():
    return sqlite3.connect(config.DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # transactions table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            txn_id TEXT,
            user_id TEXT,
            sender_hash TEXT,
            receiver_hash TEXT,
            tx_hash TEXT,
            asset TEXT,
            network TEXT,
            tx_fee REAL,
            amount REAL,
            txn_type TEXT,
            timestamp TEXT,
            location TEXT,
            device_id TEXT,
            is_fraud INTEGER,
            fraud_score REAL
        );
        """
    )

    # alerts table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            txn_id TEXT,
            user_id TEXT,
            amount REAL,
            fraud_score REAL,
            explanation TEXT,
            timestamp TEXT
        );
        """
    )

    # blocks table (blockchain ledger)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_index INTEGER,
            txn_id TEXT,
            timestamp TEXT,
            fraud_score REAL,
            explanation_hash TEXT,
            prev_hash TEXT,
            current_hash TEXT,
            signature TEXT
        );
        """
    )

    cur.execute("PRAGMA table_info(blocks)")
    cols = [r[1] for r in cur.fetchall()]
    if 'signature' not in cols:
        cur.execute("ALTER TABLE blocks ADD COLUMN signature TEXT")

    cur.execute("PRAGMA table_info(alerts)")
    cols = [r[1] for r in cur.fetchall()]
    if 'case_id' not in cols:
        cur.execute("ALTER TABLE alerts ADD COLUMN case_id TEXT")

    cur.execute("PRAGMA table_info(transactions)")
    cols = [r[1] for r in cur.fetchall()]
    for col_name, col_type in [
        ('sender_hash', 'TEXT'),
        ('receiver_hash', 'TEXT'),
        ('tx_hash', 'TEXT'),
        ('asset', 'TEXT'),
        ('network', 'TEXT'),
        ('tx_fee', 'REAL'),
    ]:
        if col_name not in cols:
            cur.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()


def insert_transaction(txn: Dict[str, Any], fraud_score: float, is_fraud: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO transactions (
            txn_id, user_id, sender_hash, receiver_hash, tx_hash, asset, network, tx_fee,
            amount, txn_type, timestamp, location, device_id, is_fraud, fraud_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            txn['txn_id'],
            txn['user_id'],
            txn.get('sender_hash'),
            txn.get('receiver_hash'),
            txn.get('tx_hash'),
            txn.get('asset'),
            txn.get('network'),
            txn.get('tx_fee'),
            txn['amount'],
            txn['txn_type'],
            txn['timestamp'],
            txn['location'],
            txn['device_id'],
            is_fraud,
            fraud_score,
        ),
    )
    conn.commit()
    conn.close()


def fetch_crypto_by_sender(sender_hash: str, since_ts: str, limit: int = 1000):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT txn_id, sender_hash, receiver_hash, amount, timestamp
        FROM transactions
        WHERE sender_hash = ? AND timestamp >= ?
        ORDER BY timestamp ASC
        LIMIT ?;
        """,
        (sender_hash, since_ts, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def insert_alert(txn: Dict[str, Any], fraud_score: float, explanation: str, case_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO alerts (
            txn_id, user_id, amount, fraud_score, explanation, timestamp, case_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            txn['txn_id'],
            txn['user_id'],
            txn['amount'],
            fraud_score,
            explanation,
            txn['timestamp'],
            case_id,
        ),
    )
    conn.commit()
    conn.close()


def insert_block(block_index: int, txn_id: str, timestamp: str,
                 fraud_score: float, explanation_hash: str,
                 prev_hash: str, current_hash: str, signature: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO blocks (
            block_index, txn_id, timestamp, fraud_score,
            explanation_hash, prev_hash, current_hash, signature
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            block_index,
            txn_id,
            timestamp,
            fraud_score,
            explanation_hash,
            prev_hash,
            current_hash,
            signature,
        ),
    )
    conn.commit()
    conn.close()


def fetch_recent_transactions(limit: int = 50):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT txn_id, user_id, amount, txn_type, timestamp, location,
               device_id, is_fraud, fraud_score
        FROM transactions
        ORDER BY id DESC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_alerts(limit: int = 50):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT case_id, txn_id, user_id, amount, fraud_score, explanation, timestamp
        FROM alerts
        ORDER BY id DESC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_blocks(limit: int = 1000):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT block_index, txn_id, timestamp, fraud_score,
               explanation_hash, prev_hash, current_hash, signature
        FROM blocks
        ORDER BY block_index ASC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_all_transactions():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT txn_id, user_id, amount, txn_type, timestamp, location,
               device_id, is_fraud, fraud_score
        FROM transactions
        ORDER BY id ASC;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_all_alerts():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT case_id, txn_id, user_id, amount, fraud_score, explanation, timestamp
        FROM alerts
        ORDER BY id ASC;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*), SUM(is_fraud) FROM transactions')
    total, fraud_cnt = cur.fetchone()
    conn.close()
    total = total or 0
    fraud_cnt = fraud_cnt or 0
    return total, fraud_cnt
