from langchain.tools import tool
from yahooquery import Ticker
from ..schemas.ticker_schema import TickerListInput, Ohlcv_input, validate_ticker_tool
from typing import Dict, List
import pandas as pd
import pandas_ta as ta
import logging

logger = logging.getLogger(__name__)


@tool(args_schema=TickerListInput)
@validate_ticker_tool(schema_class=TickerListInput)
def initial_filter(tickers: List[str]) -> List[str]:
    """
    When there is too many stocks to analyze when user ask for recommendation, this tool can filter out good stock by P/E, ROE and growth rate.
    Arg:
        tickers: list[str] - A list of tickers to filter.
    Returns:
        list[str] - filtered stocks.
    """
    
    try:
        logger.info(f'Filtering tickers...')
        filtered_tickers = {}
        df={}
        tk = Ticker(tickers)
        
        modules = ['summaryDetail', 'financialData', 'balanceSheetHistory', 'cashflowStatementHistory']
        all_data = tk.get_modules(modules)

        records = []
        
        for ticker in tickers:
            info = all_data.get(ticker)
    
            # check dict, if str then skip
            if not isinstance(info, dict):
                logger.info(f"Skipping {ticker}: data is {type(info)} - {info}")
                continue
    
            try:
                # trailingPE 
                trailing_pe = info.get('summaryDetail', {}).get('trailingPE')
            
                # use roe from financialData（stable）
                fin_data = info.get('financialData', {})
                roe = fin_data.get('returnOnEquity') 
            
                # if no, calulate
                if roe is None:
                    bs_hist = info.get('balanceSheetHistory', {}).get('balanceSheetStatementHistory', [])
                    cf_hist = info.get('cashflowStatementHistory', {}).get('cashflowStatements', [])
                    if bs_hist and cf_hist:
                        latest_bs = bs_hist[0]
                        latest_cf = cf_hist[0]
                        net_income = latest_cf.get('netIncome')
                        equity = latest_bs.get('totalStockholderEquity')
                        if equity and equity != 0:
                            roe = (net_income / equity) if net_income else None
                        else:
                            roe = None
        
                # quarterly YoY
                earnings_growth = fin_data.get('earningsGrowth')
                revenue_growth = fin_data.get('revenueGrowth')
                
                row = {
                    "Ticker": ticker,
                    "trailingPE": trailing_pe,
                    "ROE": roe*100,
                    "earningsGrowth(%)": earnings_growth * 100 if earnings_growth is not None else None,
                    "revenueGrowth(%)": revenue_growth * 100 if revenue_growth is not None else None
                }
                records.append(row)
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {e}")
                continue

        df = pd.DataFrame(records)

        # check data(for debug)
        logger.info(f"Total valid rows:", len(df.dropna(subset=['trailingPE', 'ROE'])))
        logger.info(df.head(10)) 

        # filter
        filtered = df[
            (df['trailingPE'].notna()) & (df['trailingPE'] < 25) &
            (df['ROE'].notna()) & (df['ROE'] > 12) &
            (df['earningsGrowth(%)'].notna()) & (df['earningsGrowth(%)'] > 3) &
            (df['revenueGrowth(%)'].notna()) & (df['revenueGrowth(%)'] > 3)
        ].sort_values('ROE', ascending=False)

        
        
        
        # top 30 tickers
        filtered_tickers = filtered['Ticker'].head(30).tolist()
        logger.info(f'Filtered tickers')            
        return filtered_tickers
    except Exception as e:
        logger.error(f'Error filtering tickers: {str(e)}')
        return []

@tool(args_schema=Ohlcv_input)
@validate_ticker_tool(schema_class=Ohlcv_input)
def trend_follow(tickers: List[str], ohlcv: Dict) -> Dict:
    """
    Fetch trend for a list of stocks by getting its sma50, sma100, ema12, ema26, and macd
    Arg:
        tickers: list[str] - A list of tickers to find its trend.
        ohlcv: dict - A dictionary of tickers which including its ohlcv.
    Return:
        dict - Simple and lastest indicators for analysis
    """
    try:
        logger.info(f'Fetching trend for tickers...')
        result = {}
        for ticker in tickers:
            try:
                df = ohlcv.get(ticker)  
                if not isinstance(df, pd.DataFrame):
                    df = pd.DataFrame(df)
                    
                close = df['Close']
                
                sma50_latest = ta.sma(close, length=50).iloc[-1] if len(close) >= 50 else None
                sma100_latest = ta.sma(close, length=100).iloc[-1] if len(close) >= 100 else None
                ema12_latest = ta.ema(close, length=12).iloc[-1] if len(close) >= 12 else None
                ema26_latest = ta.ema(close, length=26).iloc[-1] if len(close) >= 26 else None
                
                
                macd_df = ta.macd(close)
                macd_latest = macd_df['MACD_12_26_9'].iloc[-1] if macd_df is not None else None
                
                result={
                    "Ticker": ticker,
                    "SMA50_lastest": sma50_latest.item(),
                    "SMA_100_lastest": sma100_latest.item(),
                    "EMA_12_lastest": ema12_latest.item(),
                    "EMA_26_lastest": ema26_latest.item(),
                    "MACD_lastest": macd_latest.item()
                }
            except Exception as e:
                result[ticker] = {"error": str(e)}
                
        logger.info(f'Fetched trend')    
        return result
    except Exception as e:
        logger.error(f'Error fetching trend: {e}')
        return {}

@tool(args_schema=Ohlcv_input)
@validate_ticker_tool(schema_class=Ohlcv_input)
def mean_reversion(tickers: List[str], ohlcv: Dict) -> Dict:
    """
    Fetch mean reversion for a list of stocks by getting its RSI and Bollinger Bands
    Arg:
        tickers: list[str] - A list of tickers to get mean reversion.
        ohlcv: dict - A dictionary of tickers which including its ohlcv.
    Return:
        dict - RSI and Bollinger Bands for analysis
    """
    try:
        logger.info(f'Fetch mean reversion for tickers...')
        result = {}
        for ticker in tickers:
            try:
                df = ohlcv.get(ticker)  
                if not isinstance(df, pd.DataFrame):
                    df = pd.DataFrame(df)
                    
                close = df['Close']
                
                rsi_latest = ta.rsi(close, length=14).iloc[-1]
                bbands_latest = ta.bbands(close, length=20).iloc[-1]

                
                
                
                result={
                    "Ticker": ticker,
                    "RSI": rsi_latest.item(),
                    "Bollinger Bands": {
                        "BB_Lower": bbands_latest.get('BBL_20_2.0_2.0').item(),
                        "BB_Mid": bbands_latest.get('BBM_20_2.0_2.0').item(),
                        "BB_Upper": bbands_latest.get('BBU_20_2.0_2.0').item(),
                        "BB_Width": bbands_latest.get('BBB_20_2.0_2.0').item(),
                        "BB_Percent": bbands_latest.get('BBP_20_2.0_2.0').item(),
                        } 
                    }
            except Exception as e:
                result[ticker] = {"error": str(e)}
                
        logger.info(f'Fetched mean reversion for tickers')    
        return result
    except Exception as e:
        logger.error(f'Error fetching trend: {e}')
        return {}