# ForensiKit-IN: Deterministic Forensic Accounting Engine for Indian Equities

*Lead Architect & Author:* Mohd Affan  
*Framework Version:* 1.0.0 (Production)  
*Target Universe:* NSE / BSE Equities (Ind AS Financial Framework)

---

## 📌 Overview
ForensiKit-IN is a deterministic quantitative accounting anomaly detector engineered specifically for the Indian statutory accounting environment (Ind AS). The engine processes real-time SEC/SEBI balance sheets, income statements, and cash flows to identify working capital decay, accrual inflation, off-balance-sheet lease obligations under Ind AS 116, and cash conversion cycle divergence.

---

## 🔍 Core Forensic Modules

| Module | Accounting Framework | Anomaly Threshold Logic |
| :--- | :--- | :--- |
| *Phantom Inventory Spread* | Accrual Quality | Divergence between reported inventory growth rate vs. COGS expansion |
| *Days Inventory Outstanding (DIO)* | Working Capital Deceleration | Identifies artificial revenue preservation via slow-moving channel inventory |
| *Cash Conversion Cycle (CCC)* | Liquidity Compression | Compares statutory DIO, DSO, and DPO trajectories across 3 fiscal periods |
| *Ind AS 116 Capitalization* | Lease Liability Stress | Recalculates debt ratios by capitalizing operating lease obligations |
| *Sloan Accrual Anomaly* | Earnings Persistence | Quantifies the gap between accounting Net Income and Operating Cash Flow |

---

## ⚙️ Tech Stack & Architecture
- *Language & Runtime:* Python 3.10+
- *Data Pipeline:* yfinance real-time NSE/BSE ingestor with automated exchange routing (.NS / .BO)
- *Core Processing:* Pandas, NumPy vectorized matrix normalization
- *Interactive UI:* Streamlit with custom CSS financial styling
- *Visualization:* Plotly Institutional Financial Charts

---

## 🚀 Quickstart & Installation

```bash
# Clone the repository
git clone [https://github.com/affanequity1-collab/forensikit-in.git](https://github.com/affanequity1-collab/forensikit-in.git)
cd forensikit-in

# Activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the audit engine
streamlit run app.py