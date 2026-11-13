import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import xgboost as xgb
import shap

def train_and_export(
    csv_path: str = "backend/data/aegisfin_benchmark_5k.csv",
    output_dir: str = "backend/artifacts"
):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)

    # Feature engineering for supervised XGBoost and unsupervised Isolation Forest
    # 1. amount_ratio: amount / sender_avg
    amount_ratio = df["amount_inr"].values / np.maximum(df["sender_monthly_avg_inr"].values, 5000.0)
    # 2. pass_through: receiver_pass_through_ratio_24h
    pass_through = df["receiver_pass_through_ratio_24h"].values
    # 3. receiver_states: distinct sender states
    recv_states = df["receiver_distinct_states_24h"].values
    # 4. active_call: log_active_unknown_call
    active_call = df["log_active_unknown_call"].astype(int).values
    # 5. remote_apk: log_remote_apk_overlay
    remote_apk = df["log_remote_apk_overlay"].astype(int).values
    # 6. kyb_flag: 1 if verified merchant else 0
    kyb_flag = df["receiver_kyb_verified"].astype(int).values

    X = np.column_stack([amount_ratio, pass_through, recv_states, active_call, remote_apk, kyb_flag])
    y = df["ground_truth_is_fraud"].values

    feature_names = [
        "amount_to_avg_ratio",
        "receiver_pass_through_24h",
        "receiver_distinct_states_24h",
        "active_unknown_voice_call",
        "remote_screen_share_apk",
        "receiver_kyb_verified"
    ]

    print("[*] Fitting XGBoost Classifier...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=4,
        learning_rate=0.1,
        eval_metric="logloss",
        random_state=42
    )
    xgb_model.fit(X, y)

    print("[*] Fitting Isolation Forest on normal transactions...")
    X_normal = X[y == 0]
    iso_model = IsolationForest(contamination=0.08, random_state=42)
    iso_model.fit(X_normal)

    print("[*] Initializing TreeSHAP Explainer...")
    shap_explainer = shap.TreeExplainer(xgb_model)

    # Serialize artifacts
    joblib.dump(xgb_model, os.path.join(output_dir, "xgb_fraud.joblib"))
    joblib.dump(iso_model, os.path.join(output_dir, "iso_anomaly.joblib"))
    joblib.dump(feature_names, os.path.join(output_dir, "feature_names.joblib"))
    print(f"[+] Successfully exported trained models & SHAP explainer to {output_dir}")

if __name__ == "__main__":
    train_and_export()
