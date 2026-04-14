#!/usr/bin/env python
# coding: utf-8

# # Mechanizmy hurtowni danych - laboratorium 4
# ## ETL w hurtowniach danych
# 
# ---

# ## Importy i konfiguracja
# 
# Ponizsza komorka importuje biblioteki wymagane do realizacji calego procesu ETL. Biblioteka `pandas` sluzy do wczytywania, przetwarzania i zapisu danych tabelarycznych. Biblioteka `numpy` jest uzywana do operacji numerycznych i obslugi wartosci brakujacych.

import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)


# ---
# # Zadanie 1
# 
# ---
# ## EXTRACT
# 
# Dane sa wczytywane z pliku CSV przy uzyciu kodowania `ISO-8859-1`, poniewaz plik zawiera znaki spoza standardowego zestawu ASCII (m.in. znaki specjalne w nazwach produktow). Po wczytaniu wyswietlana jest podstawowa informacja o strukturze zbioru: typy kolumn, liczba rekordow oraz przyklad danych.

df = pd.read_csv('Online_Retail.csv', encoding='ISO-8859-1')

print(f'Liczba rekordow: {len(df):,}')
print(f'Liczba kolumn:   {len(df.columns)}')
print()
df.head()


df.info()


df.describe()


# ### Obserwacje po ekstrakcji
# 
# Na podstawie powyzszego podgladu mozna stwierdzic:
# - Kolumna `CustomerID` zawiera wartosci brakujace (typ `float64` zamiast `int`, co wynika z obecnosci `NaN`).
# - Kolumna `InvoiceDate` jest typem tekstowym (`object`), wymaga konwersji do `datetime`.
# - Kolumna `Quantity` zawiera wartosci ujemne i zerowe (zwroty, anulowania).
# - Kolumna `UnitPrice` moze zawierac wartosci ujemne lub zerowe.
# - Faktury zaczynajace sie od `C` oznaczaja anulowania (cancellations).

# ---
# ## TRANSFORM
# 
# ### 1. Analiza brakujacych wartosci
# 
# Przed przystapieniem do czyszczenia sprawdzana jest liczba i odsetek brakujacych wartosci w kazdej kolumnie.

missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({'Brakujace': missing, 'Procent [%]': missing_pct})
missing_df[missing_df['Brakujace'] > 0]


# ### 2. Czyszczenie danych
# 
# Usuwane sa rekordy niespelniajace wymagan jakosciowych:
# - Rekordy z brakujacym `CustomerID` - transakcja bez identyfikowalnego klienta nie moze byc przypisana do zadnego wymiaru klienta.
# - Rekordy z `Quantity <= 0` - wartosci zerowe i ujemne odpowiadaja zwrotom lub anulowaniom, ktore nie stanowia faktycznej sprzedazy.
# - Rekordy z `UnitPrice < 0` - cena ujemna jest bledna merytorycznie.
# - Duplikaty - zduplikowane wiersze zostaja usuniete, poniewaz ich obecnosc zafalszowuje agregacje.
# 
# Po kazdym etapie odnotowywana jest liczba usuniectych rekordow.

df_clean = df.copy()
n_start = len(df_clean)
print(f'Rekordy przed czyszczeniem: {n_start:,}')

# Usuniecie rekordow z brakujacym CustomerID
df_clean = df_clean.dropna(subset=['CustomerID'])
print(f'Po usunieciu braków CustomerID:  {len(df_clean):,}  (usunieto: {n_start - len(df_clean):,})')

# Usuniecie rekordow z Quantity <= 0 (zwroty, anulowania)
n = len(df_clean)
df_clean = df_clean[df_clean['Quantity'] > 0]
print(f'Po usunieciu Quantity <= 0:      {len(df_clean):,}  (usunieto: {n - len(df_clean):,})')

# Usuniecie rekordow z UnitPrice < 0
n = len(df_clean)
df_clean = df_clean[df_clean['UnitPrice'] >= 0]
print(f'Po usunieciu UnitPrice < 0:      {len(df_clean):,}  (usunieto: {n - len(df_clean):,})')

