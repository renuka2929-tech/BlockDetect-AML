import argparse
import os
from pathlib import Path


def download_dataset(dataset: str, out_dir: Path) -> None:
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except Exception as e:
        raise RuntimeError('Missing kaggle package. Install it with: pip install -r requirements.txt') from e

    api = KaggleApi()
    api.authenticate()

    out_dir.mkdir(parents=True, exist_ok=True)
    api.dataset_download_files(dataset, path=str(out_dir), unzip=True, quiet=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default=str(Path(__file__).parent), help='Project root (defaults to this script directory)')
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    datasets_dir = base_dir / 'Datasets'

    elliptic_dir = datasets_dir / 'elliptic'
    deanonym_dir = datasets_dir / 'elliptic_deanonymized'

    print('Downloading Elliptic dataset...')
    download_dataset('ellipticco/elliptic-data-set', elliptic_dir)

    print('Downloading deanonymized mapping dataset...')
    download_dataset('alexbenzik/deanonymized-995-pct-of-elliptic-transactions', deanonym_dir)

    print('\nDone.')
    print(f'Elliptic extracted to: {elliptic_dir}')
    print(f'Deanonymized extracted to: {deanonym_dir}')
    print('\nNext: set app/config.py MODEL_TYPE to xgboost (optional) and run: python retrain_model.py')


if __name__ == '__main__':
    main()
