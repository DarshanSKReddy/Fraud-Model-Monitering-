"""Realtime fraud detection simulation and testing."""
import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder

MODEL_PATH = 'models/baseline_model.joblib'
DATA_PATH = 'data/raw/transactions.csv'
SIMULATION_LOG = 'reports/realtime_simulation.log'
OPTIMAL_THRESHOLD = 0.29


def generate_synthetic_transactions(n_transactions=100):
    """Generate synthetic transactions for testing."""
    np.random.seed(int(datetime.now().timestamp()) % 100)
    
    transactions = []
    for i in range(n_transactions):
        trans = {
            'transaction_id': f'TXN_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i:05d}',
            'amount': np.abs(np.random.exponential(scale=100)) + 1,
            'transaction_hour': np.random.randint(0, 24),
            'merchant_category': np.random.choice(
                ['Grocery', 'Electronics', 'Travel', 'Clothing', 'Food', 'Gas', 'Entertainment']
            ),
            'foreign_transaction': int(np.random.binomial(1, 0.1)),
            'location_mismatch': int(np.random.binomial(1, 0.05)),
            'device_trust_score': np.random.uniform(0, 100),
            'velocity_last_24h': int(np.random.poisson(lam=3)),
            'cardholder_age': int(np.random.randint(18, 80)),
            'timestamp': datetime.now() + timedelta(seconds=i)
        }
        transactions.append(trans)
    
    return transactions


def preprocess_transaction(data):
    """Convert transaction dict to model input."""
    numeric_features = [
        'amount', 'transaction_hour', 'velocity_last_24h',
        'device_trust_score', 'cardholder_age', 'foreign_transaction',
        'location_mismatch'
    ]
    
    X_dict = {f: data[f] for f in numeric_features}
    
    # Encode merchant category
    if 'merchant_category' in data:
        le = LabelEncoder()
        categories = ['Grocery', 'Electronics', 'Travel', 'Clothing', 'Food', 'Gas', 'Entertainment']
        le.fit(categories)
        X_dict['merchant_category'] = le.transform([data['merchant_category']])[0]
    
    feature_order = numeric_features + ['merchant_category']
    X = np.array([[X_dict[f] for f in feature_order]])
    
    return X


def run_simulation(n_transactions=100):
    """Run realtime fraud detection simulation."""
    print("=" * 70)
    print("REALTIME FRAUD DETECTION SIMULATION")
    print("=" * 70)
    
    # Load model
    if not os.path.exists(MODEL_PATH):
        print(f"✗ Model not found: {MODEL_PATH}")
        return False
    
    model = joblib.load(MODEL_PATH)
    print(f"\n✓ Model loaded: {MODEL_PATH}")
    print(f"✓ Threshold: {OPTIMAL_THRESHOLD}")
    
    # Generate synthetic transactions
    print(f"\n📊 Generating {n_transactions} synthetic transactions...")
    transactions = generate_synthetic_transactions(n_transactions)
    
    # Score transactions
    print(f"\n🔮 Scoring transactions in real-time...\n")
    
    predictions = []
    blocked = 0
    approved = 0
    
    for i, trans in enumerate(transactions):
        try:
            # Preprocess
            X = preprocess_transaction(trans)
            
            # Predict
            prob = model.predict_proba(X)[0, 1]
            decision = 'BLOCK' if prob >= OPTIMAL_THRESHOLD else 'APPROVE'
            
            if decision == 'BLOCK':
                blocked += 1
                symbol = '🚫'
            else:
                approved += 1
                symbol = '✓'
            
            prediction = {
                'transaction_id': trans['transaction_id'],
                'timestamp': trans['timestamp'].isoformat(),
                'amount': float(trans['amount']),
                'fraud_probability': float(prob),
                'decision': decision,
                'confidence': float(max(prob, 1 - prob))
            }
            predictions.append(prediction)
            
            # Print progress
            if (i + 1) % max(1, n_transactions // 10) == 0 or i == 0:
                print(f"  [{i+1:4d}/{n_transactions}] {symbol} {decision:7s} | Prob: {prob:.4f}")
        
        except Exception as e:
            print(f"  ✗ Error scoring transaction {i}: {e}")
            continue
    
    # Summary
    print(f"\n📈 SIMULATION RESULTS:")
    print(f"   Total Transactions: {len(predictions)}")
    print(f"   Approved: {approved} ({100*approved/len(predictions):.1f}%)")
    print(f"   Blocked: {blocked} ({100*blocked/len(predictions):.1f}%)")
    print(f"   Average Fraud Probability: {np.mean([p['fraud_probability'] for p in predictions]):.4f}")
    
    # Save simulation log
    os.makedirs(os.path.dirname(SIMULATION_LOG), exist_ok=True)
    
    simulation_data = {
        'timestamp': datetime.now().isoformat(),
        'n_transactions': len(predictions),
        'approved': approved,
        'blocked': blocked,
        'block_rate': blocked / len(predictions) if predictions else 0,
        'threshold': OPTIMAL_THRESHOLD,
        'predictions': predictions[:100]  # Save first 100 for inspection
    }
    
    with open(SIMULATION_LOG, 'w') as f:
        json.dump(simulation_data, f, indent=2, default=str)
    
    print(f"\n✓ Simulation log saved: {SIMULATION_LOG}")
    
    # Performance summary
    if blocked > 0:
        avg_fraud_prob_blocked = np.mean([p['fraud_probability'] for p in predictions if p['decision'] == 'BLOCK'])
        print(f"\n   Avg Fraud Prob (Blocked): {avg_fraud_prob_blocked:.4f}")
    
    if approved > 0:
        avg_fraud_prob_approved = np.mean([p['fraud_probability'] for p in predictions if p['decision'] == 'APPROVE'])
        print(f"   Avg Fraud Prob (Approved): {avg_fraud_prob_approved:.4f}")
    
    print("\n" + "=" * 70)
    print("✓ SIMULATION COMPLETE")
    print("=" * 70)
    return True


if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Run realtime fraud detection simulation')
    parser.add_argument('--transactions', type=int, default=100, help='Number of transactions to simulate')
    args = parser.parse_args()
    
    success = run_simulation(n_transactions=args.transactions)
    sys.exit(0 if success else 1)
