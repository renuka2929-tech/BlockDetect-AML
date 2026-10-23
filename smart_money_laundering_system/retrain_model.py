#!/usr/bin/env python3
"""
Retrain the fraud detection model on the configured dataset.

This script allows periodic model updates to adapt to new fraud patterns
and user behavior. In production, this can be scheduled via cron (macOS/Linux)
or Task Scheduler (Windows).

Usage:
    python retrain_model.py

After retraining, the updated model will be automatically loaded on the next
application startup.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.ai_engine import FraudModel
from app import config


def main():
    print("=" * 80)
    print("Smart Money Laundering Fraud Detection - Model Retraining Script")
    print("=" * 80)
    print(f"\nDataset: {config.DATASET_PATH}")
    print(f"Model will be saved to: {config.MODEL_PATH}")
    print(f"Classification report: {config.REPORT_EXPORT_PATH}")
    print(f"Model comparison: {config.MODEL_COMPARISON_PATH}")
    print("\nStarting training...\n")

    try:
        model = FraudModel()
        model.train_and_save()
        
        print("\n" + "=" * 80)
        print("✓ Model training completed successfully!")
        print("=" * 80)
        print(f"\nTrained model saved to:")
        print(f"  - {config.MODEL_PATH}")
        print(f"  - {config.SCALER_PATH}")
        print(f"  - {config.FEATURES_PATH}")
        print(f"  - {config.ANOMALY_MODEL_PATH}")
        print(f"\nReports generated:")
        print(f"  - {config.REPORT_EXPORT_PATH}")
        print(f"  - {config.MODEL_COMPARISON_PATH}")
        print("\nThe updated model will be used automatically on next app startup.")
        print("\nTo schedule periodic retraining:")
        print("  macOS/Linux: Add to crontab (e.g., weekly)")
        print("    0 2 * * 0 cd /path/to/project && python retrain_model.py")
        print("  Windows: Use Task Scheduler to run this script periodically")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease ensure:")
        print(f"  1. Dataset exists at: {config.DATASET_PATH}")
        print("  2. Dataset path is correctly configured in app/config.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
