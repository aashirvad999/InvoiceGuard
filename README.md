# 🛡️ InvoiceGuard

> **AI-Powered & Deterministic Invoice Anomaly Detection, Document Forensics, and Financial Risk Engine**

InvoiceGuard is an enterprise-grade financial security application designed to detect invoice fraud, mathematical discrepancies, GSTIN non-compliance, vendor spoofing, and document tampering before payments are processed. By combining **deterministic mathematical validation** with **Google Gemini AI reasoning** and **PDF font forensics**, InvoiceGuard provides transparent, explainable risk scoring without black-box opacity.

---

## 🌟 Key Features

- **🔍 Deterministic Financial Validation**:
  - Validates line items, taxable subtotals, CGST/SGST/IGST tax rates, and grand total calculations.
  - Detects rounding discrepancies, missing taxes, and mathematical miscalculations.

- **🏛️ Statutory GSTIN Compliance**:
  - Regex-based statutory 15-character Indian GSTIN structure verification (State code, PAN, Entity number, Z flag, Checksum).

- **📄 Document Forensics & Tampering Detection**:
  - Scans PDF binary streams for embedded font structure inconsistencies (e.g., mismatched font encodings indicating text editing/manipulation).
  - SHA-256 cryptographic fingerprinting for duplicate invoice detection.
  - PDF metadata inspection to spot unauthorized modification tools.

- **🤖 Google Gemini AI Explainer & Assistant**:
  - Generates executive natural language risk summaries for non-technical finance teams.
  - Interactive AI chatbot assistant for real-time invoice query resolution.
  - Automated vendor inquiry email generator for dispute escalation.

- **⚖️ Transparent Weighted Risk Engine**:
  - Deterministic risk score (0–100) categorized into **Low Risk** (0–30), **Review Required** (31–70), and **High Risk** (71–100).
  - Fully explainable score breakdown with signal impacts, evidence, and actionable recommended protocols.

- **🛡️ Multi-Tenant Data Isolation & Admin Sentinel**:
  - Complete data boundary isolation between user accounts and vendor ledgers.
  - Admin Sentinel view with global vendor blacklist controls and system-wide audit logging.

- **🎨 Modern Visual UI**:
  - Responsive single-page interface with real-time drag-and-drop file analysis, interactive risk gauges, dark/light theme options, and vendor management.

---

## 📁 Repository Structure

```
InvoiceGuard/
├── api/
│   ├── main.py                   # FastAPI server entry point & REST endpoints
│   └── engine/
│       ├── deterministic.py      # Math checks, GSTIN validation, vendor anomaly engine
│       ├── risk_engine.py        # Centralized weighted risk scoring algorithm (0-100)
│       ├── document_forensics.py # PDF font structure inspection & hash computation
│       ├── ai_explainer.py       # Google Gemini AI integration (summaries, chat, email)
│       ├── firestore_db.py       # In-memory / Firestore multi-tenant store & audit logs
│       ├── pdf_generator.py      # Dynamic PDF generation engine for test invoices
│       └── seed_data.py          # Pre-seeded test dataset & vendor ledgers
├── static/
│   ├── index.html                # Main InvoiceGuard dashboard interface
│   ├── vendors.html              # Vendor ledger & verification panel
│   ├── feedback.html             # Audit log & complaint resolution interface
│   └── app.js                    # Frontend app logic & REST API bindings
├── demo_invoices/                # Generated sample invoices for testing scenarios
├── generate_demo_invoices.py     # Script to generate sample test invoices
├── verify_architecture.py        # Verification script for system architecture
├── verify_demo_suite.py         # End-to-end demo suite verifier
├── test_pipeline.py              # Full pipeline test runner
├── requirements.txt              # Python dependencies
├── vercel.json                   # Deployment config for Vercel Serverless
├── .env.example                  # Environment variables template
└── README.md                     # Project documentation
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python **3.10+**
- Node.js (Optional, for Vercel CLI deployments)
- A **Google Gemini API Key** (for AI explanations and chat assistant)

### 2. Installation

Clone the repository and install the dependencies:

```bash
# Navigate to project directory
cd InvoiceGuard

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the root directory by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API Key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Run the Application

Start the FastAPI backend server using Uvicorn:

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
- **Web Interface**: Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **Interactive API Docs (Swagger UI)**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## 🧪 Testing & Verification

InvoiceGuard includes a comprehensive suite of verification tools and sample invoice generators:

### Generate Test Invoices
Generate sample invoices representing various risk scenarios (Valid, Math Mismatch, Font Tampering, Invalid GSTIN, Vendor Spoofing):

```bash
python generate_demo_invoices.py
```

### Run Automated Tests & Verifications

```bash
# Verify architectural integrity and engine components
python verify_architecture.py

# Verify the complete demo suite against sample invoices
python verify_demo_suite.py

# Run end-to-end pipeline test
python test_pipeline.py
```

---

## 🛠️ API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/upload` | Upload & process PDF invoice for full fraud analysis |
| `GET` | `/api/invoices` | List invoices for active tenant user |
| `GET` | `/api/invoices/{id}` | Fetch invoice details by ID |
| `POST` | `/api/ai/chat` | Chat with Gemini AI assistant regarding an invoice |
| `POST` | `/api/ai/draft-email` | Draft a formal vendor inquiry email |
| `GET` | `/api/vendors` | List vendor ledger and verification statuses |
| `GET` | `/api/admin/overview` | Admin Sentinel dashboard overview & system audit logs |
| `POST` | `/api/admin/blacklist` | Add or remove vendor from global blacklist |
| `GET` | `/api/health/gemini` | Health check endpoint for Gemini API integration |

---

## ☁️ Deployment

InvoiceGuard is pre-configured for seamless deployment on **Vercel**:

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project root directory.
3. Configure the `GEMINI_API_KEY` environment variable in your Vercel Dashboard under **Project Settings > Environment Variables**.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
