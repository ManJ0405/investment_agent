import logging

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.state import AgentState
from prompts.responder import prompt_template

logger = logging.getLogger(__name__)

model = init_chat_model(
    "gemma4:e4b",
    temperature=0,
    model_provider="ollama",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt_template),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

responder_chain = prompt | model


def _fmt_num(value, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "N/A"


def _build_evidence_reply(state: AgentState) -> str | None:
    analysis = state.get("analysis_result") or {}
    per_ticker = analysis.get("per_ticker")
    if not isinstance(per_ticker, dict) or not per_ticker:
        return None

    lines = ["Here is the full analysis with real evidence from fetched data:"]
    for ticker, data in per_ticker.items():
        p2 = data.get("pillar2") or {}
        mean_rev = data.get("mean_reversion") or {}
        funda = data.get("latest_fundamental") or {}
        p2_evidence = p2.get("evidence") or {}

        signal = p2.get("signal", "N/A")
        score = _fmt_num(p2.get("score"))
        conf = _fmt_num(p2.get("confidence"))
        close = _fmt_num(data.get("latest_close"))
        rsi = _fmt_num(mean_rev.get("RSI"))
        adx = _fmt_num(p2_evidence.get("adx_14"))
        ema_spread = _fmt_num(p2_evidence.get("ema_spread_ratio"), 4)
        revenue = _fmt_num(funda.get("TotalRevenue"), 0)
        net_income = _fmt_num(funda.get("NetIncome"), 0)
        news_count = data.get("news_count", 0)

        if signal == "bullish":
            timing = "consider pullback entries near EMA support rather than chasing breakouts"
        elif signal == "bearish":
            timing = "wait for trend stabilization or reversal confirmation before entry"
        else:
            timing = "wait for clearer direction; avoid oversized positions"

        lines.extend(
            [
                "",
                f"### {ticker}",
                f"- Last close: {close}",
                f"- Pillar2 trend signal: `{signal}` (score {score}/100, confidence {conf})",
                f"- Technical evidence: ADX={adx}, EMA spread ratio={ema_spread}, RSI={rsi}",
                f"- Fundamental snapshot (latest): Revenue={revenue}, NetIncome={net_income}",
                f"- News items fetched: {news_count}",
                f"- Timing view: {timing}.",
            ]
        )

    lines.extend(
        [
            "",
            "This is analysis, not financial advice. Manage risk with position sizing and stop-loss rules.",
        ]
    )
    return "\n".join(lines)


def responder_node(state: AgentState) -> dict:
    """Generate the final user-facing answer."""
    logger.info("responder_node: composing final reply")
    evidence_reply = _build_evidence_reply(state)
    if evidence_reply:
        return {"messages": [AIMessage(content=evidence_reply)]}

    response = responder_chain.invoke({"messages": state["messages"]})
    if isinstance(response, AIMessage):
        return {"messages": [response]}
    return {"messages": [AIMessage(content=str(response))]}
