import pandas as pd
from forensikit.core.engine import BaseForensicRatio

class SloanAccrualRatio(BaseForensicRatio):
    name = "Sloan Accrual Ratio"
    cluster = "Earnings Quality"
    description = "(Net Income - CFO) / Total Assets. Values > 0.10 indicate non-cash accrual inflation."

    def compute(self, df: pd.DataFrame) -> pd.Series:
        return (df['net_income'] - df['operating_cash_flow']) / df['total_assets']

    def evaluate_flag(self, s: pd.Series) -> pd.Series:
        return s > 0.10

class PhantomInventorySpread(BaseForensicRatio):
    name = "Phantom Inventory Spread"
    cluster = "Working Capital"
    description = "YoY Inventory Growth minus YoY Revenue Growth. > 15% flags unsellable stock."

    def compute(self, df: pd.DataFrame) -> pd.Series:
        return df['inventory'].pct_change() - df['revenue'].pct_change()

    def evaluate_flag(self, s: pd.Series) -> pd.Series:
        return s > 0.15

class DaysInventoryOutstanding(BaseForensicRatio):
    name: str = "Days Inventory Outstanding"
    cluster = "Working Capital"
    description = "(Inventory / COGS) * 365. Retail baseline is 70-100 days; > 125 days triggers alert."

    def compute(self, df: pd.DataFrame) -> pd.Series:
        return (df['inventory'] / df['cogs']) * 365

    def evaluate_flag(self, s: pd.Series) -> pd.Series:
        return s > 125.0

class CashConversionCycle(BaseForensicRatio):
    name = "Cash Conversion Cycle"
    cluster = "Working Capital"
    description = "DIO + DSO - DPO. Measures the net cycle to turn inventory into cash."

    def compute(self, df: pd.DataFrame) -> pd.Series:
        dio = (df['inventory'] / df['cogs']) * 365
        dso = (df['receivables'] / df['revenue']) * 365
        dpo = (df['payables'] / df['cogs']) * 365
        return dio + dso - dpo

    def evaluate_flag(self, s: pd.Series) -> pd.Series:
        return s > 80.0

class IndAS116LeaseLeverage(BaseForensicRatio):
    name = "Ind AS 116 Adjusted Leverage"
    cluster = "Solvency & Leases"
    description = "(Total Debt + Lease Liabilities) / EBITDA. > 4.0x flags store lease burden."

    def compute(self, df: pd.DataFrame) -> pd.Series:
        total_obligations = df['total_debt'] + df['lease_liabilities']
        ebitda_series = df['ebitda'] if 'ebitda' in df.columns else (df['revenue'] - df['cogs'])
        return total_obligations / ebitda_series.replace(0, 1.0)

    def evaluate_flag(self, s: pd.Series) -> pd.Series:
        return s > 4.0

class ContingentLiabilityDrain(BaseForensicRatio):
    name = "Contingent Liability to Equity"
    cluster = "Off Balance Sheet"
    description = "Contingent Liabilities / Net Worth. Exceeding 20% flags severe contingent disputes."

    def compute(self, df: pd.DataFrame) -> pd.Series:
        return df['contingent_liabilities'] / df['net_worth']

    def evaluate_flag(self, s: pd.Series) -> pd.Series:
        return s > 0.20