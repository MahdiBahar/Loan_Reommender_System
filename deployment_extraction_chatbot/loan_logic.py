import pandas as pd
import re
import json
from typing import List, Dict, Any, Optional

# Load parameter weights once
def _load_weights() -> Dict[str, Any]:
    with open('parameters_weights.json', 'r', encoding='utf-8') as f:
        return json.load(f)

_parameters_weights = _load_weights()



def calculate_sort_order(loan: Dict[str, Any]) -> None:
    # Determine bucket
    loanAmountKey = 'out_of_range'
    la = loan.get('loan_amount', 0)
    if la <= 500_000_000:
        loanAmountKey = '1-50'
    elif la <= 1_000_000_000:
        loanAmountKey = '50-100'
    elif la <= 1_500_000_000:
        loanAmountKey = '100-150'
    elif la <= 2_000_000_000:
        loanAmountKey = '150-200'
    elif la <= 2_500_000_000:
        loanAmountKey = '200-250'
    elif la <= 3_000_000_000:
        loanAmountKey = '250-300'

    pw = _parameters_weights
    # Extract individual weights
    ir_key = str(loan.get('interest_rate', ''))
    rd_key = str(loan.get('repayment_duration', ''))
    dd_key = str(loan.get('deposit_duration', ''))
    # CS: first A-E or N
    cs_match = re.search(r'[ABCDE]', loan.get('credit_score', '') or '')
    cs_key = cs_match.group(0) if cs_match else 'N'

    ir_value = pw['IR'][loanAmountKey].get(ir_key, 0)
    rd_value = pw['RD'][loanAmountKey].get(rd_key, 0)
    w_type_coef = pw['w_type'][loanAmountKey].get(loan.get('nickname', ''), 1)
    dd_value = pw['DD'].get(dd_key, 0)
    cs_value = pw['CS'].get(cs_key, 0)

    # Global weights
    w = pw['w']
    coef = (
        ir_value * w['IR_score'] +
        rd_value * w['RD_score'] +
        dd_value * w['DD_score'] +
        cs_value * w['CS_score']
    )
    # Business weight
    w_business = pw['w_business'].get(loan.get('nickname', ''), 1)
    # Calculate final score
    loan['sortOrder'] = coef * w_type_coef * w_business





def update_with_la(records: List[Dict[str, Any]], la: float) -> List[Dict[str, Any]]:
    
    for rec in records:
        # calculate monthly repayment
        r = rec.get('repayment_duration', 0)
        ir_monthly = rec.get('interest_rate', 0) / (12 * 100)
        num = la * ir_monthly * (1 + ir_monthly) ** r
        den = (1 + ir_monthly) ** r - 1
        rec['loan_amount'] = la
        rec['monthly_repayment'] = num / den   # change to Rial
        rec['deposit_amount'] = (la / rec.get('loan_coefficient', 1)) * 100
        calculate_sort_order(rec)

    def valid(rec: Dict[str, Any]) -> bool:
        max_dep = rec.get('maximum_deposit_amount')
        if max_dep and max_dep.lower() != 'nan':
            try:
                deposit_amount = rec.get('deposit_amount')
                if deposit_amount is not None and deposit_amount > int(max_dep):
                    return False
            except ValueError:
                pass
        la_lim = rec.get('loan_amount_limit', float('inf'))
        min_la = rec.get('minimum_loan_amount', 0)
        return min_la <= rec.get('loan_amount') <= la_lim
    valid_records = [r for r in records if valid(r)]
    # return valid_records
    return sorted(valid_records, key=lambda x: x.get('sortOrder', 0), reverse=True)


def update_with_da(records: List[Dict[str, Any]], da: float) -> List[Dict[str, Any]]:
    
    for rec in records:
        valid_da = da
        max_dep_val = rec.get('maximum_deposit_amount')
        if max_dep_val is not None and str(max_dep_val).lower() != 'nan':
            max_dep = int(max_dep_val)
            try:
                if  valid_da > max_dep:
                    valid_da = max_dep
            except:
                print("Except")
        coeff = rec.get('loan_coefficient', 0) / 100
        la = coeff * valid_da
        if la > rec.get('loan_amount_limit', float('inf')):
            la = rec.get('loan_amount_limit', float('inf'))
            valid_da =  (la / coeff) 

        r = rec.get('repayment_duration', 0)
        ir_monthly = rec.get('interest_rate', 0) / (12 * 100)
        num = la * ir_monthly * (1 + ir_monthly) ** r
        den = (1 + ir_monthly) ** r - 1
        rec['loan_amount'] = la
        rec['monthly_repayment'] = num / den  # change to Rial
        rec['deposit_amount'] = valid_da
        calculate_sort_order(rec)

    def valid(rec: Dict[str, Any]) -> bool:
        max_dep = rec.get('maximum_deposit_amount')
        if max_dep and max_dep.lower() != 'nan':
            try:
                deposit_amount = rec.get('deposit_amount')
                if deposit_amount is not None and deposit_amount > int(max_dep):
                    return False
            except ValueError:
                pass
        la_lim = rec.get('loan_amount_limit', float('inf'))
        min_la = rec.get('minimum_loan_amount', 0)
        return min_la <= rec.get('loan_amount') <= la_lim

    valid_records = [r for r in records if valid(r)]
    # Sort descending by sortOrder
    return sorted(valid_records, key=lambda x: x.get('sortOrder', 0), reverse=True)





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

        cond_da = (deposit_amount is None or
                   rec.get('deposit_amount', 0) <= deposit_amount)
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
    return sorted(matches, key=lambda x: x.get('sortOrder', 0), reverse=True)

