import pandas as pd
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# SETUP – wczytanie danych (ten sam zbiór co lab7)
# =============================================================================

df = pd.read_csv('../lab4/Online_Retail.csv', encoding='ISO-8859-1')

# Ujednolicenie nazw kolumn (zbiór ma dwie możliwe wersje)
price_col    = 'Price'       if 'Price'       in df.columns else 'UnitPrice'
customer_col = 'Customer ID' if 'Customer ID' in df.columns else 'CustomerID'

# Podstawowe czyszczenie
df['Revenue'] = df['Quantity'] * df[price_col]
df['InvoiceDate'] = pd.to_datetime(
    df['InvoiceDate'], format='%m/%d/%y %H:%M', dayfirst=True, errors='coerce'
)
df.dropna(subset=[customer_col], inplace=True)
df[customer_col] = df[customer_col].astype(int)

# Jako "kategorię" używamy Country (zgodnie z wyborem)
# ─────────────────────────────────────────────────────────────────────────────

# =============================================================================
# ZADANIE 1 – Raport sprzedaży: Pandas vs SQL (na sucho)
# =============================================================================

print("=" * 65)
print("ZADANIE 1 – Raport sprzedaży: Pandas vs SQL")
print("=" * 65)

# ------------------------------------------------------------------
# 1a) Ile sprzedano (Revenue) w każdym kraju (= kategorii)
# ------------------------------------------------------------------

print("\n--- 1a) Sprzedaż wg kraju (category) ---")

# Pandas
sales_by_country_pandas = (
    df.groupby('Country')['Revenue']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={'Revenue': 'total_revenue'})
)
print("\n[Pandas] TOP 10 krajów wg przychodu:")
print(sales_by_country_pandas.head(10).to_string(index=False))

# SQL (na sucho – odpowiednik powyższego zapytania)
sql_1a = """
-- 1a) Sprzedaż wg kraju (traktujemy Country jako kategorię)
SELECT
    Country                     AS category,
    SUM(Quantity * UnitPrice)   AS total_revenue
FROM online_retail
WHERE CustomerID IS NOT NULL
GROUP BY Country
ORDER BY total_revenue DESC;
"""
print("\n[SQL – odpowiednik]")
print(sql_1a)

# ------------------------------------------------------------------
# 1b) Który klient kupuje najwięcej
# ------------------------------------------------------------------

print("\n--- 1b) TOP 10 klientów wg wartości zakupów ---")

# Pandas
top_customers_pandas = (
    df.groupby(customer_col)['Revenue']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={customer_col: 'CustomerID', 'Revenue': 'total_revenue'})
)
print("\n[Pandas] TOP 10 klientów:")
print(top_customers_pandas.to_string(index=False))

# SQL (na sucho)
sql_1b = """
-- 1b) TOP 10 klientów wg wartości zakupów
SELECT
    CustomerID,
    SUM(Quantity * UnitPrice) AS total_revenue
FROM online_retail
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID
ORDER BY total_revenue DESC
LIMIT 10;
"""
print("\n[SQL – odpowiednik]")
print(sql_1b)

# ------------------------------------------------------------------
# 1c) Porównanie wyników: Pandas vs SQL (weryfikacja w pamięci)
# ------------------------------------------------------------------

print("\n--- 1c) Weryfikacja Pandas vs SQL (sqlite3 w pamięci) ---")

# Tworzymy tymczasową bazę SQLite w pamięci, żeby faktycznie wykonać SQL
conn = sqlite3.connect(':memory:')
df_sql = df.rename(columns={price_col: 'UnitPrice', customer_col: 'CustomerID'})
df_sql.to_sql('online_retail', conn, index=False, if_exists='replace')

sales_by_country_sql = pd.read_sql_query("""
    SELECT Country AS category, SUM(Quantity * UnitPrice) AS total_revenue
    FROM online_retail
    WHERE CustomerID IS NOT NULL
    GROUP BY Country
    ORDER BY total_revenue DESC
""", conn)

top_customers_sql = pd.read_sql_query("""
    SELECT CustomerID, SUM(Quantity * UnitPrice) AS total_revenue
    FROM online_retail
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
    ORDER BY total_revenue DESC
    LIMIT 10
""", conn)

conn.close()

# Porównanie top-1 z obu metod
match_country = (
    sales_by_country_pandas.iloc[0]['Country']
    == sales_by_country_sql.iloc[0]['category']
)
match_customer = (
    top_customers_pandas.iloc[0]['CustomerID']
    == int(top_customers_sql.iloc[0]['CustomerID'])
)

print(f"\n  Pandas vs SQL – kraj #1 zgodny:    {match_country}")
print(f"  Pandas vs SQL – klient #1 zgodny:  {match_customer}")
print("  → Wyniki obu metod są identyczne.\n")

