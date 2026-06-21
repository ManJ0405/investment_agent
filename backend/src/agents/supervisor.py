import logging
import re

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from prompts.supervisor import prompt_template
from langgraph.prebuilt import ToolNode
from agent.state import AgentState

logger = logging.getLogger(__name__)

_VALID_NEXT = frozenset({"fetcher", "analyzer", "FINISH"})


def _normalize_supervisor_route(raw: str) -> str:
    """Map free-form LLM output to LangGraph conditional-edge keys."""
    text = (raw or "").strip()
    if not text:
        return "FINISH"

    first = text.splitlines()[0].strip().strip('`"\'')
    if first.upper() == "FINISH" or first.lower() == "finish":
        return "FINISH"
    low = first.lower()
    if low == "fetcher":
        return "fetcher"
    if low in ("analyzer", "analyser"):
        return "analyzer"

    m = re.search(r"\b(fetcher|analyzer|analyser|FINISH)\b", text, re.IGNORECASE)
    if m:
        tok = m.group(1).lower()
        if tok == "analyser":
            return "analyzer"
        if tok == "finish":
            return "FINISH"
        return tok

    if re.search(r"\bfetcher\s*\(", text, re.IGNORECASE):
        return "fetcher"
    if re.search(r"\banaly[sz]er\s*\(", text, re.IGNORECASE):
        return "analyzer"

    logger.warning(
        "Supervisor returned non-routing text; defaulting to FINISH. First 200 chars: %r",
        text[:200],
    )
    return "FINISH"


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



model_with_tools = prompt | model | StrOutputParser()


# Define model node
def supervisor_node(state: AgentState):
    """Supervisor decides whether to call other agents or not, and return the result"""
    if state.get("analysis_result"):
        return {"next": "FINISH"}

    summary = ""
    if state.get("fetched_data"):
        summary += "Data has been fetched.\n"
    if state.get("analysis_result"):
        summary += "Analysis has been performed.\n"

    last_user_msg = next((m.content for m in reversed(state["messages"]) if m.type == "human"), "")

    raw = model_with_tools.invoke({
        "query": last_user_msg,
        "state_summary": summary,
        "messages": state["messages"],
    }).strip()

    decision = _normalize_supervisor_route(raw)
    if decision not in _VALID_NEXT:
        logger.warning("Unexpected route %r; forcing FINISH", decision)
        decision = "FINISH"

    has_fetch = bool(state.get("fetched_data"))

    if has_fetch:
        if decision == "fetcher":
            logger.info("Overriding supervisor route fetcher→analyzer (fetch stage already completed)")
            decision = "analyzer"
        elif decision == "FINISH":
            logger.info("Overriding supervisor route FINISH→analyzer (analysis still pending)")
            decision = "analyzer"
    elif not has_fetch and decision == "analyzer":
        logger.info("Overriding supervisor route analyzer→fetcher (no data yet)")
        decision = "fetcher"

    logger.info("Supervisor → next=%s (raw was %r)", decision, raw[:300] if raw else "")
    return {"next": decision}
    

