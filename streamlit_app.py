import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
from app.utils import generate_thread_id


# **************** Utility functions ****************
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state["message_history"] = []
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_sidebar_threads():
    for thread_id in st.session_state['chat_threads'][::-1]:  # Display in reverse order (most recent first)

        messages = load_conversation(thread_id)

        temp_messages = []
        first_user_message = "New Chat"

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
                
                if first_user_message == "New Chat":
                    first_user_message = msg.content
            else:
                role = "assistant"
            temp_messages.append({"role": role, 'content': msg.content})
        
        # use first user message as button text
        if st.sidebar.button(first_user_message, key=thread_id):
            st.session_state['thread_id'] = thread_id
            st.session_state["message_history"] = temp_messages

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    #print(f"Loading conversation for thread_id: {state}")
    return state.values.get('messages', [])



# **************** Session setup for message history ****************
if("message_history" not in st.session_state):
    st.session_state["message_history"] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
    
add_thread(st.session_state['thread_id'])

# **************** Sidebar UI ****************
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('Recent Chats')

load_sidebar_threads()


# **************** Main Chat UI ****************
#message_history = st.session_state["message_history"]
for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])

CONFIG = {
        'configurable': {
            'thread_id': st.session_state['thread_id']
        }
    }
user_input = st.chat_input("Type your message here...")

if user_input:

    # save to message history
    st.session_state["message_history"].append({"role": "user", "content": user_input});
    with st.chat_message("user"):
        st.text(user_input)


    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content
        llm_response = st.write_stream(ai_only_stream())
    st.session_state["message_history"].append({"role": "assistant", "content": llm_response});

    