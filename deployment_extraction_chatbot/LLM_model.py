import streamlit as st
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import ast




# Initialize the LLM (using Ollama in this example).
llm = Ollama(model="phi4:latest", base_url="http://127.0.0.1:11434",temperature= 0)
#     "به عنوان مثال میتونی به این صورت جواب بدی که: من در خصوص وام اینکه چه نوع وامی با توجه به شرایطت مناسبه میتونم کمک کنم. برای ان منظور نیاز دارم که اطلاعاتی مثل اینکه چه مقدار وام میخوای، میخوای چند درصد باشه و غیره.\n\n"
# Extraction prompt and chain
def _build_extraction_chain() -> LLMChain:
    extraction_prompt = PromptTemplate(
        input_variables=["user_input"],
        template=(
           "Do not think. Do not output any reasoning—output **only** the JSON or the advisor message.\n\n"
        "If the user_input contains the words 'وام' or 'تسهیلات' but does not contain any numeric values for deposit_amount, loan_amount, deposit_duration, repayment_duration, Credit_score, or Interest_rate, then make the loan_field parameter True\n"
        "If the user_input contains the words like  'سلام' or 'خوبی' or 'چطوری' but does not contain any numeric values for deposit_amount, loan_amount, deposit_duration, repayment_duration, Credit_score, or Interest_rate, then make the hello_msg parameter True \n"
        "Otherwise, extract exactly these fields as JSON (no markdown, no fences):\n"
            "- deposit_amount (float or null) :  مقدار سپرده یا میانگین سپرده یا میزان پولی که کاربر دارد یا میخواد بخواباند \n"
            "- loan_amount (float or null) : مقدار وامی که کاربر میخواهد یا به او تعلق میگیرد\n"
            "- deposit_duration (integer months or null) : مدت زمانی که پول یا سپرده مشتری در حساب بانکی باید باشد یا میخواهد باش یا در حسابش بخواباند\n"
            "- repayment_duration (integer months or null) : مدت زمان بازپرداخت وام یا تعداد اقساط\n"
            "- Credit_score (string or null) : امتیاز اعتباری یا رتبه اعتباری\n"
            "- Interest_rate (integer percent without % or null) :  نرخ سود وام یا کارمزد وام بر حسب درصد هست\n\n"
            "مقدار سپرده و مقدار وام به صورت پیش فرض بر حسب تومان هستند. اگر در پرامپ کاربر عدد خالی گفته شد، مقدار عدد را در اسکیل میلیون درنظر بگیر\n"
            "If missing, set its value to `null`. Numbers must be plain digits (e.g. 25000000),\n"
            "no underscores, commas, or % signs.\n"
            "- Loan_field (True or null) : اگر پرامپت ورود در حوزه وام یا تسهیلات است مقدار این پارامتر True میشود در غیر این صورت مقدارش null هست\n\n"
            "- hello_msg (True or null) : این پارامتر برای زمانی است که کاربر احوال پرسی انجام میدهد (مثلا می گوید سلام) و در پاسخ این پارامتر True میشود، در غیر این صورت null هست\n\n"
            
            "### Example 1\n"
            "Input: \"من اگه ۲۰ میلیون  پول رو ۳ ماه تو حسابم بخوابونم چقدر بهم وام 14 درصد میدی\"\n"
            "Output:\n"
            "{{"
            '"deposit_amount":20_000_000,'
            '"deposit_duration":3,'
            '"loan_amount":null,'
            '"repayment_duration":null,'
            '"Credit_score":null,'
            '"Interest_rate":14,'
            '"Loan_field":True,'
            '"hello_msg" : null'
            '}}\n\n'
            "### Example 2\n"
            "Input: \سلام. خوبی؟ یه وام ۲۰ میلیونی میخوام. با چهل میلیون سپرده چقدر وام بهم تعلق میگیره؟\"\n"
            "Output:\n"
            "{{"
            '"deposit_amount":40_000_000,'
            '"deposit_duration":null,'
            '"loan_amount":20_000_000,'
            '"repayment_duration":null,'
            '"Credit_score":null,'
            '"Interest_rate":null,'
            '"Loan_field":True,'
            '"hello_msg" : True'

            '}}\n\n'
            "### Example 3\n"
            "Input: \۳۰ تومن وام بده\"\n"
            "Output:\n"
            "{{"
            '"deposit_amount":null,'
            '"deposit_duration":null,'
            '"loan_amount":30_000_000,'
            '"repayment_duration":null,'
            '"Credit_score":null,'
            '"Interest_rate":null,'
            '"Loan_field":True,'
            '"hello_msg" : null'
            '}}\n\n'

            "### Now process this input:\n"
            "Input: \"{user_input}\"\n"
            "Output:"
        )
    )
    return LLMChain(llm=llm, prompt=extraction_prompt)



def extract_chain() -> LLMChain:
    """
    Returns a chain that extracts loan parameters as JSON.
    """
    return _build_extraction_chain()



