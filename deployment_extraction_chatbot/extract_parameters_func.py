# extract_parameters_func.py
from typing import Any, Dict, Tuple
from datetime import datetime, timedelta

from LLM_parser_func import clean_and_parse
from LLM_model import extract_chain
from random_responses import (
    random_response_summary,
    random_invite,
    random_irrelevant,
    random_invalid,
    random_loan_field,
    random_hello,
)
from filter_sort import get_query_params, load_record


# 1) Validation rules, labels & suffixes
VALID_CRITERIA = {
    "deposit_amount": None,
    "deposit_duration": [1, 2, 3, 4, 6, 12],
    "loan_amount": lambda x: x <= 300_000_000,
    "Credit_score": ["A", "B", "C", "D", "E", None],
    "repayment_duration": [12, 24, 36, 48, 60],
    "Interest_rate": [4, 14, 18, 23],
    "Loan_field": None,
    "hello_msg" : None
}

LABELS = {
    "deposit_amount": "مقدار سپرده",
    "loan_amount": "مقدار وام",
    "deposit_duration": "مدت سپرده",
    "repayment_duration": "دوره بازپرداخت",
    "Credit_score": "رتبه اعتباری",
    "Interest_rate": "نرخ سود",
    "Loan_field": "",
    "hello_msg" : ""
}

SUFFIXES = {
    "deposit_amount": " تومان",
    "loan_amount": " تومان",
    "deposit_duration": " ماه",
    "repayment_duration": " ماه",
    "Credit_score": "",
    "Interest_rate": " درصد",
    "Loan_field": "",
    "hello_msg" : ""
}


# # Initialize chain once at import
# extraction_chain = extract_chain()


def format_params_message(params: Dict[str, Any], loan_number) -> str:
    """
    Build a human-readable summary of all non-None parameters.
    """
    msg_calc_loan_number = f"تعداد {loan_number} پیشنهاد وام برای شما پیدا شد."
    lines = []
    for key in (
        "deposit_amount",
        "loan_amount",
        "deposit_duration",
        "repayment_duration",
        "Credit_score",
        "Interest_rate",
    ):
        val = params.get(key)
        if val is not None:
            lines.append(f" {LABELS[key]}: {val}{SUFFIXES[key]}")
        # msg_list_param.append(".join(lines)")
        # msg_list_param.append(msg_calc_loan_number)
        # msg_list_param.append(random_invite())
    
        # if loan_number == 0:
        #     response = "متاسفانه باتوجه به اطلاعاتی که دادی، وامی برای شما پیدا نشد."
        # else:
        #     response = "\n".join(lines) + "\n\n"+ msg_calc_loan_number+"\n\n" + random_invite()




    if not lines:
        lines.append("هنوز مقادیری دریافت نکردم.")
        
    else:
        lines.append(msg_calc_loan_number)
        # lines.append(random_invite())
    return lines



