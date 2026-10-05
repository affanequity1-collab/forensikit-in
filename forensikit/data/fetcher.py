import yfinance as yf
import pandas as pd
import numpy as np

def fetch_financials(ticker_symbol: str) -> pd.DataFrame:
    ticker = yf.Ticker(ticker_symbol)
    
    # Try fetching annual statements
    bs = ticker.balance_sheet
    inc = ticker.financials
    cf = ticker.cashflow
    
    # If standard annuals are empty, check for alternate format
    if bs is None or bs.empty or inc is None or inc.empty:
        raise ValueError(f"No annual statement data found for '{ticker_symbol}'.")
    
    # Sort columns by date ascending
    cols = sorted(list(set(bs.columns.tolist() + inc.columns.tolist())))
    
    records = {}
    for col in cols:
        year_str = f"FY{str(col.year)[-2:]}"
        
        def get_val(df_source, aliases):
            if df_source is None or df_source.empty:
                return 0.0
            for name in aliases:
                if name in df_source.index and col in df_source.columns:
                    val = df_source.loc[name, col]
                    if pd.notna(val) and val is not None:
                        try:
                            return float(val)
                        except (ValueError, TypeError):
                            pass
            return 0.0

        rev = get_val(inc, ["Total Revenue", "Operating Revenue", "Revenue"])
        cogs = get_val(inc, ["Cost Of Revenue", "Reconciled Cost Of Revenue"])
        net_inc = get_val(inc, ["Net Income", "Net Income Common Stockholders"])
        ebitda = get_val(inc, ["EBITDA", "Normalized EBITDA", "Operating Income"])
        
        inv = get_val(bs, ["Inventory", "Total Inventories"])
        rec = get_val(bs, ["Receivables", "Accounts Receivable", "Net Receivables"])
        pay = get_val(bs, ["Payables", "Accounts Payable"])
        tot_assets = get_val(bs, ["Total Assets"])
        equity = get_val(bs, ["Stockholders Equity", "Total Equity Gross Minority Interest", "Common Stock Equity"])
        tot_debt = get_val(bs, ["Total Debt", "Long Term Debt And Capital Lease Obligation"])
        
        lease_liab = get_val(bs, ["Capital Lease Obligations", "Long Term Capital Lease Obligation", "Operating Lease Liabilities"])
        ocf = get_val(cf, ["Operating Cash Flow", "Cash Flowsfromusedin Operating Activities Direct"])

        records[year_str] = {
            "revenue": rev,
            "cogs": cogs,
            "ebitda": ebitda if ebitda != 0 else (rev - cogs),
            "net_income": net_inc,
            "inventory": inv,
            "receivables": rec,
            "payables": pay,
            "total_assets": tot_assets if tot_assets != 0 else 1.0,
            "total_equity": equity if equity != 0 else 1.0,
            "net_worth": equity if equity != 0 else 1.0,
            "total_debt": tot_debt,
            "operating_cash_flow": ocf,
            "lease_liabilities": lease_liab,
            "contingent_liabilities": 0.0
        }

    df = pd.DataFrame.from_dict(records, orient="index")
    df.index.name = "fiscal_year"
    return df