import os
import joblib
import pandas as pd
from datetime import datetime
from sklearn.metrics import confusion_matrix

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
REPORT_PATH = os.path.join("reports", "cost_analysis_report.txt")

# -----------------------------
# BUSINESS COST ASSUMPTIONS
# -----------------------------
COST_FALSE_NEGATIVE = 10000   # Missed fraud (₹)
COST_FALSE_POSITIVE = 500     # Wrongly blocked transaction (₹)

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
# CONFUSION MATRIX
# -----------------------------
tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

# -----------------------------
# COST CALCULATION
# -----------------------------
total_cost = (fp * COST_FALSE_POSITIVE) + (fn * COST_FALSE_NEGATIVE)

baseline_cost = y_true.sum() * COST_FALSE_NEGATIVE
savings = baseline_cost - total_cost

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------
# SAVE REPORT
# -----------------------------
os.makedirs("reports", exist_ok=True)

with open(REPORT_PATH, "a", encoding="utf-8") as f:
    f.write(f"\n[{timestamp}] COST ANALYSIS REPORT\n")
    f.write(f"True Positives  : {tp}\n")
    f.write(f"False Positives : {fp}\n")
    f.write(f"False Negatives : {fn}\n")
    f.write(f"True Negatives  : {tn}\n\n")

    f.write(f"Cost (False Negatives): ₹{fn * COST_FALSE_NEGATIVE}\n")
    f.write(f"Cost (False Positives): ₹{fp * COST_FALSE_POSITIVE}\n")
    f.write(f"Total Cost with Model: ₹{total_cost}\n\n")

    f.write(f"Estimated Cost without Model: ₹{baseline_cost}\n")
    f.write(f"Net Savings using Model: ₹{savings}\n")

# -----------------------------
# PRINT OUTPUT
# -----------------------------
print("BUSINESS COST ANALYSIS")
print("----------------------")
print(f"False Positives : {fp}")
print(f"False Negatives : {fn}")
print(f"Total Cost (with model): ₹{total_cost}")
print(f"Estimated Cost (without model): ₹{baseline_cost}")
print(f"Net Savings: ₹{savings}")
print("\nReport saved to:", REPORT_PATH)
