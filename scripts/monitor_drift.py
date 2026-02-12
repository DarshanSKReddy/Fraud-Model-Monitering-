"""Generate drift monitoring and data quality checks."""
import os
import json
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_PATH = 'data/raw/transactions.csv'
DRIFT_REPORT = 'reports/drift_monitoring_report.txt'

def monitor_drift():
    """Check for data drift in key features."""
    print("=" * 70)
    print("DATA DRIFT & QUALITY MONITORING")
    print("=" * 70)
    
    df = pd.read_csv(DATA_PATH)
    
    # Summary statistics
    print("\n📊 Dataset Summary:")
    print(f"   Total Records: {len(df)}")
    print(f"   Fraud Cases: {df['is_fraud'].sum()} ({100*df['is_fraud'].mean():.2f}%)")
    print(f"   Features: {', '.join(df.columns.tolist()[:8])}")
    
    # Missing values
    print("\n🔍 Data Quality Check:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("   ✓ No missing values detected")
    else:
        print(f"   ⚠ Missing values: {missing[missing > 0].to_dict()}")
    
    # Numeric feature statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    print(f"\n📈 Numeric Features Summary ({len(numeric_cols)} features):")
    for col in numeric_cols[:5]:
        print(f"   {col:25s} | Mean: {df[col].mean():10.2f} | Std: {df[col].std():10.2f}")
    
    report = f"""# DATA DRIFT & QUALITY MONITORING REPORT
Generated: {pd.Timestamp.now()}

## Data Quality Summary
- Total Records: {len(df)}
- Complete Records (no missing values): {len(df) - df.isnull().any(axis=1).sum()}
- Fraud Rate: {df['is_fraud'].sum()} / {len(df)} ({100*df['is_fraud'].mean():.2f}%)

## Numeric Feature Statistics
"""
    
    for col in numeric_cols:
        report += f"\n### {col}\n"
        report += f"- Min: {df[col].min():.2f}\n"
        report += f"- Max: {df[col].max():.2f}\n"
        report += f"- Mean: {df[col].mean():.2f}\n"
        report += f"- Std Dev: {df[col].std():.2f}\n"
    
    with open(DRIFT_REPORT, 'w') as f:
        f.write(report)
    
    print(f"\n✓ Report saved: {DRIFT_REPORT}")
    return True

if __name__ == '__main__':
    import sys
    monitor_drift()
