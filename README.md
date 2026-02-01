# Stock analysis agent

An intelligent investment analysis agent powered by LangGraph and Ollama (Llama 3.2), capable of fetching stock data, performing technical & fundamental analysis, and generating professional reports.

## Project Overview

This project is a **multi-tool, stateful AI agent** designed for stock market analysis. It can:
- Fetch real-time and historical stock data (HK, US, EU markets)
- Retrieve index constituents (e.g. Hang Seng, S&P 500)
- Perform technical analysis (trend following, mean reversion)
- Filter stocks based on P/E, ROE, growth rates
- Fetch news and fundamental data
- Generate detailed, data-driven reports with risk warnings

Built with **LangGraph** for agent orchestration, **Ollama** for local LLM, **yfinance**, **yahooquery**, **akshare**, and **pandas-ta** for data handling.

## Latest Update
- 01/02/2026: 
        - Merged fetch_stock_news and fetch_fundamental_data to fetch_fundamental_data_and_news (see src/tools/stock.py)
        - Merged fetch_index_tickers and fetch_index_tickers_US_EU to fetch_index_tickers (see src/tools/stock.py)
        - Add schemas for all tools (see src/schemas/ticker_schema.py)
        - Modified system prompt (see src/prompts/investment_agent.py)
        - Imporved tools call (see src/agent.py)
        - Connect to PostgreSQL for saving HSI and HSTECH tickers list (see db/)
- 20/01/2026: 
        - Uploaded an AI agent with base functions. (Tool: stock, analysis)

## Project Structure
```
.
├── src/                        # Contains processed data files
│   ├── chatroom/
|   |   ├── __init__.py
|   |   └── app.py              # Streamlit playground
│   ├── prompts/
|   |   ├── __init__.py
|   |   └── investment_agent.py # Prompts of agent
|   ├── tools/
|   |   ├── __init__.py
|   |   ├── analysis.py         # Technical analysis tools (trend_follow, mean_reversion, initial_filter)
|   |   ├── crypto.py           # Crypto data fetching (to be updated)
|   |   └── stock.py            # Stock tools (index tickers, history, news, fundamentals)
|   ├── __init__.py
|   └── agent.py                # LangGraph agent definition, nodes, edges
├── .env
├── langgraph.json              # configuration file for LangGraph
├── main.py                     # Entry point: pull model, terminal chat, Streamlit
├── README.md
└── requirements.txt            # package dependencies
```

## Requirements
- Python >= 3.12.3
- Ollama (local LLM server) → https://ollama.com
- Recommended model: `llama3.2:3b` (lightweight, good performance)
...

See `requirements.txt` for full package list.

## Installation
```bash
# Clone the repository
git clone https://github.com/ManJ0405/investment_agent.git
cd Agent

# Activate virual enviroment 
python -m venv myenv
source myenv/bin/activate   # Linux/macOS
myenv\Scripts\activate      # Windows

# Install required packages
pip install -r requirements.txt

# Run agent
python main.py run 
```

## Tools
- Analysis:
    - Stock filter
    - Trend follow
    - Mean reversion
- Stock:
    - Fetch index tickers
    - Fetch stock history data
    - Fetch stock news and fundamental data

## Future Improvements
- Add RAG
- Add more analysis method
- Train AI models for prediction

## License

## Author
ManJ0405


