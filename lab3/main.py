import pandas as pd
from datetime import datetime, date

df = pd.read_csv("Online_Retail.csv", encoding="ISO-8859-1")
print(f"Liczba wierszy przed czyszczeniem: {len(df)}")
df.head()

df.info()

# Krok 1: usuń wiersze bez CustomerID
df = df.dropna(subset=["CustomerID"])
print(f"Po usunięciu braków CustomerID: {len(df)} wierszy")

# Krok 2: usuń anulowane transakcje (InvoiceNo zaczyna się od 'C')
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
print(f"Po usunięciu anulacji: {len(df)} wierszy")

# Krok 3: usuń rekordy z Quantity <= 0
df = df[df["Quantity"] > 0]
print(f"Po usunięciu Quantity <= 0: {len(df)} wierszy")

# Krok 4: usuń rekordy z UnitPrice <= 0
df = df[df["UnitPrice"] > 0]
print(f"Po usunięciu UnitPrice <= 0: {len(df)} wierszy")

# Krok 5: konwersja dat
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%y %H:%M")

# Krok 6: usuń duplikaty
df = df.drop_duplicates()
print(f"Po usunięciu duplikatów: {len(df)} wierszy")

# Krok 7: dodaj kolumnę Revenue
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# Upewnij się, że CustomerID jest całkowitoliczbowy
df["CustomerID"] = df["CustomerID"].astype(int)

print("\nPodgląd danych po czyszczeniu:")
df.head()

