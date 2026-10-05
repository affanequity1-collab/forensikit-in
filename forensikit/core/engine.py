from abc import ABC, abstractmethod
import pandas as pd
from typing import List

class BaseForensicRatio(ABC):
    name: str = "Unnamed Ratio"
    cluster: str = "General"
    description: str = ""

    @abstractmethod
    def compute(self, df: pd.DataFrame) -> pd.Series:
        pass

    @abstractmethod
    def evaluate_flag(self, series: pd.Series) -> pd.Series:
        pass

class ForensicEngine:
    def __init__(self):
        self.registered_ratios = []

    def register(self, ratio_plugin):
        self.registered_ratios.append(ratio_plugin)
        return self

    def run_audit(self, df: pd.DataFrame) -> pd.DataFrame:
        results = pd.DataFrame(index=df.index)
        
        for ratio in self.registered_ratios:
            col_id = ratio.name.lower().replace(" ", "").replace("-", "")
            computed = ratio.compute(df)
            flagged = ratio.evaluate_flag(computed)
            
            results[f"{col_id}_val"] = computed.round(4)
            results[f"{col_id}_flag"] = flagged
            
        flag_cols = [c for c in results.columns if c.endswith("_flag")]
        if flag_cols:
            results["composite_risk_score"] = ((results[flag_cols].sum(axis=1) / len(flag_cols)) * 10).round(2)
        else:
            results["composite_risk_score"] = 0.0
            
        return results