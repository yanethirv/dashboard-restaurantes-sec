#!/usr/bin/env python3
"""
AI CFO Financial Intelligence Calculator & Sensitivity Engine
Author: AI CFO Project
Description: Computes vertical/horizontal variance, operating leverage (DOL),
break-even point, and What-If sensitivity scenarios for P&L analysis.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class IncomeStatement:
    period_name: str
    revenue: float
    cogs: float
    gross_profit: Optional[float] = None
    sga: float = 0.0
    other_opex: float = 0.0
    depreciation_amortization: float = 0.0
    ebit: Optional[float] = None
    interest_expense_net: float = 0.0
    other_non_operating: float = 0.0
    income_tax: float = 0.0
    net_income: Optional[float] = None

    def __post_init__(self):
        if self.gross_profit is None:
            self.gross_profit = self.revenue - self.cogs
        if self.ebit is None:
            self.ebit = self.gross_profit - self.sga - self.other_opex - self.depreciation_amortization
        ebt = self.ebit - self.interest_expense_net + self.other_non_operating
        if self.net_income is None:
            self.net_income = ebt - self.income_tax

    @property
    def ebitda(self) -> float:
        return self.ebit + self.depreciation_amortization

    @property
    def gross_margin_pct(self) -> float:
        return (self.gross_profit / self.revenue) * 100 if self.revenue else 0.0

    @property
    def ebitda_margin_pct(self) -> float:
        return (self.ebitda / self.revenue) * 100 if self.revenue else 0.0

    @property
    def ebit_margin_pct(self) -> float:
        return (self.ebit / self.revenue) * 100 if self.revenue else 0.0

    @property
    def net_margin_pct(self) -> float:
        return (self.net_income / self.revenue) * 100 if self.revenue else 0.0


def calculate_comparative_kpis(prior: IncomeStatement, current: IncomeStatement, 
                               scen_a_rev_pct: float = 3.0, 
                               scen_b_cogs_pct: float = 5.0, 
                               scen_c_sga_pct: float = 7.0) -> Dict[str, Any]:
    rev_growth_pct = ((current.revenue - prior.revenue) / prior.revenue) * 100 if prior.revenue else 0.0
    ebit_growth_pct = ((current.ebit - prior.ebit) / abs(prior.ebit)) * 100 if prior.ebit else 0.0
    dol = (ebit_growth_pct / rev_growth_pct) if rev_growth_pct != 0 else 0.0

    fixed_costs = current.sga + current.other_opex + current.depreciation_amortization
    cm_ratio = (current.gross_profit / current.revenue) if current.revenue else 0.0
    break_even_rev = (fixed_costs / cm_ratio) if cm_ratio > 0 else 0.0
    safety_margin_pct = ((current.revenue - break_even_rev) / current.revenue) * 100 if current.revenue else 0.0

    # Sensitivity scenarios
    # Scenario A: Price / Revenue
    scen_a_rev = current.revenue * (1 + scen_a_rev_pct / 100)
    scen_a_gp = scen_a_rev - current.cogs
    scen_a_ebit = scen_a_gp - current.sga - current.other_opex - current.depreciation_amortization
    scen_a_ebitda = scen_a_ebit + current.depreciation_amortization

    # Scenario B: COGS
    scen_b_cogs = current.cogs * (1 - scen_b_cogs_pct / 100)
    scen_b_gp = current.revenue - scen_b_cogs
    scen_b_ebit = scen_b_gp - current.sga - current.other_opex - current.depreciation_amortization
    scen_b_ebitda = scen_b_ebit + current.depreciation_amortization

    # Scenario C: SG&A
    scen_c_sga = current.sga * (1 - scen_c_sga_pct / 100)
    scen_c_ebit = current.gross_profit - scen_c_sga - current.other_opex - current.depreciation_amortization
    scen_c_ebitda = scen_c_ebit + current.depreciation_amortization

    # Combined: A + B + C
    comb_rev = scen_a_rev
    comb_cogs = scen_b_cogs
    comb_gp = comb_rev - comb_cogs
    comb_sga = scen_c_sga
    comb_ebit = comb_gp - comb_sga - current.other_opex - current.depreciation_amortization
    comb_ebitda = comb_ebit + current.depreciation_amortization

    return {
        "revenue_growth_pct": rev_growth_pct,
        "ebit_growth_pct": ebit_growth_pct,
        "dol": dol,
        "break_even_revenue": break_even_rev,
        "safety_margin_pct": safety_margin_pct,
        "current_ebitda": current.ebitda,
        "scenarios": {
            "scenario_a_ebitda": scen_a_ebitda,
            "scenario_b_ebitda": scen_b_ebitda,
            "scenario_c_ebitda": scen_c_ebitda,
            "scenario_combined_ebitda": comb_ebitda,
        }
    }


if __name__ == "__main__":
    print("AI CFO Calculation Engine Initialized.")
