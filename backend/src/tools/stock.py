from langchain.tools import tool
from pytickersymbols import PyTickerSymbols
from yahooquery import Ticker
from datetime import datetime
import yfinance as yf
import pandas as pd
try:
    import psycopg
except ModuleNotFoundError:  # pragma: no cover - optional local dependency path
    psycopg = None
from src.schemas.ticker_schema import IndexConstituentsInput, HistoricalPriceInput,TickerListInput, validate_historical_prices, validate_ticker_tool
from typing import List, Dict, Any
import logging
import os
import sys
logger = logging.getLogger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from db.init_db import make_dsn


def _load_hk_index_tickers_from_csv(index: str) -> list[str]:
    csv_path = os.path.join(project_root, "db", "data", "HSI.csv")
    if not os.path.exists(csv_path):
        logger.warning("HK index fallback CSV not found at %s", csv_path)
        return []
    try:
        frame = pd.read_csv(csv_path)
        subset = frame[frame["index_name"].astype(str).str.upper() == index]
        tickers = subset["ticker"].dropna().astype(str).str.strip().tolist()
        return tickers
    except Exception as e:
        logger.warning("Failed to read HK fallback CSV: %s", e)
        return []


def _normalize_column_name(column: Any, ticker: str) -> str:
    """Convert pandas column labels (including MultiIndex tuples) to plain strings."""
    if isinstance(column, tuple):
        parts = [str(p) for p in column if p not in ("", None)]
        if not parts:
            return "value"
        # yfinance can include ticker as one MultiIndex level.
        filtered = [p for p in parts if p != ticker]
        if filtered:
            parts = filtered
        return parts[-1]
    if column is None:
        return "value"
    return str(column)


def _history_records_for_ticker(data: pd.DataFrame, ticker: str, multi_ticker: bool) -> list[dict[str, Any]]:
    """Return normalized OHLCV records with string keys for one ticker."""
    frame = data[ticker] if multi_ticker else data
    if frame is None or frame.empty:
        return []

    normalized = frame.copy()
    if isinstance(normalized.columns, pd.MultiIndex):
        normalized.columns = [_normalize_column_name(c, ticker) for c in normalized.columns]

    normalized = normalized.reset_index()
    normalized.columns = [_normalize_column_name(c, ticker) for c in normalized.columns]

    # Keep key naming stable for downstream schemas/tools.
    rename_map = {}
    for col in normalized.columns:
        low = col.lower()
        if low in {"datetime", "date", "index"}:
            rename_map[col] = "Date"
        elif low == "open":
            rename_map[col] = "Open"
        elif low == "high":
            rename_map[col] = "High"
        elif low == "low":
            rename_map[col] = "Low"
        elif low == "close":
            rename_map[col] = "Close"
        elif low in {"adj close", "adj_close"}:
            rename_map[col] = "Adj Close"
        elif low == "volume":
            rename_map[col] = "Volume"
    normalized = normalized.rename(columns=rename_map)
    return normalized.to_dict(orient="records")

@tool(args_schema=IndexConstituentsInput)
@validate_ticker_tool(schema_class=IndexConstituentsInput)    
def fetch_index_tickers(index: str) -> list[str]:
    """
    Fetch list of tickers for a given index.
    A index name for fetching its constituents, must be one of these:
            AEX
            BEL 20
            CAC 40
            CAC MID 60
            DAX
            DOW JONES
            EURO STOXX 50
            FTSE 100
            IBEX 35
            MDAX
            NASDAQ 100
            OMX Helsinki 25
            OMX Stockholm 30
            S&P 100
            S&P 500
            S&P 600
            SDAX
            Switzerland 20
            TECDAX
            HSI
            HSTECH
    Arg:
        index: str - A index name for fetching its constituents.
    Returns:
        list[str] - A list of tickers for the given index.
    """
    try:
        logger.info(f'Fetching {index} tickers...')
        tickers = []
        if index == "HSI" or index == "HSTECH":
            if psycopg is not None:
                try:
                    sql = "SELECT ticker FROM constituents WHERE index_name = %s"
                    dsn = make_dsn()
                    with psycopg.connect(dsn) as conn:
                        with conn.cursor() as cur:
                            cur.execute(sql, (index,))
                            result = cur.fetchall()
                            for row in result:
                                tickers.append(row[0])
                except Exception as e:
                    logger.warning(
                        "DB fetch for %s failed (%s), fallback to local CSV",
                        index,
                        e,
                    )
                    tickers = _load_hk_index_tickers_from_csv(index)
            else:
                tickers = _load_hk_index_tickers_from_csv(index)
        else:
            stock_data = PyTickerSymbols()
            logger.info(f'Fetching {index} tickers...')
            stock_info = stock_data.get_stocks_by_index(index)
            for item in stock_info:
                tickers.append(item['symbol'])

        return tickers
    except Exception as e:
        logger.error(f"Error fetching {index} tickers: {e}")
        return []
    

