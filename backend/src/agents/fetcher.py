from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from prompts.fetcher import prompt_template
from langgraph.prebuilt import ToolNode
from tools.stock import fetch_index_tickers, fetch_stock_history_data, fetch_fundamental_data_and_news
from tools.analysis import initial_filter
import logging

logger = logging.getLogger(__name__)


# Define model
model = init_chat_model(
    "gemma4:e4b",
    temperature=0,
    model_provider="ollama",
)
# Set prompt
prompt = ChatPromptTemplate.from_messages([
    ("system",prompt_template),
    MessagesPlaceholder(variable_name="messages")
                                      ])

# Define tool node
tools = [fetch_index_tickers, fetch_stock_history_data, fetch_fundamental_data_and_news, initial_filter]

tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = prompt | model.bind_tools(tools) | StrOutputParser()
tool_node = ToolNode(tools)

# Define model node
def fetcher_node(state):
    """Fetcher fetches data from the web"""
    logger.info(
        "fetcher_node: in (messages=%d, fetched=%s)",
        len(state.get("messages", [])),
        bool(state.get("fetched_data")),
    )
    response = model_with_tools.invoke(state["messages"])
    rpreview = response if isinstance(response, str) else repr(response)[:200]
    logger.info("fetcher_node: out preview=%r", rpreview[:400])
    return {
        "messages": [response],
        "fetched_data": {"completed": True},
    }
    

