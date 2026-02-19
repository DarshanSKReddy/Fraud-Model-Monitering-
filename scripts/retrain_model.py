"""Automated model retraining pipeline with triggering logic."""
import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

MODEL_PATH = 'models/baseline_model.joblib'
DATA_PATH = 'data/raw/transactions.csv'
RETRAINING_LOG = 'reports/retraining_log.txt'
DRIFT_METRICS = 'reports/drift_metrics.json'


def check_retraining_needed():
    """Check if model retraining is needed based on drift or performance."""
    reasons = []
    
    # Check drift
    if os.path.exists(DRIFT_METRICS):
        with open(DRIFT_METRICS, 'r') as f:
            drift_data = json.load(f)
        
        if drift_data.get('drift_count', 0) > 2:
            reasons.append(f"Data drift detected in {drift_data['drift_count']} features")
    
    # Check model age (optional - based on file modification time)
    if os.path.exists(MODEL_PATH):
        days_old = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(MODEL_PATH))).days
        if days_old > 30:
            reasons.append(f"Model is {days_old} days old - periodic retraining recommended")
    
    return len(reasons) > 0, reasons


def retrain_model():
    """Retrain model with latest data."""
    print("=" * 70)
    print("AUTOMATED MODEL RETRAINING")
    print("=" * 70)
    
    # Check if retraining needed
    needed, reasons = check_retraining_needed()
    
    print(f"\n📊 Retraining Check:")
    print(f"   Needed: {'Yes' if needed else 'No'}")
    for reason in reasons:
        print(f"   • {reason}")
    
    if not needed:
        print("\n   ✓ Model is up-to-date. No retraining needed.")
        return True
    
    print("\n🔄 Starting retraining process...\n")
    
    # Load data
    if not os.path.exists(DATA_PATH):
        print(f"✗ Data not found: {DATA_PATH}")
        return False
    
    df = pd.read_csv(DATA_PATH)
    print(f"✓ Data loaded: {len(df)} records")
    
    # Prepare features
    X = df.select_dtypes(include=['number']).drop(columns=['is_fraud', 'transaction_id'], errors='ignore')
    y = df['is_fraud'].astype(int)
    
    cat_cols = df.select_dtypes(include=['object']).columns
    if len(cat_cols) > 0:
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(df[col])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print(f"✓ Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Train new model
    print(f"\n🤖 Training new model...")
    model = RandomForestClassifier(
        n_estimators=150,  # Increased from 100
        class_weight='balanced',
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    print(f"\n📈 Evaluating new model...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_validate(
        model, X_train, y_train, cv=cv,
        scoring=['accuracy', 'precision', 'recall', 'roc_auc']
    )
    
    accuracy = cv_scores['test_accuracy'].mean()
    roc_auc = cv_scores['test_roc_auc'].mean()
    
    print(f"   Accuracy: {accuracy:.4f}")
    print(f"   ROC-AUC: {roc_auc:.4f}")
    
    # Save new model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Backup old model
    if os.path.exists(MODEL_PATH):
        backup_path = MODEL_PATH.replace('.joblib', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.joblib')
        import shutil
        shutil.copy(MODEL_PATH, backup_path)
        print(f"✓ Old model backed up: {backup_path}")
    
    joblib.dump(model, MODEL_PATH)
    print(f"✓ New model saved: {MODEL_PATH}")
    
    # Log retraining
    log_entry = f"""
RETRAINING COMPLETED
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Reasons:
{chr(10).join([f"  • {r}" for r in reasons])}

Performance:
  Accuracy: {accuracy:.4f}
  ROC-AUC: {roc_auc:.4f}
  Training samples: {len(X_train)}
  Test samples: {len(X_test)}

Model saved: {MODEL_PATH}
"""
    
    os.makedirs(os.path.dirname(RETRAINING_LOG), exist_ok=True)
    with open(RETRAINING_LOG, 'a') as f:
        f.write(log_entry)
    
    print(f"✓ Retraining logged: {RETRAINING_LOG}")
    
    print("\n" + "=" * 70)
    print("✓ RETRAINING COMPLETE")
    print("=" * 70)
    return True


if __name__ == '__main__':
    success = retrain_model()
    sys.exit(0 if success else 1)
