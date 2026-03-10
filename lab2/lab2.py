import pandas as pd
from itertools import permutations

# Zadanie 1 – Wczytanie danych

filename = "Online_Retail.csv"
df = pd.read_csv(filename, encoding="ISO-8859-1")

print(f"===== PODSTAWOWE INFORMACJE O DANYCH =====")
print(f"Liczba rekordów: {df.shape[0]}")
print(f"Liczba kolumn: {df.shape[1]}")
print(f"\nKolumny: {df.columns.tolist()}")

print(f"\n===== 5 PRZYKŁADOWYCH WIERSZY =====")
print(f"{df.head()}")


# Zadanie 2 – Identyfikacja encji

print(f"\n===== IDENTYFIKACJA ENCJI =====")

columns = df.columns

for col1, col2 in permutations(columns, 2):

    counts = df.groupby(col1)[col2].nunique()
    dependency = counts.max()

    if dependency < 20 and dependency != 1:
        print(f"\nwiele wartości występuje (nie można od razu utworzyć encji):\n{col1} ~ {col2} ({dependency})")
        max_keys = counts[counts == dependency].index
        for key in max_keys:
            unique_vals = df[df[col1] == key][col2].unique()
            print(f"\n{col1} = {key}")
            print(unique_vals)
    
    if dependency == 1:
        print(f"\nzależność 1:1 występuje:\n\t{col1} -> {col2}")

# konwersja na datetime
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%y %H:%M")

entities = {
    "Customer": {
        "PrimaryKey": ["CustomerID"],
        "Attributes": []
    },
    "Product": {
        "PrimaryKey": ["StockCode"],
        "Attributes": ["Description"]
    },
    "Invoice": {
        "PrimaryKey": ["InvoiceNo"],
        "Attributes": ["CustomerID", "InvoiceDate", "Country"]
    },
    "InvoiceLine": {
        "PrimaryKey": ["InvoiceNo", "StockCode"],
        "Attributes": ["Quantity", "UnitPrice"]
    },
    "Country": {
        "PrimaryKey": ["Country"],
        "Attributes": []
    }
}

for entity, info in entities.items():
    print(f"\nEncja: {entity}")
    print(f"Klucz główny: {info['PrimaryKey']}")
    print(f"Atrybuty: {info['Attributes']}")

# Rozwiązywanie niespójności

# InvoiceNo może mieć kilka InvoiceDate, zatem wybieramy najpóźniejszą datę
latest_invoice_dates = df.groupby("InvoiceNo")["InvoiceDate"].max()

# StockCode może mieć kilka Description, zatem wybieramy pierwszy opis
first_descriptions = df.groupby("StockCode")["Description"].first()

# aktualizacja danych
df = df.copy()
df["InvoiceDate"] = df["InvoiceNo"].map(latest_invoice_dates)
df["Description"] = df["StockCode"].map(first_descriptions)

# Automatyczne tworzenie tabel encji

tables = {}

for entity, config in entities.items():

    cols = config["PrimaryKey"] + config["Attributes"]
    table = df[cols].drop_duplicates()

    if len(config["PrimaryKey"]) == 1:
        table = table.dropna(subset=config["PrimaryKey"])

    tables[entity] = table

    print(f"\n===== {entity} =====")
    print(f"Kolumny: {cols}")
    print(f"Liczba rekordów: {len(table)}")
    print(f"{table.head()}")

# zapis tabel

for name, table in tables.items():
    filename = f"{name.lower()}.csv"
    table.to_csv(filename, index=False)

# Zadanie 4 – Refleksja
refl = """
Znormalizowany model 3NF nie jest wygodny do analiz OLAP,
bo dane są rozbite na wiele tabel: Customer, Product, Invoice, InvoiceLine i Country.
Aby policzyć np. sprzedaż produktów w konkretnym kraju w danym miesiącu, trzeba połączyć tabelę
InvoiceLine z Invoice, następnie z Product, a Country pobrać z tabeli Invoice.
Customer w tym przypadku nie jest bezpośrednio powiązany z Country, więc też wymaga joinów przy analizach dotyczących klientów.
Każde takie zapytanie wymaga wielu joinów, co sprawia, że analizy stają się bardziej skomplikowane i mniej wydajne.
"""
print(refl)