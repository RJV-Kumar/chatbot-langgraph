import streamlit as st
from app.chatbot import chatbot
from langchain_core.messages import HumanMessage, AIMessage
from app.utils import generate_thread_id


# **************** Chat Thread Utilities ****************

def create_new_chat():
    new_thread_id = generate_thread_id()

    st.session_state["active_thread_id"] = new_thread_id
    add_chat_thread(new_thread_id)

    st.session_state["chat_history"] = []


def add_chat_thread(thread_id):
    if thread_id not in st.session_state["chat_thread_ids"]:
        st.session_state["chat_thread_ids"].append(thread_id)


def fetch_conversation(thread_id):
    graph_state = chatbot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return graph_state.values.get("messages", [])


def render_sidebar_chat_threads():

    for thread_id in st.session_state["chat_thread_ids"][::-1]:

        conversation_messages = fetch_conversation(thread_id)

        formatted_messages = []
        chat_title = "New Chat"

        for message in conversation_messages:

            if isinstance(message, HumanMessage):
                role = "user"

                # first user message becomes chat title
                if chat_title == "New Chat":
                    chat_title = message.content

            else:
                role = "assistant"

            formatted_messages.append({
                "role": role,
                "content": message.content
            })

        if st.sidebar.button(chat_title, key=thread_id):

            st.session_state["active_thread_id"] = thread_id
            st.session_state["chat_history"] = formatted_messages


# **************** Session State Initialization ****************

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "active_thread_id" not in st.session_state:
    st.session_state["active_thread_id"] = generate_thread_id()

if "chat_thread_ids" not in st.session_state:
    st.session_state["chat_thread_ids"] = []

add_chat_thread(st.session_state["active_thread_id"])


# **************** Sidebar UI ****************

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    create_new_chat()

st.sidebar.header("Recent Chats")

render_sidebar_chat_threads()


# **************** Main Chat UI ****************

for chat_message in st.session_state["chat_history"]:

    with st.chat_message(chat_message["role"]):
        st.text(chat_message["content"])


CHATBOT_CONFIG = {
    "configurable": {
        "thread_id": st.session_state["active_thread_id"]
    }
}


user_prompt = st.chat_input("Type your message here...")


if user_prompt:

    st.session_state["chat_history"].append({
        "role": "user",
        "content": user_prompt
    })

    with st.chat_message("user"):
        st.text(user_prompt)

    with st.chat_message("assistant"):

        def stream_ai_response():

            for response_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_prompt)]},
                config=CHATBOT_CONFIG,
                stream_mode="messages"
            ):

                if isinstance(response_chunk, AIMessage):
                    yield response_chunk.content

        assistant_response = st.write_stream(stream_ai_response())

    st.session_state["chat_history"].append({
        "role": "assistant",
        "content": assistant_response
    })