



def check_input_value (user_input,param, extracted_params,hints, criteria):
    attempt = 0
    while  attempt <=5:
        if user_input == "":
            extracted_params[param] = None
            break
        else:
            try:
                if param in ["deposit_duration", "number_of_installments", "interest_rate"]:
                    # candidate_val = int(user_input)
                    candidate_val = float(user_input)
                elif param in ["loan_amount", "deposit_amount"]:
                    candidate_val = float(user_input)
                else:
                    candidate_val = user_input.upper()
            except Exception:
                print(f"Could not convert your input for '{param}'. Please try again.")
                attempt +=1
                continue
            if criteria(candidate_val):
                extracted_params[param] = candidate_val
                break
            else:
                user_input = input(f"I got your value for '{param}' as {candidate_val}, which is not valid. {hints[param]}. Please enter a valid value for '{param}', or press Enter to set it as None: ").strip()
                print(f"Your provided value '{candidate_val}' for '{param}' is not valid. {hints[param]}.")
                attempt +=1
    return extracted_params


def validate_parameters(extracted_params: dict) -> dict:

    # Define valid criteria as lambda functions.
    valid_criteria = {
        "deposit_amount": lambda x: True,  # No limitations.
        "deposit_duration": lambda x: 1 <= x <= 12,
        "loan_amount": lambda x: x <= 300000000,
        "credit_score": lambda x: x in ["A", "B", "C", "D", "E", "None"],
        "number_of_installments": lambda x: x in [4, 6, 9, 12, 18, 24, 36, 48],
        "interest_rate": lambda x: x in [0, 2, 4, 18, 23]
    }
    
    # Define user hints.
    hints = {
        "deposit_amount": "Enter any number (no limitations).",
        "deposit_duration": "Enter an integer between 1 and 12 (months).",
        "loan_amount": "Enter an integer no more than 300000000.",
        "credit_score": "Enter one of: A, B, C, D, E, None.",
        "number_of_installments": "Allowed values: 4, 6, 9, 12, 18, 24, 36, 48.",
        "interest_rate": "Allowed values: 0, 2, 4, 18, 23."
    }
    
    for param, criteria in valid_criteria.items():
        # Get current extracted value.
        value = extracted_params.get(param)
        if value is not None:
            try:
                if param in ["deposit_duration", "number_of_installments", "interest_rate"]:
                    current_val = int(value)
                elif param in ["loan_amount", "deposit_amount"]:
                    current_val = float(value)
                else:
                    current_val = str(value).upper()
            except Exception:
                current_val = None
        else:
            current_val = None

        # If a valid value is present, ask if the user wants to keep or override it.
        if current_val is not None and criteria(current_val):
            user_input = input(
                    f"The extracted value for '{param}' is {current_val}. Press Enter to keep it, "
                    f"or enter a new value. (Hint: {hints[param]}). "
                    f"Press Enter without input to keep the value, or type a new value: "
                ).strip()
            extracted_params= check_input_value (user_input,param, extracted_params,hints, criteria)
        else:
            if current_val is not None:
        
                user_input = input(
                        f"I got your value for '{param}' as {current_val}, which is not valid. {hints[param]}." 
                        f"Please enter a valid value for '{param}', or press Enter to set it as None: "
                        ).strip()
                extracted_params= check_input_value (user_input,param, extracted_params,hints, criteria)
    
            else:
                # No valid value is present.
                user_input = input(
                        f"No valid value was extracted for '{param}'. {hints[param]}. "
                        f"Please enter a valid value for '{param}', or press Enter to set it to None: "
                    ).strip()
                extracted_params= check_input_value (user_input,param, extracted_params,hints, criteria)
    return extracted_params
