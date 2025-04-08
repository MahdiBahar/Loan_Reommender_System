import streamlit as st
import json

# --- Configuration: Valid Criteria, Hints, and Parameter Order ---

VALID_CRITERIA = {
    "deposit_amount": lambda x: True,  # No limitations.
    "deposit_duration": lambda x: 1 <= x <= 12,
    "loan_amount": lambda x: x <= 300000000,
    "credit_score": lambda x: x in ["A", "B", "C", "D", "E", "None"],
    "number_of_installments": lambda x: x in [4, 6, 9, 12, 18, 24, 36, 48],
    "interest_rate": lambda x: x in [0, 2, 4, 18, 23]
}

HINTS = {
    "deposit_amount": "Enter any number.",
    "deposit_duration": "Enter an integer between 1 and 12 (months).",
    "loan_amount": "Enter an integer no more than 300000000.",
    "credit_score": "Enter one of: A, B, C, D, E, None.",
    "number_of_installments": "Allowed values: 4, 6, 9, 12, 18, 24, 36, 48.",
    "interest_rate": "Allowed values: 0, 2, 4, 18, 23."
}

REQUIRED_PARAMS = [
    "deposit_amount", "deposit_duration",
    "loan_amount", "credit_score",
    "number_of_installments", "interest_rate"
]


PERSIAN_LABELS = {
    "deposit_amount": "مبلغ سپرده",
    "deposit_duration": "مدت سپرده",
    "loan_amount": "مبلغ وام",
    "credit_score": "رتبه اعتباری",
    "number_of_installments": "تعداد اقساط",
    "interest_rate": "نرخ بهره"
}

# --- Initialize Session State Variables ---
if "params" not in st.session_state:
    st.session_state.params = {
        "deposit_amount": 30000000.0,
        "deposit_duration": 6,
        "loan_amount": None,
        "credit_score": None,
        "number_of_installments": 12,  # Simulated extracted value (invalid).
        "interest_rate": 4
    }

if "param_index" not in st.session_state:
    st.session_state.param_index = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# --- Display Chat History ---
st.title("چت بات تسهیلات")
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

# --- Parameter Conversation Using a Form ---
if st.session_state.param_index < len(REQUIRED_PARAMS):
    current_param = REQUIRED_PARAMS[st.session_state.param_index]
    current_val = st.session_state.params.get(current_param)
    
        # Persian display of the parameter name:
    persian_label = PERSIAN_LABELS.get(current_param, current_param)
    # Determine if the current extracted value is valid.
    valid_extracted = (current_val is not None) and VALID_CRITERIA[current_param](current_val)
    
    if valid_extracted:
        # prompt_text = (
        #     f"The extracted value for '{current_param}' is {current_val}.\n"
        #     "Press Enter to keep it, or enter a new value below.\n"
        #     f"(Hint: {HINTS[current_param]})"
        # )
        prompt_text = (
        f"مقدار استخراج شده برای '{persian_label}' برابر است با {current_val}.\n"
            f"برای تایید آن، روی دکمه «تایید» کلیک کنید یا مقدار جدید را وارد نمایید.\n"
            # f"(راهنمایی: {HINTS[current_param]}"
        )
    else:
        # prompt_text = (
        #     f"No valid value was extracted for '{current_param}'.\n"
        #     f"(Hint: {HINTS[current_param]}).\n"
        #     "Please enter a valid value for this parameter, or leave it blank to set it to None."
        # )

        prompt_text = (
            f"مقدار معتبر برای '{persian_label}' استخراج نشده است.\n"
            # f"(راهنمایی: {HINTS[current_param]}).\n"
            "لطفاً مقدار معتبری وارد کنید، یا فیلد را خالی بگذارید تا مقدار آن به None تنظیم شود."
        )

    
    st.chat_message("assistant").markdown(prompt_text)
    
    # Create a form for the current parameter.
    with st.form(key=f"form_{current_param}"):
        # Text input accepts empty input.
        response = st.text_input(f"پاسخ شما برای '{persian_label}' چیه؟", value="", key=f"input_{current_param}"
  )
        submitted = st.form_submit_button("تایید")
    
    if submitted:
        # Process response.
        if response.strip() == "":
            # If the field is empty, keep current valid value or use None.
            updated_val = current_val if valid_extracted else None
        else:
            try:
                if current_param in ["deposit_duration", "loan_amount", "number_of_installments", "interest_rate"]:
                    if current_param == "deposit_amount":
                        updated_val = float(response.strip())
                    else:
                        updated_val = int(response.strip())
                else:
                    updated_val = response.strip().upper()
            except Exception:
                updated_val = None
        
        if updated_val is None or not VALID_CRITERIA[current_param](updated_val):
            st.chat_message("assistant").markdown(
                f"مقدار ({updated_val}) که برای '{persian_label}' دریافت شده معنبر نیست .\n"
                f"{HINTS[current_param]}\n"
                # f"مقدار به **None** تنظیم خواهد شد.\ق\n"
            )
            st.session_state.params[current_param] = None
        else:
            st.session_state.params[current_param] = updated_val
            st.chat_message("assistant").markdown(
                f"' {persian_label}'  بروزرسانی شد: {updated_val} "
            )
        
        add_message("user", response if response.strip() != "" else f"مقدار قبلی پارامتر رو حفظ کن")
        add_message("assistant", f"مقدار {persian_label} برابر شد با : {st.session_state.params[current_param]}")
       
        st.session_state.param_index += 1
        # No call to st.experimental_rerun(); the form submission automatically reruns the script.
        
# --- Final Display ---
if st.session_state.param_index >= len(REQUIRED_PARAMS):
    st.chat_message("assistant").markdown("تمام پارامترها استخراج شدند")
    final_str = json.dumps(st.session_state.params, indent=2, ensure_ascii=False)
    st.write(final_str)