# ── DimCustomer ──────────────────────────────────────────────────────────────
dim_customer = (
    df[["CustomerID", "Country"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
# Klucz sztuczny
dim_customer.insert(0, "CustomerKey", dim_customer.index + 1)

print("DimCustomer (pierwsze wiersze):")
print(dim_customer.head())
print(f"Liczba klientów: {len(dim_customer)}")

# ── DimProduct ───────────────────────────────────────────────────────────────
dim_product = (
    df[["StockCode", "Description"]]
    .drop_duplicates(subset=["StockCode"])
    .reset_index(drop=True)
)
# Klucz sztuczny
dim_product.insert(0, "ProductKey", dim_product.index + 1)

print("DimProduct (pierwsze wiersze):")
print(dim_product.head())
print(f"Liczba produktów: {len(dim_product)}")

# ── DimDate ──────────────────────────────────────────────────────────────────
unique_dates = df["InvoiceDate"].dt.date.unique()
dim_date = pd.DataFrame({"Date": pd.to_datetime(unique_dates)})
dim_date = dim_date.sort_values("Date").reset_index(drop=True)

# Atrybuty czasowe
dim_date["Year"]      = dim_date["Date"].dt.year
dim_date["Month"]     = dim_date["Date"].dt.month
dim_date["Day"]       = dim_date["Date"].dt.day
dim_date["DayOfWeek"] = dim_date["Date"].dt.day_name()
dim_date["Quarter"]   = dim_date["Date"].dt.quarter

# Klucz sztuczny (format YYYYMMDD)
dim_date.insert(0, "DateKey", dim_date["Date"].dt.strftime("%Y%m%d").astype(int))

print("DimDate (pierwsze wiersze):")
print(dim_date.head())
print(f"Liczba dat: {len(dim_date)}")

# Przygotuj klucz daty w df
df["DateKey"] = df["InvoiceDate"].dt.strftime("%Y%m%d").astype(int)

# Dołącz klucze sztuczne z wymiarów
fact_sales = df.merge(dim_customer[["CustomerKey", "CustomerID", "Country"]],
                      on=["CustomerID", "Country"], how="left")
fact_sales = fact_sales.merge(dim_product[["ProductKey", "StockCode"]],
                              on="StockCode", how="left")

# Wybierz tylko potrzebne kolumny do tabeli faktów
fact_sales = fact_sales[[
    "InvoiceNo",    # klucz naturalny faktury (do identyfikacji transakcji)
    "CustomerKey",
    "ProductKey",
    "DateKey",
    "Quantity",
    "UnitPrice",
    "Revenue"
]].reset_index(drop=True)

# Klucz sztuczny tabeli faktów
fact_sales.insert(0, "SalesKey", fact_sales.index + 1)

print("FactSales (pierwsze wiersze):")
print(fact_sales.head())
print(f"\nLiczba wierszy w tabeli faktów: {len(fact_sales)}")
print(f"Łączny przychód: {fact_sales['Revenue'].sum():,.2f}")

# Budowa DimCustomer_SCD2
# Bazujemy na istniejącym dim_customer i symulujemy aktualizację

dim_customer_scd2 = dim_customer.copy()
dim_customer_scd2["valid_from"]  = pd.Timestamp("2010-01-01")
dim_customer_scd2["valid_to"]    = pd.Timestamp("9999-12-31")  # brak daty końcowej = aktualny
dim_customer_scd2["is_current"]  = True

# ── Symulacja zmiany kraju dla wybranego klienta ─────────────────────────────
# Przyjmijmy, że klient CustomerID=12346 zmienił kraj z 'United Kingdom' na 'Germany'
# w dniu 2011-06-01.

def apply_scd2_update(dim_df, customer_id, new_country, change_date):
    """Aktualizuje DimCustomer_SCD2 zgodnie z logiką SCD2."""
    mask = (dim_df["CustomerID"] == customer_id) & (dim_df["is_current"] == True)

    if mask.sum() == 0:
        print(f"Klient {customer_id} nie istnieje lub nie ma aktualnego rekordu.")
        return dim_df

    idx = dim_df[mask].index[0]
    old_country = dim_df.loc[idx, "Country"]

    if old_country == new_country:
        print(f"Brak zmiany – klient {customer_id} nadal w: {old_country}")
        return dim_df

    # Zamknij stary rekord
    dim_df.loc[idx, "valid_to"]   = pd.Timestamp(change_date) - pd.Timedelta(days=1)
    dim_df.loc[idx, "is_current"] = False

    # Dodaj nowy rekord
    new_key = dim_df["CustomerKey"].max() + 1
    new_row = {
        "CustomerKey": new_key,
        "CustomerID":  customer_id,
        "Country":     new_country,
        "valid_from":  pd.Timestamp(change_date),
        "valid_to":    pd.Timestamp("9999-12-31"),
        "is_current":  True
    }
    dim_df = pd.concat([dim_df, pd.DataFrame([new_row])], ignore_index=True)
    print(f"Klient {customer_id}: '{old_country}' → '{new_country}' od {change_date}")
    return dim_df


# Sprawdź czy CustomerID=12346 istnieje w danych
sample_customers = dim_customer_scd2["CustomerID"].head(3).tolist()
test_customer = sample_customers[0]  # użyj pierwszego dostępnego klienta
old_ctry = dim_customer_scd2.loc[dim_customer_scd2["CustomerID"] == test_customer, "Country"].values[0]

# Symuluj zmianę kraju
new_ctry = "Germany" if old_ctry != "Germany" else "France"
dim_customer_scd2 = apply_scd2_update(
    dim_customer_scd2,
    customer_id  = test_customer,
    new_country  = new_ctry,
    change_date  = "2011-06-01"
)

# Pokaż oba rekordy tego klienta
print("\nOba rekordy zmienionego klienta (historia):")
print(dim_customer_scd2[dim_customer_scd2["CustomerID"] == test_customer].to_string(index=False))

# Podsumowanie wymiaru SCD2
print(f"DimCustomer_SCD2 – łączna liczba rekordów: {len(dim_customer_scd2)}")
print(f"Rekordy aktualne (is_current=True):  {dim_customer_scd2['is_current'].sum()}")
print(f"Rekordy historyczne (is_current=False): {(~dim_customer_scd2['is_current']).sum()}")
print("\nPodgląd wymiaru SCD2:")
dim_customer_scd2.head()

# Sprawdzenie integralności referencyjnej
missing_customer = fact_sales["CustomerKey"].isna().sum()
missing_product  = fact_sales["ProductKey"].isna().sum()
missing_date     = (~fact_sales["DateKey"].isin(dim_date["DateKey"])).sum()

print("=== Weryfikacja integralności referencyjnej ===")
print(f"Brakujące CustomerKey w FactSales: {missing_customer}")
print(f"Brakujące ProductKey  w FactSales: {missing_product}")
print(f"DateKey bez odpowiednika w DimDate: {missing_date}")

print("\n=== Podsumowanie tabel ===")
print(f"DimCustomer:    {len(dim_customer):>6} wierszy")
print(f"DimProduct:     {len(dim_product):>6} wierszy")
print(f"DimDate:        {len(dim_date):>6} wierszy")
print(f"FactSales:      {len(fact_sales):>6} wierszy")
print(f"\nŁączny przychód: {fact_sales['Revenue'].sum():>12,.2f}")
print(f"Średni przychód na pozycję: {fact_sales['Revenue'].mean():>8,.2f}")