@tool(args_schema=HistoricalPriceInput)
@validate_ticker_tool(schema_class=HistoricalPriceInput,extra_validation=validate_historical_prices)
def fetch_stock_history_data(tickers: List[str], period: str = "6mo", interval: str = "1d") -> Dict[str, Any]:
    """
    Fetch stock history data for a list of tickers, if only one ticker is provided, return the data for that ticker and if no tickers are provided, return the data for all tickers.
    This tool will provide ohlcv data of tickers.
    Suggest only fetch 20-30 tickers in one time.
    Arg:
        tickers: list[str] - A list of tickers to fetch history data.
        period: str - The period to fetch data, available: (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: str - The interval of K-line, available: (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    Returns:
        Dict[str, Any] - A dictionary of ticker and its history data.
    """
    try:
        logger.info(f'Fetching OHLCV...')
            
        data = yf.download(
            tickers,
            period=period,
            interval=interval,
            group_by='ticker',
            auto_adjust=False, 
            progress=False      
        )
        
        result = {}
        multi_ticker = len(tickers) > 1
        for ticker in tickers:
            try:
                result[ticker] = _history_records_for_ticker(data, ticker, multi_ticker)
            except KeyError:
                result[ticker] = {"error": f"No data for {ticker}"}
        
        return result
    except Exception as e:
        raise RuntimeError(f"Fail to download from yfinance: {str(e)}")
    
    
@tool(args_schema=TickerListInput)
@validate_ticker_tool(schema_class=TickerListInput)
def fetch_fundamental_data_and_news(tickers: list[str]) -> list[dict]:
    """
    Fetch fundamental data and news including balance sheet, cash flow and income statement, will merage together for analysis.
    Each ticker can get at most 5 news
    Arg:
        tickers: list[str] - A list of tickers to fetch fundamental data and news.
    Returns:
        list[dict] - A list of fundamental data and news for the given tickers.
    """
    try:
        logger.info(f'Fetching fundamental data and news...')
        result = []
        ticker = Ticker(tickers)
    
        bs = ticker.balance_sheet(frequency='a')
        cf = ticker.cash_flow(frequency='a')
        is_ = ticker.income_statement(frequency='a')
        
        # merge
        
        bs = bs.reset_index()
        cf = cf.reset_index()
        is_ = is_.reset_index()

        
        bs_keep = bs.filter(items = ['symbol', 'asOfDate', 'periodType', 'TotalAssets', 'TotalLiabilitiesNetMinorityInterest', 'StockholdersEquity'])
        is_keep = is_.filter(items = ['symbol', 'asOfDate', 'periodType', 'TotalRevenue', 'GrossProfit', 'OperatingIncome', 'NetIncome'])
        cf_keep = cf.filter(items = ['symbol', 'asOfDate', 'periodType', 'OperatingCashFlow', 'CapitalExpenditure', 'FinancingCashFlow'])

        merged = (
            bs_keep
            .merge(is_keep, on=['symbol', 'asOfDate', 'periodType'], how='left')
            .merge(cf_keep, on=['symbol', 'asOfDate', 'periodType'], how='left')
        )

        # Sort to show most recent (TTM/12M first)
        merged_sorted = merged.sort_values(['symbol', 'asOfDate'], ascending=[True, False])
        
        for t in tickers:
            item = {"ticker": t, "state": "success", "error": None}
            
            try:
                fundamental_data = merged_sorted[merged_sorted["symbol"] == t]
                
                data_list = []
                for _, row in fundamental_data.iterrows():
                    record = row.to_dict()
                    #  Timestamp → str
                    if pd.notnull(record.get('asOfDate')):
                        record['asOfDate'] = record['asOfDate'].strftime('%Y-%m-%d')
                    #  nan → None（
                    for key, value in record.items():
                        if pd.isna(value):
                            record[key] = None
                    data_list.append(record)
                    
                item["data"] = data_list   
                    
            except Exception as e:
                logger.warning(f'Fail to fetch fundamental data of {t}. ')
                item["data"] = []
                item["state"] = "partical"
                item["error"] = f'Fail to fetch fundamental data: str{e}'
            
            # fetch news
            try:    
                yf_ticker = yf.Ticker(t)
                news_raw = yf_ticker.news or []
                
                news_clean = []
                for new in news_raw[:5]:
                    content = new.get("content")
                    date = datetime.fromisoformat(content.get("pubDate").replace("Z", "+00:00"))
                    news_clean.append({
                        "title": content.get("title"),
                        "summary": content.get("summary"),
                        "pubDate": date.strftime('%Y-%m-%d'),
                    })
                    item["news"] = news_clean
            except Exception as e:
                logger.warning(f'Fail to fetch news for {t}.')
                item["news"] = []
                item["state"] = "partical" if item["state"] == "success" else "error"
                item["error"] = f'Fail to fetch news: str{e}'
                
            result.append(item)
            
            
        return result
    
    except Exception as e:
        logger.error(f'Error fetching fundamential data: {e}')
        return []