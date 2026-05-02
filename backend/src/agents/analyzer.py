from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from prompts.analyser import prompt_template
from langgraph.prebuilt import ToolNode
from tools.analysis import trend_follow, mean_reversion
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
tools = [trend_follow, mean_reversion]

tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = prompt | model.bind_tools(tools) | StrOutputParser()
tool_node = ToolNode(tools)

# Define model node
def analyzer_node(state):
    """Analyzer analyses data"""
    logger.info(
        "analyzer_node: in (messages=%d, has_analysis=%s)",
        len(state.get("messages", [])),
        bool(state.get("analysis_result")),
    )
    response = model_with_tools.invoke(state["messages"])
    rpreview = response if isinstance(response, str) else repr(response)[:200]
    logger.info("analyzer_node: out preview=%r", rpreview[:400])
    return {
        "messages": [response],
        "analysis_result": {"completed": True},
    }
    

