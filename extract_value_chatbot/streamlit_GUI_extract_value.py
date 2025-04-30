from LLM_parser_func import clean_and_parse
from LLM_model import extract_chain
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from random_responses import (
    random_response_summary,
    random_invite,
    random_irrelevant,
    random_invalid,
    random_loan_field,
)

# Validation criteria for each parameter
VALID_CRITERIA = {
    "deposit_amount": None,
    "deposit_duration": [1, 2, 3, 4, 6, 12],
    "loan_amount": lambda x: x <= 300_000_000,
    "Credit_score": ["A", "B", "C", "D", "E", None],
    "repayment_duration": [12, 24, 36, 48, 60],
    "Interest_rate": [4, 14, 18, 23],
    "Loan_field": None,
}

# Labels and suffixes for messages
LABELS = {
    "deposit_amount": "مقدار سپرده",
    "loan_amount": "مقدار وام",
    "deposit_duration": "مدت سپرده",
    "repayment_duration": "دوره بازپرداخت",
    "Credit_score": "رتبه اعتباری",
    "Interest_rate": "نرخ سود",
    "Loan_field": "حوزه وام",
}
SUFFIXES = {
    "deposit_amount": "",
    "loan_amount": "",
    "deposit_duration": " ماه",
    "repayment_duration": " ماه",
    "Credit_score": "",
    "Interest_rate": " درصد",
    "Loan_field": "",
}

# Helper: format parameters message

def format_params_message(params: dict) -> str:
    lines = []
    for key in [
        "deposit_amount", "loan_amount", "deposit_duration",
        "repayment_duration", "Credit_score", "Interest_rate"
    ]:
        val = params.get(key)
        if val is not None:
            lines.append(f" {LABELS[key]}: {val}{SUFFIXES[key]}")
    if not lines:
        return "هنوز مقادیری دریافت نکردم."
    msg = "\n".join(lines)
    msg += "\n\n"
    msg += random_invite() + "\n"
    return msg

# Build the LLM chains
extraction_chain = extract_chain()
# advisor_chain = advisor_chain()

# Inject RTL CSS
st.markdown(
    """
    <style>
    input, textarea { direction: rtl !important; text-align: right !important; }
    h1 { direction: rtl; text-align: right !important; }
    [data-testid="stChatMessage"][role="user"] {
        display: flex !important;
        flex-direction: row-reverse !important;
        align-items: flex-start !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown('<h1>وام چی داریم</h1>', unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "params" not in st.session_state:
    st.session_state.params = {k: None for k in VALID_CRITERIA}

# Display chat history
for msg in st.session_state.messages:
    rendered = msg.content.replace("\n", "<br>")
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(
            f'<div dir="rtl" style="text-align:right;">{rendered}</div>',
            unsafe_allow_html=True
        )

# User input
prompt = st.chat_input(placeholder="چطور میتونم کمکت کنم؟")
if prompt:
    # Echo user
    with st.chat_message("user"):
        st.markdown(
            f'<div dir="rtl" style="text-align:right;">{prompt}</div>',
            unsafe_allow_html=True
        )
        st.session_state.messages.append(HumanMessage(prompt))

    # 1) Try extraction
    raw_output = extraction_chain.predict(user_input=prompt)
    # new_params = clean_and_parse(raw_output)
    try:
        new_params = clean_and_parse(raw_output)
    except ValueError:
        new_params = {k: None for k in VALID_CRITERIA}
        apology = random_irrelevant()


    other_keys = [k for k in new_params if k != "Loan_field"]
    if new_params.get("Loan_field") and all(new_params.get(k) is None for k in other_keys):
        loan_field = random_loan_field()
        result_str = (
            f"{loan_field}\n\n"
        )
    
    elif not any(v is not None for v in new_params.values()):

        apology = random_irrelevant()
        result_str = f"{apology}\n\n{random_response_summary(format_params_message(st.session_state.params))}"
    else:
        # 3) Validate extracted params
        invalid_msgs, valid_updates = [], {}
        for key, val in new_params.items():
            if key == "Loan_field" or val is None:
                continue
            crit = VALID_CRITERIA[key]
            ok, hint = True, None
            if isinstance(crit, list) and val not in crit:
                ok, hint = False, ", ".join(str(x) for x in crit if x is not None)
            if callable(crit) and not crit(val):
                ok, hint = False, "کوچکتر یا مساوی 300000000"
            if ok:
                valid_updates[key] = val
            else:
                invalid_msgs.append(random_invalid(LABELS[key]) + f"\nراهنمایی: {hint}")
        if invalid_msgs:
            result_str = f"{'\n'.join(invalid_msgs)}\n\n{random_response_summary(format_params_message(st.session_state.params))}"
        else:
            st.session_state.params.update(valid_updates)
            result_str = random_response_summary(format_params_message(st.session_state.params))

    # 4) Display assistant response
    with st.chat_message("assistant"):
        st.markdown(
            f'<div dir="rtl" style="text-align:right;">{result_str.replace("\n","<br>")}</div>',
            unsafe_allow_html=True
        )
        st.session_state.messages.append(AIMessage(result_str))
