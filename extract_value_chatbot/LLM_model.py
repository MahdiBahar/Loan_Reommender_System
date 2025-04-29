import streamlit as st
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import ast




# Initialize the LLM (using Ollama in this example).
llm = Ollama(model="phi4:latest", base_url="http://127.0.0.1:11434")

# Extraction prompt and chain
def _build_extraction_chain() -> LLMChain:
    extraction_prompt = PromptTemplate(
        input_variables=["user_input"],
        template=(
            "Do not think. Do not output any reasoning—output **only** the JSON.\n\n"
            "Extract exactly these fields as JSON (no markdown, no fences):\n"
            "- deposit_amount (float or null) : مقدار سپرده یا میانگین سپرده یا میزان پولی که کاربر دارد \n"
            "- loan_amount (float or null) : مقدار وامی که کاربر میخواهد یا به او تعلق میگیرد\n"
            "- deposit_duration (integer months or null) : مدت زمانی که پول یا سپرده مشتری در حساب بانکی باید باشد یا میخواهد باش یا در حسابش بخواباند\n"
            "- repayment_duration (integer months or null) : مدت زمان بازپرداخت وام یا تعداد اقساط\n"
            "- Credit_score (string or null) : امتیاز اعتباری یا رتبه اعتباری\n"
            "- Interest_rate (integer percent without % or null) : نرخ سود وام یا کارمزد وام\n\n"
            "مقدار سپرده و مقدار وام به صورت پیش فرض بر حسب تومان هستند. اگر کاربر به تومن مقادیر را بیان کرد آن را با فرض ریال بودن درنظر بگیر\n"
            "If missing, set its value to `null`. Numbers must be plain digits (e.g. 25000000),\n"
            "no underscores, commas, or % signs.\n\n"
            "### Example 1\n"
            "Input: \"من میخوام ببینم سود سپرده بانک اگه ۶۰ میلیون پول بخوابونم چقدره\"\n"
            "Output:\n"
            "{{"
            '"deposit_amount":600_000_000,'
            '"deposit_duration":null,'
            '"loan_amount":null,'
            '"repayment_duration":null,'
            '"Credit_score":null,'
            '"Interest_rate":null'
            '}}\n\n'
            "### Now process this input:\n"
            "Input: \"{user_input}\"\n"
            "Output:"
        )
    )
    return LLMChain(llm=llm, prompt=extraction_prompt)

# Advisor prompt and chain for keyword-based queries
def _build_advisor_chain() -> LLMChain:
    advisor_prompt = PromptTemplate(
        input_variables=["user_input"],
        template=(
            "شما یک مشاور وام هستید. به پرسش زیر با توجه به مثالی که بهت دادم به صورت خیلی خلاصه و در حد یک الی دو خط پاسخ بده:\n"
            "{user_input}"
            "به عنوان مثال میتونی به این صورت جواب بدی که: من در خصوص وام اینکه چه نوع وامی با توجه به شرایطت مناسبه میتونم کمک کنم. برای ان منظور نیاز دارم که اطلاعاتی مثل اینکه چه مقدار وام میخوای، میخوای چند درصد باشه و غیره. \n"
        )
    )
    return LLMChain(llm=llm, prompt=advisor_prompt)

# Public constructors

def extract_chain() -> LLMChain:
    """
    Returns a chain that extracts loan parameters as JSON.
    """
    return _build_extraction_chain()


def advisor_chain() -> LLMChain:
    """
    Returns a chain that provides loan-advice on keyword queries.
    """
    return _build_advisor_chain()
