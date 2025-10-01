import pandas as pd
from openbb import obb

def long_investment_strategy(ticker="AAPL", start="2015-01-01", end="2025-01-01"):
    df = obb.equity.price.historical(
        symbol=ticker,
        start_date=start,
        end_date=end
    ).to_df()

    if df.empty or "close" not in df.columns:
        raise ValueError(f"No data found for ticker '{ticker}'")

    df = df.sort_index()
    df['200_MA'] = df['close'].rolling(window=200, min_periods=1).mean()

    df['Signal'] = 0
    df.loc[df['close'] > df['200_MA'], 'Signal'] = 1
    df.loc[df['close'] <= df['200_MA'], 'Signal'] = -1

    df.reset_index(inplace=True)
    df.rename(columns={
        "date": "Date",
        "close": "Close"
    }, inplace=True)

    df = df[['Date', 'Close', '200_MA', 'Signal']]
    return df
