import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import time
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# ETAP 1 – Przygotowanie danych
# =============================================================================

print("=" * 60)
print("ETAP 1 – Przygotowanie danych")
print("=" * 60)

# Wczytanie danych
df = pd.read_csv('../lab5/online_retail_II.csv', sep=';', decimal=',')

print(f"\nWczytano {len(df)} rekordów")
print(f"Kolumny: {list(df.columns)}")

# Dynamiczne nazwy kolumn
customer_col = 'Customer ID' if 'Customer ID' in df.columns else 'CustomerID'
price_col    = 'Price'       if 'Price'       in df.columns else 'UnitPrice'
invoice_col  = 'Invoice'

# Parsowanie daty
df['InvoiceDate'] = pd.to_datetime(
    df['InvoiceDate'], format='%d.%m.%Y %H:%M', dayfirst=True, errors='coerce'
)
df['Month'] = df['InvoiceDate'].dt.month
df['Year']  = df['InvoiceDate'].dt.year

# Czyszczenie: usunięcie braków CustomerID i ujemnych/zerowych ilości
df = df.dropna(subset=[customer_col])
df = df[df['Quantity'] > 0]

# Kolumna miary analitycznej
df['TotalPrice'] = df['Quantity'] * df[price_col]

print(f"\nPo czyszczeniu: {len(df)} rekordów")
print(f"Zakres dat: {df['InvoiceDate'].min()} – {df['InvoiceDate'].max()}")
print(f"Brakujące wartości:\n{df.isnull().sum().to_string()}")

# =============================================================================
# ETAP 2 – Agregacja danych trzema metodami
# =============================================================================

print("\n" + "=" * 60)
print("ETAP 2 – Agregacja danych (3 metody x 3 analizy)")
print("=" * 60)

# Pomocnicza funkcja do pomiaru czasu
def measure_time(func, *args, **kwargs):
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    t1 = time.perf_counter()
    return result, t1 - t0

# ── Analiza A: sprzedaż wg kraju ──────────────────────────────────────────────
print("\n── A. Sprzedaż wg kraju ──")

# Metoda 1: groupby()
res_a1, t_a1 = measure_time(
    lambda: df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)
)
print(f"  groupby():      {t_a1*1000:.4f} ms  | top: {res_a1.index[0]} = {res_a1.iloc[0]:,.2f}")

# Metoda 2: pivot_table()
res_a2, t_a2 = measure_time(
    lambda: pd.pivot_table(df, values='TotalPrice', index='Country', aggfunc='sum')['TotalPrice'].sort_values(ascending=False)
)
print(f"  pivot_table():  {t_a2*1000:.4f} ms  | top: {res_a2.index[0]} = {res_a2.iloc[0]:,.2f}")

# Metoda 3: set_index() + groupby(level=0)
df2_country = df.set_index('Country')
res_a3, t_a3 = measure_time(
    lambda: df2_country.groupby(level=0)['TotalPrice'].sum().sort_values(ascending=False)
)
print(f"  set_index():    {t_a3*1000:.4f} ms  | top: {res_a3.index[0]} = {res_a3.iloc[0]:,.2f}")

# ── Analiza B: sprzedaż wg miesiąca ──────────────────────────────────────────
print("\n── B. Sprzedaż wg miesiąca ──")

df_m = df.dropna(subset=['Month'])

# Metoda 1: groupby()
res_b1, t_b1 = measure_time(
    lambda: df_m.groupby(df_m['Month'].astype(int))['TotalPrice'].sum().sort_index()
)
print(f"  groupby():      {t_b1*1000:.4f} ms")

# Metoda 2: pivot_table()
res_b2, t_b2 = measure_time(
    lambda: pd.pivot_table(df_m, values='TotalPrice', index=df_m['Month'].astype(int), aggfunc='sum')['TotalPrice'].sort_index()
)
print(f"  pivot_table():  {t_b2*1000:.4f} ms")

