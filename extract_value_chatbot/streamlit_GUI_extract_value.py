from LLM_parser_func import clean_and_parse
from LLM_model import extract_chain
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# Validation criteria for each parameter
VALID_CRITERIA = {
    "deposit_amount": None,  # no limitation
    "deposit_duration": [1, 2, 3, 6, 12],
    "loan_amount": lambda x: x <= 300_000_000,
    "Credit_score": ["A", "B", "C", "D", "E", None],
    "repayment_duration": [4, 6, 9, 12, 18, 24, 36, 48],
    "Interest_rate": [4, 14, 18, 23],
}

# Labels and suffixes for user-friendly messages
LABELS = {
    "deposit_amount": "مقدار سپرده",
    "loan_amount": "مقدار وام",
    "deposit_duration": "مدت سپرده",
    "repayment_duration": "دوره بازپرداخت",
    "Credit_score": "امتیاز اعتباری",
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

# Helper: format extracted parameters into a user-friendly Persian message
# Only non-null values are shown, each on its own line

def format_params_message(params: dict) -> str:
    lines = []
    for key in ["deposit_amount", "loan_amount", "deposit_duration", "repayment_duration", "Credit_score", "Interest_rate"]:
        value = params.get(key)
        if value is not None:
            lines.append(f" {LABELS[key]}: {value}{SUFFIXES[key]}")
    if not lines:
        return "هنوز مقادیری برای اینکه بتوانم وام معرفی کنم، تعیین نکردی!"
    msg = "تا اینجا برای من مشخص شده که مقادیر زیر مدنظر شما هست:\n"
    msg += "\n".join(lines)
    msg += "\n"
    msg += "اگر میخوای که اطلاعات دقیق‌تری از وام‌ها و شرایطش داشته باشی می‌تونم تو رو به صفحه توصیه‌گر وام ببرم."
    return msg

# Build the LLM extraction chain
extraction_chain = extract_chain()

st.title("وام چی داریم")

# Initialize chat history and parameters
if "messages" not in st.session_state:
    st.session_state.messages = []
if "params" not in st.session_state:
    st.session_state.params = {k: None for k in VALID_CRITERIA}

# Display existing chat messages
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.text(message.content)

# User input
prompt = st.chat_input("چطور میتونم کمکت کنم؟")

if prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(prompt))

    try:
        # Extract parameters
        raw_output = extraction_chain.predict(user_input=prompt)
        new_params = clean_and_parse(raw_output)

        # If no parameter was provided, treat as irrelevant
        if not any(v is not None for v in new_params.values()):
            # Irrelevant question fallback
            apology = (
                "با توجه به اینکه من چت‌بات مخصوص تسهیلات هستم، متاسفانه "
                "در مورد موضوعی که بهم گفتی اطلاع خاصی ندارم. لطفا در مورد "
                "موضوعات مرتبط با من صحبت کن."
            )
            params_msg = format_params_message(st.session_state.params)
            result_str = f"{apology}\n\n{params_msg}"
        else:
            # Check validity of each provided parameter
            invalid_msgs = []
            valid_updates = {}
            for key, value in new_params.items():
                if value is None:
                    continue
                crit = VALID_CRITERIA.get(key)
                is_valid = True
                valid_hint = None
                if isinstance(crit, list):
                    if value not in crit:
                        is_valid = False
                        valid_hint = ", ".join(str(v) for v in crit if v is not None)
                elif callable(crit):
                    if not crit(value):
                        is_valid = False
                        valid_hint = "<= 300000000"
                if is_valid:
                    valid_updates[key] = value
                else:
                    label = LABELS.get(key, key)
                    invalid_msgs.append(
                        f"ببین مقداری که برای {label} گفتی توی رنج تعریف شده برای وام‌های ما نیست. "
                        f"پیشنهاد می‌کنم دوباره مقدار درست را به ما بگی.\n"
                        f"راهنمایی: {label} میتواند {valid_hint} باشد"
                    )
            # If any invalid inputs, prepare error response
            if invalid_msgs:
                apology = "\n".join(invalid_msgs)
                params_msg = format_params_message(st.session_state.params)
                result_str = f"{apology}\n\n{params_msg}"
            else:
                # merge valid updates into session params
                st.session_state.params.update(valid_updates)
                result_str = format_params_message(st.session_state.params)

    except Exception:
        # Parsing error fallback (also treat as irrelevant)
        apology = (
            "با توجه به اینکه من چت‌بات مخصوص تسهیلات هستم، متاسفانه "
            "در مورد موضوعی که بهم گفتی اطلاع خاصی ندارم. لطفا در مورد "
            "موضوعات مرتبط با من صحبت کن."
        )
        params_msg = format_params_message(st.session_state.params)
        result_str = f"{apology}\n\n{params_msg}"

    # Display assistant response
    with st.chat_message("assistant"):
        st.text(result_str)
        st.session_state.messages.append(AIMessage(result_str))
