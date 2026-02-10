from typing import Literal, Type, List, Dict, Any, Callable
from pydantic import BaseModel, Field, field_validator, model_validator
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# pydantic schema
# For all tools that need to input ticker list
class TickerListInput(BaseModel):
    '''
    Structure of input parameter of ticker list for all tools
    '''
    tickers: List[str]  = Field(
        ...,
        description= "A list of stock code, at least one ticker, e.g: ['0700.HK', '0005.HK', 'AAPL', '2330.TW']"
    )
    
    @field_validator("tickers", mode="before")
    @classmethod
    def normalize_tickers(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v = [t.strip() for t in v.split(",") if t.strip()]
        if not isinstance(v, list):
            raise ValueError(f"Invalid tickers: {v}")
        return [t.upper().strip() for t in v if t.strip()]
    
    @model_validator(mode="after")
    def check_ticker_count(self):
        if len(self.tickers) == 0:
            raise ValueError("At least one stock code")
        if len(self.tickers) > 30:
            logger.warning(f"Received {len(self.tickers)} stocks, limited in first 30 stocks automatically")
            self.tickers = self.tickers[:30]
        return self

# For historical price fetching tool
class HistoricalPriceInput(TickerListInput):
    """
    Structure of Input Parameters for fectching stock price
    """
    period: str = Field(
        default="6mo", 
        description= "The period to fetch data, available: (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"
    )
    interval: Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", 
        "1d", "5d", "1wk", "1mo", "3mo"] = Field(
        default= "1d",
        description="The interval of K-line, caution: for those interval less than 1d is only available within 60 days "
    )

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        valid = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
        if v not in valid:
            raise ValueError(f"Invalid period: {v}, Valid period: {', '.join(valid)}")
        return v

# For index constituents
class IndexConstituentsInput(BaseModel):
    index: str = Field(
        description="""
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
        """
    ) 
    
    @field_validator("index", mode="before")
    @classmethod
    def normalize_index(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Index must be a string!")
        
        return v.upper()
        
    @field_validator("index", mode="after")
    @classmethod
    def validate_index(cls, v: Any) -> str:
        index_list = {"AEX", "BEL 20", "CAC 40", "CAC MID 60", "DAX", "DOW JONES", "EURO STOXX 50", "FTSE 100", "IBEX 35", "MDAX", "NASDAQ 100",
                      "OMX Helsinki 25", "OMX Stockholm 30", "S&P 100", "S&P 500", "S&P 600", "SDAX", "Switzerland 20", "TECDAX", "HSI", "HSTECH"}
        if v not in index_list:
            raise ValueError(f"Invalid index: {v}, Valid index: {', '.join(index_list)}")
        return v


class Ohlcv_input(TickerListInput):
    ohlcv: Dict[str, List[Dict[str, Any]]] = Field(
        ...,
        description="""
        A price data of a ticker including ticker, date and ohlcv
        O - Open
        H - High
        L - Low
        C - Close
        V - Volume
        """
    )
    @field_validator("ohlcv", mode="after")
    @classmethod
    def validate_ohlcv(cls, v: Any) -> Dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError(f"Ohlcv must be a dictionary")
        
        for ticker, ohlcv in v.items():
            if not isinstance(ticker, str):
                raise ValueError(f"Ticker must be a string")
            if not ohlcv:
                raise ValueError(f"ohlcv['{ticker}'] is empty")
            for data in ohlcv:
                if not isinstance(data, dict):
                    raise ValueError(f"Each ohlcv data must be a dictionary")
                if not data:
                    raise ValueError(f"ohlcv data is empty")
        return v
               
    
   
# Validation + error handle wrapper
def validate_ticker_tool(schema_class: Type[BaseModel], extra_validation: Callable[[Dict], None] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(**kwargs) -> Dict[str, Any]:
            try:
                # First layer：Pydantic validation
                validated = schema_class(**kwargs)
                params = validated.model_dump()
                
                # Second layer：extra validation
                if extra_validation:
                    extra_validation(params)
                
                
                # Execute tool
                result = func(**params)

                tickers_processed = params.get("tickers", [params.get("index", "N/A")])
                
                # Normalize successful return format
                return {
                    "status": "success",
                    "data": result,
                    "tickers_processed": tickers_processed
                }
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Validation/execution fail:{error_msg}")
                
                # # Normalize failure return format，for LLM re-prompt
                return {
                    "status": "error",
                    "message": error_msg,
                    "original_input": kwargs,
                    "suggestion": (
                        "Please check:\n"
                        "1. Are tickers correct? (e.g 0700.HK not 0700)\n"
                        "2. Are period and interval compatible?\n"
                        "3. Maximum 30 tickers per request\n"
                        "4. Is index correct? (e.g S&P 500 not s&p500)\n"
                        "5. Only one index per request"
                    )
                }

        return wrapper  
    return decorator  
    
        
def validate_historical_prices(params: Dict):
            # logic validation
            short_intervals = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
            if params["interval"] in short_intervals and params["period"] not in {"1d", "5d", "1mo"}:
                raise ValueError(
                    f"Period {params['interval']} only support period=1d,5d,1mo (limited by yfinance)"
                )
