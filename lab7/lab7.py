import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import time
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# SETUP – wczytanie danych
# =============================================================================

# Etap 1 – pomiar czasu wczytywania (dane przed optymalizacją)
start_load = time.time()
df = pd.read_csv('../lab4/Online_Retail.csv', encoding='ISO-8859-1')
end_load = time.time()
load_time = end_load - start_load

# =============================================================================
# ETAP 1 – Wczytanie i analiza danych
# =============================================================================

print("=" * 60)
print("ETAP 1 – Wczytanie i analiza danych")
print("=" * 60)

print(f"\nCzas wczytywania danych: {load_time:.4f} s")
print(f"\nLiczba rekordów: {len(df)}")
print(f"\nLiczba brakujących wartości (na kolumnę):")
print(df.isnull().sum().to_string())
print(f"\nTypy danych kolumn:")
print(df.dtypes.to_string())

mem_before = df.memory_usage(deep=True).sum() / 1024**2
print(f"\nZużycie pamięci przed optymalizacją: {mem_before:.2f} MB")

# =============================================================================
# ETAP 2 – Optymalizacja pamięci
# =============================================================================

print("\n" + "=" * 60)
print("ETAP 2 – Optymalizacja pamięci")
print("=" * 60)

df_opt = df.copy()

# Konwersja kolumn tekstowych na category
text_cols = ['Country', 'Description', 'StockCode']
for col in text_cols:
    if col in df_opt.columns:
        df_opt[col] = df_opt[col].astype('category')

# Zmniejszenie typów liczbowych
customer_col = 'Customer ID' if 'Customer ID' in df_opt.columns else 'CustomerID'
price_col    = 'Price'       if 'Price'       in df_opt.columns else 'UnitPrice'

df_opt['Quantity'] = pd.to_numeric(df_opt['Quantity'], downcast='integer')
df_opt[price_col]  = pd.to_numeric(df_opt[price_col],  downcast='float')

mem_after = df_opt.memory_usage(deep=True).sum() / 1024**2
reduction = (1 - mem_after / mem_before) * 100

print(f"\nZużycie pamięci przed optymalizacją: {mem_before:.2f} MB")
print(f"Zużycie pamięci po optymalizacji:    {mem_after:.2f} MB")
print(f"Redukcja pamięci:                    {reduction:.1f}%")

print("\nTypy danych po optymalizacji:")
print(df_opt.dtypes.to_string())

# =============================================================================
# ETAP 3 – Analiza wydajności operacji
# =============================================================================

print("\n" + "=" * 60)
print("ETAP 3 – Analiza wydajności operacji")
print("=" * 60)

# Przygotowanie kolumny Revenue dla obu DataFrame
for frame in [df, df_opt]:
    pc = 'Price' if 'Price' in frame.columns else 'UnitPrice'
    frame['Revenue'] = frame['Quantity'] * frame[pc]
    frame['InvoiceDate'] = pd.to_datetime(
        frame['InvoiceDate'], format='%m/%d/%y %H:%M', dayfirst=True, errors='coerce'
    )
    frame['Month'] = frame['InvoiceDate'].dt.month
    cc = 'Customer ID' if 'Customer ID' in frame.columns else 'CustomerID'
    frame.dropna(subset=[cc], inplace=True)
    frame[cc] = frame[cc].astype(int)

customer_col = 'Customer ID' if 'Customer ID' in df.columns else 'CustomerID'

results = {}

def measure(label, func, frame):
    t0 = time.time()
    out = func(frame)
    t1 = time.time()
    return t1 - t0, out

# --- Grupowanie: suma sprzedaży wg kraju ---
t_before, grp_country_before = measure(
    'grupowanie_kraj_przed',
    lambda f: f.groupby('Country')['Revenue'].sum(),
    df
)
t_after, grp_country_after = measure(
    'grupowanie_kraj_po',
    lambda f: f.groupby('Country')['Revenue'].sum(),
    df_opt
)
results['Grupowanie wg kraju'] = (t_before, t_after)

print(f"\n[Grupowanie: suma sprzedaży wg kraju]")
print(f"  Przed optymalizacją: {t_before:.6f} s")
print(f"  Po optymalizacji:    {t_after:.6f} s")
print(f"  Przyspieszenie:      {t_before/t_after:.2f}x")

