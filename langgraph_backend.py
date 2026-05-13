from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from streamlit_frontend import message_history
from langchain_core.messages import HumanMessage

thread_id = '1'
CONFIG = {
        'configurable': {
            'thread_id': thread_id
        }
    }

from dotenv import load_dotenv
load_dotenv()

selectedModel="gemini-2.5-flash"

llm = ChatGoogleGenerativeAI(
    model=selectedModel,
    temperature=0.7
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# thread_id = '1'

#checkpoint saver
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)

graph.add_edge(START, "chat")
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=checkpointer)
