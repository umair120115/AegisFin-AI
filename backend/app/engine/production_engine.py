import os
import joblib
import numpy as np
import networkx as nx
import shap
from typing import Dict, List, Tuple, Any
from app.models import (
    FinTechPaymentRequest, FinTechRiskDecisionResponse,
    ReceiverInstantHistory, XaiFactor
)
from app.engine.feature_store_db import HybridFeatureStore

class ProductionAIEngine:
    def __init__(self, artifacts_dir: str = "backend/artifacts"):
        self.tx_graph = nx.MultiDiGraph()
        self.recent_requests: List[FinTechPaymentRequest] = []
        self.feature_store = HybridFeatureStore()

        # Load serialized production models if available
        xgb_path = os.path.join(artifacts_dir, "xgb_fraud.joblib")
        iso_path = os.path.join(artifacts_dir, "iso_anomaly.joblib")

        if os.path.exists(xgb_path) and os.path.exists(iso_path):
            self.xgb_model = joblib.load(xgb_path)
            self.iso_model = joblib.load(iso_path)
            self.shap_explainer = shap.TreeExplainer(self.xgb_model)
            print("[+] Loaded trained XGBoost & IsolationForest models from artifacts.")
        else:
            self.xgb_model = None
            self.iso_model = None
            self.shap_explainer = None
            print("[!] Artifacts not found. Using calibrated internal ML scoring.")

        self.feature_names = [
            "amount_to_avg_ratio",
            "receiver_pass_through_24h",
            "receiver_distinct_states_24h",
            "active_unknown_voice_call",
            "remote_screen_share_apk",
            "receiver_kyb_verified"
        ]

    def evaluate_request(self, req: FinTechPaymentRequest) -> FinTechRiskDecisionResponse:
        import time
        t0 = time.perf_counter()
        xai: List[XaiFactor] = []

        # Sliding window & Graph ingestion
        self.recent_requests.append(req)
        self.tx_graph.add_edge(req.sender_vpa, req.receiver_vpa, key=req.tx_id, amount=req.amount_inr)

        # Hydrate receiver history from feature store if default
        if req.receiver_history.account_age_days == 450 and not req.receiver_history.kyb_verified_merchant:
            cached_recv = self.feature_store.get_receiver_history(req.receiver_vpa)
            if cached_recv.account_age_days != 450 or cached_recv.kyb_verified_merchant:
                req.receiver_history = cached_recv

        # PILLAR 1: Receiver Instant Reputation (0 to 1)
        r_score, r_factors = self._score_receiver_history(req.receiver_history, req.amount_inr)
        xai.extend(r_factors)

        # PILLAR 2: ML Inference & TreeSHAP
        s_sup, s_anom, ml_factors = self._score_ml_and_shap(req)
        xai.extend(ml_factors)

        # PILLAR 3: Graph AML Topology Score (0 to 1)
        g_score, aml_typology, g_factors = self._score_graph_aml(req)
        xai.extend(g_factors)

        # PILLAR 4: Session Shield & Life-Event Dampeners
        log_boost, life_dampener, ctx_factors = self._evaluate_logs_and_life_events(req, r_score)
        xai.extend(ctx_factors)

        # Context-Gated Fusion:
        base_100 = (0.20 * s_sup + 0.15 * s_anom + 0.35 * r_score + 0.30 * g_score) * 100.0
        composite = float(np.clip(base_100 + log_boost - life_dampener, 1.0, 99.9))

        # Critical Overrides for Active Mule Rings or Active Vishing Call + High-Risk Receiver
        if g_score >= 0.85 or (r_score >= 0.80 and log_boost >= 30.0):
            composite = max(composite, 94.0)

        composite = round(composite, 1)
        xai.sort(key=lambda f: abs(f.impact_pts), reverse=True)

        # Determine Enforcement Action & Vernacular Audio/Text Warning
        vernacular_msg = None
        if composite >= 85.0:
            tier = "CRITICAL"
            if log_boost >= 30.0:
                action = "COOLING_OFF_15M_AND_VERNACULAR_VOICE_ALERT"
                vernacular_msg = (
                    "Savdhaan! Aap phone call ya link ke zariye ek sandigdh (suspicious) account mein paise bhej rahe hain. "
                    "Suraksha ke liye yeh payment 15 minute ke liye roka gaya hai."
                )
            else:
                action = "BLOCK_AND_FREEZE_MULE_GRAPH"
                vernacular_msg = "Transaction blocked: Destination account flagged for suspected money laundering / mule aggregation."
        elif composite >= 60.0:
            tier = "HIGH"
            action = "SHOW_RECEIVER_CAUTION_BANNER"
            vernacular_msg = "Caution: This receiving account has unusual transaction history. Please verify beneficiary identity."
        elif composite >= 35.0:
            tier = "MEDIUM"
            action = "SHOW_RECEIVER_CAUTION_BANNER"
        else:
            tier = "LOW"
            action = "ALLOW_SETTLEMENT"

        latency = round((time.perf_counter() - t0) * 1000.0, 2)
        response = FinTechRiskDecisionResponse(
            request_id=req.request_id,
            tx_id=req.tx_id,
            composite_risk_score=composite,
            risk_tier=tier,
            enforcement_action=action,
            sub_scores={
                "receiver_history_score": round(r_score * 100, 1),
                "sender_supervised_score": round(s_sup * 100, 1),
                "sender_anomaly_score": round(s_anom * 100, 1),
                "graph_aml_score": round(g_score * 100, 1),
                "app_log_modifier_pts": round(log_boost - life_dampener, 1)
            },
            aml_typology_detected=aml_typology,
            xai_waterfall=xai[:6],
            vernacular_user_message=vernacular_msg,
            fiu_ind_sar_ready=(composite >= 80.0),
            latency_ms=latency
        )

        self.feature_store.update_state_async(req.sender_vpa, req.receiver_vpa, req.amount_inr, response.model_dump())
        return response

    def _score_receiver_history(self, rh: ReceiverInstantHistory, amount: float) -> Tuple[float, List[XaiFactor]]:
        pts = 15.0
        factors: List[XaiFactor] = []

        if rh.kyb_verified_merchant and rh.account_age_days > 180:
            pts -= 12.0
            factors.append(XaiFactor(
                pillar="RECEIVER_HISTORY", feature="kyb_verified_merchant", impact_pts=-12.0,
                reason=f"Verified Merchant ({rh.mcc_code}) with {rh.account_age_days}d clean operating history."
            ))
        elif rh.account_age_days > 365 and rh.pass_through_outflow_ratio_24h < 0.30:
            pts -= 8.0
            factors.append(XaiFactor(
                pillar="RECEIVER_HISTORY", feature="established_peer_retention", impact_pts=-8.0,
                reason=f"Established receiver ({rh.account_age_days}d old) with healthy fund retention."
            ))

        if rh.pass_through_outflow_ratio_24h >= 0.85 and rh.avg_holding_time_minutes < 30:
            pts += 42.0
            factors.append(XaiFactor(
                pillar="RECEIVER_HISTORY", feature="pass_through_outflow_ratio_24h", impact_pts=+42.0,
                reason=f"Mule Pass-Through: Receiver sweeps out {rh.pass_through_outflow_ratio_24h*100:.0f}% of inflows in <{rh.avg_holding_time_minutes:.0f} mins."
            ))

        if not rh.kyb_verified_merchant and rh.distinct_sender_states_24h >= 5:
            pts += 25.0
            factors.append(XaiFactor(
                pillar="RECEIVER_HISTORY", feature="distinct_sender_states_24h", impact_pts=+25.0,
                reason=f"High Inflow Entropy: Unverified account received money from {rh.distinct_sender_states_24h} different states today."
            ))

        if rh.dot_fri_risk_tier in ["HIGH", "VERY_HIGH"] or rh.ncrp_1930_lien_flags > 0:
            pts += 35.0
            factors.append(XaiFactor(
                pillar="RECEIVER_HISTORY", feature="dot_fri_risk_tier", impact_pts=+35.0,
                reason=f"DoT FRI Telecom Flag ({rh.dot_fri_risk_tier}) & {rh.ncrp_1930_lien_flags} NCRP 1930 cybercrime liens active."
            ))

        return float(np.clip(pts / 100.0, 0.02, 0.99)), factors

    def _score_ml_and_shap(self, req: FinTechPaymentRequest) -> Tuple[float, float, List[XaiFactor]]:
        factors: List[XaiFactor] = []
        amount_ratio = float(req.amount_inr / max(req.sender_context.monthly_avg_outflow_inr, 5000.0))
        pass_through = float(req.receiver_history.pass_through_outflow_ratio_24h)
        recv_states = float(req.receiver_history.distinct_sender_states_24h)
        active_call = 1.0 if req.app_log.call_telemetry.is_on_active_call else 0.0
        remote_apk = 1.0 if req.app_log.os_integrity.accessibility_remote_control_active else 0.0
        kyb_flag = 1.0 if req.receiver_history.kyb_verified_merchant else 0.0

        feat_vec = np.array([[amount_ratio, pass_through, recv_states, active_call, remote_apk, kyb_flag]])

        if self.xgb_model and self.iso_model:
            sup_prob = float(self.xgb_model.predict_proba(feat_vec)[0, 1])
            raw_iso = float(self.iso_model.decision_function(feat_vec)[0])
            anom_score = float(np.clip(0.5 - raw_iso, 0.0, 1.0))

            if self.shap_explainer:
                shap_vals = self.shap_explainer.shap_values(feat_vec)[0]
                for idx, fname in enumerate(self.feature_names):
                    impact = round(float(shap_vals[idx]) * 20.0, 1)
                    if abs(impact) >= 2.0:
                        direction = "increased" if impact > 0 else "reduced"
                        factors.append(XaiFactor(
                            pillar="SENDER_BEHAVIOR",
                            feature=fname,
                            impact_pts=impact,
                            reason=f"TreeSHAP: {fname} {direction} risk score by {abs(impact):.1f} pts."
                        ))
        else:
            sup_prob = min(0.95, 0.12 + 0.14 * amount_ratio)
            anom_score = min(0.95, 0.10 + 0.18 * amount_ratio)
            if amount_ratio >= 1.5:
                factors.append(XaiFactor(
                    pillar="SENDER_BEHAVIOR",
                    feature="amount_to_monthly_avg_ratio",
                    impact_pts=round(amount_ratio * 6.5, 1),
                    reason=f"Transfer amount (₹{req.amount_inr:,.0f}) is {amount_ratio:.1f}x sender's monthly average outflow."
                ))

        return sup_prob, anom_score, factors

    def _score_graph_aml(self, req: FinTechPaymentRequest) -> Tuple[float, str, List[XaiFactor]]:
        factors: List[XaiFactor] = []

        # Structuring check (₹45k - ₹49.99k)
        recent_splits = [
            r for r in self.recent_requests
            if r.receiver_vpa == req.receiver_vpa and 45000 <= r.amount_inr < 50000
        ]
        if len(recent_splits) >= 3 and not req.sender_context.shared_family_bssid_with_sender_group:
            factors.append(XaiFactor(
                pillar="GRAPH_AML", feature="structuring_smurfing_band", impact_pts=+34.0,
                reason=f"Structuring detected: {len(recent_splits)} split transfers in ₹45k–₹50k band to evade PAN reporting rules."
            ))
            return 0.92, "STRUCTURING_SMURFING", factors

        # Cycle detection
        if nx.has_path(self.tx_graph, req.receiver_vpa, req.sender_vpa):
            path = nx.shortest_path(self.tx_graph, source=req.receiver_vpa, target=req.sender_vpa)
            if 2 <= len(path) <= 6:
                cycle_str = " -> ".join([req.sender_vpa] + path)
                factors.append(XaiFactor(
                    pillar="GRAPH_AML", feature="circular_round_trip", impact_pts=+38.0,
                    reason=f"Circular AML Loop detected across {len(path)} hops: {cycle_str}"
                ))
                return 0.96, "CIRCULAR_ROUND_TRIP", factors

        return 0.05, "NONE", factors

    def _evaluate_logs_and_life_events(self, req: FinTechPaymentRequest, r_score: float) -> Tuple[float, float, List[XaiFactor]]:
        log_boost = 0.0
        life_dampener = 0.0
        factors: List[XaiFactor] = []
        log = req.app_log

        if log.os_integrity.accessibility_remote_control_active or log.os_integrity.screen_overlay_detected:
            log_boost += 45.0
            factors.append(XaiFactor(
                pillar="APP_LOG_SHIELD", feature="remote_access_apk_active", impact_pts=+45.0,
                reason=f"Request Log Flag: Remote screen-sharing/overlay active ({log.os_integrity.active_remote_package}) during payment."
            ))

        if log.call_telemetry.is_on_active_call and not log.call_telemetry.caller_in_address_book:
            log_boost += 30.0
            factors.append(XaiFactor(
                pillar="APP_LOG_SHIELD", feature="active_unknown_voice_call", impact_pts=+30.0,
                reason=f"Vishing Telemetry: Sender ({req.sender_context.age_cohort}) is on an active call with an unsaved number."
            ))

        if log.session_behavior.deep_link_referrer in ["SMS_SHORTLINK", "WHATSAPP_LINK"] or req.channel == "UPI_COLLECT_PULL":
            log_boost += 18.0
            factors.append(XaiFactor(
                pillar="APP_LOG_SHIELD", feature="phishing_intent_origin", impact_pts=+18.0,
                reason=f"High-Risk Initiation: Payment triggered via {log.session_behavior.deep_link_referrer}."
            ))

        trusted_mccs = ["5944_JEWELLERY", "8062_HOSPITAL", "7011_BANQUET_HOTEL", "8220_EDUCATION"]
        if r_score <= 0.20 and (
            req.sender_context.recent_fd_or_mf_redemption_7d
            or req.sender_context.shared_family_bssid_with_sender_group
            or req.receiver_history.mcc_code in trusted_mccs
        ):
            life_dampener = 35.0
            factors.append(XaiFactor(
                pillar="LIFE_EVENT_CONTEXT", feature="indian_life_event_whitelist", impact_pts=-35.0,
                reason="Life-Event Verified: High-value spike backed by FD/savings redemption or family split to a verified merchant."
            ))

        return log_boost, life_dampener, factors

    def get_graph_topology(self) -> Dict[str, Any]:
        nodes = []
        for n in self.tx_graph.nodes():
            degree = self.tx_graph.degree(n)
            nodes.append({"id": n, "label": n, "degree": degree})
        edges = []
        for u, v, k, data in self.tx_graph.edges(keys=True, data=True):
            edges.append({
                "source": u,
                "target": v,
                "tx_id": k,
                "amount": data.get("amount", 0.0)
            })
        return {"nodes": nodes[-35:], "edges": edges[-45:]}
