import pytest



from langchain.tools import tool
from .stock import fetch_index_tickers, fetch_stock_history_data, fetch_fundamental_data_and_news
from .analysis import initial_filter, trend_follow, mean_reversion


#stock test
# result_stock_1 = fetch_index_tickers.invoke({"index":"HSi"})
# result_stock_2 = fetch_stock_history_data.invoke({
#     "tickers": ["0700.HK", "0005.HK"],
#     "period": "1y",
#     "interval": "1d"
# })
# result_stock_3 = fetch_fundamental_data_and_news.invoke({"tickers": ["0700.HK",  "0005.HK"]})

# print(result_stock_1)
# print(result_stock_2) 
# print(result_stock_3) 

# result 3 ouput
# {'id': 'feba57b3-12ce-3056-b809-6266644f307c',
# 'content': {'id': 'feba57b3-12ce-3056-b809-6266644f307c',
# 'contentType': 'STORY',
# 'title': 'HSBC Just Doubled Its Price Target on Intel Stock. Should You Buy INTC Ahead of Earnings?',
# 'description': '',
# 'summary': 'Analysts sharp target hike puts Intel back in focus as AI-driven server demand builds ahead of earnings.',
# 'pubDate': '2026-01-22T15:46:56Z',
# 'displayTime': '2026-01-22T15:46:56Z',
# 'isHosted': True,
# 'bypassModal': False,
# 'previewUrl': None,
# 'thumbnail': {'originalUrl': 'https://media.zenfs.com/en/barchart_com_477/fa34ffabb30933c9de6fa5fe37361c9d',
# 'originalWidth': 1000,
# 'originalHeight': 667,
# 'caption': 'Intel Corp_ badge holder-by hasrul_rais via Shutterstock',
# 'resolutions': [{'url': 'https://s.yimg.com/uu/api/res/1.2/aSVlaBi5aiT2JYOFuAb9Dg--~B/aD02Njc7dz0xMDAwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/barchart_com_477/fa34ffabb30933c9de6fa5fe37361c9d',
# 'width': 1000,
# 'height': 667,
# 'tag': 'original'},
# {'url': 'https://s.yimg.com/uu/api/res/1.2/sQ3U.1079RdTspNtoJuYhQ--~B/Zmk9c3RyaW07aD0xMjg7dz0xNzA7YXBwaWQ9eXRhY2h5b24-/https://media.zenfs.com/en/barchart_com_477/fa34ffabb30933c9de6fa5fe37361c9d',
# 'width': 170, 'height': 128, 'tag': '170x128'}]},
# 'provider': {'displayName': 'Barchart', 'url': 'https://www.barchart.com/'},
# 'canonicalUrl': {'url': 'https://www.barchart.com/story/news/37176834/hsbc-just-doubled-its-price-target-on-intel-stock-should-you-buy-intc-ahead-of-earnings',
# 'site': 'finance', 'region': 'US', 'lang': 'en-US'},
# 'clickThroughUrl': {'url': 'https://finance.yahoo.com/news/hsbc-just-doubled-price-target-154656148.html',
# 'site': 'finance', 'region': 'US', 'lang': 'en-US'},
# 'metadata': {'editorsPick': False},
# 'finance': {'premiumFinance': {'isPremiumNews': False, 'isPremiumFreeNews': False}}, 'storyline': None}}


