from nicegui import ui, app
from pydantic import BaseModel

from app import ui as app_ui
from app.animations_page import create_animations_page
from app import services


class CryptoPredictRequest(BaseModel):
    sender_hash: str
    receiver_hash: str
    tx_hash: str
    amount: float
    tx_fee: float = 0.0
    asset: str = 'BTC'
    network: str = 'bitcoin'


@app.post('/api/predict_crypto')
def predict_crypto(req: CryptoPredictRequest):
    txn, score, is_fraud, explanation = services.handle_crypto_transaction(
        sender_hash=req.sender_hash,
        receiver_hash=req.receiver_hash,
        tx_hash=req.tx_hash,
        amount=req.amount,
        tx_fee=req.tx_fee,
        asset=req.asset,
        network=req.network,
    )
    return {
        'txn_id': txn.get('txn_id'),
        'sender_hash': txn.get('sender_hash'),
        'receiver_hash': txn.get('receiver_hash'),
        'tx_hash': txn.get('tx_hash'),
        'asset': txn.get('asset'),
        'network': txn.get('network'),
        'amount': txn.get('amount'),
        'tx_fee': txn.get('tx_fee'),
        'score': score,
        'is_fraud': bool(is_fraud),
        'explanation': explanation,
    }


@app.get('/api/predict_elliptic/{tx_id}')
def api_predict_elliptic(tx_id: int):
    return services.predict_elliptic_txid(int(tx_id))


@ui.page('/')
def index_page():
    app_ui.landing_page()


@ui.page('/login')
def login():
    app_ui.login_page()


@ui.page('/animations')
def animations():
    create_animations_page()


@ui.page('/dashboard')
def dashboard():
    # Admin-only access - redirect to login if not authenticated
    if not app_ui.CURRENT_ROLE['role']:
        ui.notify('Please log in to access the dashboard', color='warning')
        ui.navigate.to('/login')
        return
    app_ui.dashboard_page()


if __name__ in {'__main__', '__mp_main__'}:
    print('Starting Smart Money Laundering System Cyber Forensic Dashboard at http://localhost:8080')
    ui.run(host='0.0.0.0', port=8080)

