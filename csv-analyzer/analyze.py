import pandas as pd
df = pd.read_csv("data.csv")

print("First 5 rows:")
print(df.head())

print("\nSummary of the stats:")
print(df.describe())

print("\nColumn names:")
print(df.columns.tolist())