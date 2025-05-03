from loan_logic import calculate_sort_order, update_with_da, update_with_la, query_complex


import json
from typing import List, Dict, Any, Optional

# Load parameter weights once
def _load_record() -> Dict[str, Any]:
    with open('MEC-LoanRecomn_Scenarios-V15.json', 'r', encoding='utf-8') as f:
        return json.load(f)

_records = _load_record()




def filter_sort(_records, loan_amount=None, deposit_amount=None):

    if loan_amount is not None:
        updated_records = update_with_la(_records, loan_amount)

    elif deposit_amount is not None:
        updated_records = update_with_da(_records, deposit_amount)
    else:
        updated_records = _records
    # Filter out records with None values

    return updated_records