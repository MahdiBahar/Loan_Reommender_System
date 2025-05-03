from loan_logic import update_with_da, update_with_la, query_complex


import json
from typing import List, Dict, Any, Optional

# Load parameter weights once
def load_record() -> Dict[str, Any]:
    with open('MEC-LoanRecomn_Scenarios-V15.json', 'r', encoding='utf-8') as f:
        return json.load(f)

_records = load_record()



def get_query_params( _records, 
    deposit__amount: Optional[float] = None,
    repayment__duration: Optional[int] = None,
    deposit__duration: Optional[int] = None,
    interest__rate: Optional[float] = None,
    credit__score: Optional[str] = None,
    loan__amount: Optional[float] = None
):

    report = query_complex(
        _records,
        deposit_amount=deposit__amount,
        repayment_duration=repayment__duration,
        deposit_duration=deposit__duration,
        interest_rate=interest__rate,
        credit_score=credit__score
    )

    if loan__amount:
        scenarios = update_with_la(report, loan__amount)
    elif deposit__amount and loan__amount is None:
        scenarios = update_with_da(report, deposit__amount)
    else:
        scenarios = report

    
    msg= f"تعداد {len(scenarios)} پیشنهاد برای شما پیدا شد.\n\n"

    return scenarios, msg

