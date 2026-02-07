import os
import joblib
import pandas as pd

from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)

# -----------------------------
# FORCE PROJECT ROOT
# -----------------------------
while not os.path.exists("data"):
    os.chdir("..")

# -----------------------------
# PATHS
# -----------------------------
DATA_PATH = os.path.join("data", "raw", "transactions.csv")
MODEL_PATH = os.path.join("models", "fraud_model.pkl")

# -----------------------------
# LOAD
# -----------------------------
model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

X = df.drop(["is_fraud", "transaction_id"], axis=1)
y = df["is_fraud"]

# -----------------------------
# PREDICT
# -----------------------------
y_pred = model.predict(X)

# -----------------------------
# METRICS
# -----------------------------
print("\nMODEL EVALUATION\n")
print("Precision :", precision_score(y, y_pred))
print("Recall    :", recall_score(y, y_pred))
print("F1 Score  :", f1_score(y, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y, y_pred))