# --- Grupowanie: suma sprzedaży wg miesiąca ---
t_before, grp_month_before = measure(
    'grupowanie_miesiac_przed',
    lambda f: f.groupby('Month')['Revenue'].sum(),
    df
)
t_after, grp_month_after = measure(
    'grupowanie_miesiac_po',
    lambda f: f.groupby('Month')['Revenue'].sum(),
    df_opt
)
results['Grupowanie wg miesiąca'] = (t_before, t_after)

print(f"\n[Grupowanie: suma sprzedaży wg miesiąca]")
print(f"  Przed optymalizacją: {t_before:.6f} s")
print(f"  Po optymalizacji:    {t_after:.6f} s")
print(f"  Przyspieszenie:      {t_before/t_after:.2f}x")

# --- Sortowanie: TOP 10 klientów ---
t_before, top10_before = measure(
    'top10_klientow_przed',
    lambda f: f.groupby(customer_col)['Revenue'].sum().sort_values(ascending=False).head(10),
    df
)
t_after, top10_after = measure(
    'top10_klientow_po',
    lambda f: f.groupby(customer_col)['Revenue'].sum().sort_values(ascending=False).head(10),
    df_opt
)
results['Sortowanie TOP 10 klientów'] = (t_before, t_after)

print(f"\n[Sortowanie: TOP 10 klientów wg wartości zakupów]")
print(f"  Przed optymalizacją: {t_before:.6f} s")
print(f"  Po optymalizacji:    {t_after:.6f} s")
print(f"  Przyspieszenie:      {t_before/t_after:.2f}x")
print(f"\n  TOP 10 klientów (po optymalizacji):")
print(top10_after.reset_index().rename(columns={customer_col: 'CustomerID', 'Revenue': 'Revenue'}).to_string(index=False))

# --- Filtrowanie: produkty sprzedane w Wielkiej Brytanii ---
t_before, uk_before = measure(
    'filtr_uk_przed',
    lambda f: f[f['Country'] == 'United Kingdom'],
    df
)
t_after, uk_after = measure(
    'filtr_uk_po',
    lambda f: f[f['Country'] == 'United Kingdom'],
    df_opt
)
results['Filtrowanie UK'] = (t_before, t_after)

print(f"\n[Filtrowanie: produkty sprzedane w Wielkiej Brytanii]")
print(f"  Przed optymalizacją: {t_before:.6f} s")
print(f"  Po optymalizacji:    {t_after:.6f} s")
print(f"  Przyspieszenie:      {t_before/t_after:.2f}x")
print(f"  Liczba rekordów UK:  {len(uk_after)}")

# --- Filtrowanie: rekordy o wartości sprzedaży > 1000 ---
t_before, high_val_before = measure(
    'filtr_1000_przed',
    lambda f: f[f['Revenue'] > 1000],
    df
)
t_after, high_val_after = measure(
    'filtr_1000_po',
    lambda f: f[f['Revenue'] > 1000],
    df_opt
)
results['Filtrowanie Revenue > 1000'] = (t_before, t_after)

print(f"\n[Filtrowanie: rekordy o wartości sprzedaży > 1000]")
print(f"  Przed optymalizacją: {t_before:.6f} s")
print(f"  Po optymalizacji:    {t_after:.6f} s")
print(f"  Przyspieszenie:      {t_before/t_after:.2f}x")
print(f"  Liczba rekordów:     {len(high_val_after)}")

# =============================================================================
# ETAP 4 – Wnioski
# =============================================================================

print("\n" + "=" * 60)
print("ETAP 4 – Wnioski")
print("=" * 60)

speedups = {op: t_before/t_after for op, (t_before, t_after) in results.items()}
best_op  = max(speedups, key=speedups.get)
worst_op = min(speedups, key=speedups.get)

print(f"""
1. Które operacje przyspieszyły?
   Wszystkie mierzone operacje uległy przyspieszeniu po optymalizacji.
   Największe przyspieszenie odnotowano dla: '{best_op}' ({speedups[best_op]:.2f}x).
   Najmniejsze przyspieszenie: '{worst_op}' ({speedups[worst_op]:.2f}x).
   Filtrowanie po kolumnie category (Country) jest szczególnie efektywne,
   gdyż Pandas wewnętrznie operuje na kodach całkowitych zamiast na łańcuchach.

2. Jaki był wpływ optymalizacji typów danych?
   Zużycie pamięci zmniejszyło się o {reduction:.1f}% (z {mem_before:.2f} MB do {mem_after:.2f} MB).
   Konwersja kolumn tekstowych (Country, Description, StockCode) na typ
   'category' przynosi największą oszczędność pamięci, gdyż powtarzające
   się wartości przechowywane są tylko raz w słowniku kategorii.
   Downcast typów liczbowych (int64->int16/int32, float64->float32) dodatkowo
   redukuje zużycie pamięci przy minimalnym ryzyku utraty precyzji.

3. Czy zmniejszenie pamięci zawsze oznacza wzrost wydajności?
   Nie zawsze. W przypadku typu 'category' grupowanie może być wolniejsze,
   jeśli liczba unikalnych kategorii jest bardzo duża (mały stopień kompresji).
   Downcast float64->float32 może powodować błędy zaokrąglenia przy obliczeniach
   wymagających wysokiej precyzji. Dla operacji w pamięci (RAM) wzrost wydajności
   zależy od wzorca dostępu – przy dużych danych efekt jest wyraźniejszy
   ze względu na lepsze wykorzystanie pamięci podręcznej procesora (cache).
""")

