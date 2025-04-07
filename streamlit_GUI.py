
from llm_parser_func import parse_extraction_result
from main import extract_chain
from validate_params_func import validate_parameters
import streamlit as st

extraction_chain = extract_chain()


st.title("Loan Chatbot")

# Step 1: Get user input for extraction.
user_query = st.text_area("Enter your query:", "I want to take a 35-million Toman loan and pay it in 8 installments.")

if st.button("Extract Parameters"):
    extraction_result = extraction_chain.run({"user_input": user_query})
    st.write("LLM Extraction Result:")
    st.write(extraction_result)
    try:
        extracted_params = parse_extraction_result(extraction_result)
        st.write("Extracted Parameters:")
        st.write(extracted_params)
        st.session_state["params"] = extracted_params
    except Exception as e:
        st.error(f"Error parsing extraction result: {e}")

# Step 2: Validate and override parameters.
if "params" in st.session_state:
    st.write("Current Extracted Parameters:")
    st.write(st.session_state["params"])
    
    if st.button("Validate/Override Parameters"):
        updated_params = validate_parameters(st.session_state["params"])
        st.session_state["params"] = updated_params
        st.write("Final Validated Parameters:")
        st.write(updated_params)
        
# Step 3: Show final parameters or proceed with further calculation.
if "params" in st.session_state:
    st.write("Final Parameters for Calculation:")
    st.write(st.session_state["params"])