# Usuniecie duplikatow
n = len(df_clean)
df_clean = df_clean.drop_duplicates()
print(f'Po usunieciu duplikatow:         {len(df_clean):,}  (usunieto: {n - len(df_clean):,})')

print(f'\nLaczna liczba usuniectych rekordow: {n_start - len(df_clean):,} ({(n_start - len(df_clean))/n_start*100:.1f}%)')


# ### 3. Poprawienie typow danych
# 
# Kolumna `InvoiceDate` jest konwertowana z tekstu na typ `datetime`, co umozliwia ekstrakcje skladowych czasowych. Kolumna `CustomerID` jest konwertowana z `float64` na `int64`, poniewaz identyfikator klienta nie powinien zawierac wartosci dziesietnych.

df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'], format="%m/%d/%y %H:%M")
df_clean['CustomerID'] = df_clean['CustomerID'].astype(int)

print('Typy danych po korekcie:')
print(df_clean.dtypes)


# ### 4. Rozbicie kolumny daty
# 
# Kolumna `InvoiceDate` zostaje rozbita na trzy oddzielne kolumny: `Year`, `Month` oraz `Day`. Takie przygotowanie danych jest wymagane do prawidlowego zasilenia wymiaru czasu (dim_date) w schemacie gwiazdy, a takze ulatwia filtrowanie i grupowanie po skladowych czasowych.

df_clean['Year']  = df_clean['InvoiceDate'].dt.year
df_clean['Month'] = df_clean['InvoiceDate'].dt.month
df_clean['Day']   = df_clean['InvoiceDate'].dt.day

df_clean[['InvoiceDate', 'Year', 'Month', 'Day']].head()


# ### 5. Wyliczenie miar pochodnych
# 
# Na etapie ETL wyliczana jest kolumna `TotalPrice` (przychod brutto z linii faktury) jako iloczyn `Quantity` i `UnitPrice`. Prekalkulacja tej miary na etapie transformacji eliminuje koniecznosc jej wyliczania przy kazdym zapytaniu analitycznym, co przyspiesza dzialanie raportow i kwerend agregujacych.

df_clean['TotalPrice'] = df_clean['Quantity'] * df_clean['UnitPrice']

print(f'Laczny przychod w zbiorze: {df_clean["TotalPrice"].sum():,.2f}')
df_clean[['InvoiceNo', 'StockCode', 'Quantity', 'UnitPrice', 'TotalPrice']].head()


# ### 6. Budowa tabeli faktow
# 
# Z przetworzonego zbioru wyodrebniana jest tabela faktow zawierajaca klucze obce do wymiarow oraz miary. Tabela faktow jest ziarnem transakcji liniowej (jeden wiersz = jedna linia faktury). Zawiera:
# - **InvoiceNo** - klucz faktury (relacja do dim_invoice)
# - **StockCode** - klucz produktu (relacja do dim_product)
# - **CustomerID** - klucz klienta (relacja do dim_customer)
# - **InvoiceDate** - pelna data (relacja do dim_date)
# - **Year, Month, Day** - skladowe daty (dla wygodnego filtrowania)
# - **Quantity** - miara: liczba sprzedanych jednostek
# - **UnitPrice** - miara: cena jednostkowa
# - **TotalPrice** - miara: wartosc linii faktury

fact_columns = [
    'InvoiceNo', 'StockCode', 'CustomerID', 'InvoiceDate',
    'Year', 'Month', 'Day',
    'Quantity', 'UnitPrice', 'TotalPrice'
]

fact_sales = df_clean[fact_columns].copy()

print(f'Liczba rekordow w tabeli faktow: {len(fact_sales):,}')
print(f'Liczba kolumn:                   {len(fact_sales.columns)}')
print()
fact_sales.head()


# ---
# ## LOAD
# 
# Tabela faktow zostaje zapisana do pliku CSV. Parametr `index=False` wyklucza automatyczny indeks Pandas z pliku wyjsciowego. Plik `fact_sales.csv` stanowi wynik etapu L procesu ETL i jest gotowy do zaladowania do docelowej bazy danych hurtowni danych.