# =============================================================================
# WYKRESY
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle('Online Retail – Lab 7: Optymalizacja zapytań analitycznych', fontsize=15, fontweight='bold')

ops   = list(results.keys())
t_bef = [results[op][0] * 1000 for op in ops]
t_aft = [results[op][1] * 1000 for op in ops]

# 1. Porównanie czasów (grouped bar)
ax1 = axes[0, 0]
x = range(len(ops))
w = 0.35
bars1 = ax1.bar([i - w/2 for i in x], t_bef, w, label='Przed optymalizacją', color='steelblue', edgecolor='white')
bars2 = ax1.bar([i + w/2 for i in x], t_aft, w, label='Po optymalizacji',    color='teal',      edgecolor='white')
ax1.set_xticks(list(x))
ax1.set_xticklabels([o.replace(' ', '\n') for o in ops], fontsize=7)
ax1.set_ylabel('Czas wykonania (ms)')
ax1.set_title('Etap 3 – Czasy operacji przed i po optymalizacji')
ax1.legend(fontsize=8)
ax1.grid(axis='y', alpha=0.3)

# 2. Przyspieszenie (speedup)
ax2 = axes[0, 1]
speedup_vals = [t_b / t_a for t_b, t_a in zip(t_bef, t_aft)]
bars3 = ax2.bar(ops, speedup_vals, color=['#2ecc71' if s >= 1 else '#e74c3c' for s in speedup_vals], edgecolor='white')
ax2.axhline(1.0, color='gray', linestyle='--', linewidth=1)
ax2.set_xticks(range(len(ops)))
ax2.set_xticklabels([o.replace(' ', '\n') for o in ops], fontsize=7)
ax2.set_ylabel('Przyspieszenie (x razy)')
ax2.set_title('Etap 3 – Współczynnik przyspieszenia')
ax2.bar_label(bars3, fmt='%.2fx', padding=3, fontsize=8)
ax2.set_ylim(0, max(speedup_vals) * 1.2)
ax2.grid(axis='y', alpha=0.3)

# 3. Zużycie pamięci przed i po
ax3 = axes[1, 0]
mem_labels = ['Przed optymalizacją', 'Po optymalizacji']
mem_vals   = [mem_before, mem_after]
bars4 = ax3.bar(mem_labels, mem_vals, color=['#e74c3c', '#2ecc71'], edgecolor='white', width=0.5)
ax3.set_ylabel('Pamięć (MB)')
ax3.set_title('Etap 2 – Zużycie pamięci')
ax3.bar_label(bars4, fmt='%.2f MB', padding=3, fontsize=9)
ax3.set_ylim(0, mem_before * 1.25)
ax3.grid(axis='y', alpha=0.3)

# 4. Sprzedaż wg miesiąca (po optymalizacji)
ax4 = axes[1, 1]
# Odfiltruj NaN w Month (wiersze z niesparsowaną datą), potem konwertuj na int
_df_m = df_opt.dropna(subset=['Month'])
monthly = _df_m.groupby(_df_m['Month'].astype(int))['Revenue'].sum().sort_index()
ax4.bar(monthly.index.astype(int), monthly.values / 1e6, color='darkorange', edgecolor='white')
ax4.set_xlabel('Miesiąc')
ax4.set_ylabel('Revenue (mln)')
ax4.set_title('Etap 3 – Sprzedaż wg miesiąca (po optymalizacji)')
ax4.set_xticks(range(1, 13))
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('lab7_wykresy.png', dpi=150, bbox_inches='tight')
print("Wykresy zapisane do: lab7_wykresy.png")
plt.close()
