"""yfinance client for fetching IDX stock data."""

import time
from datetime import date
from decimal import Decimal

import yfinance as yf
from pandas import DataFrame

from app.config import settings
from app.core.exceptions import DataImportException
from app.core.logging import logger


class YFinanceClient:
    """Client for fetching stock data from Yahoo Finance."""

    def __init__(self):
        self.delay = settings.YFINANCE_DELAY
        self.retries = settings.YFINANCE_RETRIES

    async def fetch_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> DataFrame:
        """Fetch OHLCV data for a ticker from yfinance.
        
        Args:
            ticker: Stock ticker (e.g., "BBCA.JK")
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            DataImportException: If fetching fails
        """
        logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
        
        for attempt in range(self.retries):
            try:
                # Add delay to respect rate limits
                if attempt > 0:
                    time.sleep(self.delay * (attempt + 1))
                
                stock = yf.Ticker(ticker)
                
                # Fetch data with auto_adjust=False to get both close and adj_close
                df = stock.history(
                    start=start_date,
                    end=end_date,
                    auto_adjust=False,
                )
                
                if df.empty:
                    logger.warning(f"No data returned for {ticker}")
                    return DataFrame()
                
                # Rename columns to lowercase
                df.columns = [col.lower().replace(" ", "_") for col in df.columns]
                
                # Ensure required columns exist
                required_cols = ["open", "high", "low", "close", "adj_close", "volume"]
                for col in required_cols:
                    if col not in df.columns:
                        raise DataImportException(f"Missing required column: {col}")
                
                # Reset index to get date as column
                df = df.reset_index()
                
                # Rename Date column to date
                if "Date" in df.columns:
                    df = df.rename(columns={"Date": "date"})
                elif "date" in df.columns:
                    pass  # Already lowercase
                
                # Convert date to datetime.date
                df["date"] = df["date"].dt.date
                
                logger.info(f"Fetched {len(df)} records for {ticker}")
                return df
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {ticker}: {str(e)}")
                if attempt == self.retries - 1:
                    raise DataImportException(
                        f"Failed to fetch data for {ticker} after {self.retries} attempts: {str(e)}"
                    )
        
        return DataFrame()  # Should never reach here

    async def get_stock_info(self, ticker: str) -> dict:
        """Get stock metadata from yfinance.
        
        Args:
            ticker: Stock ticker (e.g., "BBCA.JK")
            
        Returns:
            Dictionary with stock info
        """
        try:
            time.sleep(self.delay)
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "ticker": ticker,
                "name": info.get("longName", info.get("shortName", ticker)),
                "sector": info.get("sector"),
            }
        except Exception as e:
            logger.error(f"Failed to get info for {ticker}: {str(e)}")
            return {
                "ticker": ticker,
                "name": ticker,
                "sector": None,
            }