#result_4 ouput: 
# [
#     {'ticker': '0700.HK',
#      'state': 'success',
#      'error': None,
#      'data': [
#          {'symbol': '0700.HK', 'asOfDate': '2024-12-31', 'periodType': '12M', 'TotalAssets': 1780995000000.0, 'TotalLiabilitiesNetMinorityInterest': 727099000000.0, 'StockholdersEquity': 973548000000.0, 'TotalRevenue': 660257000000.0, 'GrossProfit': 349246000000.0, 'OperatingIncome': 208786000000.0, 'NetIncome': 194073000000.0, 'OperatingCashFlow': 258521000000.0, 'CapitalExpenditure': -96048000000.0, 'FinancingCashFlow': -176494000000.0},
#          {'symbol': '0700.HK', 'asOfDate': '2023-12-31', 'periodType': '12M', 'TotalAssets': 1577246000000.0, 'TotalLiabilitiesNetMinorityInterest': 703565000000.0, 'StockholdersEquity': 808591000000.0, 'TotalRevenue': 609015000000.0, 'GrossProfit': 293109000000.0, 'OperatingIncome': 165658000000.0, 'NetIncome': 115216000000.0, 'OperatingCashFlow': 221962000000.0, 'CapitalExpenditure': -47407000000.0, 'FinancingCashFlow': -82573000000.0},
#          {'symbol': '0700.HK', 'asOfDate': '2022-12-31', 'periodType': '12M', 'TotalAssets': 1578131000000.0, 'TotalLiabilitiesNetMinorityInterest': 795271000000.0, 'StockholdersEquity': 721391000000.0, 'TotalRevenue': 554552000000.0, 'GrossProfit': 238746000000.0, 'OperatingIncome': 113940000000.0, 'NetIncome': 188243000000.0, 'OperatingCashFlow': 146091000000.0, 'CapitalExpenditure': -50850000000.0, 'FinancingCashFlow': -59953000000.0},
#          {'symbol': '0700.HK', 'asOfDate': '2021-12-31', 'periodType': '12M', 'TotalAssets': 1612364000000.0, 'TotalLiabilitiesNetMinorityInterest': 735671000000.0, 'StockholdersEquity': 806299000000.0, 'TotalRevenue': 560118000000.0, 'GrossProfit': 245944000000.0, 'OperatingIncome': 122341000000.0, 'NetIncome': 224822000000.0, 'OperatingCashFlow': 175186000000.0, 'CapitalExpenditure': -62165000000.0, 'FinancingCashFlow': 21620000000.0}],
#      'news': [
#          {'title': 'Nvidia, IBD Stock Of The Day, Looks To Finally Score China Sales', 'summary': 'Nvidia is the IBD Stock Of The Day as signs point to the AI chipmaker finally regaining access to the China market.', 'pubDate': '2026-01-23'},
#          {'title': 'Sector Update: Tech Stocks Mixed Friday Afternoon', 'summary': 'Tech stocks were mixed Friday afternoon, with the State Street Technology Select Sector SPDR ETF (XL', 'pubDate': '2026-01-23'},
#          {'title': 'China Signals H200 Purchase Preparations for Alibaba, Tencent, ByteDance', 'summary': "Regulators gave in-principle approval for talks on Nvidia's H200 orders, with domestic chip buying encouraged as a condition.", 'pubDate': '2026-01-23'},
#          {'title': 'Top Midday Stories: Intel Shares Fall on Downbeat Earnings Outlook; Chinese Tech Firms Clear Regulatory Hurdle for Buying Nvidia Chips', 'summary': 'US stocks were mixed in late-morning trading Friday after a two-day rally stemming from an easing of', 'pubDate': '2026-01-23'},
#          {'title': 'Sector Update: Consumer Stocks Lean Lower Premarket Friday', 'summary': 'Consumer stocks were leaning lower premarket Friday, with the State Street Consumer Staples Select S', 'pubDate': '2026-01-23'}
#          ]
#      }, 
#     {'ticker': '0005.HK',
#      'state': 'success',
#      'error': None,
#      'data': [
#          {'symbol': '0005.HK', 'asOfDate': '2024-12-31', 'periodType': '12M', 'TotalAssets': 3017048000000.0, 'TotalLiabilitiesNetMinorityInterest': 2824775000000.0, 'StockholdersEquity': 184973000000.0, 'TotalRevenue': 67396000000.0, 'GrossProfit': None, 'OperatingIncome': None, 'NetIncome': 23979000000.0, 'OperatingCashFlow': 65305000000.0, 'CapitalExpenditure': -3886000000.0, 'FinancingCashFlow': -26459000000.0},
#          {'symbol': '0005.HK', 'asOfDate': '2023-12-31', 'periodType': '12M', 'TotalAssets': 3038677000000.0, 'TotalLiabilitiesNetMinorityInterest': 2846067000000.0, 'StockholdersEquity': 185329000000.0, 'TotalRevenue': 64440000000.0, 'GrossProfit': None, 'OperatingIncome': None, 'NetIncome': 23533000000.0, 'OperatingCashFlow': 39111000000.0, 'CapitalExpenditure': -3695000000.0, 'FinancingCashFlow': -17558000000.0},
#          {'symbol': '0005.HK', 'asOfDate': '2022-12-31', 'periodType': '12M', 'TotalAssets': 2949286000000.0, 'TotalLiabilitiesNetMinorityInterest': 2764089000000.0, 'StockholdersEquity': 177833000000.0, 'TotalRevenue': 53719000000.0, 'GrossProfit': None, 'OperatingIncome': None, 'NetIncome': 15559000000.0, 'OperatingCashFlow': 19355000000.0, 'CapitalExpenditure': -4409000000.0, 'FinancingCashFlow': -6286000000.0},
#          {'symbol': '0005.HK', 'asOfDate': '2021-12-31', 'periodType': '12M', 'TotalAssets': 2957939000000.0, 'TotalLiabilitiesNetMinorityInterest': 2751162000000.0, 'StockholdersEquity': 198250000000.0, 'TotalRevenue': 64247000000.0, 'GrossProfit': None, 'OperatingIncome': None, 'NetIncome': 13917000000.0, 'OperatingCashFlow': 104312000000.0, 'CapitalExpenditure': -3565000000.0, 'FinancingCashFlow': -10794000000.0}],
#      'news': [
#          {'title': 'HSBC Just Doubled Its Price Target on Intel Stock. Should You Buy INTC Ahead of Earnings?', 'summary': 'Analysts sharp target hike puts Intel back in focus as AI-driven server demand builds ahead of earnings.', 'pubDate': '2026-01-22'}, 
#          {'title': 'Intel Stock Falls Back from 4-Year High Ahead of Earnings. What Has the Market Excited.', 'summary': 'Intel  stock was cooling off Thursday ahead of the chip company’s earnings report but remains at multiyear highs.  Intel was down 1% at $53.77 in early trading.  Intel is expected to report adjusted earnings of eight cents a share on revenue of $13.42 billion for the fourth quarter of 2025, according to a FactSet poll of analysts’ estimates.', 'pubDate': '2026-01-22'}, 
#          {'title': 'How Investors May Respond To Albemarle (ALB) After HSBC Upgrade And Stronger Balance Sheet Focus', 'summary': 'Earlier this week, HSBC upgraded Albemarle, highlighting expectations of tighter lithium supply and improved company fundamentals including stronger free cash flow and a healthier balance sheet. The bank also pointed to Albemarle’s recent capital raising and operational efficiency efforts as key factors enhancing its leverage in upcoming lithium contract negotiations. Next, we’ll examine how HSBC’s focus on Albemarle’s bolstered balance sheet and lithium market backdrop shapes the company’s...', 'pubDate': '2026-01-21'}, 
#          {'title': 'Here’s why HSBC remains bullish on global stocks', 'summary': 'Investing.com -- HSBC is staying firmly positive on global equities, arguing that rising geopolitical tensions and fresh U.S. tariffs do not alter the underlying outlook.', 'pubDate': '2026-01-21'}, 
#          {'title': 'Best credit card deals of the week', 'summary': 'Discover the best credit cards to save money, earn rewards and travel smarter.', 'pubDate': '2026-01-21'}
#          ]
#      }
#     ]


