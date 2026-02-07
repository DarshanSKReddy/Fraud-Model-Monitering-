import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.inspection import permutation_importance

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

FEATURE_REPORT_PATH = os.path.join("reports", "feature_importance.txt")
TRANSACTION_REPORT_PATH = os.path.join("reports", "transaction_explanations.txt")

# -----------------------------
# LOAD MODEL & DATA
# -----------------------------
model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

X = df.drop(["is_fraud", "transaction_id"], axis=1)
y = df["is_fraud"]

# -----------------------------
# GLOBAL EXPLAINABILITY
# (Permutation Importance)
# -----------------------------
print("Computing global feature importance...")

perm = permutation_importance(
    model,
    X,
    y,
    n_repeats=10,
    random_state=42,
    n_jobs=-1
)

feature_importance = pd.DataFrame({
    "feature": X.columns,
    "importance": perm.importances_mean
}).sort_values(by="importance", ascending=False)

# -----------------------------
# SAVE FEATURE IMPORTANCE
# -----------------------------
os.makedirs("reports", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(FEATURE_REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(f"[{timestamp}] GLOBAL FEATURE IMPORTANCE\n")
    f.write("=" * 45 + "\n\n")

    for _, row in feature_importance.iterrows():
        f.write(f"{row['feature']}: {row['importance']:.4f}\n")

print("Global feature importance saved.")

# -----------------------------
# LOCAL EXPLAINABILITY
# (Explain top fraud cases)
# -----------------------------
print("Generating transaction-level explanations...")

df["prediction"] = model.predict(X)
fraud_cases = df[df["prediction"] == 1].head(10)

with open(TRANSACTION_REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(f"[{timestamp}] TRANSACTION EXPLANATIONS\n")
    f.write("=" * 45 + "\n\n")

    for idx, row in fraud_cases.iterrows():
        f.write(f"Transaction ID: {row['transaction_id']}\n")
        f.write("Reasons for fraud prediction:\n")

        # Simple rule-based explanation using high-risk patterns
        if row["amount"] > df["amount"].quantile(0.90):
            f.write("- High transaction amount\n")
        if row["foreign_transaction"] == 1:
            f.write("- Foreign transaction\n")
        if row["location_mismatch"] == 1:
            f.write("- Location mismatch detected\n")
        if row["device_trust_score"] < df["device_trust_score"].quantile(0.25):
            f.write("- Low device trust score\n")
        if row["velocity_last_24h"] > df["velocity_last_24h"].quantile(0.90):
            f.write("- High transaction velocity\n")

        f.write("\n")

print("Transaction explanations saved.")

# -----------------------------
# DONE
# -----------------------------
print("\nEXPLAINABILITY COMPLETED")
print("Feature importance report:", FEATURE_REPORT_PATH)
print("Transaction explanation report:", TRANSACTION_REPORT_PATH)