def extract_parameters(
    user_input: str,
    prior_params: Dict[str, Any], new_params
) -> Tuple[Dict[str, Any], str]:
    
    # rb = False
    first_result = {}
    fallback = prior_params.copy()
    msg_list_param = []
    # Try extraction
    try:
        # raw = extraction_chain.predict(user_input=user_input)
        # new_params = clean_and_parse(raw)
        new_params = new_params
    except Exception:
        # If parsing fails, return fallback
        # fallback = {k: None for k in VALID_CRITERIA}
        msg_list_param.append(random_irrelevant())
        
        return fallback, msg_list_param , False, {}

    # Determine template-based response and collect valid updates
    valid_updates: Dict[str, Any] = {}
    invalid_msgs = []
    invalid_keys = []
    inv_keys = []
    # Template logic for raw message
    if new_params.get("Loan_field") and all(
        new_params.get(k) is None for k in new_params if k != "Loan_field"
    ):
        # raw_msg = random_loan_field()
        msg_list_param.append(random_loan_field())
        rb = False

    elif new_params.get("hello_msg") and all(
        new_params.get(k) is None for k in new_params if k != "hello_msg"  
    ):
        # msg_response_hi = "چه کمکی در زمینه وام از من برمیاد که برات انجام بدم؟"
        msg_response_hi = random_hello()
        msg_list_param.append(msg_response_hi)
        rb = False

    elif new_params.get("Loan_field") and new_params.get("hello_msg") and all(
        new_params.get(k) is None for k in new_params if k != "Loan_field" and k != "hello_msg"
    ):
        # msg_response_hi = "چه کمکی در زمینه وام از من برمیاد که برات انجام بدم؟"
        # msg_list_param.append(msg_response_hi)
        msg_list_param.append(random_loan_field())
        rb = False

    elif not any(v is not None for v in new_params.values()):
        # raw_msg = random_irrelevant()
        msg_list_param.append(random_irrelevant())
        rb = False
    else:
        # Validate each extracted value
        for k, v in new_params.items():
            if k == "Loan_field" or v is None:
                continue
            elif k == "hello_msg" or v is None:
                continue
            crit = VALID_CRITERIA[k]
            ok, hint = True, None
            if isinstance(crit, list) and v not in crit:
                ok, hint = False, ", ".join(str(x) for x in crit if x is not None)
            if callable(crit) and not crit(v):
                ok, hint = False, " حداکثر مقدار وام، ۳۰۰ میلیون تومان هست."
            if ok:
                valid_updates[k] = v
            else:
                invalid_keys.append(k)
                inv_keys.append(LABELS[k])
                invalid_msgs.append(
                    random_invalid(LABELS[k]) 
                    # + f"invalid_key : {inv_keys}"
                    + (f"( راهنمایی : مقادیر مجاز  {hint}.)" if hint else "")
                )

          # Merge prior state with valid updates
    updated_params = prior_params.copy()
    for k, v in valid_updates.items():
        updated_params[k] = v

        # Case: only invalid
    if not valid_updates and invalid_keys:
        # msg = "\n".join(invalid_msgs)
        msg_list_param.extend(invalid_msgs)
        rb = False

        # Case: only valid
    elif valid_updates and not invalid_keys:
        first_result, loan_number = param_values_chat(updated_params)
        
        if loan_number == 0:
            msg_list_param.append(random_response_summary())
            msg_list_param.extend (format_params_message(updated_params,loan_number))
            # msg = "ببین، باتوجه به اطلاعاتی که دادی، وامی نتونستم پیدا کنم. میتونی مقادیر را همین جا تغییر بدی یا اگر خواستی به صفحه توصیه گر بری"
            # msg_list_param.append(msg)
            if all(updated_params.get(k) is None for k in updated_params if k == "deposit_amount" or k == "loan_amount"):
                msg = "ببین، باتوجه به اطلاعاتی که دادی، وامی نتونستم پیدا کنم. میتونی مقادیر را مجدد تغییر بدی."
                msg_list_param.append(msg)
                msg_list_param.append("اگر مقدار وام یا میزان سپرده مدنظرت را بهم بگی بهتر میتونم کمکت کنم.")
                rb =False
            else:
                msg = "ببین، باتوجه به اطلاعاتی که دادی، وامی نتونستم پیدا کنم. میتونی مقادیر را همین جا تغییر بدی یا اگر خواستی به صفحه توصیه گر بری."
                msg_list_param.append(msg)
                rb =True
            # msg_list_param.append(random_invite())
            
        else:
            # msg = random_response_summary()
            # msg = format_params_message(updated_params,loan_number)
            msg_list_param.append(random_response_summary())
            msg_list_param.extend (format_params_message(updated_params,loan_number))
            if all(updated_params.get(k) is None for k in updated_params if k == "deposit_amount" or k == "loan_amount"):
                msg_list_param.append("اگر مقدار وام یا میزان سپرده مدنظرت را بهم بگی بهتر میتونم کمکت کنم.")
                rb =False
            else:
                msg_list_param.append(random_invite())
                rb = True


            
    elif valid_updates and invalid_keys:
        # raw_msg_invalid = "\n".join(invalid_msgs)
        # msg_list_param.append(raw_msg_invalid)
        # inv_keys = invalid_keys
        first_result, loan_number = param_values_chat(updated_params)
        if loan_number == 0:
            msg_list_param.extend(invalid_msgs)
            msg_list_param.append(random_response_summary())
            msg_list_param.extend (format_params_message(updated_params,loan_number))
            
            # msg_list_param.append("ببین، باتوجه به اطلاعاتی که دادی، وامی نتونستم پیدا کنم. میتونی مقادیر را همین جا تغییر بدی یا اگر خواستی به صفحه توصیه گر بری")
            
            if all(updated_params.get(k) is None for k in updated_params if k == "deposit_amount" or k == "loan_amount"):
                msg = "ببین، باتوجه به اطلاعاتی که دادی، وامی نتونستم پیدا کنم. میتونی مقادیر را مجدد تغییر بدی."
                msg_list_param.append(msg)
                msg_list_param.append("اگر مقدار وام یا میزان سپرده مدنظرت را بهم بگی بهتر میتونم کمکت کنم.")
                rb =False
            else:
                msg = "ببین، باتوجه به اطلاعاتی که دادی، وامی نتونستم پیدا کنم. میتونی مقادیر را همین جا تغییر بدی یا اگر خواستی به صفحه توصیه گر بری."
                msg_list_param.append(msg)
                rb =True
        else:
            # Generate a summary message for valid updates
            # raw_msg_valid = random_response_summary(format_params_message(updated_params,loan_number))
            
            # msg = f"{raw_msg_invalid}\n\n{raw_msg_valid}"
            msg_list_param.extend(invalid_msgs)
            msg_list_param.append(random_response_summary())
            msg_list_param.extend(format_params_message(updated_params,loan_number))
            if all(updated_params.get(k) is None for k in updated_params if k == "deposit_amount" or k == "loan_amount"):
                msg_list_param.append("اگر مقدار وام یا میزان سپرده مدنظرت را بهم بگی بهتر میتونم کمکت کنم.")
                rb =False
            else:
                msg_list_param.append(random_invite())
                rb = True
    else:
        # No updates: use the template-based reply
        # msg = raw_msg
        # msg_list_param.append(msg)
        rb = False
    return updated_params, msg_list_param, rb , first_result, inv_keys


def param_values_chat(updated_params: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    
    # Safely extract values, defaulting to 0 or None

    if updated_params.get("deposit_amount") is not None:

        deposit_amount     = (updated_params.get("deposit_amount")) * 10

    else: 
        deposit_amount = None


    if updated_params.get("loan_amount") is not None:
        loan_amount        = (updated_params.get("loan_amount")) * 10
    else:
        loan_amount = None

    repayment_duration =  updated_params.get("repayment_duration") 
    deposit_duration   =  updated_params.get("deposit_duration")  
    interest_rate      = updated_params.get("Interest_rate") 
    credit_score       =  updated_params.get("Credit_score") 

    # Load records and perform query
    _records = load_record()
    results, loan_num = get_query_params(
        _records,
        deposit_amount,
        repayment_duration,
        deposit_duration,
        interest_rate,
        credit_score,
        loan_amount,
    )

    # If no matching loans, return empty/default
    if not results:
        return {}, 0

    # Return first matching loan and the total number
    return results[0], loan_num