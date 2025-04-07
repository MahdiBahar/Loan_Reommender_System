
from llm_parser_func import parse_extraction_result
from main import extract_chain
from validate_params_func import validate_parameters
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

import json



extraction_chain = extract_chain()

st.title("Loan Chatbot")



#####----------------------------------------------------
# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# display chat messages from history on app rerun
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

prompt = st.chat_input("چطور میتونم کمکت کنم؟")

if prompt:
    # add the message from the user to the screen
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(prompt))

    # Run the extraction chain using the conversation history
    extraction_result = extraction_chain.run({"user_input": st.session_state.messages})
    try:
        extracted_params = parse_extraction_result(extraction_result)
        st.session_state["params"] = extracted_params
    except Exception as e:
        st.error(f"Error parsing extraction result: {e}")
    
    updated_params = validate_parameters(st.session_state["params"])
#         st.session_state["params"] = updated_params

    st.session_state["params"] = updated_params
    
    result = st.session_state["params"]
    



    # Convert the result dictionary to a string before appending to chat messages.
    result_str = json.dumps(result, indent=2, ensure_ascii=False)
    with st.chat_message("assistant"):
        st.markdown(result_str)
        st.session_state.messages.append(AIMessage(result_str))


##########_________________________________________________

# extraction_chain = extract_chain()


# st.title("Loan Chatbot")

# # initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

#     # st.session_state.messages.append(SystemMessage("Act like an astronaut"))

# # display chat messages from history on app rerun
# for message in st.session_state.messages:
#     if isinstance(message, HumanMessage):
#         with st.chat_message("user"):
#             st.markdown(message.content)
#     elif isinstance(message, AIMessage):
#         with st.chat_message("assistant"):
#             st.markdown(message.content)



# prompt = st.chat_input("چطور میتونم کمکت کنم؟")

# if prompt:

#     # add the message from the user (prompt) to the screen with streamlit
#     with st.chat_message("user"):
#         st.markdown(prompt)

#         st.session_state.messages.append(HumanMessage(prompt))

#     extraction_result = extraction_chain.run({"user_input": st.session_state.messages})
#     # st.write("LLM Extraction Result:")
#     # st.write(extraction_result)
#     try:
#         extracted_params = parse_extraction_result(extraction_result)
#         # st.write("Extracted Parameters:")
#         # st.write(extracted_params)
#         st.session_state["params"] = extracted_params
#     except Exception as e:
#         st.error(f"Error parsing extraction result: {e}")
#     result = extracted_params

#     # create the echo (response) and add it to the screen

#     # llm = ChatOllama(
#     #     model="phi4:latest",
#     #     temperature=0
#     # )

#     # result = llm.invoke(st.session_state.messages).content

#     with st.chat_message("assistant"):
#         st.markdown(result)

#         st.session_state.messages.append(AIMessage(result))



# # Step 1: Get user input for extraction.
# user_query = st.text_area("Enter your query:", "I want to take a 35-million Toman loan and pay it in 8 installments.")

# if st.button("Extract Parameters"):
#     extraction_result = extraction_chain.run({"user_input": user_query})
#     st.write("LLM Extraction Result:")
#     st.write(extraction_result)
#     try:
#         extracted_params = parse_extraction_result(extraction_result)
#         st.write("Extracted Parameters:")
#         st.write(extracted_params)
#         st.session_state["params"] = extracted_params
#     except Exception as e:
#         st.error(f"Error parsing extraction result: {e}")

# # Step 2: Validate and override parameters.
# if "params" in st.session_state:
#     st.write("Current Extracted Parameters:")
#     st.write(st.session_state["params"])
    
#     if st.button("Validate/Override Parameters"):
#         updated_params = validate_parameters(st.session_state["params"])
#         st.session_state["params"] = updated_params
#         st.write("Final Validated Parameters:")
#         st.write(updated_params)
        
# # Step 3: Show final parameters or proceed with further calculation.
# if "params" in st.session_state:
#     st.write("Final Parameters for Calculation:")
#     st.write(st.session_state["params"])