fact_sales.to_csv('fact_sales.csv', index=False)
print('Plik fact_sales.csv zostal zapisany.')
print(f'Rozmiar pliku: {fact_sales.memory_usage(deep=True).sum() / 1024**2:.2f} MB (w pamieci)')


# ---
# # Zadanie 2
# 
# Zadanie polega na polaczeniu dwoch roznorodnnych zbiorow danych w jedna spojna tabele faktow. Rozne zrodla danych moga roznic sie struktura kolumn, typami danych, formatami dat oraz konwencjami nazewnictwa - wszystkie te roznice musza zostac zniwelowane na etapie transformacji.
# 
# ---
# ## EXTRACT
# 
# ### Wczytanie zbioru Online_Retail (df1)
# 
# Pierwszy zbior danych to plik `Online_Retail.csv`, wczytany z kodowaniem `ISO-8859-1`.

df1 = pd.read_csv('Online_Retail.csv', encoding='ISO-8859-1')
print(f'df1 ksztalt: {df1.shape}')
print(f'df1 kolumny: {list(df1.columns)}')


# ### Wczytanie zbioru Online Retail II (df2)
# 
# Drugi zbior danych pochodzi z repozytorium UCI.
# 
# Plik ma format XLSX i zawiera dwa arkusze: `Year 2009-2010` oraz `Year 2010-2011`. Oba arkusze sa wczytywane i laczone w jeden DataFrame.

# Wczytanie obu arkuszy pliku XLSX
df2_2009 = pd.read_excel('online_retail_II.xlsx', sheet_name='Year 2009-2010')
df2_2010 = pd.read_excel('online_retail_II.xlsx', sheet_name='Year 2010-2011')
df2 = pd.concat([df2_2009, df2_2010], ignore_index=True)

print(f'df2 ksztalt: {df2.shape}')
print(f'df2 kolumny: {list(df2.columns)}')


# ---
# ## Analiza porownawcza zbiorow
# 
# Przed polaczeniem zbiorow przeprowadzana jest analiza porownawcza: nazwy kolumn, typy danych oraz liczba brakujacych wartosci. Pozwala to zidentyfikowac roznice wymagajace korekty.

compare = pd.DataFrame({
    'df1_dtype': df1.dtypes,
    'df1_missing': df1.isnull().sum(),
    'df1_missing_pct': (df1.isnull().sum() / len(df1) * 100).round(2)
})

compare2 = pd.DataFrame({
    'df2_dtype': df2.dtypes,
    'df2_missing': df2.isnull().sum(),
    'df2_missing_pct': (df2.isnull().sum() / len(df2) * 100).round(2)
})

print('=== Zbior df1 (Online_Retail.csv) ===')
print(compare)
print()
print('=== Zbior df2 (Online_Retail_II.xlsx) ===')
print(compare2)


cols_df1 = set(df1.columns)
cols_df2 = set(df2.columns)

print(f'Kolumny wspolne:         {cols_df1 & cols_df2}')
print(f'Tylko w df1:             {cols_df1 - cols_df2}')
print(f'Tylko w df2:             {cols_df2 - cols_df1}')
print()
print('Przyklad danych df2:')
df2.head(3)


# ### Wnioski z analizy porownawczej
# 
# Zbior `df2` rozni sie od `df1` nastepujacymi cechami:
# - Kolumna `Description` nie wystepuje pod ta sama nazwa - w df2 jej odpowiednikiem moze byc `Description` lub brak.
# - Kolumna `Customer ID` w df2 zawiera spacje (zamiast `CustomerID`).
# - Kolumna `Invoice` w df2 odpowiada kolumnie `InvoiceNo` w df1.
# - Kolumna `Price` w df2 odpowiada kolumnie `UnitPrice` w df1.
# - Przyjety zostaje schemat df1 jako docelowy, poniewaz zostal on juz oczyszczony i zwalidowany w Zadaniu 1.