# Metoda 3: set_index() + groupby(level=0)
df2_month = df_m.copy()
df2_month['Month'] = df2_month['Month'].astype(int)
df2_month = df2_month.set_index('Month')
res_b3, t_b3 = measure_time(
    lambda: df2_month.groupby(level=0)['TotalPrice'].sum().sort_index()
)
print(f"  set_index():    {t_b3*1000:.4f} ms")
print(f"\n  Najlepszy miesiąc: {int(res_b1.idxmax())} (sprzedaż: {res_b1.max():,.2f})")

# ── Analiza C: liczba transakcji wg klienta ───────────────────────────────────
print("\n── C. Liczba transakcji wg klienta ──")

# Metoda 1: groupby()
res_c1, t_c1 = measure_time(
    lambda: df.groupby(customer_col)[invoice_col].nunique().sort_values(ascending=False)
)
print(f"  groupby():      {t_c1*1000:.4f} ms  | top klient: {res_c1.index[0]} = {res_c1.iloc[0]} transakcji")

# Metoda 2: pivot_table()
res_c2, t_c2 = measure_time(
    lambda: pd.pivot_table(df, values=invoice_col, index=customer_col, aggfunc=pd.Series.nunique)[invoice_col].sort_values(ascending=False)
)
print(f"  pivot_table():  {t_c2*1000:.4f} ms")

# Metoda 3: set_index() + groupby(level=0)
df2_cust = df[[customer_col, invoice_col]].set_index(customer_col)
res_c3, t_c3 = measure_time(
    lambda: df2_cust.groupby(level=0)[invoice_col].nunique().sort_values(ascending=False)
)
print(f"  set_index():    {t_c3*1000:.4f} ms")

# Zbiorczy słownik czasów (etap 2)
timings_small = {
    'Sprzedaż/kraj':      (t_a1, t_a2, t_a3),
    'Sprzedaż/miesiąc':   (t_b1, t_b2, t_b3),
    'Transakcje/klient':  (t_c1, t_c2, t_c3),
}

# =============================================================================
# ETAP 3 – Symulacja dużej hurtowni danych (x10)
# =============================================================================

print("\n" + "=" * 60)
print("ETAP 3 – Symulacja dużej hurtowni danych (x10)")
print("=" * 60)

large_df = pd.concat([df] * 10, ignore_index=True)
print(f"\nRozmiar powiększonego zbioru: {len(large_df)} rekordów")

large_df_m = large_df.dropna(subset=['Month'])

# A – kraj
_, lt_a1 = measure_time(lambda: large_df.groupby('Country')['TotalPrice'].sum())
_, lt_a2 = measure_time(lambda: pd.pivot_table(large_df, values='TotalPrice', index='Country', aggfunc='sum'))
ldf2c = large_df.set_index('Country')
_, lt_a3 = measure_time(lambda: ldf2c.groupby(level=0)['TotalPrice'].sum())

# B – miesiąc
_, lt_b1 = measure_time(lambda: large_df_m.groupby(large_df_m['Month'].astype(int))['TotalPrice'].sum())
_, lt_b2 = measure_time(lambda: pd.pivot_table(large_df_m, values='TotalPrice', index=large_df_m['Month'].astype(int), aggfunc='sum'))
ldf2m = large_df_m.copy(); ldf2m['Month'] = ldf2m['Month'].astype(int); ldf2m = ldf2m.set_index('Month')
_, lt_b3 = measure_time(lambda: ldf2m.groupby(level=0)['TotalPrice'].sum())

# C – klient
_, lt_c1 = measure_time(lambda: large_df.groupby(customer_col)[invoice_col].nunique())
_, lt_c2 = measure_time(lambda: pd.pivot_table(large_df, values=invoice_col, index=customer_col, aggfunc=pd.Series.nunique))
ldf2cu = large_df[[customer_col, invoice_col]].set_index(customer_col)
_, lt_c3 = measure_time(lambda: ldf2cu.groupby(level=0)[invoice_col].nunique())