# analysis test
# list for initial_filter
#['MMM', 'AOS', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMD', 'AES', 'AFL', 'A', 'APD', 'ABNB', 'AKAM', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'AME', 'AMGN', 'APH', 'ADI', 'AON', 'APA', 'APO', 'AAPL', 'AMAT', 'APP', 'APTV', 'ACGL', 'ADM', 'ARES', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'AXON', 'BKR', 'BALL', 'BAC', 'BAX', 'BDX', 'BRK.B', 'BBY', 'TECH', 'BIIB', 'BLK', 'BX', 'XYZ', 'BK', 'BA', 'BKNG', 'BSX', 'BMY', 'AVGO', 'BR', 'BRO', 'BF.B', 'BLDR', 'BG', 'BXP', 'CHRW', 'CDNS', 'CPT', 'CPB', 'COF', 'CAH', 'CCL', 'CARR', 'CVNA', 'CAT', 'CBOE', 'CBRE', 'CDW', 'COR', 'CNC', 'CNP', 'CF', 'CRL', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'COIN', 'CL', 'CMCSA', 'FIX', 'CAG', 'COP', 'ED', 'STZ', 'CEG', 'COO', 'CPRT', 'GLW', 'CPAY', 'CTVA', 'CSGP', 'COST', 'CTRA', 'CRH', 'CRWD', 'CCI', 'CSX', 'CMI', 'CVS', 'DHR', 'DRI', 'DDOG', 'DVA', 'DAY', 'DECK', 'DE', 'DELL', 'DAL', 'DVN', 'DXCM', 'FANG', 'DLR', 'DG', 'DLTR', 'D', 'DPZ', 'DASH', 'DOV', 'DOW', 'DHI', 'DTE', 'DUK', 'DD', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'ELV', 'EME', 'EMR', 'ETR', 'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX', 'EQR', 'ERIE', 'ESS', 'EL', 'EG', 'EVRG', 'ES', 'EXC', 'EXE', 'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'FDS', 'FICO', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'FISV', 'F', 'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN', 'FCX', 'GRMN', 'IT', 'GE', 'GEHC', 'GEV', 'GEN', 'GNRC', 'GD', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GL', 'GDDY', 'GS', 'HAL', 'HIG', 'HAS', 'HCA', 'DOC', 'HSIC', 'HSY', 'HPE', 'HLT', 'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUBB', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX', 'ITW', 'INCY', 'IR', 'PODD', 'INTC', 'IBKR', 'ICE', 'IFF', 'IP', 'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV', 'IRM', 'JBHT', 'JBL', 'JKHY', 'J', 'JNJ', 'JCI', 'JPM', 'KVUE', 'KDP', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KKR', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LDOS', 'LEN', 'LII', 'LLY', 'LIN', 'LYV', 'LMT', 'L', 'LOW', 'LULU', 'LYB', 'MTB', 'MPC', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MTCH', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'META', 'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA', 'MOH', 'TAP', 'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS', 'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NEM', 'NWSA', 'NWS', 'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 'NTRS', 'NOC', 'NCLH', 'NRG', 'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'ON', 'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG', 'PLTR', 'PANW', 'PSKY', 'PH', 'PAYX', 'PAYC', 'PYPL', 'PNR', 'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 'PNC', 'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PTC', 'PSA', 'PHM', 'PWR', 'QCOM', 'DGX', 'Q', 'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'HOOD', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SNDK', 'SBAC', 'SLB', 'STX', 'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SJM', 'SW', 'SNA', 'SOLV', 'SO', 'LUV', 'SWK', 'SBUX', 'STT', 'STLD', 'STE', 'SYK', 'SMCI', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO', 'TPR', 'TRGP', 'TGT', 'TEL', 'TDY', 'TER', 'TSLA', 'TXN', 'TPL', 'TXT', 'TMO', 'TJX', 'TKO', 'TTD', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB', 'TFC', 'TYL', 'TSN', 'USB', 'UBER', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI', 'UNH', 'UHS', 'VLO', 'VTR', 'VLTO', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VTRS', 'VICI', 'V', 'VST', 'VMC', 'WRB', 'GWW', 'WAB', 'WMT', 'DIS', 'WBD', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST', 'WDC', 'WY', 'WSM', 'WMB', 'WTW', 'WDAY', 'WYNN', 'XEL', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZTS']

