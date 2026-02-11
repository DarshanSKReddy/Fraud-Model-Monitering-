"""Generate synthetic fraud transaction dataset for training."""
import os
import numpy as np
import pandas as pd

np.random.seed(42)

# Generate 10,000 synthetic transactions
n_records = 10000

# Parameters
fraud_rate = 0.015  # 1.5% fraud rate

# Create features
data = {
    'transaction_id': np.arange(n_records),
    'amount': np.abs(np.random.exponential(scale=100, size=n_records)) + 1,  # Right-skewed
    'transaction_hour': np.random.randint(0, 24, n_records),
    'merchant_category': np.random.choice(
        ['Grocery', 'Electronics', 'Travel', 'Clothing', 'Food', 'Gas', 'Entertainment'],
        n_records
    ),
    'foreign_transaction': np.random.binomial(1, 0.1, n_records),
    'location_mismatch': np.random.binomial(1, 0.05, n_records),
    'device_trust_score': np.random.uniform(0, 100, n_records),
    'velocity_last_24h': np.random.poisson(lam=3, size=n_records),
    'cardholder_age': np.random.randint(18, 80, n_records),
}

# Create target (fraud) with some feature correlation
is_fraud = np.zeros(n_records, dtype=int)
fraud_count = int(n_records * fraud_rate)

# Create correlated fraud patterns
fraud_indices = []
# High velocity + foreign = higher fraud risk
high_vel_foreign = np.where((data['velocity_last_24h'] > 6) & (data['foreign_transaction'] == 1))[0]
fraud_indices.extend(np.random.choice(high_vel_foreign, min(len(high_vel_foreign)//2, 20), replace=False))

# Location mismatch + low device trust
loc_mismatch_low_trust = np.where((data['location_mismatch'] == 1) & (data['device_trust_score'] < 30))[0]
fraud_indices.extend(np.random.choice(loc_mismatch_low_trust, min(len(loc_mismatch_low_trust)//2, 30), replace=False))

# Random fraud (remaining)
other_indices = np.setdiff1d(np.arange(n_records), fraud_indices)
remaining_fraud = fraud_count - len(fraud_indices)
fraud_indices.extend(np.random.choice(other_indices, min(remaining_fraud, len(other_indices)), replace=False))

is_fraud[fraud_indices[:fraud_count]] = 1

data['is_fraud'] = is_fraud

df = pd.DataFrame(data)

# Create directories
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# Save
csv_path = 'data/raw/transactions.csv'
df.to_csv(csv_path, index=False)
print(f"✓ Generated {len(df)} transactions: {df['is_fraud'].sum()} frauds ({100*df['is_fraud'].mean():.2f}%)")
print(f"✓ Saved to: {csv_path}")