timings_large = {
    'Sprzedaż/kraj':      (lt_a1, lt_a2, lt_a3),
    'Sprzedaż/miesiąc':   (lt_b1, lt_b2, lt_b3),
    'Transakcje/klient':  (lt_c1, lt_c2, lt_c3),
}

print("\nCzasy wykonania (ms) – mały zbiór vs powiększony (x10):")
header = f"{'Analiza':<22} {'groupby':>10} {'pivot':>10} {'set_idx':>10}  | {'groupby':>10} {'pivot':>10} {'set_idx':>10}"
print(header)
print("-" * len(header))
for key in timings_small:
    ts = timings_small[key]
    tl = timings_large[key]
    print(f"{key:<22} "
          f"{ts[0]*1000:>10.2f} {ts[1]*1000:>10.2f} {ts[2]*1000:>10.2f}  | "
          f"{tl[0]*1000:>10.2f} {tl[1]*1000:>10.2f} {tl[2]*1000:>10.2f}")

# Współczynniki skalowalności (x10 danych → ile razy wolniej)
print("\nWspółczynniki skalowalności (czas_duży / czas_mały):")
methods = ['groupby()', 'pivot_table()', 'set_index()']
for key in timings_small:
    ts = timings_small[key]
    tl = timings_large[key]
    ratios = [tl[i]/ts[i] if ts[i] > 0 else float('nan') for i in range(3)]
    print(f"  {key:<22}: " + "  ".join(f"{m}: {r:.1f}x" for m, r in zip(methods, ratios)))

# =============================================================================
# ETAP 4 – Wnioski
# =============================================================================

print("\n" + "=" * 60)
print("ETAP 4 – Wnioski i raport końcowy")
print("=" * 60)

# Wyznaczenie najszybszej i najbardziej czytelnej metody
all_times = {'groupby()': [], 'pivot_table()': [], 'set_index()': []}
for key in timings_large:
    tl = timings_large[key]
    all_times['groupby()'].append(tl[0])
    all_times['pivot_table()'].append(tl[1])
    all_times['set_index()'].append(tl[2])

avg_times = {m: sum(v)/len(v) for m, v in all_times.items()}
fastest = min(avg_times, key=avg_times.get)
slowest = max(avg_times, key=avg_times.get)

print(f"""
1. KTÓRA METODA BYŁA NAJSZYBSZA?
   Średnie czasy na dużym zbiorze:
   - groupby():     {avg_times['groupby()']*1000:.2f} ms
   - pivot_table(): {avg_times['pivot_table()']*1000:.2f} ms
   - set_index():   {avg_times['set_index()']*1000:.2f} ms
   Najszybsza: {fastest}
   Najwolniejsza: {slowest}

   groupby() jest zazwyczaj najszybszy, bo bezpośrednio wywołuje
   zoptymalizowane operacje C w silniku Pandas bez budowania
   pełnej struktury pivot. set_index() ma podobną wydajność, ale
   wymaga dodatkowego kosztu przeindeksowania DataFrame.
   pivot_table() jest wolniejszy ze względu na ogólniejszą implementację
   i większy overhead (obsługa wielu wymiarów, fill_value, margins).

2. KTÓRA METODA BYŁA NAJBARDZIEJ CZYTELNA?
   pivot_table() jest najbardziej czytelna dla analityków – składnia
   wprost opisuje co agregujemy (values), po czym (index/columns)
   i jak (aggfunc). groupby() jest czytelna dla programistów Pandas.
   set_index() jest najmniej intuicyjna (groupby(level=0) jest niejasne
   bez znajomości kontekstu).

3. PROBLEMY PRZY BARDZO DUŻYCH HURTOWNIACH DANYCH:
   a) Pamięć RAM – pivot_table() tworzy dwuwymiarową macierz (kraj x miesiąc),
      która przy milionach kategorii może nie zmieścić się w pamięci.
   b) Czas wykonania – wszystkie metody działają jednowątkowo w Pandas;
      przy miliardach rekordów potrzebne są Dask, Spark lub bazy kolumnowe.
   c) Skalowalność – liniowy wzrost czasu może być nieakceptowalny w produkcji;
      konieczne są pre-agregacje (materialized views, summary tables).
   d) Typy danych – pivot_table() z aggfunc=nunique jest bardzo powolne
      na dużych zbiorach (złożoność kwadratowa dla niektórych danych).
   e) I/O – wczytywanie CSV dziesiątek GB jest nieefektywne; formaty
      kolumnowe (Parquet, ORC) są 10–100x szybsze.
""")