#result_analysis_1 = initial_filter.invoke({"tickers": ['MMM', 'AOS', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMD', 'AES', 'AFL', 'A', 'APD', 'ABNB', 'AKAM', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'AME', 'AMGN', 'APH', 'ADI', 'AON', 'APA', 'APO', 'AAPL', 'AMAT', 'APP', 'APTV', 'ACGL', 'ADM', 'ARES', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'AXON', 'BKR', 'BALL', 'BAC', 'BAX', 'BDX', 'BRK.B', 'BBY', 'TECH', 'BIIB', 'BLK', 'BX', 'XYZ', 'BK', 'BA', 'BKNG', 'BSX', 'BMY', 'AVGO', 'BR', 'BRO', 'BF.B', 'BLDR', 'BG', 'BXP', 'CHRW', 'CDNS', 'CPT', 'CPB', 'COF', 'CAH', 'CCL', 'CARR', 'CVNA', 'CAT', 'CBOE', 'CBRE', 'CDW', 'COR', 'CNC', 'CNP', 'CF', 'CRL', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'COIN', 'CL', 'CMCSA', 'FIX', 'CAG', 'COP', 'ED', 'STZ', 'CEG', 'COO', 'CPRT', 'GLW', 'CPAY', 'CTVA', 'CSGP', 'COST', 'CTRA', 'CRH', 'CRWD', 'CCI', 'CSX', 'CMI', 'CVS', 'DHR', 'DRI', 'DDOG', 'DVA', 'DAY', 'DECK', 'DE', 'DELL', 'DAL', 'DVN', 'DXCM', 'FANG', 'DLR', 'DG', 'DLTR', 'D', 'DPZ', 'DASH', 'DOV', 'DOW', 'DHI', 'DTE', 'DUK', 'DD', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'ELV', 'EME', 'EMR', 'ETR', 'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX', 'EQR', 'ERIE', 'ESS', 'EL', 'EG', 'EVRG', 'ES', 'EXC', 'EXE', 'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'FDS', 'FICO', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'FISV', 'F', 'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN', 'FCX', 'GRMN', 'IT', 'GE', 'GEHC', 'GEV', 'GEN', 'GNRC', 'GD', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GL', 'GDDY', 'GS', 'HAL', 'HIG', 'HAS', 'HCA', 'DOC', 'HSIC', 'HSY', 'HPE', 'HLT', 'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUBB', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX', 'ITW', 'INCY', 'IR', 'PODD', 'INTC', 'IBKR', 'ICE', 'IFF', 'IP', 'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV', 'IRM', 'JBHT', 'JBL', 'JKHY', 'J', 'JNJ', 'JCI', 'JPM', 'KVUE', 'KDP', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KKR', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LDOS', 'LEN', 'LII', 'LLY', 'LIN', 'LYV', 'LMT', 'L', 'LOW', 'LULU', 'LYB', 'MTB', 'MPC', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MTCH', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'META', 'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA', 'MOH', 'TAP', 'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS', 'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NEM', 'NWSA', 'NWS', 'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 'NTRS', 'NOC', 'NCLH', 'NRG', 'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'ON', 'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG', 'PLTR', 'PANW', 'PSKY', 'PH', 'PAYX', 'PAYC', 'PYPL', 'PNR', 'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 'PNC', 'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PTC', 'PSA', 'PHM', 'PWR', 'QCOM', 'DGX', 'Q', 'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'HOOD', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SNDK', 'SBAC', 'SLB', 'STX', 'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SJM', 'SW', 'SNA', 'SOLV', 'SO', 'LUV', 'SWK', 'SBUX', 'STT', 'STLD', 'STE', 'SYK', 'SMCI', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO', 'TPR', 'TRGP', 'TGT', 'TEL', 'TDY', 'TER', 'TSLA', 'TXN', 'TPL', 'TXT', 'TMO', 'TJX', 'TKO', 'TTD', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB', 'TFC', 'TYL', 'TSN', 'USB', 'UBER', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI', 'UNH', 'UHS', 'VLO', 'VTR', 'VLTO', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VTRS', 'VICI', 'V', 'VST', 'VMC', 'WRB', 'GWW', 'WAB', 'WMT', 'DIS', 'WBD', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST', 'WDC', 'WY', 'WSM', 'WMB', 'WTW', 'WDAY', 'WYNN', 'XEL', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZTS']})


#print(result_analysis_1)