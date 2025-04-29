from LLM_parser_func import clean_and_parse
from LLM_model import extract_chain
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from random_responses import (
    random_response_summary,
    random_invite,
    random_irrelevant,
    random_invalid,
)




# Validation criteria for each parameter
VALID_CRITERIA = {
    "deposit_amount": None,
    "deposit_duration": [1, 2, 3, 4, 6, 12],
    "loan_amount": lambda x: x <= 300_000_000,
    "Credit_score": ["A", "B", "C", "D", "E", None],
    "repayment_duration": [12, 24, 36, 48, 60],
    "Interest_rate": [4, 14, 18, 23],
}

# Labels and suffixes for messages
LABELS = {
    "deposit_amount": "مقدار سپرده",
    "loan_amount": "مقدار وام",
    "deposit_duration": "مدت سپرده",
    "repayment_duration": "دوره بازپرداخت",
    "Credit_score": "رتبه اعتباری",
    "Interest_rate": "نرخ سود",
}
SUFFIXES = {
    "deposit_amount": "",
    "loan_amount": "",
    "deposit_duration": " ماه",
    "repayment_duration": " ماه",
    "Credit_score": "",
    "Interest_rate": " درصد",
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
        return "تا اینجا، هنوز مقادیری دریافت نکردم."
    # msg = "بسیار خب. تا اینجا برای من مشخص شده که مقادیر زیر مدنظر شما هست:\n"
    # msg = random_invite() + "\n"
    msg = "\n".join(lines)
    msg += "\n\n"
    msg += random_invite() + "\n"
    # msg += "اگر میخوای که اطلاعات دقیق‌تری از وام‌ها و شرایطش داشته باشی می‌تونم تو رو به صفحه توصیه‌گر وام ببرم."
    return msg

# Build the LLM extraction chain
extraction_chain = extract_chain()

# Inject RTL CSS for inputs, title, and user bubble alignment
st.markdown(
    """
    <style>
    /* RTL for inputs and title */
    input, textarea { direction: rtl !important; text-align: right !important; }
    h1 { direction: rtl; text-align: right !important; }
    /* Reverse user chat bubble layout: avatar on the right */
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

# Display chat history: preserve line breaks
for msg in st.session_state.messages:
    rendered = msg.content.replace("\n", "<br>")
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(
                f'<div dir="rtl" style="text-align:right;">{rendered}</div>',
                unsafe_allow_html=True
            )
    else:
        with st.chat_message("assistant"):
            st.markdown(
                f'<div dir="rtl" style="text-align:right;">{rendered}</div>',
                unsafe_allow_html=True
            )

# User input
prompt = st.chat_input(placeholder="چطور میتونم کمکت کنم؟")
if prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(
            f'<div dir="rtl" style="text-align:right;">{prompt}</div>',
            unsafe_allow_html=True
        )
        st.session_state.messages.append(HumanMessage(prompt))

    # Process input
    try:
        raw_output = extraction_chain.predict(user_input=prompt)
        new_params = clean_and_parse(raw_output)
        # Irrelevant if no params
        if not any(v is not None for v in new_params.values()):
            # apology = (
            #     "با توجه به اینکه من چت‌بات توصیه‌گر تسهیلات هستم، نیاز دارم که اطلاعاتی در مورد وامی که مد نظرتان هست داشته باشم. "
            #     "متأسفانه در مورد پیامی که فرستادید، نمی‌توانم پاسخ دهم."
            # )
            apology = random_irrelevant()
            result_str = f"{apology}\n\n{random_response_summary(format_params_message(st.session_state.params))}"
        else:
            invalid_msgs = []
            valid_updates = {}
            for key, val in new_params.items():
                if val is None:
                    continue
                crit = VALID_CRITERIA[key]
                valid_flag = True
                hint = None
                if isinstance(crit, list) and val not in crit:
                    valid_flag = False
                    hint = ", ".join(str(x) for x in crit if x is not None)
                if callable(crit) and not crit(val):
                    valid_flag = False
                    hint = "کوچکتر یا مساوی 300000000"
                if valid_flag:
                    valid_updates[key] = val
                else:
                    label = LABELS[key]
                    invalid_msgs.append(random_invalid(label) + f"\nراهنمایی: {hint}")
                    # invalid_msgs.append(
                    #     f"ببین مقداری که برای {LABELS[key]} گفتی توی رنج تعریف شده برای وام‌های ما نیست. "
                    #     f"راهنمایی: {hint}"  
                    # )
            if invalid_msgs:
                result_str = f"{'\n'.join(invalid_msgs)}\n\n{random_response_summary(format_params_message(st.session_state.params))}"
            else:
                st.session_state.params.update(valid_updates)
                # Use random template for summary
                canonical = format_params_message(st.session_state.params)
                result_str = random_response_summary(canonical)
    except Exception:
        # apology = (
        #     "با توجه به اینکه من چت‌بات مخصوص تسهیلات هستم، متأسفانه در مورد موضوعی که فرستادید اطلاعی ندارم."
        # )
        apology = random_irrelevant()
        result_str = f"{apology}\n\n{format_params_message(st.session_state.params)}"

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(
            f'<div dir="rtl" style="text-align:right;">{result_str.replace("\n","<br>")}</div>',
            unsafe_allow_html=True
        )
        st.session_state.messages.append(AIMessage(result_str))
