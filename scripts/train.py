"""Train baseline fraud detection model."""
import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.train_model import train_baseline
from src.explainability import permutation_importance_report

# Paths
DATA_PATH = 'data/raw/transactions.csv'
MODEL_OUT = 'models/baseline_model.joblib'
METRICS_OUT = 'reports/training_metrics.json'
EVAL_REPORT = 'reports/model_evaluation.txt'

def main():
    print("=" * 60)
    print("BASELINE MODEL TRAINING")
    print("=" * 60)
    
    # Check data exists
    if not os.path.exists(DATA_PATH):
        print(f"✗ Data file not found: {DATA_PATH}")
        print("  Run: python scripts/generate_data.py")
        return False
    
    # Load data
    print(f"\n📦 Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"   {len(df)} rows, {df['is_fraud'].sum()} frauds ({100*df['is_fraud'].mean():.2f}%)")
    
    # Prepare features
    print("\n🔧 Preparing features...")
    X = df.select_dtypes(include=['number']).drop(columns=['is_fraud', 'transaction_id'], errors='ignore')
    y = df['is_fraud'].astype(int)
    
    # Encode categorical if present
    cat_cols = df.select_dtypes(include=['object']).columns
    if len(cat_cols) > 0:
        print(f"   Encoding {len(cat_cols)} categorical columns: {list(cat_cols)}")
        from sklearn.preprocessing import LabelEncoder
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(df[col])
    
    print(f"   Features: {X.shape[1]} | Target balance: {y.value_counts().to_dict()}")
    
    # Train-test split
    print("\n📊 Splitting data (80-20, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")
    
    # Train baseline
    print("\n🤖 Training RandomForest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("   ✓ Model trained")
    
    # Cross-validation
    print("\n📈 5-Fold Cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_validate(
        model, X_train, y_train, cv=cv,
        scoring=['accuracy', 'precision', 'recall', 'roc_auc']
    )
    print(f"   Accuracy:  {cv_scores['test_accuracy'].mean():.4f} (+/- {cv_scores['test_accuracy'].std():.4f})")
    print(f"   Precision: {cv_scores['test_precision'].mean():.4f} (+/- {cv_scores['test_precision'].std():.4f})")
    print(f"   Recall:    {cv_scores['test_recall'].mean():.4f} (+/- {cv_scores['test_recall'].std():.4f})")
    print(f"   ROC-AUC:   {cv_scores['test_roc_auc'].mean():.4f} (+/- {cv_scores['test_roc_auc'].std():.4f})")
    
    # Test set evaluation
    print("\n🧪 Test Set Performance...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    cm = confusion_matrix(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"   ROC-AUC: {roc_auc:.4f}")
    print(f"   Confusion Matrix:\n{cm}")
    
    # Feature importance
    print("\n⭐ Feature Importance (top 10)...")
    importances = model.feature_importances_
    feature_names = X.columns.tolist()
    ranked = sorted(zip(feature_names, importances), key=lambda x: -x[1])
    for i, (feat, imp) in enumerate(ranked[:10], 1):
        print(f"   {i:2d}. {feat:25s} {imp:.6f}")
    
    # Save model
    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
    joblib.dump(model, MODEL_OUT)
    print(f"\n✓ Model saved: {MODEL_OUT}")
    
    # Save metrics
    metrics = {
        'train_size': len(X_train),
        'test_size': len(X_test),
        'fraud_rate': float(y.mean()),
        'cv_accuracy_mean': float(cv_scores['test_accuracy'].mean()),
        'cv_accuracy_std': float(cv_scores['test_accuracy'].std()),
        'cv_precision_mean': float(cv_scores['test_precision'].mean()),
        'cv_recall_mean': float(cv_scores['test_recall'].mean()),
        'cv_roc_auc_mean': float(cv_scores['test_roc_auc'].mean()),
        'test_roc_auc': float(roc_auc),
        'confusion_matrix': cm.tolist(),
        'top_features': [{'feature': f, 'importance': float(i)} for f, i in ranked[:10]],
    }
    
    os.makedirs(os.path.dirname(METRICS_OUT), exist_ok=True)
    with open(METRICS_OUT, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✓ Metrics saved: {METRICS_OUT}")
    
    # Save evaluation report
    report_text = f"""# MODEL TRAINING REPORT
Generated: {pd.Timestamp.now()}

## Dataset Summary
- Train: {len(X_train)} samples
- Test: {len(X_test)} samples  
- Fraud rate: {y.mean():.2%}

## Cross-Validation Results (5-Fold Stratified)
- Accuracy:  {cv_scores['test_accuracy'].mean():.4f} ± {cv_scores['test_accuracy'].std():.4f}
- Precision: {cv_scores['test_precision'].mean():.4f} ± {cv_scores['test_precision'].std():.4f}
- Recall:    {cv_scores['test_recall'].mean():.4f} ± {cv_scores['test_recall'].std():.4f}
- ROC-AUC:   {cv_scores['test_roc_auc'].mean():.4f} ± {cv_scores['test_roc_auc'].std():.4f}

## Test Set Performance
- ROC-AUC: {roc_auc:.4f}
- Confusion Matrix:
  [[TN: {cm[0,0]}, FP: {cm[0,1]}],
   [FN: {cm[1,0]}, TP: {cm[1,1]}]]

## Top 10 Features
"""
    for i, (feat, imp) in enumerate(ranked[:10], 1):
        report_text += f"{i:2d}. {feat:25s} {imp:.6f}\n"
    
    report_text += f"""
## Model Details
- Algorithm: Random Forest
- N Estimators: 100
- Max Depth: 15
- Class Weight: balanced
- Model Path: {MODEL_OUT}
"""
    
    with open(EVAL_REPORT, 'w') as f:
        f.write(report_text)
    print(f"✓ Report saved: {EVAL_REPORT}")
    
    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
