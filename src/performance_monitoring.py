import os
import joblib
import pandas as pd
from datetime import datetime
from sklearn.metrics import precision_score, recall_score, f1_score

# -----------------------------
# FORCE PROJECT ROOT
# -----------------------------
while not os.path.exists("models"):
    os.chdir("..")

# -----------------------------
# PATHS
# -----------------------------
MODEL_PATH = os.path.join("models", "fraud_model.pkl")
DATA_PATH = os.path.join("data", "raw", "transactions.csv")
REPORT_PATH = os.path.join("reports", "performance_report.txt")

# -----------------------------
# LOAD MODEL & DATA
# -----------------------------
model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

X = df.drop(["is_fraud", "transaction_id"], axis=1)
y_true = df["is_fraud"]

# -----------------------------
# PREDICT
# -----------------------------
y_pred = model.predict(X)

# -----------------------------
# METRICS
# -----------------------------
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------
# SAVE PERFORMANCE REPORT
# -----------------------------
os.makedirs("reports", exist_ok=True)

with open(REPORT_PATH, "a", encoding="utf-8") as f:
    f.write(f"\n[{timestamp}] MODEL PERFORMANCE\n")
    f.write(f"Precision : {precision:.4f}\n")
    f.write(f"Recall    : {recall:.4f}\n")
    f.write(f"F1 Score  : {f1:.4f}\n")

# -----------------------------
# PRINT OUTPUT
# -----------------------------
print("MODEL PERFORMANCE MONITORING")
print("----------------------------")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print("\nReport saved to:", REPORT_PATH)
