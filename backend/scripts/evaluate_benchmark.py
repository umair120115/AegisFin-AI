import time
import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)

def run_comparative_benchmark(csv_path: str = "backend/data/aegisfin_benchmark_5k.csv"):
    df = pd.read_csv(csv_path)
    y_true = df["ground_truth_is_fraud"].values
    t0 = time.perf_counter()

    # --- BASELINE: Traditional Sender-Only Rule / ML System ---
    baseline_scores = np.where(
        (df["amount_inr"] > 2.5 * df["sender_monthly_avg_inr"]) |
        ((df["amount_inr"] >= 45000) & (df["amount_inr"] < 50000)),
        0.85, 0.15
    )
    baseline_preds = (baseline_scores >= 0.50).astype(int)

    # --- AEGISFIN-CORE: 4-Pillar Request-Level Bi-Directional Engine ---
    aegis_scores = []
    for _, row in df.iterrows():
        # 1. Sender ratio score
        ratio = row["amount_inr"] / max(row["sender_monthly_avg_inr"], 5000.0)
        s_score = min(0.95, 0.10 + 0.14 * ratio)

        # 2. Instant Receiver History Score (Weight: 40%)
        r_pts = 15.0
        if row["receiver_kyb_verified"] and row["receiver_account_age_days"] > 180:
            r_pts -= 12.0
        if row["receiver_pass_through_ratio_24h"] >= 0.85 and row["receiver_avg_holding_mins"] < 30:
            r_pts += 45.0
        if not row["receiver_kyb_verified"] and row["receiver_distinct_states_24h"] >= 5:
            r_pts += 25.0
        if row["receiver_dot_fri_tier"] in ["HIGH", "VERY_HIGH"] or row["receiver_ncrp_flags"] > 0:
            r_pts += 35.0
        r_score = np.clip(r_pts / 100.0, 0.01, 0.99)

        # 3. App Log Telemetry Boost & Indian Life-Event Dampener
        log_boost = 0.0
        if row["log_remote_apk_overlay"]:
            log_boost += 45.0
        if row["log_active_unknown_call"]:
            log_boost += 30.0
        if row["log_intent_referrer"] != "NATIVE_APP":
            log_boost += 18.0

        life_dampener = 0.0
        if r_score <= 0.20 and (row["recent_fd_liquidation"] or row["shared_family_bssid"]):
            life_dampener = 35.0

        # 4. Structuring / Graph AML Boost
        g_score = 0.90 if (45000 <= row["amount_inr"] < 50000 and not row["shared_family_bssid"] and r_score > 0.5) else 0.05
        final_100 = np.clip((0.25 * s_score + 0.45 * r_score + 0.30 * g_score) * 100.0 + log_boost - life_dampener, 1.0, 99.9)
        aegis_scores.append(final_100 / 100.0)

    aegis_scores = np.array(aegis_scores)
    aegis_preds = (aegis_scores >= 0.60).astype(int)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Verification assertions & metrics
    wedding_mask = (df["scenario_tag"] == "INDIAN_LIFE_EVENT_LEGIT").values
    vishing_mask = (df["scenario_tag"] == "ELDER_OTP_VISHING_SCAM").values

    wedding_fp_rate = float(aegis_preds[wedding_mask].mean())
    elder_vishing_catch_rate = float(aegis_preds[vishing_mask].mean())
    f1 = float(f1_score(y_true, aegis_preds))

    results = {
        "total_transactions_tested": len(df),
        "avg_latency_per_tx_ms": round(elapsed_ms / len(df), 3),
        "baseline_sender_only": {
            "precision": round(precision_score(y_true, baseline_preds), 4),
            "recall": round(recall_score(y_true, baseline_preds), 4),
            "f1_score": round(f1_score(y_true, baseline_preds), 4),
            "roc_auc": round(roc_auc_score(y_true, baseline_scores), 4),
            "wedding_false_positive_rate": f"{baseline_preds[wedding_mask].mean() * 100:.1f}%",
            "elder_vishing_detection_rate": f"{baseline_preds[vishing_mask].mean() * 100:.1f}%"
        },
        "aegisfin_bidirectional_middleware": {
            "precision": round(precision_score(y_true, aegis_preds), 4),
            "recall": round(recall_score(y_true, aegis_preds), 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc_score(y_true, aegis_scores), 4),
            "wedding_false_positive_rate": f"{wedding_fp_rate * 100:.1f}%",
            "elder_vishing_detection_rate": f"{elder_vishing_catch_rate * 100:.1f}%",
            "confusion_matrix": confusion_matrix(y_true, aegis_preds).tolist()
        }
    }
    return results

if __name__ == "__main__":
    import json
    res = run_comparative_benchmark()
    print(json.dumps(res, indent=2))