# ---
# ## TRANSFORM
# 
# ### 1. Ujednolicenie schematu df1
# 
# Pierwszy zbior zostaje poddany temu samemu procesowi czyszczenia co w Zadaniu 1. Wyodrbniana jest funkcja `clean_dataframe`, co pozwala na jednolite zastosowanie tych samych regul do obu zbiorow.

def clean_dataframe(df, invoice_col='InvoiceNo', customer_col='CustomerID',
                    quantity_col='Quantity', price_col='UnitPrice',
                    date_col='InvoiceDate', stock_col='StockCode',
                    country_col='Country', desc_col='Description'):
    """
    Oczyszcza i normalizuje DataFrame do wspolnego schematu tabeli faktow.
    Zwraca DataFrame ze standardowymi nazwami kolumn.
    """
    d = df.copy()

    # Ujednolicenie nazw kolumn do standardowego schematu
    d = d.rename(columns={
        invoice_col:  'InvoiceNo',
        customer_col: 'CustomerID',
        quantity_col: 'Quantity',
        price_col:    'UnitPrice',
        date_col:     'InvoiceDate',
        stock_col:    'StockCode',
        country_col:  'Country',
        desc_col:     'Description'
    })

    # Zachowanie tylko kolumn docelowego schematu
    target_cols = ['InvoiceNo', 'StockCode', 'Description',
                   'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country']
    d = d[[c for c in target_cols if c in d.columns]]

    # Czyszczenie
    d = d.dropna(subset=['CustomerID'])
    d = d[d['Quantity'] > 0]
    d = d[d['UnitPrice'] >= 0]
    d = d.drop_duplicates()

    # Typy danych
    d['InvoiceDate'] = pd.to_datetime(d['InvoiceDate'], format="%m/%d/%y %H:%M")
    d['CustomerID']  = d['CustomerID'].astype(int)
    d['InvoiceNo']   = d['InvoiceNo'].astype(str)
    d['StockCode']   = d['StockCode'].astype(str)

    # Miary pochodne
    d['TotalPrice'] = d['Quantity'] * d['UnitPrice']

    # Skladowe daty
    d['Year']  = d['InvoiceDate'].dt.year
    d['Month'] = d['InvoiceDate'].dt.month
    d['Day']   = d['InvoiceDate'].dt.day

    return d


# ### 2. Zastosowanie transformacji do obu zbiorow
# 
# Funkcja czyszczaca jest stosowana do obu zbiorow z odpowiednimi mapowaniami nazw kolumn. W przypadku df2 kolumny maja inne nazwy niz w df1, dlatego przekazywane sa parametry mapowania.

df1_clean = clean_dataframe(df1)
print(f'df1 po czyszczeniu: {df1_clean.shape}')

df2_clean = clean_dataframe(
    df2,
    invoice_col='Invoice',
    customer_col='Customer ID',
    quantity_col='Quantity',
    price_col='Price',
    date_col='InvoiceDate',
    stock_col='StockCode',
    country_col='Country',
    desc_col='Description'
)
print(f'df2 po czyszczeniu: {df2_clean.shape}')


# ### 3. Analiza jakosci danych - duplikaty miedzy zbiorami
# 
# Zbior df1 obejmuje dane z lat 2010-2011, natomiast df2 obejmuje lata 2009-2011. Istnieje zatem mozliwosc pokrywania sie rekordow w obszarze 2010-2011. Duplikaty miedzyzbiorowe sa identyfikowane na podstawie klucza: `InvoiceNo` + `StockCode` + `CustomerID` + `InvoiceDate` + `Quantity`.

key_cols = ['InvoiceNo', 'StockCode', 'CustomerID', 'Quantity']

print('Zakresy dat:')
print(f'  df1: {df1_clean["InvoiceDate"].min().date()} - {df1_clean["InvoiceDate"].max().date()}')
print(f'  df2: {df2_clean["InvoiceDate"].min().date()} - {df2_clean["InvoiceDate"].max().date()}')
print()

