from typing import Dict, Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, MessagesState, add_messages, END
from urllib3 import response
from tools.stock import fetch_fundamental_data_and_news, fetch_index_tickers, fetch_stock_history_data
from tools.analysis import initial_filter, trend_follow, mean_reversion
from prompts.investment_agent import prompt_template
from langchain.messages import AnyMessage, SystemMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from IPython.display import Image, display
from langserve import add_routes
from fastapi import FastAPI

# Define model
model = init_chat_model(
    "llama3.2:3b",
    temperature=0,
    model_provider="ollama",
)
# Set prompt
prompt = ChatPromptTemplate.from_messages([
    ("system",prompt_template),
    MessagesPlaceholder(variable_name="messages")
                                      ])

# Augment the LLM with tools
tools = [
    fetch_index_tickers,
    fetch_stock_history_data, 
    fetch_fundamental_data_and_news,
    initial_filter,
    trend_follow,
    mean_reversion
    ]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = prompt | model.bind_tools(tools)

# Define state
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    llm_calls: int
    query: str
    tickers: list[dict]
    indicators: str
    analysis: str
    scorce: dict
    new: str
    report: str

# Define model node
def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""
    response = model_with_tools.invoke(state["messages"])

    return {
        "messages": [response],
        "llm_calls": state.get('llm_calls', 0) + 1
    }
    
tool_node = ToolNode(tools)

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
agent_builder = StateGraph(state_schema=MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
memory = MemorySaver() 
agent = agent_builder.compile(checkpointer=memory)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces")

add_routes(app, agent, path="/agent")

