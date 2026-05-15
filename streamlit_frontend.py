import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage


thread_id = '1'
CONFIG = {
        'configurable': {
            'thread_id': thread_id
        }
    }


if("message_history" not in st.session_state):
    st.session_state["message_history"] = []

message_history = st.session_state["message_history"]

for message in message_history:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input("Type your message here...")

if user_input:

    # save to message history
    st.session_state["message_history"].append({"role": "user", "content": user_input});
    with st.chat_message("user"):
        st.text(user_input)


    with st.chat_message("assistant"):
        llm_response = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )
    st.session_state["message_history"].append({"role": "assistant", "content": llm_response});

    