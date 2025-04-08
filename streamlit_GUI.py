
from llm_parser_func import parse_extraction_result
from main import extract_chain
from validate_params_func import validate_parameters
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

import json



extraction_chain = extract_chain()

st.title("چت بات تسهیلات")



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
        result = st.session_state["params"]
        result_str = json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        # st.error(f"Error parsing extraction result: {e}")
        result_str = "با توجه به اینکه من چت بات مخصوص تسهیلات هستم، متاسفانه در مورد موضوعی که بهم گفتی اطلاع خاصی ندارم. لطفا در مورد مضوعات مرتبط باهام صحبت کن"
    # updated_params = validate_parameters(st.session_state["params"])
#         st.session_state["params"] = updated_params

    # st.session_state["params"] = updated_params
    # st.session_state["params"] = extracted_params
    
    



    # Convert the result dictionary to a string before appending to chat messages.
  
    with st.chat_message("assistant"):
        st.markdown(result_str)
        st.session_state.messages.append(AIMessage(result_str))


##########_________________________________________________
