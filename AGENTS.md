# AegisFin-Core: Request-Level FinTech AI Security & AML Middleware

## Core Architecture
- **Backend (`./backend`)**: Python 3.12, FastAPI, Pydantic v2, XGBoost, IsolationForest (`scikit-learn`), TreeSHAP (`shap`), NetworkX, `google-genai` SDK.
- **Frontend (`./frontend`)**: React 18 / Vite + Tailwind CSS + Lucide Icons + Recharts / Cytoscape network graph.
- **Port Bindings**: Backend on `http://localhost:8000`; Frontend on `http://localhost:3000` (or `5173`).

## The 4-Pillar Bi-Directional Risk Equation
Every request to `POST /api/v2/fintech/evaluate-request` computes a Composite Risk Score (1.0 to 99.9):
`S_final = clip(100 * (0.20*P_xgb + 0.15*A_iso + 0.35*R_recv + 0.30*G_aml) + Log_Boost - Life_Event_Dampener, 1.0, 99.9)`

1. **`R_recv` (35% weight)**: Evaluates receiver `account_age_days`, `kyb_verified_merchant`, `pass_through_outflow_ratio_24h`, `avg_holding_time_minutes`, `distinct_sender_states_24h`, and DoT FRI / NCRP 1930 flags.
2. **`G_aml` (30% weight)**: Detects Structuring (`₹45,000-₹49,999` split transfers), Circular Round-Tripping (`A -> B -> C -> A` cycles <= 6 hops), and Fan-In / Fan-Out mule aggregation/dispersion.
3. **`Log_Boost`**: Adds +30 to +65 pts when `app_log` shows `is_on_active_call: true` (unknown caller), remote screen sharing (`com.anydesk.anydeskandroid`), or phishing shortlinks.
4. **`Life_Event_Dampener`**: Subtracts 32 to 35 pts when high-value transfers are backed by `recent_fd_or_mf_redemption_7d: true`, shared family Wi-Fi/BSSID, or trusted merchant MCCs (5944 Jewellery, 8062 Hospital).

## Regulatory & Framework Foundations
- **RBIH MuleHunter.AI**: Shifts primary fraud indicator to receiving accounts.
- **DoT & I4C FRI & NCRP 1930**: Evaluates telecom indicators and cybercrime liens.
- **NPCI ReqValAdd & ReqPay Integration**: Sub-25ms pre-settlement authorization check.
- **FIU-IND Anti-Smurfing & SAR Filing**: Automated narrative generation using Gemini 2.5 Flash.
