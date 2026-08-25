"""
Thin wrapper around yfinance.

Isolated in its own module so the rest of the app never imports yfinance
directly — if the data source ever changes (e.g. to Alpha Vantage), only
this file needs to change.
"""
import pandas as pd
import yfinance as yf


class NoDataError(Exception):
    """Raised when yfinance returns no rows for the given ticker/date range."""


def fetch_close_prices(ticker: str, start_date: str, end_date: str) -> pd.Series:
    data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
    if data.empty:
        raise NoDataError(f"No price data returned for {ticker} between {start_date} and {end_date}")
    return data["Close"].squeeze()
