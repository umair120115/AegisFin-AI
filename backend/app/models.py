from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime

class CallTelemetry(BaseModel):
    is_on_active_call: bool = False
    call_type: str = "NONE" # "CELLULAR_VOICE", "WHATSAPP_VOICE"
    caller_in_address_book: bool = True
    call_duration_sec: int = 0

class OsIntegrity(BaseModel):
    screen_overlay_detected: bool = False
    accessibility_remote_control_active: bool = False
    active_remote_package: str = "none" # e.g. "com.anydesk.anydeskandroid"
    sim_swap_within_72h: bool = False

class SessionBehavior(BaseModel):
    deep_link_referrer: str = "NATIVE_APP" # "SMS_SHORTLINK", "WHATSAPP_LINK", "COLLECT_PULL"
    clipboard_paste_detected: bool = False
    mpin_entry_hesitation_ms: float = 250.0

class AppLogTelemetry(BaseModel):
    sdk_version: str = "4.2.1-android"
    device_id_hash: str = "sha256_mock_device"
    ip_address: str = "49.36.128.14"
    ip_city: str = "Lucknow"
    lat: float = 26.8467
    lon: float = 80.9462
    call_telemetry: CallTelemetry = Field(default_factory=CallTelemetry)
    os_integrity: OsIntegrity = Field(default_factory=OsIntegrity)
    session_behavior: SessionBehavior = Field(default_factory=SessionBehavior)

class SenderContext(BaseModel):
    age_cohort: Literal["YOUTH", "ADULT", "SENIOR_60_PLUS"] = "ADULT"
    monthly_avg_outflow_inr: float = 65000.0
    recent_fd_or_mf_redemption_7d: bool = False
    shared_family_bssid_with_sender_group: bool = False
    prior_tx_count_with_receiver: int = 0

class ReceiverInstantHistory(BaseModel):
    receiver_id: Optional[str] = None
    account_age_days: int = 450
    kyb_verified_merchant: bool = False
    mcc_code: str = "0000_P2P"
    dot_fri_risk_tier: Literal["NONE", "MEDIUM", "HIGH", "VERY_HIGH"] = "NONE"
    ncrp_1930_lien_flags: int = 0
    distinct_sender_states_24h: int = 1
    avg_holding_time_minutes: float = 1440.0
    pass_through_outflow_ratio_24h: float = 0.15

class FinTechPaymentRequest(BaseModel):
    request_id: str
    tx_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender_vpa: str
    receiver_vpa: str
    amount_inr: float
    channel: Literal["UPI_PUSH", "UPI_COLLECT_PULL", "IMPS", "NEFT", "WALLET"] = "UPI_PUSH"
    app_log: AppLogTelemetry = Field(default_factory=AppLogTelemetry)
    sender_context: SenderContext = Field(default_factory=SenderContext)
    receiver_history: ReceiverInstantHistory = Field(default_factory=ReceiverInstantHistory)

class XaiFactor(BaseModel):
    pillar: Literal["RECEIVER_HISTORY", "APP_LOG_SHIELD", "GRAPH_AML", "SENDER_BEHAVIOR", "LIFE_EVENT_CONTEXT"]
    feature: str
    impact_pts: float
    reason: str

class FinTechRiskDecisionResponse(BaseModel):
    request_id: str
    tx_id: str
    composite_risk_score: float
    risk_tier: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    enforcement_action: Literal[
        "ALLOW_SETTLEMENT",
        "SHOW_RECEIVER_CAUTION_BANNER",
        "COOLING_OFF_15M_AND_VERNACULAR_VOICE_ALERT",
        "BLOCK_AND_FREEZE_MULE_GRAPH"
    ]
    sub_scores: Dict[str, float]
    aml_typology_detected: str
    xai_waterfall: List[XaiFactor]
    vernacular_user_message: Optional[str] = None
    fiu_ind_sar_ready: bool = False
    latency_ms: float