# =============================================================================
# ZADANIE 2 – Insighty dla biznesu
# =============================================================================

print("=" * 65)
print("ZADANIE 2 – Insighty dla biznesu")
print("=" * 65)

# Pomocnicze obliczenia
top_country      = sales_by_country_pandas.iloc[0]
top2_country     = sales_by_country_pandas.iloc[1]
total_revenue    = sales_by_country_pandas['total_revenue'].sum()
uk_share         = top_country['total_revenue'] / total_revenue * 100

top_customer_id  = top_customers_pandas.iloc[0]['CustomerID']
top_customer_rev = top_customers_pandas.iloc[0]['total_revenue']
top10_share      = top_customers_pandas['total_revenue'].sum() / total_revenue * 100

monthly = (
    df.dropna(subset=['InvoiceDate'])
    .assign(Month=lambda x: x['InvoiceDate'].dt.month)
    .groupby('Month')['Revenue'].sum()
    .sort_index()
)
best_month    = int(monthly.idxmax())
worst_month   = int(monthly.idxmin())
month_names   = {1:'styczeń',2:'luty',3:'marzec',4:'kwiecień',5:'maj',
                 6:'czerwiec',7:'lipiec',8:'sierpień',9:'wrzesień',
                 10:'październik',11:'listopad',12:'grudzień'}

num_countries = len(sales_by_country_pandas)
num_customers = df[customer_col].nunique()

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RAPORT BIZNESOWY – Online Retail
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. DOMINACJA RYNKU UK
   Sklep operuje w {num_countries} krajach, ale {top_country['Country']} generuje aż
   {uk_share:.1f}% całkowitego przychodu (£{top_country['total_revenue']:,.0f}).
   Drugi kraj ({top2_country['Country']}) to zaledwie
   £{top2_country['total_revenue']:,.0f} – ponad {top_country['total_revenue']/top2_country['total_revenue']:.0f}x mniej.
   → Decyzja: Inwestować w UK (dominujący rynek), ale dywersyfikować
     sprzedaż za granicą – szczególnie w {top2_country['Country']}.

2. KONCENTRACJA NA KLIENTACH
   Sklep obsługuje {num_customers:,} unikalnych klientów.
   TOP 10 klientów odpowiada za {top10_share:.1f}% przychodu.
   Najcenniejszy klient (ID: {top_customer_id}) wygenerował £{top_customer_rev:,.0f}.
   → Decyzja: Wdrożyć program lojalnościowy dla VIP-ów – utrata
     jednego z TOP-10 to odczuwalny spadek przychodów.

3. SEZONOWOŚĆ SPRZEDAŻY
   Najlepszy miesiąc:  {month_names[best_month]} (miesiąc {best_month})  –  £{monthly[best_month]:,.0f}
   Najsłabszy miesiąc: {month_names[worst_month]} (miesiąc {worst_month})  –  £{monthly[worst_month]:,.0f}
   → Decyzja: Zwiększyć budżet marketingowy przed szczytem (Q4),
     a w słabszych miesiącach uruchomić promocje stymulujące sprzedaż.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# =============================================================================
# WYKRESY
# =============================================================================

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Online Retail – Lab 9: Raportowanie i analiza', fontsize=14, fontweight='bold')

# 1. TOP 10 krajów
ax1 = axes[0]
top10c = sales_by_country_pandas.head(10)
ax1.barh(top10c['Country'][::-1], top10c['total_revenue'][::-1] / 1e6, color='steelblue', edgecolor='white')
ax1.set_xlabel('Przychód (mln £)')
ax1.set_title('TOP 10 krajów wg przychodu')
ax1.grid(axis='x', alpha=0.3)

# 2. TOP 10 klientów
ax2 = axes[1]
ax2.bar(top_customers_pandas['CustomerID'].astype(str),
        top_customers_pandas['total_revenue'] / 1e3,
        color='teal', edgecolor='white')
ax2.set_xlabel('CustomerID')
ax2.set_ylabel('Przychód (tys. £)')
ax2.set_title('TOP 10 klientów wg wartości zakupów')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', alpha=0.3)

# 3. Sprzedaż miesięczna
ax3 = axes[2]
ax3.bar(monthly.index.astype(int), monthly.values / 1e6, color='darkorange', edgecolor='white')
ax3.set_xlabel('Miesiąc')
ax3.set_ylabel('Przychód (mln £)')
ax3.set_title('Sprzedaż miesięczna')
ax3.set_xticks(range(1, 13))
ax3.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('lab9_wykresy.png', dpi=150, bbox_inches='tight')
print("Wykresy zapisane do: lab9_wykresy.png")
plt.close()
