import streamlit as st
import json

# --- Configuration ---
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

# --- Assume extracted parameters are already in session_state ---
if "params" not in st.session_state:
    # Simulated extracted parameters (this may come from your LLM extraction chain).
    st.session_state.params = {
        "deposit_amount": 2000000.0,
        "deposit_duration": 4,
        "loan_amount": None,
        "credit_score": None,
        "number_of_installments": 8,  # 8 is invalid.
        "interest_rate": None
    }

if "param_index" not in st.session_state:
    st.session_state.param_index = 0

# --- Display Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# --- Parameter Conversation ---
if st.session_state.param_index < len(REQUIRED_PARAMS):
    current_param = REQUIRED_PARAMS[st.session_state.param_index]
    current_val = st.session_state.params.get(current_param)
    
    # Build the prompt message.
    if current_val is not None and VALID_CRITERIA[current_param](current_val):
        prompt_message = (
            f"The extracted value for '{current_param}' is {current_val}.\n"
            f"Press Enter to keep it, or enter a new value. (Hint: {HINTS[current_param]})"
        )
    else:
        prompt_message = (
            f"No valid value was extracted for '{current_param}'.\n"
            f"(Hint: {HINTS[current_param]}). Please enter a valid value for '{current_param}', "
            "or press Enter to set it to None."
        )
    
    st.chat_message("assistant").markdown(prompt_message)
    
    # Get the user's response for the current parameter.
    user_response = st.chat_input(f"Your response for '{current_param}':", key=current_param)
    # user_response = st.text_input(f"Your response for '{current_param}' (leave blank to keep current):", key=current_param)

    if user_response is not None:
        user_response = user_response.strip()
        # If the user presses Enter (empty input)
        if user_response == "z":
            if current_val is not None and VALID_CRITERIA[current_param](current_val):
                updated_val = current_val
            else:
                updated_val = None
        else:
            try:
                if current_param in ["deposit_duration", "loan_amount", "number_of_installments", "interest_rate"]:
                    if current_param == "deposit_amount":
                        updated_val = float(user_response)
                    else:
                        updated_val = int(user_response)
                else:
                    updated_val = user_response.upper()
            except Exception:
                updated_val = None
        
        if updated_val is None or not VALID_CRITERIA[current_param](updated_val):
            st.chat_message("assistant").markdown(
                f"I got your value for '{current_param}' as {updated_val}, which is not valid. {HINTS[current_param]}.\n"
                "It will be set to None."
            )
            st.session_state.params[current_param] = None
        else:
            st.session_state.params[current_param] = updated_val
            st.chat_message("assistant").markdown(
                f"'{current_param}' is updated to: {updated_val}"
            )
        
        add_message("user", user_response if user_response != "" else "(kept current)")
        add_message("assistant", f"{current_param} is now set to {st.session_state.params[current_param]}")
        
        st.session_state.param_index += 1

# When all parameters have been processed, display the final parameters.
if st.session_state.param_index >= len(REQUIRED_PARAMS):
    st.chat_message("assistant").markdown("All parameters have been verified:")
    final_str = json.dumps(st.session_state.params, indent=2, ensure_ascii=False)
    st.write(final_str)
