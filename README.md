# AegisFin-AI: Request-Level FinTech AI Security & AML Middleware

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python)](https://www.python.org/)

An enterprise-grade, request-level financial fraud prevention and Anti-Money Laundering (AML) middleware shield tailored for high-speed digital payment rails (UPI, IMPS, RTGS, mobile wallets).

---

## Key Features

1. **Sub-25ms Pre-Settlement Interception**:
   - Sits at the API gateway layer to evaluate payment requests *before* ledger debit execution.
2. **4-Pillar Bi-Directional Risk Equation**:
   - **Pillar 1 (35% - $R_{\text{recv}}$)**: Receiver Mule Profiling (inflow pass-through ratio, dormancy wake-up, DoT FRI, NCRP 1930 flags).
   - **Pillar 2 (35% - $P_{\text{xgb}}, A_{\text{iso}}$)**: Supervised XGBoost + Isolation Forest Anomaly Detection.
   - **Pillar 3 (30% - $G_{\text{aml}}$)**: Temporal MultiDiGraph detecting structuring ($\text{₹45k-₹49.99k}$) and circular cycles ($A \to B \to C \to A$).
   - **Pillar 4 (Context Modifiers)**: Stops elder vishing/remote APK scams while whitelisting legitimate life events (weddings, hospital bills).
3. **TreeSHAP Explainable AI**:
   - Instant local additive feature attributions for regulatory transparency.
4. **Automated Regulatory SAR Generation**:
   - One-click FIU-IND / FinCEN Suspicious Activity Report drafting powered by Gemini 2.5 Flash.

---

## Project Structure

```
AegisFin-AI/
├── backend/
│   ├── app/
│   │   ├── engine/          # 4-Pillar Scoring, Feature Store & SAR Generator
│   │   ├── models.py        # Pydantic Schemas
│   │   └── main.py          # FastAPI Endpoints & Scenario Simulators
│   ├── scripts/             # PaySim Dataset Builder & Benchmark Ablation
│   ├── tests/               # Pytest Contract & SLA Test Suite
│   └── requirements.txt
├── frontend/                # React 18 / Vite / Tailwind CSS Command Center
├── deploy_gcp.sh            # Google Cloud Run automated deployment script
└── AGENTS.md                # Agent Architecture & Domain Rules
```

---

## Quickstart

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```
Swagger UI available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Security Command Center accessible at `http://localhost:3000`.
