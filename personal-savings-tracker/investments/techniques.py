import pandas as pd
from openbb.stocks.stocks import load  # latest OpenBB import

def long_investment_strategy(ticker="AAPL", start="2015-01-01", end="2025-01-01"):
    """
    Long-term investment strategy using OpenBB stock data.
    Returns DataFrame with Date, Close, 200-day MA, and Signal.
    Signal: 1 = Buy/Hold, -1 = Stay out/Sell
    """
    # Fetch historical stock data
    df = load(ticker, start_date=start, end_date=end)

    if df.empty or "Close" not in df.columns:
        raise ValueError(f"No data found for ticker '{ticker}'")

    df = df.sort_index()
    df['200_MA'] = df['Close'].rolling(window=200, min_periods=1).mean()

    df['Signal'] = 0
    df.loc[df['Close'] > df['200_MA'], 'Signal'] = 1
    df.loc[df['Close'] <= df['200_MA'], 'Signal'] = -1

    df.reset_index(inplace=True)
    df = df[['Date', 'Close', '200_MA', 'Signal']]
    return df
