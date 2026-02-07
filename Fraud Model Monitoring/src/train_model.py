import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

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
# LOAD DATA
# -----------------------------
df = pd.read_csv(DATA_PATH)

X = df.drop(["is_fraud", "transaction_id"], axis=1)
y = df["is_fraud"]

# -----------------------------
# FEATURES
# -----------------------------
numeric_features = [
    "amount",
    "transaction_hour",
    "foreign_transaction",
    "location_mismatch",
    "device_trust_score",
    "velocity_last_24h",
    "cardholder_age"
]

categorical_features = ["merchant_category"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ]
)

# -----------------------------
# TRAIN TEST SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# -----------------------------
# MODEL
# -----------------------------
model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

# -----------------------------
# TRAIN
# -----------------------------
pipeline.fit(X_train, y_train)

# -----------------------------
# EVALUATE
# -----------------------------
y_pred = pipeline.predict(X_test)
print("\nMODEL PERFORMANCE\n")
print(classification_report(y_test, y_pred))

# -----------------------------
# SAVE MODEL
# -----------------------------
os.makedirs("models", exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)

print("\nModel saved at:", MODEL_PATH)
