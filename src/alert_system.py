import os
from datetime import datetime

# -----------------------------
# FORCE PROJECT ROOT
# -----------------------------
while not os.path.exists("reports"):
    os.chdir("..")

# -----------------------------
# PATHS
# -----------------------------
DRIFT_REPORT_PATH = os.path.join("reports", "drift_report.txt")
ALERT_LOG_PATH = os.path.join("reports", "alerts.log")

# -----------------------------
# THRESHOLDS
# -----------------------------
PSI_THRESHOLD = 0.2
KS_PVALUE_THRESHOLD = 0.05

# -----------------------------
# READ DRIFT REPORT
# -----------------------------
if not os.path.exists(DRIFT_REPORT_PATH):
    raise FileNotFoundError("Drift report not found. Run monitor_drift.py first.")

with open(DRIFT_REPORT_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

# -----------------------------
# PARSE DRIFT RESULTS
# -----------------------------
alerts = []
current_feature = None
psi = None
ks_p = None

for line in lines:
    line = line.strip()

    if line.startswith("Feature:"):
        current_feature = line.split(":")[1].strip()

    elif line.startswith("PSI"):
        psi = float(line.split(":")[1].strip())

    elif line.startswith("KS p-value"):
        ks_p = float(line.split(":")[1].strip())

        if psi > PSI_THRESHOLD or ks_p < KS_PVALUE_THRESHOLD:
            alerts.append(
                f"DRIFT DETECTED in feature '{current_feature}' "
                f"(PSI={psi}, KS_p={ks_p})"
            )

# -----------------------------
# WRITE ALERTS (UTF-8 SAFE)
# -----------------------------
os.makedirs("reports", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(ALERT_LOG_PATH, "a", encoding="utf-8") as log:
    if alerts:
        log.write(f"\n[{timestamp}] ALERTS TRIGGERED\n")
        for alert in alerts:
            log.write(alert + "\n")
    else:
        log.write(f"\n[{timestamp}] No drift detected\n")

# -----------------------------
# PRINT STATUS
# -----------------------------
if alerts:
    print("ALERTS GENERATED:")
    for alert in alerts:
        print(alert)
else:
    print("No drift detected. System stable.")
