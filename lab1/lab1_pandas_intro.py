import matplotlib
matplotlib.use("Agg")

import pandas as pd
df = pd.read_csv("sales_raw.csv")

print(df.head())
print(df.shape)

df["order_date"] = pd.to_datetime(df["order_date"])
df["total_value"] = df["quantity"] * df["unit_price"]
df["year"] = df["order_date"].dt.year

total_sales = df["total_value"].sum()
sales_by_country = df.groupby("country")["total_value"].sum()
sales_by_year = df.groupby("year")["total_value"].sum()

print(total_sales)
print(sales_by_country)
print(sales_by_year)

df_agg = df.groupby(["country", "year"])["total_value"].sum().reset_index()

df_agg.to_csv("sales_aggregated.csv", index=False)
