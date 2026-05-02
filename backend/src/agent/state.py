from typing_extensions import TypedDict, Annotated
from langchain.messages import AnyMessage
from langgraph.graph import add_messages
from typing import Optional


# Define state
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    llm_calls: int
    query: str
    tickers: list[dict]
    indicators: str
    fetched_data: Optional[dict]           # raw data from fetcher
    fetched_news: Optional[dict]           # raw news data from fetcher
    analysis_result: Optional[dict]        # structured analysis output
    report_content: Optional[str]          # markdown or final text