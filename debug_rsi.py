
import pandas as pd
import pandas_ta as ta

dates = pd.date_range(start="2023-01-01", periods=300, freq="D")
prices = [100 + i for i in range(300)]
df = pd.DataFrame({"close": prices}, index=dates)

rsi = ta.rsi(df["close"], length=14)
print(f"Last RSI value: {rsi.iloc[-1]}")
print(f"RSI tail: {rsi.tail()}")
