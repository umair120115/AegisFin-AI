import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Literal
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    FinTechPaymentRequest, FinTechRiskDecisionResponse,
    AppLogTelemetry, CallTelemetry, OsIntegrity, SessionBehavior,
    SenderContext, ReceiverInstantHistory
)
from app.engine.production_engine import ProductionAIEngine
from app.engine.sar_generator import generate_regulatory_sar
from scripts.evaluate_benchmark import run_comparative_benchmark

app = FastAPI(title="AegisFin-Core: Request-Level FinTech Risk & AML Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ProductionAIEngine()
recent_decisions: List[Dict[str, Any]] = []

@app.get("/")
def health_check():
    return {"status": "ONLINE", "version": "2.0.0", "engine": "AegisFin-Core Bi-Directional Request Shield"}

@app.get("/api/v2/fintech/download-dataset")
def download_benchmark_dataset():
    csv_path = "backend/data/aegisfin_benchmark_5k.csv"
    if not os.path.exists(csv_path):
        csv_path = "data/aegisfin_benchmark_5k.csv"
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Benchmark dataset not found.")
    return FileResponse(
        path=csv_path,
        filename="aegisfin_benchmark_5k.csv",
        media_type="text/csv"
    )

@app.post("/api/v2/fintech/evaluate-request", response_model=FinTechRiskDecisionResponse)
def evaluate_payment_request(payload: FinTechPaymentRequest):
    decision = engine.evaluate_request(payload)
    recent_decisions.insert(0, decision.model_dump())
    del recent_decisions[100:] # Keep latest 100
    return decision

@app.get("/api/v2/fintech/feed")
def get_live_feed():
    return recent_decisions

@app.get("/api/v2/fintech/graph-topology")
def get_aml_graph():
    return engine.get_graph_topology()

@app.post("/api/v2/fintech/simulate/{scenario_id}", response_model=FinTechRiskDecisionResponse)
def simulate_scenario(scenario_id: Literal[
    "WEDDING_LEGIT", "FAMILY_SPLIT_LEGIT", "ELDER_VISHING_SCAM", "AML_SMURFING", "CIRCULAR_AML_LOOP"
]):
    now = datetime.utcnow()
    tx_code = f"UPI-{uuid.uuid4().hex[:6].upper()}"

    if scenario_id == "WEDDING_LEGIT":
        req = FinTechPaymentRequest(
            request_id=f"REQ-{uuid.uuid4().hex[:8]}",
            tx_id=tx_code,
            sender_vpa="rahul.verma@okaxis",
            receiver_vpa="tanishq.jewellers.lko@hdfcbank",
            amount_inr=450000.0,
            channel="UPI_PUSH",
            app_log=AppLogTelemetry(),
            sender_context=SenderContext(
                age_cohort="ADULT",
                monthly_avg_outflow_inr=75000.0,
                recent_fd_or_mf_redemption_7d=True
            ),
            receiver_history=ReceiverInstantHistory(
                account_age_days=2150,
                kyb_verified_merchant=True,
                mcc_code="5944_JEWELLERY",
                pass_through_outflow_ratio_24h=0.08,
                avg_holding_time_minutes=2880.0
            )
        )
    elif scenario_id == "FAMILY_SPLIT_LEGIT":
        req = FinTechPaymentRequest(
            request_id=f"REQ-{uuid.uuid4().hex[:8]}",
            tx_id=tx_code,
            sender_vpa="priya.sharma@ybl",
            receiver_vpa="apollo.hospital.billing@icici",
            amount_inr=95000.0,
            channel="UPI_PUSH",
            app_log=AppLogTelemetry(),
            sender_context=SenderContext(
                age_cohort="ADULT",
                monthly_avg_outflow_inr=40000.0,
                shared_family_bssid_with_sender_group=True
            ),
            receiver_history=ReceiverInstantHistory(
                account_age_days=2800,
                kyb_verified_merchant=True,
                mcc_code="8062_HOSPITAL",
                pass_through_outflow_ratio_24h=0.04,
                avg_holding_time_minutes=4320.0
            )
        )
    elif scenario_id == "ELDER_VISHING_SCAM":
        req = FinTechPaymentRequest(
            request_id=f"REQ-{uuid.uuid4().hex[:8]}",
            tx_id=tx_code,
            sender_vpa="ramesh.gupta.senior@sbi",
            receiver_vpa="ebill.kyc.officer99@ybl",
            amount_inr=48500.0,
            channel="UPI_PUSH",
            app_log=AppLogTelemetry(
                call_telemetry=CallTelemetry(
                    is_on_active_call=True,
                    call_type="CELLULAR_VOICE",
                    caller_in_address_book=False,
                    call_duration_sec=320
                ),
                os_integrity=OsIntegrity(
                    accessibility_remote_control_active=True,
                    active_remote_package="com.anydesk.anydeskandroid"
                ),
                session_behavior=SessionBehavior(
                    deep_link_referrer="SMS_SHORTLINK",
                    clipboard_paste_detected=True
                )
            ),
            sender_context=SenderContext(
                age_cohort="SENIOR_60_PLUS",
                monthly_avg_outflow_inr=28000.0
            ),
            receiver_history=ReceiverInstantHistory(
                account_age_days=11,
                kyb_verified_merchant=False,
                mcc_code="0000_P2P",
                dot_fri_risk_tier="VERY_HIGH",
                ncrp_1930_lien_flags=2,
                distinct_sender_states_24h=9,
                avg_holding_time_minutes=6.5,
                pass_through_outflow_ratio_24h=0.98
            )
        )
    elif scenario_id == "AML_SMURFING":
        # Simulate prior split transfers to populate recent history
        for i in range(2):
            prior_req = FinTechPaymentRequest(
                request_id=f"REQ-PRE-{i}",
                tx_id=f"TX-PRE-{i}",
                sender_vpa="shell.corp.alpha@icici",
                receiver_vpa="mule.cashout.77@axis",
                amount_inr=48900.0 + i * 200,
                channel="UPI_PUSH"
            )
            engine.recent_requests.append(prior_req)

        req = FinTechPaymentRequest(
            request_id=f"REQ-{uuid.uuid4().hex[:8]}",
            tx_id=tx_code,
            sender_vpa="shell.corp.alpha@icici",
            receiver_vpa="mule.cashout.77@axis",
            amount_inr=49500.0,
            channel="UPI_PUSH",
            app_log=AppLogTelemetry(),
            sender_context=SenderContext(
                age_cohort="ADULT",
                monthly_avg_outflow_inr=150000.0
            ),
            receiver_history=ReceiverInstantHistory(
                account_age_days=14,
                kyb_verified_merchant=False,
                dot_fri_risk_tier="HIGH",
                distinct_sender_states_24h=6,
                pass_through_outflow_ratio_24h=0.94,
                avg_holding_time_minutes=15.0
            )
        )
    else: # CIRCULAR_AML_LOOP
        # Seed graph cycle A -> B -> C -> A
        engine.tx_graph.add_edge("ENTITY_ALPHA", "SHELL_BETA", key="TX-C1", amount=350000.0)
        engine.tx_graph.add_edge("SHELL_BETA", "OFFSHORE_GAMMA", key="TX-C2", amount=345000.0)
        req = FinTechPaymentRequest(
            request_id=f"REQ-{uuid.uuid4().hex[:8]}",
            tx_id=tx_code,
            sender_vpa="OFFSHORE_GAMMA",
            receiver_vpa="ENTITY_ALPHA",
            amount_inr=340000.0,
            channel="IMPS",
            app_log=AppLogTelemetry(),
            sender_context=SenderContext(
                age_cohort="ADULT",
                monthly_avg_outflow_inr=300000.0
            ),
            receiver_history=ReceiverInstantHistory(
                account_age_days=25,
                kyb_verified_merchant=False,
                dot_fri_risk_tier="HIGH",
                pass_through_outflow_ratio_24h=0.95
            )
        )

    decision = engine.evaluate_request(req)
    recent_decisions.insert(0, decision.model_dump())
    return decision

@app.post("/api/v2/fintech/benchmark-csv")
def run_benchmark():
    return run_comparative_benchmark()

@app.post("/api/v2/fintech/generate-sar")
def create_sar(alert_data: Dict[str, Any]):
    narrative = generate_regulatory_sar(alert_data)
    return {
        "status": "GENERATED",
        "sar_narrative_markdown": narrative,
        "filing_destination": "FIU-IND_PORTAL"
    }
