# logic.py
"""
Python port of your loan suggestion logic from logic.js.
Functions:
  - update_with_la(records, la)
  - update_with_da(records, da)
  - query_complex(scenarios, deposit_amount=None, repayment_duration=None,
                  deposit_duration=None, interest_rate=None, credit_score=None)
  - calculate_sort_order(loan)

Expect each record to be a dict with fields matching your JS schema.
Requires a JSON file 'parameters_weights.json' in the same directory.
"""
import json
from typing import List, Dict, Any, Optional

# Load parameter weights once
def _load_weights() -> Dict[str, Any]:
    with open('parameters_weights.json', 'r', encoding='utf-8') as f:
        return json.load(f)

_parameters_weights = _load_weights()


def calculate_sort_order(loan: Dict[str, Any]) -> None:
    """
    Mutates loan by adding a 'sortOrder' key based on weighted criteria.
    """
    # Determine loanAmountKey
    la = loan.get('loan_amount', 0)
    if la <= 500_000_000:
        bracket = '1-50'
    elif la <= 1_000_000_000:
        bracket = '50-100'
    elif la <= 1_500_000_000:
        bracket = '100-150'
    elif la <= 2_000_000_000:
        bracket = '150-200'
    elif la <= 2_500_000_000:
        bracket = '200-250'
    elif la <= 3_000_000_000:
        bracket = '250-300'
    else:
        bracket = 'out_of_range'

    pw = _parameters_weights
    # Extract individual scores
    ir_str = str(loan.get('interest_rate'))
    rd_str = str(loan.get('repayment_duration'))
    dd_str = str(loan.get('deposit_duration'))
    cs_val = (loan.get('credit_score') or '')
    # pick first letter A-E or 'N'
    cs_letter = next((c for c in cs_val if c in 'ABCDE'), 'N')

    ir_value = pw['IR'][bracket].get(ir_str, 0)
    rd_value = pw['RD'][bracket].get(rd_str, 0)
    w_type_coef = pw['w_type'][bracket].get(loan.get('nickname', ''), 1)
    dd_value = pw['DD'].get(dd_str, 0)
    cs_value = pw['CS'].get(cs_letter, 0)

    # weight scores
    w = pw['w']
    coef = (
        ir_value * w['IR_score'] +
        rd_value * w['RD_score'] +
        dd_value * w['DD_score'] +
        cs_value * w['CS_score']
    )
    w_business = pw.get('w_business', {}).get(loan.get('nickname', ''), 1)
    sort_order = coef * w_type_coef * w_business
    loan['sortOrder'] = sort_order


def update_with_la(records: List[Dict[str, Any]], la: float) -> List[Dict[str, Any]]:
    """
    Given desired loan amount 'la', update each record's
    loan_amount, monthly_repayment, deposit_amount,
    then filter and return valid records.
    """
    for rec in records:
        # calculate monthly repayment
        r = rec.get('repayment_duration', 0)
        ir_monthly = rec.get('interest_rate', 0) / (12 * 100)
        num = la * ir_monthly * (1 + ir_monthly) ** r
        den = (1 + ir_monthly) ** r - 1
        rec['loan_amount'] = la
        rec['monthly_repayment'] = num / den / 10  # change to Toman
        rec['deposit_amount'] = (la / rec.get('loan_coefficient', 1)) * 100
        calculate_sort_order(rec)

    def valid(rec: Dict[str, Any]) -> bool:
        max_dep = rec.get('maximum_deposit_amount')
        if max_dep and max_dep.lower() != 'nan':
            try:
                if rec['deposit_amount'] > int(max_dep):
                    return False
            except ValueError:
                pass
        la_lim = rec.get('loan_amount_limit', float('inf'))
        min_la = rec.get('minimum_loan_amount', 0)
        return min_la <= rec['loan_amount'] <= la_lim

    return [r for r in records if valid(r)]


def update_with_da(records: List[Dict[str, Any]], da: float) -> List[Dict[str, Any]]:
    """
    Given deposit amount 'da', update each record's
    loan_amount, monthly_repayment, deposit_amount,
    then filter and return valid records.
    """
    for rec in records:
        coeff = rec.get('loan_coefficient', 0) / 100
        la = coeff * da
        r = rec.get('repayment_duration', 0)
        ir_monthly = rec.get('interest_rate', 0) / (12 * 100)
        num = la * ir_monthly * (1 + ir_monthly) ** r
        den = (1 + ir_monthly) ** r - 1
        rec['loan_amount'] = la
        rec['monthly_repayment'] = num / den / 10
        rec['deposit_amount'] = da
        calculate_sort_order(rec)

    def valid(rec: Dict[str, Any]) -> bool:
        max_dep = rec.get('maximum_deposit_amount')
        if max_dep and max_dep.lower() != 'nan':
            try:
                if rec['deposit_amount'] > int(max_dep):
                    return False
            except ValueError:
                pass
        la_lim = rec.get('loan_amount_limit', float('inf'))
        min_la = rec.get('minimum_loan_amount', 0)
        return min_la <= rec['loan_amount'] <= la_lim

    return [r for r in records if valid(r)]


def query_complex(
    scenarios: List[Dict[str, Any]],
    deposit_amount: Optional[float] = None,
    repayment_duration: Optional[int] = None,
    deposit_duration: Optional[int] = None,
    interest_rate: Optional[float] = None,
    credit_score: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter scenarios based on provided parameters.
    """
    matches = []
    for rec in scenarios:
        # deposit range: up to 1.6x
        cond_da = (deposit_amount is None or
                   rec.get('deposit_amount', 0) <= deposit_amount * 10_000_000 * 1.6)
        cond_rd = (repayment_duration is None or
                   rec.get('repayment_duration') == repayment_duration)
        cond_dep = (deposit_duration is None or
                    rec.get('deposit_duration') == deposit_duration)
        cond_ir = (interest_rate is None or
                   rec.get('interest_rate') == interest_rate)
        cs_field = rec.get('credit_score', '')
        cond_cs = (credit_score is None or
                   (credit_score in cs_field) or
                   (credit_score == 'N' and 'فاقد رتبه' in cs_field))
        if cond_da and cond_rd and cond_dep and cond_ir and cond_cs:
            matches.append(rec)
    return matches


