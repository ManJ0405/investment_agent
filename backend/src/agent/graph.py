from typing import Dict, Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, MessagesState, add_messages, END
from urllib3 import response
from langchain.messages import AnyMessage, SystemMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from IPython.display import Image, display
from langserve import add_routes
from fastapi import FastAPI
from agents.supervisor import supervisor_node
from agents.fetcher import fetcher_node
from agents.analyzer import analyzer_node
from agent.state import AgentState


memory = MemorySaver() 


# Define logic to determine whether to end
# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END

# Step 6: Build agent

# Build workflow
agent_builder = StateGraph(state_schema=AgentState)

# Add nodes
agent_builder.add_node("supervisor_node", supervisor_node)
agent_builder.add_node("fetcher_node", fetcher_node)
agent_builder.add_node("analyzer_node", analyzer_node)


# Add edges to connect nodes
agent_builder.add_edge(START, "supervisor_node")
agent_builder.add_conditional_edges(
    "supervisor_node",
    lambda state: state["next"],
    {
        "fetcher": "fetcher_node",
        "analyzer": "analyzer_node",
       # "reporter": "reporter",
        "FINISH": END
    }
)
agent_builder.add_edge("fetcher_node", "supervisor_node")
agent_builder.add_edge("analyzer_node", "supervisor_node")

# Compile the agent
agent = agent_builder.compile()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces")

add_routes(app, agent, path="/agent")

