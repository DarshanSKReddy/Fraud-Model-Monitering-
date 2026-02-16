"""Batch fraud prediction pipeline for daily scoring runs."""
import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH = 'models/baseline_model.joblib'
DATA_PATH = 'data/raw/transactions.csv'
BATCH_PREDICTIONS = 'reports/batch_predictions.json'
BATCH_SUMMARY = 'reports/batch_summary.txt'
OPTIMAL_THRESHOLD = 0.29


def batch_predict():
    """Run batch predictions on entire dataset."""
    print("=" * 70)
    print("BATCH FRAUD PREDICTION")
    print("=" * 70)
    
    # Load model
    if not os.path.exists(MODEL_PATH):
        print(f"✗ Model not found: {MODEL_PATH}")
        return False
    
    model = joblib.load(MODEL_PATH)
    print(f"\n✓ Model loaded: {MODEL_PATH}")
    
    # Load data
    if not os.path.exists(DATA_PATH):
        print(f"✗ Data not found: {DATA_PATH}")
        return False
    
    df = pd.read_csv(DATA_PATH)
    print(f"✓ Data loaded: {len(df)} records")
    
    # Prepare features
    X = df.select_dtypes(include=['number']).drop(columns=['is_fraud', 'transaction_id'], errors='ignore')
    
    # Encode categoricals
    cat_cols = df.select_dtypes(include=['object']).columns
    if len(cat_cols) > 0:
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(df[col])
    
    # Get predictions
    print(f"\n🔮 Scoring {len(df)} transactions...")
    y_pred_proba = model.predict_proba(X)[:, 1]
    y_pred = (y_pred_proba >= OPTIMAL_THRESHOLD).astype(int)
    
    # Add predictions to dataframe
    df['fraud_probability'] = y_pred_proba
    df['fraud_prediction'] = y_pred
    df['decision'] = df['fraud_prediction'].map({1: 'BLOCK', 0: 'APPROVE'})
    df['confidence'] = np.where(
        y_pred_proba >= OPTIMAL_THRESHOLD,
        y_pred_proba,
        1 - y_pred_proba
    )
    df['timestamp'] = datetime.utcnow().isoformat()
    
    # Calculate statistics
    total = len(df)
    blocked = (y_pred == 1).sum()
    approved = total - blocked
    actual_fraud = df['is_fraud'].sum() if 'is_fraud' in df.columns else 0
    
    print(f"\n📊 Results:")
    print(f"   Total Transactions: {total}")
    print(f"   Predicted Fraud (BLOCK): {blocked} ({100*blocked/total:.2f}%)")
    print(f"   Predicted Safe (APPROVE): {approved} ({100*approved/total:.2f}%)")
    if actual_fraud > 0:
        print(f"   Actual Frauds: {actual_fraud} ({100*actual_fraud/total:.2f}%)")
    
    # Calculate fraud detection if ground truth available
    if 'is_fraud' in df.columns:
        true_positives = ((y_pred == 1) & (df['is_fraud'] == 1)).sum()
        false_positives = ((y_pred == 1) & (df['is_fraud'] == 0)).sum()
        false_negatives = ((y_pred == 0) & (df['is_fraud'] == 1)).sum()
        
        print(f"\n🎯 Performance:")
        print(f"   True Positives (Frauds Caught): {true_positives}")
        print(f"   False Positives (False Alarms): {false_positives}")
        print(f"   False Negatives (Missed Frauds): {false_negatives}")
        
        if actual_fraud > 0:
            recall = true_positives / actual_fraud
            print(f"   Recall (Detection Rate): {recall:.4f} ({100*recall:.2f}%)")
        if blocked > 0:
            precision = true_positives / blocked
            print(f"   Precision: {precision:.4f}")
    
    # Save predictions
    os.makedirs(os.path.dirname(BATCH_PREDICTIONS), exist_ok=True)
    
    # Save as JSON (subset for size)
    predictions_subset = df[['transaction_id', 'fraud_probability', 'decision', 'confidence']].head(1000).to_dict(orient='records')
    with open(BATCH_PREDICTIONS, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat(),
            'total_records': len(df),
            'sample_predictions': predictions_subset
        }, f, indent=2)
    
    print(f"\n✓ Predictions saved: {BATCH_PREDICTIONS}")
    
    # Save full CSV for analysis
    csv_out = 'reports/batch_predictions_full.csv'
    df.to_csv(csv_out, index=False)
    print(f"✓ Full predictions CSV: {csv_out}")
    
    # Generate summary report
    summary = f"""# BATCH PREDICTION SUMMARY REPORT
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Total Transactions Scored: {total}
- Scoring Date: {datetime.utcnow().isoformat()}
- Model Threshold: {OPTIMAL_THRESHOLD}

## Predictions
- BLOCK (Fraud Suspected): {blocked} ({100*blocked/total:.2f}%)
- APPROVE (Legitimate): {approved} ({100*approved/total:.2f}%)

## Fraud Stats
"""
    
    if actual_fraud > 0:
        summary += f"""- Actual Frauds in Dataset: {actual_fraud}
- Detection Rate (Recall): {100*true_positives/actual_fraud:.2f}%
- False Positive Rate: {100*false_positives/approved:.2f}% (if approved transactions)

## Performance Metrics
- True Positives (Frauds Caught): {true_positives}
- False Positives (False Alarms): {false_positives}
- False Negatives (Missed Frauds): {false_negatives}
- Precision: {true_positives / blocked:.4f} if {blocked} > 0 else "N/A"
"""
    
    summary += f"""
## Probability Distribution
- Min Fraud Probability: {y_pred_proba.min():.4f}
- Max Fraud Probability: {y_pred_proba.max():.4f}
- Mean Fraud Probability: {y_pred_proba.mean():.4f}
- Median Fraud Probability: {np.median(y_pred_proba):.4f}

## Recommendations
1. Review top {min(10, blocked)} flagged transactions manually
2. Monitor false positive rate weekly
3. Update threshold if detection rate drops below target
4. Log all predictions for model monitoring

## Files Generated
- {BATCH_PREDICTIONS} - JSON predictions sample
- {csv_out} - Full predictions CSV
- {BATCH_SUMMARY} - This report
"""
    
    with open(BATCH_SUMMARY, 'w') as f:
        f.write(summary)
    
    print(f"✓ Summary report: {BATCH_SUMMARY}")
    
    print("\n" + "=" * 70)
    print("✓ BATCH PREDICTION COMPLETE")
    print("=" * 70)
    return True


if __name__ == '__main__':
    success = batch_predict()
    sys.exit(0 if success else 1)
