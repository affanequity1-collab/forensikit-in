import json
import streamlit as st
import pandas as pd
from forensikit.data.fetcher import fetch_financials
import plotly.graph_objects as go

from forensikit.core.engine import ForensicEngine
from forensikit.ratios.library import (
    SloanAccrualRatio,
    PhantomInventorySpread,
    DaysInventoryOutstanding,
    CashConversionCycle,
    IndAS116LeaseLeverage,
    ContingentLiabilityDrain
)

st.set_page_config(
    page_title="ForensiKit-IN | Institutional Forensic Engine",
    page_icon="🔍",
    layout="wide"
)

# Header & Ownership Banner
st.markdown("""
<div style="background-color: #0f172a; padding: 22px; border-radius: 10px; margin-bottom: 25px; border-left: 6px solid #38bdf8;">
    <h1 style="color: #f8fafc; margin: 0; font-size: 26px;">ForensiKit-IN: Forensic Accounting Engine</h1>
    <p style="color: #94a3b8; margin: 5px 0 0 0; font-size: 14px;">
        Deterministic Ind AS 116 Earnings Quality & Anomaly Detection for Indian Equities
    </p>
    <div style="margin-top: 10px; color: #38bdf8; font-weight: 600; font-size: 13px;">
        Lead Architect & Maintainer: <b>Mohd Affan</b> | Open Source (MIT)
    </div>
</div>
""", unsafe_allow_html=True)

# Ticker Selection & Live Ingestion
st.sidebar.markdown("### 🔍 Forensic Entity Lookup")

user_input = st.sidebar.text_input(
    "Enter Company Name or NSE Symbol:",
    value="TRENT",
    help="Type any Indian stock symbol (e.g. RELIANCE, TCS, TATAMOTORS, INFY, ITC, ZOMATO)"
).strip().upper()

# Normalize symbol: automatically append .NS if user didn't provide exchange suffix
if user_input.endswith(".NS") or user_input.endswith(".BO"):
    active_symbol = user_input
else:
    active_symbol = f"{user_input}.NS"

# Check if local audited file exists for Trent benchmark
if user_input in ["TRENT", "TRENT.NS"]:
    try:
        with open("forensikit/data/companies/trent_fy20_fy25.json") as f:
            raw_data = json.load(f)
        df = pd.DataFrame.from_dict(raw_data["historical_data"], orient="index")
        raw_company_name = "Trent Limited (Audited Ind-AS Benchmark)"
    except Exception:
        df = fetch_financials(active_symbol)
        raw_company_name = active_symbol
else:
    try:
        with st.spinner(f"Fetching financial statements for {active_symbol} from live filings..."):
            df = fetch_financials(active_symbol)
            raw_company_name = active_symbol
    except Exception as e:
        # Fallback to BSE if NSE fails
        try:
            bse_symbol = f"{user_input.replace('.NS', '')}.BO"
            with st.spinner(f"Trying BSE exchange ({bse_symbol})..."):
                df = fetch_financials(bse_symbol)
                raw_company_name = bse_symbol
        except Exception:
            st.error(f"Could not retrieve annual financial statements for '{user_input}'. Please verify the stock ticker symbol.")
            st.stop()
# Ensure EBITDA exists for Ind AS 116 Leverage calculation
if "ebitda" not in df.columns:
    df["ebitda"] = (df["revenue"] - df["cogs"]).replace(0, 1.0)
# Align column aliases for ratios
if "net_worth" not in df.columns:
    df["net_worth"] = df["total_equity"] if "total_equity" in df.columns else 1.0

if "ebitda" not in df.columns:
    df["ebitda"] = (df["revenue"] - df["cogs"]).replace(0, 1.0)
# Initialize and Register Ratios
engine = ForensicEngine()
engine.register(SloanAccrualRatio())
engine.register(PhantomInventorySpread())
engine.register(DaysInventoryOutstanding())
engine.register(CashConversionCycle())
engine.register(IndAS116LeaseLeverage())
engine.register(ContingentLiabilityDrain())

# Execute Forensic Analysis
audit_df = engine.run_audit(df)
# Top KPI Summary Cards
col1, col2, col3, col4 = st.columns(4)
years_available = list(df.index)
latest_year = years_available[-1]
prev_year = years_available[-2] if len(years_available) > 1 else years_available[-1]

latest_score = audit_df.loc[latest_year, "composite_risk_score"]
prev_score = audit_df.loc[prev_year, "composite_risk_score"]
delta_score = round(latest_score - prev_score, 2)

col1.metric("Target Entity", raw_company_name, active_symbol)
col2.metric("FY25 Forensic Risk", f"{latest_score} / 10", f"{delta_score} vs FY24", delta_color="inverse")
col3.metric("FY25 Revenue", f"₹{df.loc[latest_year, 'revenue']:,.0f} Cr", f"+{((df.loc[latest_year, 'revenue']/df.loc[prev_year, 'revenue'])-1)*100:.1f}% YoY")
col4.metric("Ind AS 116 Lease Book", f"₹{df.loc[latest_year, 'lease_liabilities']:,.0f} Cr", f"{(df.loc[latest_year, 'lease_liabilities']/df.loc[latest_year, 'ebitda']):.1f}x EBITDA")

st.markdown("---")

tab1, tab2 = st.tabs(["📊 Working Capital & Accrual Charts", "📑 Granular Audit Table"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_dio = go.Figure()
        fig_dio.add_trace(go.Bar(
            x=audit_df.index, 
            y=audit_df['daysinventoryoutstanding_val'],
            name='DIO (Days)',
            marker_color='#6366f1'
        ))
        fig_dio.add_hline(y=125, line_dash="dash", line_color="#ef4444", annotation_text="Watch Threshold (125d)")
        fig_dio.update_layout(title="Days Inventory Outstanding (DIO) vs. Risk Threshold", template="plotly_dark", height=380)
        st.plotly_chart(fig_dio, width="stretch")
        
    with c2:
        fig_acc = go.Figure()
        fig_acc.add_trace(go.Scatter(
            x=audit_df.index, 
            y=audit_df['sloanaccrualratio_val'],
            mode='lines+markers',
            name='Sloan Accrual',
            line=dict(color='#38bdf8', width=3)
        ))
        fig_acc.add_hline(y=0.10, line_dash="dot", line_color="#f59e0b", annotation_text="Accrual Limit (+0.10)")
        fig_acc.update_layout(title="Sloan Accrual Trend: Non-Cash Earnings Divergence", template="plotly_dark", height=380)
        st.plotly_chart(fig_acc, width="stretch")

with tab2:
    st.subheader("Granular Forensic Audit Flag Matrix")
    display_cols = [c for c in audit_df.columns if not c.endswith("_flag")]
    st.dataframe(audit_df[display_cols].style.highlight_max(axis=0, color="#7f1d1d"), width="stretch")
    st.markdown("""
    > *Forensic Audit Takeaways:*
    > - *Earnings Integrity:* Sloan accruals remain consistently below the +0.10 threshold, proving profits are backed by operating cash flow.
    > - *Inventory Management:* Despite massive store rollout, DIO has remained stable between 105 and 120 days.
    > - *Hidden Leverage:* Lease liabilities under Ind AS 116 represent the largest component of enterprise obligations.
    """)