from llm_parser_func import parse_extraction_result
from main import extract_chain


extraction_chain = extract_chain()

user_input = (
    "من ۲۰۰۰۰۰۰ پول توی ۴ ماه گذاشتم تو حسابم. الان میخوام ببینم چقدر وام ۴ درصد میتونم بگیرم. رتبه اعتباریم رو هم نمیدونم"
)

# user_input = (
#     "من میخوام یه وام ۳۵ میلیونی بگیرم. کلا هم میتونم تعداد ۸ قسط پرداختش کنم"
# )


# Run the extraction chain.
extraction_result = extraction_chain.run({"user_input": user_input})
print("Extraction result:")
print(extraction_result)

# Parse the extracted output.
parsed_params = parse_extraction_result(extraction_result)
print("Parsed parameters:")
print(parsed_params)
