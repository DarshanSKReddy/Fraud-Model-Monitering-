"""Cost-sensitive evaluation and threshold optimization for fraud detection.

This script analyzes the business cost of different decision thresholds
and recommends an optimal threshold that minimizes total cost.
"""
import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_auc_score, roc_curve
import warnings

warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Paths
MODEL_PATH = 'models/baseline_model.joblib'
DATA_PATH = 'data/raw/transactions.csv'
COST_REPORT = 'reports/cost_analysis_report.txt'
COST_METRICS = 'reports/cost_metrics.json'

# Business cost parameters (in USD)
COST_FALSE_NEGATIVE = 100.0   # Cost of undetected fraud (chargeback + investigation)
COST_FALSE_POSITIVE = 5.0     # Cost of false alarm (customer friction, decline cost)
COST_TRUE_NEGATIVE = 0.0      # No cost for correct approvals
COST_TRUE_POSITIVE = 0.0      # No cost for correct fraud blocks


def calculate_threshold_costs(y_true, y_pred_proba, cost_fn, cost_fp, thresholds):
    """Calculate total cost for each threshold."""
    costs = []
    fp_counts = []
    fn_counts = []
    tp_counts = []
    tn_counts = []

    for threshold in thresholds:
        y_pred = (y_pred_proba >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        total_cost = (
            cost_fn * fn +  # False negatives (missed fraud)
            cost_fp * fp    # False positives (false alarms)
        )
        costs.append(total_cost)
        fp_counts.append(fp)
        fn_counts.append(fn)
        tp_counts.append(tp)
        tn_counts.append(tn)

    return np.array(costs), np.array(fp_counts), np.array(fn_counts), np.array(tp_counts), np.array(tn_counts)


def main():
    print("=" * 70)
    print("COST-SENSITIVE THRESHOLD OPTIMIZATION")
    print("=" * 70)

    # Check files exist
    if not os.path.exists(MODEL_PATH):
        print(f"✗ Model not found: {MODEL_PATH}")
        return False

    if not os.path.exists(DATA_PATH):
        print(f"✗ Data not found: {DATA_PATH}")
        return False

    # Load model and data
    print(f"\n📦 Loading model and data...")
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH)
    
    X = df.select_dtypes(include=['number']).drop(columns=['is_fraud', 'transaction_id'], errors='ignore')
    y = df['is_fraud'].astype(int)
    
    # Encode categoricals
    cat_cols = df.select_dtypes(include=['object']).columns
    if len(cat_cols) > 0:
        from sklearn.preprocessing import LabelEncoder
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(df[col])
    
    # Get predictions
    y_pred_proba = model.predict_proba(X)[:, 1]
    
    print(f"   ✓ Model loaded")
    print(f"   ✓ Data loaded: {len(df)} records, {y.sum()} frauds ({100*y.mean():.2f}%)")

    # Calculate metrics for different thresholds
    print(f"\n📊 Evaluating thresholds (0.01 to 0.99)...")
    thresholds = np.arange(0.01, 1.0, 0.01)
    
    costs, fp_counts, fn_counts, tp_counts, tn_counts = calculate_threshold_costs(
        y, y_pred_proba, COST_FALSE_NEGATIVE, COST_FALSE_POSITIVE, thresholds
    )

    # Find optimal threshold
    optimal_idx = np.argmin(costs)
    optimal_threshold = thresholds[optimal_idx]
    optimal_cost = costs[optimal_idx]

    print(f"   Optimal threshold: {optimal_threshold:.3f}")
    print(f"   Minimum cost: ${optimal_cost:.2f}")
    print(f"   Cost per fraud: ${optimal_cost/y.sum():.2f}")

    # Default threshold performance (0.5)
    default_cost = costs[np.argmin(np.abs(thresholds - 0.5))]
    print(f"\n   Default threshold (0.5) cost: ${default_cost:.2f}")
    print(f"   Savings with optimal: ${default_cost - optimal_cost:.2f} ({100*(default_cost-optimal_cost)/default_cost:.1f}%)")

    # Get confusion matrix at optimal threshold
    y_pred_optimal = (y_pred_proba >= optimal_threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, y_pred_optimal).ravel()

    print(f"\n🎯 Performance at Optimal Threshold ({optimal_threshold:.3f}):")
    print(f"   True Positives (Frauds Caught): {tp}")
    print(f"   False Positives (False Alarms): {fp}")
    print(f"   True Negatives (Correct Approvals): {tn}")
    print(f"   False Negatives (Missed Frauds): {fn}")
    
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    print(f"   Recall (Fraud Detection Rate): {recall:.4f} ({100*recall:.2f}%)")
    print(f"   Precision (Positive Predictions Correct): {precision:.4f}" if (tp+fp) > 0 else "   Precision: N/A (no positive predictions)")
    
    # Calculate ROC-AUC
    roc_auc = roc_auc_score(y, y_pred_proba)
    print(f"   ROC-AUC: {roc_auc:.4f}")

    # Cost breakdown
    cost_fn_total = COST_FALSE_NEGATIVE * fn
    cost_fp_total = COST_FALSE_POSITIVE * fp
    
    print(f"\n💰 Cost Breakdown:")
    print(f"   False Negatives Cost: ${cost_fn_total:.2f} ({fn} × ${COST_FALSE_NEGATIVE})")
    print(f"   False Positives Cost: ${cost_fp_total:.2f} ({fp} × ${COST_FALSE_POSITIVE})")
    print(f"   Total Cost: ${optimal_cost:.2f}")

    # Save cost metrics
    os.makedirs(os.path.dirname(COST_METRICS), exist_ok=True)
    cost_data = {
        'optimal_threshold': float(optimal_threshold),
        'optimal_cost': float(optimal_cost),
        'cost_per_fraud': float(optimal_cost / y.sum()),
        'savings_vs_default': float(default_cost - optimal_cost),
        'savings_percent': float(100 * (default_cost - optimal_cost) / default_cost),
        'confusion_matrix': {
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn),
            'tp': int(tp)
        },
        'recall': float(recall),
        'precision': float(precision),
        'roc_auc': float(roc_auc),
        'cost_fn_total': float(cost_fn_total),
        'cost_fp_total': float(cost_fp_total),
        'business_costs': {
            'cost_false_negative': COST_FALSE_NEGATIVE,
            'cost_false_positive': COST_FALSE_POSITIVE
        }
    }

    with open(COST_METRICS, 'w') as f:
        json.dump(cost_data, f, indent=2)
    print(f"\n✓ Metrics saved: {COST_METRICS}")

    # Generate cost report
    report = f"""# COST-SENSITIVE THRESHOLD OPTIMIZATION REPORT
Generated: {pd.Timestamp.now()}

## Business Cost Parameters
- Cost of False Negative (Missed Fraud): ${COST_FALSE_NEGATIVE:.2f}
  (Chargeback liability + investigation cost)
- Cost of False Positive (False Alarm): ${COST_FALSE_POSITIVE:.2f}
  (Customer friction + transaction decline cost)

## Optimal Threshold Analysis
- **Recommended Threshold: {optimal_threshold:.3f}**
- **Minimum Total Cost: ${optimal_cost:.2f}**
- Cost per fraud detected: ${optimal_cost/y.sum():.2f}

## Cost Comparison
- Default Threshold (0.5) Cost: ${default_cost:.2f}
- Potential Savings: ${default_cost - optimal_cost:.2f} ({100*(default_cost-optimal_cost)/default_cost:.1f}%)

## Performance at Optimal Threshold
Confusion Matrix:
  - True Positives (Frauds Caught): {tp}
  - False Positives (False Alarms): {fp}
  - True Negatives (Correct Approvals): {tn}
  - False Negatives (Missed Frauds): {fn}

Key Metrics:
  - Fraud Detection Rate (Recall): {recall:.4f} ({100*recall:.2f}%)
  - Precision (Accuracy of positive predictions): {precision:.4f} 
  - ROC-AUC Score: {roc_auc:.4f}

## Cost Breakdown
- False Negative Cost: ${cost_fn_total:.2f} ({fn} missed frauds × ${COST_FALSE_NEGATIVE})
- False Positive Cost: ${cost_fp_total:.2f} ({fp} false alarms × ${COST_FALSE_POSITIVE})
- **Total Operating Cost: ${optimal_cost:.2f}**

## Recommendations
1. **Threshold Update**: Change decision threshold from 0.5 to {optimal_threshold:.3f}
   - Reduces total operational cost by {100*(default_cost-optimal_cost)/default_cost:.1f}%
   - Balances fraud detection vs. customer friction

2. **Monitoring**: Track false positive rate weekly
   - Target: {100*precision:.1f}% precision (minimize customer disruption)
   - Ensure fraud detection rate ≥ {100*recall:.1f}%

3. **Customer Communication**: Prepare for {fp} potential false alarms per {len(df)} transactions
   - Reduced verification time with new threshold
   - Improved customer experience

4. **Cost Recovery**: Monitor chargebacks and costs monthly
   - Expected savings: ${default_cost - optimal_cost:.2f}
   - Adjust threshold if fraud patterns change

## Implementation Steps
1. Update model serving code to use threshold {optimal_threshold:.3f}
2. Deploy to fraud detection API/pipeline
3. Monitor precision and recall in production
4. Re-optimize threshold monthly with new data

---
Report Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open(COST_REPORT, 'w') as f:
        f.write(report)
    print(f"✓ Report saved: {COST_REPORT}")

    print("\n" + "=" * 70)
    print("✓ COST ANALYSIS COMPLETE")
    print("=" * 70)
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
