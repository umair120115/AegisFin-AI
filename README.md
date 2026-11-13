# AegisFin-AI: Request-Level FinTech AI Security & AML Middleware

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python)](https://www.python.org/)

An enterprise-grade, request-level financial fraud prevention and Anti-Money Laundering (AML) middleware shield tailored for high-speed digital payment rails (UPI, IMPS, RTGS, mobile wallets).

---

## 🎯 Alignment with Problem Statement & Core Objectives

Our solution is specifically architected to fulfill the challenge goals, utilizing a hybrid AI approach to intercept, analyze, and explain financial risks in real-time.

### Core Objectives Met
1. **Fraud Detection:** Implemented supervised machine learning using a highly tuned **XGBoost Classifier** (`backend/artifacts/xgb_fraud.joblib`). The engine intercepts transactions at the API layer to block known fraud topologies before ledger execution.
2. **Anomaly Detection:** Deployed an unsupervised **Isolation Forest Model** (`backend/artifacts/iso_anomaly.joblib`) to detect unusual transaction frequencies, abnormal amounts, and zero-day account takeovers without relying on historical fraud labels.
3. **Anti-Money Laundering (AML):** Engineered a **Temporal MultiDiGraph algorithm** within the 4-Pillar Risk Equation to automatically flag suspicious transaction splitting (structuring, e.g., ₹45k-₹49.99k) and circular money movement ($A \to B \to C \to A$).
4. **Risk Assessment:** Developed a proprietary **4-Pillar Bi-Directional Risk Equation** (`backend/app/engine/production_engine.py`) that aggregates receiver mule profiling, ML anomaly scores, graph-based AML signals, and contextual modifiers into a unified, actionable risk score (0-100).
5. **Real-Time Monitoring:** Built on a highly concurrent **FastAPI** backend (`backend/app/main.py`), the middleware achieves **sub-25ms pre-settlement interception**, enabling real-time blocking and instant alerting via WebSockets.
6. **Explainable AI (XAI):** Integrated **TreeSHAP** to provide instant, human-readable local additive feature attributions. If a transaction is flagged, the system explicitly details *why* (e.g., "Device location mismatch + High velocity transfer").
7. **Security Dashboard:** Developed a modern, intuitive command center using **React 18 and Tailwind CSS v4** (`frontend/`). It provides investigators with interactive transaction graphs, live fraud alerts, risk timelines, and automated Suspicious Activity Reports (SAR).

### Deliverables & Implementation
* **Working Prototype:** A full-stack (React/FastAPI) system deployable via Docker/GCP (`deploy_gcp.sh`).
* **AI/ML Scoring & Alerts:** Automated, algorithmic risk assignment and alert generation handled by the `request_engine.py`.
* **Automated SARs:** Features a Gemini-powered one-click FIU-IND / FinCEN Suspicious Activity Report drafting module (`backend/app/engine/sar_generator.py`).
* **Ethical & Synthetic Data Integration:** Strictly utilizes an anonymized, synthetic dataset generated via PaySim (`backend/scripts/prepare_demo_dataset.py`), completely avoiding unauthorized real banking data while proving the system's efficacy at scale.

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
   - One-click FIU-IND / FinCEN Suspicious Activity Report drafting powered by LLMs.

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
