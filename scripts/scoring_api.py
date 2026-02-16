"""Real-time fraud scoring API using Flask."""
import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, request, jsonify
from sklearn.preprocessing import LabelEncoder
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MODEL_PATH = 'models/baseline_model.joblib'
OPTIMAL_THRESHOLD = 0.29
PREDICTIONS_LOG = 'reports/realtime_predictions.log'

# Initialize Flask app
app = Flask(__name__)

# Load model on startup
try:
    model = joblib.load(MODEL_PATH)
    logger.info(f"✓ Model loaded from {MODEL_PATH}")
except Exception as e:
    logger.error(f"✗ Failed to load model: {e}")
    model = None


def preprocess_transaction(data):
    """Preprocess transaction data for model scoring."""
    try:
        # Create DataFrame from input
        df = pd.DataFrame([data])
        
        # Select numeric features
        numeric_features = [
            'amount', 'transaction_hour', 'velocity_last_24h',
            'device_trust_score', 'cardholder_age', 'foreign_transaction',
            'location_mismatch'
        ]
        
        X = df[numeric_features].copy()
        
        # Handle categorical
        if 'merchant_category' in data:
            le = LabelEncoder()
            categories = ['Grocery', 'Electronics', 'Travel', 'Clothing', 'Food', 'Gas', 'Entertainment']
            le.fit(categories)
            X['merchant_category'] = le.transform([data['merchant_category']])
        
        return X
    except Exception as e:
        logger.error(f"Preprocessing error: {e}")
        return None


def log_prediction(transaction_id, input_data, prediction, probability, decision):
    """Log prediction to audit trail."""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'transaction_id': transaction_id,
        'fraud_probability': float(probability),
        'decision': decision,
        'threshold': OPTIMAL_THRESHOLD,
        'features': input_data
    }
    
    os.makedirs(os.path.dirname(PREDICTIONS_LOG), exist_ok=True)
    with open(PREDICTIONS_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    return log_entry


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    """Score a single transaction for fraud risk."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        transaction_id = data.get('transaction_id', 'unknown')
        
        # Preprocess
        X = preprocess_transaction(data)
        if X is None or X.shape[1] == 0:
            return jsonify({'error': 'Invalid transaction features'}), 400
        
        # Predict
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        probability = model.predict_proba(X)[0, 1]
        decision = 'BLOCK' if probability >= OPTIMAL_THRESHOLD else 'APPROVE'
        confidence = max(probability, 1 - probability)
        
        # Log
        log_prediction(transaction_id, data, 1 if decision == 'BLOCK' else 0, probability, decision)
        
        logger.info(f"Transaction {transaction_id}: {decision} (prob={probability:.4f})")
        
        return jsonify({
            'transaction_id': transaction_id,
            'fraud_probability': float(probability),
            'decision': decision,
            'confidence': float(confidence),
            'threshold': OPTIMAL_THRESHOLD,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Score multiple transactions."""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'error': 'Expected list of transactions'}), 400
        
        results = []
        for transaction in data:
            X = preprocess_transaction(transaction)
            if X is None:
                results.append({
                    'transaction_id': transaction.get('transaction_id', 'unknown'),
                    'error': 'Invalid features'
                })
                continue
            
            probability = model.predict_proba(X)[0, 1]
            decision = 'BLOCK' if probability >= OPTIMAL_THRESHOLD else 'APPROVE'
            
            result = {
                'transaction_id': transaction.get('transaction_id', 'unknown'),
                'fraud_probability': float(probability),
                'decision': decision,
                'confidence': float(max(probability, 1 - probability))
            }
            results.append(result)
            
            # Log
            log_prediction(result['transaction_id'], transaction, 1 if decision == 'BLOCK' else 0, probability, decision)
        
        logger.info(f"Batch prediction completed: {len(results)} transactions")
        
        return jsonify({
            'count': len(results),
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    """Get prediction statistics."""
    try:
        if not os.path.exists(PREDICTIONS_LOG):
            return jsonify({'error': 'No predictions yet'}), 404
        
        with open(PREDICTIONS_LOG, 'r') as f:
            lines = f.readlines()
        
        total = len(lines)
        blocked = sum(1 for line in lines if 'BLOCK' in line)
        approved = total - blocked
        
        return jsonify({
            'total_predictions': total,
            'blocked': blocked,
            'approved': approved,
            'block_rate': blocked / total if total > 0 else 0,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("FRAUD DETECTION REAL-TIME SCORING API")
    print("=" * 70)
    print(f"\n✓ Model loaded from: {MODEL_PATH}")
    print(f"✓ Optimal threshold: {OPTIMAL_THRESHOLD}")
    print(f"✓ Predictions logged to: {PREDICTIONS_LOG}")
    print("\nAvailable endpoints:")
    print("  GET  /health           - Health check")
    print("  POST /predict          - Score single transaction")
    print("  POST /batch_predict    - Score multiple transactions")
    print("  GET  /stats            - Prediction statistics")
    print("\n" + "=" * 70)
    print("Starting server on http://localhost:5000")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
