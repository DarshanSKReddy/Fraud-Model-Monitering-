import os
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

# -----------------------------
# FORCE PROJECT ROOT
# -----------------------------
while not os.path.exists("data"):
    os.chdir("..")

# -----------------------------
# PATHS
# -----------------------------
DATA_PATH = os.path.join("data", "raw", "transactions.csv")
REPORT_PATH = os.path.join("reports", "drift_report.txt")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(DATA_PATH)

reference = df.sample(3000, random_state=42)
current = reference.copy()

# -----------------------------
# SIMULATE DRIFT
# -----------------------------
current["amount"] *= 1.5
current["velocity_last_24h"] += 2

# -----------------------------
# PSI FUNCTION
# -----------------------------
def calculate_psi(expected, actual, bins=10):
    expected = np.array(expected)
    actual = np.array(actual)

    breakpoints = np.linspace(0, 100, bins + 1)
    expected_perc = np.percentile(expected, breakpoints)
    actual_perc = np.percentile(actual, breakpoints)

    psi = 0
    for i in range(bins):
        exp_pct = np.mean((expected >= expected_perc[i]) & (expected < expected_perc[i + 1]))
        act_pct = np.mean((actual >= actual_perc[i]) & (actual < actual_perc[i + 1]))

        exp_pct = max(exp_pct, 1e-6)
        act_pct = max(act_pct, 1e-6)

        psi += (exp_pct - act_pct) * np.log(exp_pct / act_pct)

    return psi

# -----------------------------
# NUMERIC FEATURES ONLY
# -----------------------------
numeric_features = [
    "amount",
    "transaction_hour",
    "device_trust_score",
    "velocity_last_24h",
    "cardholder_age"
]

# -----------------------------
# DRIFT ANALYSIS
# -----------------------------
results = []

for col in numeric_features:
    psi = calculate_psi(reference[col], current[col])
    ks_stat, ks_p = ks_2samp(reference[col], current[col])

    results.append({
        "feature": col,
        "PSI": round(psi, 4),
        "KS_stat": round(ks_stat, 4),
        "KS_p_value": round(ks_p, 6),
        "Drift": "YES" if psi > 0.2 or ks_p < 0.05 else "NO"
    })

# -----------------------------
# SAVE REPORT
# -----------------------------
os.makedirs("reports", exist_ok=True)

with open(REPORT_PATH, "w") as f:
    f.write("DATA DRIFT REPORT (PSI + KS TEST)\n")
    f.write("=" * 40 + "\n\n")

    for r in results:
        f.write(f"Feature: {r['feature']}\n")
        f.write(f"  PSI        : {r['PSI']}\n")
        f.write(f"  KS stat    : {r['KS_stat']}\n")
        f.write(f"  KS p-value : {r['KS_p_value']}\n")
        f.write(f"  Drift     : {r['Drift']}\n\n")

print("✅ Drift analysis completed")
print("📄 Report saved at:", REPORT_PATH)
