import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/raw/transactions.csv')
plt.style.use('seaborn-v0_8-darkgrid')

# Plot 1: Amount distribution
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df['amount'], bins=50, ax=ax[0], kde=True)
ax[0].set_title('Amount distribution (linear)', fontsize=12, fontweight='bold')
sns.boxplot(x=df['amount'], ax=ax[1])
ax[1].set_title('Amount boxplot', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/01_amount_dist.png', dpi=100, bbox_inches='tight')
print("✓ reports/01_amount_dist.png")
plt.close()

# Plot 2: Categorical distributions
fig, ax = plt.subplots(1, 3, figsize=(18, 5))
sns.countplot(y='merchant_category', data=df, order=df['merchant_category'].value_counts().index, ax=ax[0])
ax[0].set_title('Merchant category counts', fontsize=12, fontweight='bold')
sns.countplot(x='foreign_transaction', data=df, ax=ax[1], palette='Set2')
ax[1].set_title('Foreign transaction flag', fontsize=12, fontweight='bold')
sns.countplot(x='location_mismatch', data=df, ax=ax[2], palette='Set2')
ax[2].set_title('Location mismatch flag', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/02_categorical_dist.png', dpi=100, bbox_inches='tight')
print("✓ reports/02_categorical_dist.png")
plt.close()

# Plot 3: Fraud vs features
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
sns.kdeplot(data=df, x='amount', hue='is_fraud', common_norm=False, ax=ax[0], fill=True)
ax[0].set_xlim(0, df['amount'].quantile(0.99))
ax[0].set_title('Amount by fraud label', fontsize=12, fontweight='bold')
sns.kdeplot(data=df, x='device_trust_score', hue='is_fraud', common_norm=False, ax=ax[1], fill=True)
ax[1].set_title('Device trust score by fraud label', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/03_fraud_features.png', dpi=100, bbox_inches='tight')
print("✓ reports/03_fraud_features.png")
plt.close()

# Plot 4: Correlation heatmap
num_cols = ['amount', 'transaction_hour', 'device_trust_score', 'velocity_last_24h', 'cardholder_age', 'is_fraud']
corr = df[num_cols].corr()
plt.figure(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True)
plt.title('Numeric feature correlations', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/04_correlation_heatmap.png', dpi=100, bbox_inches='tight')
print("✓ reports/04_correlation_heatmap.png")
plt.close()

# Plot 5: Hourly fraud rate
hour_counts = df.groupby('transaction_hour')['is_fraud'].agg(['sum', 'count'])
hour_counts['fraud_rate'] = hour_counts['sum'] / hour_counts['count'] * 100
hour_counts.reset_index(inplace=True)
plt.figure(figsize=(13, 5))
sns.barplot(x='transaction_hour', y='fraud_rate', data=hour_counts, palette='viridis')
plt.ylabel('Fraud rate (%)', fontsize=11)
plt.xlabel('Transaction hour', fontsize=11)
plt.title('Fraud rate by transaction hour', fontsize=12, fontweight='bold')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('reports/05_hourly_fraud_rate.png', dpi=100, bbox_inches='tight')
print("✓ reports/05_hourly_fraud_rate.png")
plt.close()

# Plot 6: Velocity and device analysis
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
sns.boxplot(x='is_fraud', y='velocity_last_24h', data=df, ax=ax[0], palette='Set2')
ax[0].set_title('Velocity (last 24h) by fraud label', fontsize=12, fontweight='bold')
ax[0].set_xlabel('Is fraud (0=legit, 1=fraud)')
sns.violinplot(x='is_fraud', y='device_trust_score', data=df, ax=ax[1], palette='Set2')
ax[1].set_title('Device trust score by fraud label', fontsize=12, fontweight='bold')
ax[1].set_xlabel('Is fraud (0=legit, 1=fraud)')
plt.tight_layout()
plt.savefig('reports/06_velocity_device_analysis.png', dpi=100, bbox_inches='tight')
print("✓ reports/06_velocity_device_analysis.png")
plt.close()

print("\n✓ All 6 visualizations generated")