# =============================================================================
# WYKRESY
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle('Lab8 – Porównanie metod agregacji danych', fontsize=15, fontweight='bold')

analyses = list(timings_small.keys())
methods_labels = ['groupby()', 'pivot_table()', 'set_index()']
colors = ['#4e79a7', '#f28e2b', '#e15759']
x = range(len(analyses))
w = 0.25

# 1. Czasy – mały zbiór
ax1 = axes[0, 0]
for i, (method, color) in enumerate(zip(methods_labels, colors)):
    vals = [timings_small[a][i] * 1000 for a in analyses]
    bars = ax1.bar([xi + (i-1)*w for xi in x], vals, w, label=method, color=color, edgecolor='white')
ax1.set_xticks(list(x))
ax1.set_xticklabels([a.replace('/', '/\n') for a in analyses], fontsize=9)
ax1.set_ylabel('Czas (ms)')
ax1.set_title('Etap 2 – Czasy agregacji (oryginalny zbiór)')
ax1.legend(fontsize=8)
ax1.grid(axis='y', alpha=0.3)

# 2. Czasy – duży zbiór (x10)
ax2 = axes[0, 1]
for i, (method, color) in enumerate(zip(methods_labels, colors)):
    vals = [timings_large[a][i] * 1000 for a in analyses]
    ax2.bar([xi + (i-1)*w for xi in x], vals, w, label=method, color=color, edgecolor='white')
ax2.set_xticks(list(x))
ax2.set_xticklabels([a.replace('/', '/\n') for a in analyses], fontsize=9)
ax2.set_ylabel('Czas (ms)')
ax2.set_title('Etap 3 – Czasy agregacji (zbiór x10)')
ax2.legend(fontsize=8)
ax2.grid(axis='y', alpha=0.3)

# 3. Współczynniki skalowalności
ax3 = axes[1, 0]
for i, (method, color) in enumerate(zip(methods_labels, colors)):
    ratios = [
        timings_large[a][i] / timings_small[a][i]
        if timings_small[a][i] > 0 else 0
        for a in analyses
    ]
    ax3.bar([xi + (i-1)*w for xi in x], ratios, w, label=method, color=color, edgecolor='white')
ax3.axhline(10, color='red', linestyle='--', linewidth=1, label='Liniowy (x10)')
ax3.set_xticks(list(x))
ax3.set_xticklabels([a.replace('/', '/\n') for a in analyses], fontsize=9)
ax3.set_ylabel('Współczynnik spowolnienia')
ax3.set_title('Skalowalność metod (x10 danych)')
ax3.legend(fontsize=8)
ax3.grid(axis='y', alpha=0.3)

# 4. Sprzedaż wg miesiąca (groupby, oryginalny zbiór)
ax4 = axes[1, 1]
monthly = res_b1.reset_index()
monthly.columns = ['Month', 'TotalPrice']
ax4.bar(monthly['Month'].astype(int), monthly['TotalPrice'] / 1e6,
        color='steelblue', edgecolor='white')
ax4.set_xlabel('Miesiąc')
ax4.set_ylabel('Sprzedaż (mln)')
ax4.set_title('Sprzedaż wg miesiąca (groupby)')
ax4.set_xticks(range(1, 13))
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('lab8_wykresy.png', dpi=150, bbox_inches='tight')
print("Wykresy zapisane do: lab8_wykresy.png")
plt.close()
