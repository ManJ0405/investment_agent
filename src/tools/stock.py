from langchain.tools import tool
from pytickersymbols import PyTickerSymbols
from yahooquery import Ticker
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

@tool
def fetch_index_tickers_HK() -> list[str]:
    """
    Fetch list of tickers for HSI indices(HK) via web scraping from wiki
    """
    try:
        logger.info(f'Fetching HSI tickers...')
        url = 'https://zh.wikipedia.org/wiki/%E6%81%92%E7%94%9F%E6%8C%87%E6%95%B8#%E6%81%92%E7%94%9F%E6%8C%87%E6%95%B8%E6%88%90%E4%BB%BD%E8%82%A1'
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        tables = soup.find_all('table', class_='wikitable')
        if not tables:
            logger.error("error: Cannot find constituent table on Wikipedia")
            
        tickers = []
        table = tables[8]

        for row in table.find_all("tr")[3:]:  # skip the 3 header rows
            cells = row.find_all("td")
            if not cells:
                continue

            code_cell = cells[0].get_text(strip=True) 
            code = "".join(ch for ch in code_cell if ch.isdigit())
            if not code:
                continue
            
            code_int = int(code)
            ticker = str(code_int).zfill(4) + ".HK"
            tickers.append(ticker)

        logger.info(f'Fetched HSI tickers: {len(tickers), tickers[:10]}')
        return tickers
    except Exception as e:
        logger.error(f"Error fetching HSI tickers: {e}")
        return []
    
@tool
def fetch_index_tickers_US_EU(index: str) -> list[str]:
    """
    fetch list of tickers for major indices (US/EU).
    Supported(The input index shoudld be same as follow): 
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
    """
    try:
        tickers = []
        stock_data = PyTickerSymbols()
        logger.info(f'Fetching {index} tickers...')
        stock_info = stock_data.get_stocks_by_index(index)
        for item in stock_info:
            tickers.append(item['symbol'])

        return tickers
            
            
    except Exception as e:
        logger.error(f"Error fetching {index} tickers: {e}")
        return []

@tool
def fetch_stock_history_data(tickers: list[str], period: str = "6mo", interval: str = "1d") -> dict:
    """
    Fetch stock history data for a list of tickers, if only one ticker is provided, return the data for that ticker and if no tickers are provided, return the data for all tickers.
    Args:
        tickers: list[str] - A list of tickers to fetch data for.
        period: str - The period to fetch data for(1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
        interval: str - The interval to fetch data for(1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
    Returns:
        dict - A dictionary containing the stock history data for each ticker.
    """
    try:
        logger.info(f'Fetching OHLCV...')
        if not tickers:
            return f"Error: No tickers provided"
        if len(tickers) > 30:
            logger.info(f"Fetching stock history data for {len(tickers)} tickers, reducing to 30")
            tickers = tickers[:30]
            
        data = yf.download(
            tickers,
            period=period,
            interval=interval,
            group_by='ticker',
            auto_adjust=False, 
            progress=False      
        )
        
        result = {}
        for ticker in tickers:
            try:
                result[ticker] = data[ticker]
            except KeyError:
                result[ticker] = {"error": f"No data for {ticker}"}
        
        return result
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return {}
    
@tool
def fetch_stock_news(tickers: list[str]) -> dict:
    """
    Fetch stock news for a list of tickers(use to provide some insight for stock analysis, limit to 5), if only one ticker is provided, return the news for that ticker and if no tickers are provided, return the news for all tickers.
    Args:
        tickers: list[str] - A list of tickers to fetch news for.
    Returns:
        dict - A list of dictionaries containing the stock news for each ticker.
    """
    try:
        logger.info(f'Fetching stock news...')
        for ticker in tickers[:10]:
            t = yf.Ticker(ticker)
            news = t.news
        return news
    except Exception as e:
        logger.error(f"Error fetching stock news: {e}")
        return {}
    
@tool
def fetch_fundamental_data(symbol_list: list[str]) -> list[dict]:
    """
    Fetch fundamental data including balance sheet, cash flow and income statement, will merage together for analysis.
    Args:
        symbol_list: str - stock code.
    Returns:
        list[dict] - A list of dictionaries containing balance sheet, cash flow and income statement.
    """
    try:
        logger.info(f'Fetching fundamental data...')
        tickers = Ticker(symbol_list)
    
        bs = tickers.balance_sheet(frequency='a')
        cf = tickers.cash_flow(frequency='a')
        is_ = tickers.income_statement(frequency='a')
        
        
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
        merged_sorted = merged.sort_values(['symbol', 'asOfDate', 'periodType'], ascending=[True, False, True])
        financials_data = merged_sorted.to_dict(orient='records')
        
        return financials_data
    
    except Exception as e:
        logger.error(f'Error fetching fundamential data: {e}')
        return
    
#test
#result_1 = get_index_tickers_US_EU.invoke("S&P 500")
# result_2 = fetch_stock_history_data.invoke({
#     "tickers": ["0700.HK", "0005.HK"],
#     "period": "1d"
# })
# #result_3 = fetch_stock_news.invoke({"tickers": ["0700.HK", "0005.HK"]})
#result_4 = fetch_fundamental_data.invoke({"symbol_list": ["0700.HK",  "0005.HK"]})
#result_5 = fetch_index_tickers_HK.invoke({})

