import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Wczytanie danych
filename = "Online_Retail.csv"
df = pd.read_csv(filename, encoding="ISO-8859-1")

# Konwersja daty
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%y %H:%M")

# Obsługa braków i zwrotów
df = df.dropna(subset=["CustomerID", "InvoiceNo"])

# Oznaczanie zwrotów (InvoiceNo zaczynające się od 'C')
df["IsReturn"] = df["InvoiceNo"].astype(str).str.startswith("C")

# Utworzenie miary SalesAmount
df["SalesAmount"] = df["Quantity"] * df["UnitPrice"]

# Sprzedaż wg krajów
sales_by_country = df.groupby("Country")["SalesAmount"].sum().sort_values(ascending=False)
print("===== Sprzedaż wg krajów =====")
print(sales_by_country)

# 5. Trend sprzedaży w czasie (dzienne)
sales_over_time = df.groupby(df["InvoiceDate"].dt.floor("D"))["SalesAmount"].sum().reset_index()
sales_over_time.rename(columns={"InvoiceDate": "Date"}, inplace=True)

# Tworzymy pełną serię dat
full_dates = pd.DataFrame({
    "Date": pd.date_range(start=sales_over_time["Date"].min(),
                          end=sales_over_time["Date"].max())
})

# Merge i uzupełnianie braków zerami
sales_over_time_full = full_dates.merge(sales_over_time, on="Date", how="left")
sales_over_time_full["SalesAmount"] = sales_over_time_full["SalesAmount"].fillna(0)

print("\n===== Trend sprzedaży dziennej (pierwsze 10 dni) =====")
print(sales_over_time_full.head(10))

# Wykres trendu sprzedaży dziennej
plt.figure(figsize=(14,6))
plt.plot(sales_over_time_full["Date"], sales_over_time_full["SalesAmount"], marker='', color='tab:blue')
plt.title("Trend sprzedaży w czasie")
plt.xlabel("Data")
plt.ylabel("SalesAmount")
plt.grid(True, linestyle='--', alpha=0.5)

# Podwajanie liczby ticków dziennych
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("sales_over_time.png")
plt.close()
print("\nWykres zapisany jako sales_over_time.png")

# Trend sprzedaży miesięczny
sales_over_month = df.groupby(df["InvoiceDate"].dt.to_period("M"))["SalesAmount"].sum().reset_index()
sales_over_month["Date"] = sales_over_month["InvoiceDate"].dt.to_timestamp()
sales_over_month = sales_over_month[["Date", "SalesAmount"]]

# Tworzymy pełną serię miesięcy
full_months = pd.DataFrame({
    "Date": pd.date_range(start=sales_over_month["Date"].min(),
                          end=sales_over_month["Date"].max(),
                          freq="MS")  # MS = Month Start
})

# Merge i uzupełnianie zerami
sales_over_month_full = full_months.merge(sales_over_month, on="Date", how="left")
sales_over_month_full["SalesAmount"] = sales_over_month_full["SalesAmount"].fillna(0)

# Wykres miesięczny
plt.figure(figsize=(12,5))
plt.plot(sales_over_month_full["Date"], sales_over_month_full["SalesAmount"], marker='o', color='tab:orange')
plt.title("Trend sprzedaży miesięcznej")
plt.xlabel("Miesiąc")
plt.ylabel("SalesAmount")
plt.grid(True, linestyle='--', alpha=0.5)

# Podwajanie liczby ticków miesięcznych
ax = plt.gca()
ax.ticklabel_format(style='plain', axis='y')
ax.xaxis.set_major_locator(mdates.MonthLocator())                   # główne ticki co miesiąc
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("sales_over_month.png")
plt.close()
print("Wykres miesięczny zapisany jako sales_over_month.png")