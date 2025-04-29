import streamlit as st
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import ast




# Initialize the LLM (using Ollama in this example).
llm = Ollama(model="phi4:latest", base_url="http://127.0.0.1:11434")


extraction_prompt = PromptTemplate(
    input_variables=["user_input"],
    template=(
        # 1) absolutely forbid chain‐of‐thought
        "Do not think. Do not output any reasoning—output **only** the JSON.\n\n"

        # 2) define the fields
        "Extract exactly these fields as JSON (no markdown, no fences):\n"
        "- deposit_amount (float or null) : مقدار سپرده یا میانگین سپرده یا میزان پولی که کاربر دارد \n"
        "- loan_amount (float or null) : مقدار وامی که کاربر میخواهد یا به او تعلق میگیرد\n"
        "- deposit_duration (integer months or null) : مدت زمانی که پول یا سپرده مشتری در حساب بانکی باید باشد یا میخواهد باش یا در حسابش بخواباند\n"
        "- repayment_duration (integer months or null) : مدت زمان بازپرداخت وام یا تعداد اقساط\n"
        "- Credit_score (string or null) : امتیاز اعتباری یا رتبه اعتباری\n"
        "- Interest_rate (integer percent without % or null) : نرخ سود وام یا کارمزد وام\n\n"
        "مقدار سپرده و مقدار وام به صورت پیش فرض بر حسب تومان هستند. اگر کاربر به تومن مقادیر را بیان کرد آن را با فرض ریال بودن درنظر بگیر\n"
        # 3) if a field is not mentioned, it must be null
        "If missing, set its value to `null`. Numbers must be plain digits (e.g. 25000000),\n"
        "no underscores, commas, or % signs.\n\n"

        # 4) few‐shot example for missing durations
        "### Example 1\n"
        "Input: \"من میخوام ببینم سود سپرده بانک اگه ۶۰ میلیون پول بخوابونم چقدره\"\n"
        "Output:\n"
        '{{'
        '"deposit_amount":600_000_000,'
        '"deposit_duration":null,'
        '"loan_amount":null,'
        '"repayment_duration":null,'
        '"Credit_score":null,'
        '"Interest_rate":null'
        '}}\n\n'

        # 5) now YOUR input
        "### Now process this input:\n"
        "Input: \"{user_input}\"\n"
        "Output:"
    )
)


def extract_chain():
# Create the extraction chain.
    extraction_chain = LLMChain(llm=llm, prompt=extraction_prompt, verbose=True)
    return extraction_chain
#



