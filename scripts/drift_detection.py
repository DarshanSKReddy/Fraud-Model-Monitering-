"""Drift detection system using PSI and KS-test for production monitoring."""
import os
import json
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from datetime import datetime

DATA_PATH = 'data/raw/transactions.csv'
DRIFT_REPORT = 'reports/drift_detection_report.txt'
DRIFT_METRICS = 'reports/drift_metrics.json'

# Drift thresholds
PSI_THRESHOLD = 0.1  # PSI > 0.1 suggests moderate drift
KS_THRESHOLD = 0.05  # KS p-value < 0.05 suggests statistically significant drift


def calculate_psi(expected, actual, buckets=10):
    """Calculate Population Stability Index."""
    expected = np.array(expected).astype(float)
    actual = np.array(actual).astype(float)
    
    if expected.size == 0 or actual.size == 0:
        return np.nan
    
    # Create quantile-based bins
    quantiles = np.linspace(0, 1, buckets + 1)
    bins = np.unique(np.percentile(expected, quantiles * 100))
    
    if bins.size <= 1:
        return 0.0
    
    expected_counts, _ = np.histogram(expected, bins=bins)
    actual_counts, _ = np.histogram(actual, bins=bins)
    
    # Avoid division by zero
    expected_perc = expected_counts / expected_counts.sum()
    actual_perc = actual_counts / actual_counts.sum()
    expected_perc = np.where(expected_perc == 0, 1e-6, expected_perc)
    actual_perc = np.where(actual_perc == 0, 1e-6, actual_perc)
    
    psi_val = np.sum((expected_perc - actual_perc) * np.log(expected_perc / actual_perc))
    return float(psi_val)


