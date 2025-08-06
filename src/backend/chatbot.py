import os
from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import START, END, StateGraph
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

search_tool = TavilySearchResults(max_results = 3)
tools = [search_tool]

llm=ChatGroq(model="openai/gpt-oss-120b")

llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages' : [response]}


checkpointer = InMemorySaver()


graph = StateGraph(state_schema=ChatState)

graph.add_node('chat_node',chat_node)
graph.add_node('tools',ToolNode(tools))


graph.add_edge(START,'chat_node')
graph.add_conditional_edges('chat_node',tools_condition)
graph.add_edge('tools','chat_node')
graph.add_edge('chat_node',END)


chatbot = graph.compile(checkpointer=checkpointer)