# print(result_1)
# if isinstance(result_1, list):
#     print("It's a list!")
# print(result_2) 
#print(result_3) successed
#print(result_4)
#print(result_5)


#result_4 ouput: 
#[{'symbol': '0005.HK', 
# 'asOfDate': Timestamp('2024-12-31 00:00:00'), 
# 'periodType': '12M', 
# 'TotalAssets': 3017048000000.0, 
# 'TotalLiabilitiesNetMinorityInterest': 2824775000000.0, 
# 'StockholdersEquity': 184973000000.0, 
# 'TotalRevenue': 67396000000.0, 
# 'GrossProfit': nan, 
# 'OperatingIncome': nan, 
# 'NetIncome': 23979000000.0, 
# 'OperatingCashFlow': 65305000000.0, 
# 'CapitalExpenditure': -3886000000.0, 
# 'FinancingCashFlow': -26459000000.0}, 
# {'symbol': '0005.HK', 
# 'asOfDate': Timestamp('2023-12-31 00:00:00'), 
# 'periodType': '12M', 
# 'TotalAssets': 3038677000000.0, 
# 'TotalLiabilitiesNetMinorityInterest': 2846067000000.0, 
# 'StockholdersEquity': 185329000000.0, 
# 'TotalRevenue': 64440000000.0, 
# 'GrossProfit': nan, 
# 'OperatingIncome': nan, 
# 'NetIncome': 23533000000.0, 
# 'OperatingCashFlow': 39111000000.0, 
# 'CapitalExpenditure': -3695000000.0, 
# 'FinancingCashFlow': -17558000000.0}, 
# {'symbol': '0005.HK', 
# 'asOfDate': Timestamp('2022-12-31 00:00:00'), 
# 'periodType': '12M', 
# 'TotalAssets': 2949286000000.0, 
# 'TotalLiabilitiesNetMinorityInterest': 2764089000000.0, 
# 'StockholdersEquity': 177833000000.0, 
# 'TotalRevenue': 53719000000.0, 
# 'GrossProfit': nan, 
# 'OperatingIncome': nan, 
# 'NetIncome': 15559000000.0, 
# 'OperatingCashFlow': 19355000000.0, 
# 'CapitalExpenditure': -4409000000.0, 
# 'FinancingCashFlow': -6286000000.0}, {'symbol': '0005.HK', 'asOfDate': Timestamp('2021-12-31 00:00:00'), 'periodType': '12M', 'TotalAssets': 2957939000000.0, 'TotalLiabilitiesNetMinorityInterest': 2751162000000.0, 'StockholdersEquity': 198250000000.0, 'TotalRevenue': 64247000000.0, 'GrossProfit': nan, 'OperatingIncome': nan, 'NetIncome': 13917000000.0, 'OperatingCashFlow': 104312000000.0, 'CapitalExpenditure': -3565000000.0, 'FinancingCashFlow': -10794000000.0}, {'symbol': '0700.HK', 'asOfDate': Timestamp('2024-12-31 00:00:00'), 'periodType': '12M', 'TotalAssets': 1780995000000.0, 'TotalLiabilitiesNetMinorityInterest': 727099000000.0, 'StockholdersEquity': 973548000000.0, 'TotalRevenue': 660257000000.0, 'GrossProfit': 349246000000.0, 'OperatingIncome': 208786000000.0, 'NetIncome': 194073000000.0, 'OperatingCashFlow': 258521000000.0, 'CapitalExpenditure': -96048000000.0, 'FinancingCashFlow': -176494000000.0}, {'symbol': '0700.HK', 'asOfDate': Timestamp('2023-12-31 00:00:00'), 'periodType': '12M', 'TotalAssets': 1577246000000.0, 'TotalLiabilitiesNetMinorityInterest': 703565000000.0, 'StockholdersEquity': 808591000000.0, 'TotalRevenue': 609015000000.0, 'GrossProfit': 293109000000.0, 'OperatingIncome': 165658000000.0, 'NetIncome': 115216000000.0, 'OperatingCashFlow': 221962000000.0, 'CapitalExpenditure': -47407000000.0, 'FinancingCashFlow': -82573000000.0}, {'symbol': '0700.HK', 'asOfDate': Timestamp('2022-12-31 00:00:00'), 'periodType': '12M', 'TotalAssets': 1578131000000.0, 'TotalLiabilitiesNetMinorityInterest': 795271000000.0, 'StockholdersEquity': 721391000000.0, 'TotalRevenue': 554552000000.0, 'GrossProfit': 238746000000.0, 'OperatingIncome': 113940000000.0, 'NetIncome': 188243000000.0, 'OperatingCashFlow': 146091000000.0, 'CapitalExpenditure': -50850000000.0, 'FinancingCashFlow': -59953000000.0}, {'symbol': '0700.HK', 'asOfDate': Timestamp('2021-12-31 00:00:00'), 'periodType': '12M', 'TotalAssets': 1612364000000.0, 'TotalLiabilitiesNetMinorityInterest': 735671000000.0, 'StockholdersEquity': 806299000000.0, 'TotalRevenue': 560118000000.0, 'GrossProfit': 245944000000.0, 'OperatingIncome': 122341000000.0, 'NetIncome': 224822000000.0, 'OperatingCashFlow': 175186000000.0, 'CapitalExpenditure': -62165000000.0, 'FinancingCashFlow': 21620000000.0}]