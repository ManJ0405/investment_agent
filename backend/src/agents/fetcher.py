import logging
import re

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import ToolNode
from prompts.fetcher import prompt_template
from tools.analysis import initial_filter
from tools.stock import (
    fetch_fundamental_data_and_news,
    fetch_index_tickers,
    fetch_stock_history_data,
)

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 4

# Common uppercase words that are not tickers.
_NON_TICKERS = frozenset(
    {
        "A", "AI", "AM", "AN", "AND", "ARE", "AS", "AT", "BE", "BY", "CAN", "DO",
        "FOR", "HI", "HK", "I", "IF", "IN", "IS", "IT", "ME", "MY", "NO", "NOT",
        "OF", "OK", "ON", "OR", "PM", "SO", "THE", "TO", "US", "WE", "YOU",
        "WANT", "KNOW", "BUY", "WHEN", "WHAT", "SHOULD",
    }
)

model = init_chat_model(
    "gemma4:e4b",
    temperature=0,
    model_provider="ollama",
)

prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_template),
    MessagesPlaceholder(variable_name="messages"),
])

ALL_FETCHER_TOOLS = [
    fetch_index_tickers,
    fetch_stock_history_data,
    fetch_fundamental_data_and_news,
    initial_filter,
]
SINGLE_TICKER_TOOLS = [
    fetch_stock_history_data,
    fetch_fundamental_data_and_news,
]


def _extract_tickers(text: str) -> list[str]:
    """Pull likely ticker symbols from the latest user message."""
    if not text:
        return []

    candidates: list[str] = []
    # Keep original casing to avoid converting all words to uppercase tokens.
    for match in re.finditer(r"\b([A-Za-z]{1,5}\.[A-Za-z]{1,3})\b", text):
        symbol = match.group(1).upper()
        if symbol not in _NON_TICKERS:
            candidates.append(symbol)
    for match in re.finditer(r"\b([A-Z]{2,5})\b", text):
        symbol = match.group(1).upper()
        if symbol not in _NON_TICKERS:
            candidates.append(symbol)

    # Preserve order, drop duplicates.
    return list(dict.fromkeys(candidates))


def _last_human_message(messages) -> str:
    for message in reversed(messages):
        if getattr(message, "type", None) == "human":
            return message.content or ""
    return ""


def fetcher_node(state):
    """Fetcher fetches data from the web."""
    logger.info(
        "fetcher_node: in (messages=%d, fetched=%s)",
        len(state.get("messages", [])),
        bool(state.get("fetched_data")),
    )

    base_messages = list(state["messages"])
    user_text = _last_human_message(base_messages)
    tickers = _extract_tickers(user_text)

    if tickers:
        logger.info("fetcher_node: scoped to explicit tickers %s", tickers)
        price_result = fetch_stock_history_data.invoke(
            {"tickers": tickers, "period": "6mo", "interval": "1d"}
        )
        fundamentals_result = fetch_fundamental_data_and_news.invoke({"tickers": tickers})
        price_data = price_result.get("data", {}) if isinstance(price_result, dict) else {}
        fundamentals_data = fundamentals_result.get("data", []) if isinstance(fundamentals_result, dict) else []

        valid_tickers = []
        for ticker in tickers:
            rows = price_data.get(ticker)
            if isinstance(rows, list) and rows:
                valid_tickers.append(ticker)

        summary = (
            f"Fetched market data for {', '.join(valid_tickers or tickers)}. "
            "Collected OHLCV and fundamentals/news for downstream analysis."
        )
        return {
            "messages": [AIMessage(content=summary)],
            "fetched_data": {
                "completed": True,
                "tickers": valid_tickers or tickers,
                "ohlcv": price_data,
                "fundamentals": fundamentals_data,
            },
        }

    tools = ALL_FETCHER_TOOLS
    hint = None

    fetcher_chain = prompt | model.bind_tools(tools)
    tool_node = ToolNode(tools)

    new_messages = []
    invoke_messages = base_messages + ([hint] if hint else [])

    ai_msg = fetcher_chain.invoke({"messages": invoke_messages + new_messages})
    new_messages.append(ai_msg)

    for _ in range(MAX_TOOL_ROUNDS):
        if not getattr(ai_msg, "tool_calls", None):
            break
        tool_out = tool_node.invoke({"messages": invoke_messages + new_messages})
        new_messages.extend(tool_out["messages"])
        ai_msg = fetcher_chain.invoke({"messages": invoke_messages + new_messages})
        new_messages.append(ai_msg)

    logger.info("fetcher_node: completed with %d new messages", len(new_messages))
    return {
        "messages": new_messages,
        "fetched_data": {"completed": True, "tickers": tickers or None},
    }