# Identyfikacja potencjalnych duplikatow miedzyzbiorowych
keys_df1 = df1_clean[key_cols].drop_duplicates()
keys_df2 = df2_clean[key_cols].drop_duplicates()

overlap = keys_df1.merge(keys_df2, on=key_cols, how='inner')
print(f'Liczba potencjalnych rekordow pokrywajacych sie: {len(overlap):,}')


# ### 4. Analiza niespojnosci cenowych
# 
# Sprawdzane sa produkty wystepujace w obu zbiorach, dla ktorych cena jednostkowa rozni sie miedzy zrodlami. Takie roznice moga wynikac z korekt cenowych, bledow danych lub roznych polityk rabatowych.

price_df1 = df1_clean.groupby('StockCode')['UnitPrice'].median().rename('price_df1')
price_df2 = df2_clean.groupby('StockCode')['UnitPrice'].median().rename('price_df2')

price_compare = pd.concat([price_df1, price_df2], axis=1).dropna()
price_compare['roznica'] = (price_compare['price_df1'] - price_compare['price_df2']).abs()
price_compare['roznica_pct'] = (price_compare['roznica'] / price_compare['price_df2'] * 100).round(2)

inconsistent = price_compare[price_compare['roznica_pct'] > 10].sort_values('roznica_pct', ascending=False)
print(f'Produkty z roznica ceny mediany > 10%: {len(inconsistent):,}')
inconsistent.head(10)


# ### 5. Polaczenie zbiorow
# 
# Stosowana jest metoda `pd.concat`, poniewaz oba zbory maja ten sam schemat kolumn i sa laczone pionowo (union). Metoda `merge` bylaby stosowana do laczenia tabel o roznych kolumnach za pomoca klucza wspolnego.
# 
# Strategia rozwiazania konfliktow: rekordy pokrywajace sie sa usuwane jako duplikaty po polaczeniu. Priorytet ma zbior df2 jako nowszy i dokladniejszy. Duplikaty sa usuwane przez `drop_duplicates` z zachowaniem pierwszego wystapienia po posortowaniu (df2 jest pierwszym elementem concat).

# df2 jest umieszczony jako pierwszy - jego rekordy maja pierwszenstwo przy usuwaniu duplikatow
df_all = pd.concat([df2_clean, df1_clean], ignore_index=True)

n_before = len(df_all)
dedup_cols = ['InvoiceNo', 'StockCode', 'CustomerID', 'Quantity', 'Year', 'Month', 'Day']
df_all = df_all.drop_duplicates(subset=dedup_cols, keep='first')
n_after = len(df_all)

print(f'Rekordy po polaczeniu (przed dedup): {n_before:,}')
print(f'Rekordy po usunieciu duplikatow:     {n_after:,}')
print(f'Usuniete duplikaty miedzyzbiorowe:   {n_before - n_after:,}')
print()
print(f'Zakres dat po integracji: {df_all["InvoiceDate"].min().date()} - {df_all["InvoiceDate"].max().date()}')


# Ostateczna tabela faktow
fact_columns_all = [
    'InvoiceNo', 'StockCode', 'CustomerID', 'InvoiceDate',
    'Year', 'Month', 'Day',
    'Quantity', 'UnitPrice', 'TotalPrice', 'Country'
]

fact_sales_integrated = df_all[[c for c in fact_columns_all if c in df_all.columns]].copy()

print(f'Ostateczna tabela faktow: {fact_sales_integrated.shape}')
fact_sales_integrated.head()


# ---
# ## LOAD - Zapis zintegrowanej tabeli faktow
# 
# Zintegrowana tabela faktow zostaje zapisana do pliku `fact_sales_integrated.csv`. Plik ten stanowi wynik procesu ETL dla obu zrodel danych i zawiera spojny, oczyszczony i wzbogacony zbior gotowy do zaladowania do hurtowni danych.

fact_sales_integrated.to_csv('fact_sales_integrated.csv', index=False)
print('Plik fact_sales_integrated.csv zostal zapisany.')

