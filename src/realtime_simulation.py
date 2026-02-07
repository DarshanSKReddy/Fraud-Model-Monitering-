import os
import time
import joblib
import pandas as pd
from datetime import datetime

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
LOG_PATH = os.path.join("reports", "realtime_predictions.log")

# -----------------------------
# LOAD MODEL & DATA
# -----------------------------
model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

X = df.drop(["is_fraud", "transaction_id"], axis=1)
y = df["is_fraud"]

# -----------------------------
# SETUP LOG FILE
# -----------------------------
os.makedirs("reports", exist_ok=True)

with open(LOG_PATH, "w", encoding="utf-8") as log:
    log.write("REAL-TIME FRAUD PREDICTION LOG\n")
    log.write("=" * 40 + "\n\n")

# -----------------------------
# REAL-TIME SIMULATION
# -----------------------------
print("Starting real-time fraud simulation...\n")

for i in range(len(X)):
    transaction = X.iloc[[i]]
    actual_label = y.iloc[i]

    prediction = model.predict(transaction)[0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = "FRAUD" if prediction == 1 else "LEGIT"

    log_line = (
        f"[{timestamp}] "
        f"Transaction #{i+1} | "
        f"Prediction: {result} | "
        f"Actual: {actual_label}\n"
    )

    print(log_line.strip())

    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(log_line)

    time.sleep(0.5)  # simulate streaming delay

print("\nSimulation completed.")
print("Log saved at:", LOG_PATH)
