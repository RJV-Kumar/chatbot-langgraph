import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import sqlite3

from dotenv import load_dotenv
load_dotenv()

selectedModel="gemini-2.5-flash"

llm = ChatGoogleGenerativeAI(
    model= os.getenv("SELECTED_MODEL"),
    temperature=0.7
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# thread_id = '1'

# **************** Database ****************
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

#checkpoint saver
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)

graph.add_edge(START, "chat")
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)