def detect_drift():
    """Monitor features for drift."""
    print("=" * 70)
    print("DATA DRIFT DETECTION")
    print("=" * 70)
    
    if not os.path.exists(DATA_PATH):
        print(f"✗ Data not found: {DATA_PATH}")
        return False
    
    df = pd.read_csv(DATA_PATH)
    print(f"\n✓ Data loaded: {len(df)} records")
    
    # Split data into train (first 80%) and test (last 20%) for drift comparison
    split_idx = int(len(df) * 0.8)
    train_data = df.iloc[:split_idx]
    test_data = df.iloc[split_idx:]
    
    print(f"  Train set: {len(train_data)} records")
    print(f"  Test set: {len(test_data)} records")
    
    # Numeric features
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['transaction_id', 'is_fraud']]
    
    print(f"\n🔍 Checking drift in {len(numeric_cols)} features...")
    
    drift_results = {}
    drift_detected = []
    
    for col in numeric_cols:
        train_vals = train_data[col].dropna().values
        test_vals = test_data[col].dropna().values
        
        if len(train_vals) == 0 or len(test_vals) == 0:
            continue
        
        # Calculate PSI
        psi = calculate_psi(train_vals, test_vals)
        
        # KS test
        ks_stat, ks_pval = ks_2samp(train_vals, test_vals)
        
        # Check drift
        drift = psi > PSI_THRESHOLD or ks_pval < KS_THRESHOLD
        
        result = {
            'feature': col,
            'psi': float(psi),
            'ks_statistic': float(ks_stat),
            'ks_pvalue': float(ks_pval),
            'drift_detected': bool(drift),
            'train_mean': float(train_vals.mean()),
            'test_mean': float(test_vals.mean()),
            'train_std': float(train_vals.std()),
            'test_std': float(test_vals.std()),
        }
        
        drift_results[col] = result
        
        if drift:
            drift_detected.append(col)
        
        status = "⚠ DRIFT" if drift else "✓ OK"
        print(f"  {col:25s} | PSI: {psi:7.4f} | KS p-value: {ks_pval:.4f} | {status}")
    
    print(f"\n📊 Summary:")
    print(f"   Total Features Monitored: {len(drift_results)}")
    print(f"   Features with Drift: {len(drift_detected)}")
    
    if drift_detected:
        print(f"   ⚠ Drifted Features: {', '.join(drift_detected)}")
        print(f"\n   Action Required: Consider retraining model")
    else:
        print(f"   ✓ All features stable - no drift detected")
    
    # Save metrics
    os.makedirs(os.path.dirname(DRIFT_METRICS), exist_ok=True)
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'total_features_checked': len(drift_results),
        'features_with_drift': drift_detected,
        'drift_count': len(drift_detected),
        'drift_percentage': 100 * len(drift_detected) / len(drift_results) if drift_results else 0,
        'feature_details': drift_results,
        'psi_threshold': PSI_THRESHOLD,
        'ks_threshold': KS_THRESHOLD
    }
    
    with open(DRIFT_METRICS, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\n✓ Metrics saved: {DRIFT_METRICS}")
    
    # Generate report
    report = f"""# DATA DRIFT DETECTION REPORT
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- Total Features Monitored: {len(drift_results)}
- Features with Drift: {len(drift_detected)} ({100*len(drift_detected)/len(drift_results):.1f}%)
- Overall Status: {"⚠ DRIFT DETECTED - ACTION REQUIRED" if drift_detected else "✓ NO DRIFT DETECTED"}

## Drift Detection Methodology
- PSI (Population Stability Index) Threshold: {PSI_THRESHOLD}
  - PSI > {PSI_THRESHOLD} suggests moderate drift
- KS Test P-value Threshold: {KS_THRESHOLD}
  - P-value < {KS_THRESHOLD} indicates statistically significant distribution shift

## Feature Status
"""
    
    for col, metrics_dict in sorted(drift_results.items(), key=lambda x: x[1]['psi'], reverse=True):
        drift_status = "⚠ DRIFT DETECTED" if metrics_dict['drift_detected'] else "✓ OK"
        report += f"""
### {col} - {drift_status}
- PSI Score: {metrics_dict['psi']:.6f}
- KS Statistic: {metrics_dict['ks_statistic']:.6f}
- KS P-value: {metrics_dict['ks_pvalue']:.6f}
- Train Mean: {metrics_dict['train_mean']:.4f}
- Test Mean: {metrics_dict['test_mean']:.4f}
- Mean Change: {abs(metrics_dict['test_mean'] - metrics_dict['train_mean']):.4f}
"""
    
    report += f"""

## Key Findings
"""
    
    if drift_detected:
        report += f"""**Critical:** Features with detected drift should be investigated:
- Device Trust Score: Monitor for changes in device security landscape
- Transaction Amount: Check for inflation, region expansion, or fraud pattern changes
- Velocity: Verify if customer behavior has shifted
- Transaction Hour: Look for timezone or operational changes

## Recommended Actions
1. **Immediate:** Review flagged features for root cause
2. **Short-term:** Collect more recent data for model retraining
3. **Medium-term:** Retrain model with updated data distribution
4. **Long-term:** Implement continuous monitoring dashboard
"""
    else:
        report += """**Status:** All monitored features show stable distributions. Model continues
to perform reliably with current data conditions.

## Recommendations
1. Continue weekly monitoring
2. Set up alerts for PSI > {PSI_THRESHOLD}
3. Archive baseline statistics for future comparisons
4. Schedule monthly drift reviews
"""
    
    report += f"""

## Data Summary
- Training Set: {len(train_data)} records ({100*len(train_data)/len(df):.1f}%)
- Test/Monitoring Set: {len(test_data)} records ({100*len(test_data)/len(df):.1f}%)

---
Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
    
    with open(DRIFT_REPORT, 'w') as f:
        f.write(report)
    
    print(f"✓ Report saved: {DRIFT_REPORT}")
    
    print("\n" + "=" * 70)
    print("✓ DRIFT DETECTION COMPLETE")
    print("=" * 70)
    return True


if __name__ == '__main__':
    import sys
    success = detect_drift()
    sys.exit(0 if success else 1)
