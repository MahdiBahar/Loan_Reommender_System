import streamlit as st
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import ast




# Initialize the LLM (using Ollama in this example).
llm = Ollama(model="phi4:latest", base_url="http://127.0.0.1:11434")



# Create a prompt template for extracting parameters.
extraction_prompt = PromptTemplate(
    input_variables=["user_input"],
    template=(
        "Given the following user input:\n"
        "\"{user_input}\"\n\n"
        "Extract the following parameters as a JSON object:\n"
        "- deposit_amount: The amount of money deposited (if mentioned; otherwise, None).\n"
        "- deposit_duration: The duration of the deposit in months (if mentioned; otherwise, None).\n"
        "- loan_amount: The total loan amount (if mentioned; otherwise, None).\n"
        "- credit_score (if mentioned; otherwise, None).\n"
        "- number_of_installments (if mentioned; otherwise, None).\n"
        "- interest_rate (if mentioned; otherwise, None).\n\n"
        "If a parameter is not mentioned in the input, set its value to None.\n\n"
        "Example output:\n"
        "{{\n"
        '  "deposit_amount": 5000000,\n'
        '  "deposit_duration": 6,\n'
        '  "loan_amount": "None",\n'
        '  "credit_score": "None",\n'
        '  "number_of_installments": "None",\n'
        '  "interest_rate": "None"\n'
        "}}"
    )
)


def extract_chain():
# Create the extraction chain.
    extraction_chain = LLMChain(llm=llm, prompt=extraction_prompt, verbose=True)
    return extraction_chain
#


