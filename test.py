from llm_parser_func import parse_extraction_result
from main import extract_chain
from validate_params_func import validate_parameters

extraction_chain = extract_chain()

# Example user input (this could be from a chatbot, web form, etc.).
# user_input = (
#     "I deposited 5 million Tomans for 6 months. I took a loan of 250000000 from Bank X. "
#     "My credit score is A. I have 12 installments and the interest rate is 4."
# )

# user_input = (
#     "من میخوام یه وام ۳۵ میلیونی بگیرم. کلا هم میتونم توی اقساط ۸ ماهه پرداختش کنم"
# )

user_input = (
    "من ۲۰۰۰۰۰۰ پول توی ۴ ماه گذاشتم تو حسابم. الان میخوام ببینم چقدر وام ۳ درصد میتونم بگیرم. رتبه اعتباریم رو هم نمیدونم"
)



# Use the LLM extraction chain to get parameters from the input.
extraction_result = extraction_chain.run({"user_input": user_input})
print("LLM Extraction Result:")
print(extraction_result)

# Parse the extraction result to a Python dictionary.
extracted_params = parse_extraction_result(extraction_result)
print("Extracted Parameters (from LLM):")
print(extracted_params)

# Validate or prompt the user for any missing/incorrect parameters.
final_params = validate_parameters(extracted_params)
# final_params = double_check_parameters(extracted_params)
print("Final Validated Parameters:")
print(final_params)