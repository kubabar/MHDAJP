import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# SETUP – wczytanie i połączenie danych
# =============================================================================

df1 = pd.read_csv('../lab4/Online_Retail.csv',    encoding='ISO-8859-1')
df2 = pd.read_csv('../lab5/online_retail_II.csv', sep=';', encoding='ISO-8859-1', decimal=',')
df = pd.concat([df1, df2]).drop_duplicates()

customer_col = 'Customer ID' if 'Customer ID' in df.columns else 'CustomerID'
price_col    = 'Price'       if 'Price'       in df.columns else 'UnitPrice'

df = df.dropna(subset=[customer_col])
df = df[df['Quantity'] > 0]
df['Revenue'] = df['Quantity'] * df[price_col]
df[customer_col] = df[customer_col].astype(int)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%d.%m.%Y %H:%M', dayfirst=True)
df['Month'] = df['InvoiceDate'].dt.month

# =============================================================================
# ZADANIE 1 – Tabela pivot: Country × Month, wartości = suma Revenue
# =============================================================================
 
print("=" * 60)
print("ZADANIE 1 – Tabela pivot (Country × Month)")
print("=" * 60)
 
pivot = df.pivot_table(
    values='Revenue',
    index='Country',
    columns='Month',
    aggfunc='sum',
    fill_value=0
)
pivot.columns = [f'M{int(m):02d}' for m in pivot.columns]
print(pivot.round(2).to_string())
 
# Które miesiące mają najwyższą sprzedaż (suma po wszystkich krajach)
monthly_totals = pivot.sum().sort_values(ascending=False)
print("\nMiesiące wg łącznej sprzedaży (malejąco):")
print(monthly_totals.round(2).to_string())
print(f"\nNajlepszy miesiąc: {monthly_totals.index[0]}  ({monthly_totals.iloc[0]:,.2f})")
 
# =============================================================================
# ZADANIE 2 – Ranking krajów (TOP 10)
# =============================================================================
 
print("\n" + "=" * 60)
print("ZADANIE 2 – Ranking krajów (TOP 10)")
print("=" * 60)
 
ranking = (
    df.groupby('Country')['Revenue']
    .sum()
    .sort_values(ascending=False)
)
top10 = ranking.head(10).reset_index()
top10.columns = ['Country', 'Revenue']
top10['Revenue'] = top10['Revenue'].round(2)
print(top10.to_string(index=False))
 
# =============================================================================
# ZADANIE 3 – Analiza klientów
# =============================================================================
 
print("\n" + "=" * 60)
print("ZADANIE 3 – Analiza klientów")
print("=" * 60)
 
customers = df.groupby(customer_col)['Revenue'].sum()
 
top_customers = customers.sort_values(ascending=False).head(10).reset_index()
top_customers.columns = ['CustomerID', 'Revenue']
top_customers['Revenue'] = top_customers['Revenue'].round(2)
print("TOP 10 klientów:")
print(top_customers.to_string(index=False))
 
avg_revenue = customers.mean()
print(f"\nŚredni przychód na klienta: {avg_revenue:,.2f}")
 
# =============================================================================
# ZADANIE 4 – Segmentacja krajów (kwartyle)
# =============================================================================
 
print("\n" + "=" * 60)
print("ZADANIE 4 – Segmentacja krajów")
print("=" * 60)
 
country_revenue = ranking.reset_index()
country_revenue.columns = ['Country', 'Revenue']
 
q75 = country_revenue['Revenue'].quantile(0.75)
q25 = country_revenue['Revenue'].quantile(0.25)
 
def segment(rev):
    if rev >= q75:
        return 'Wysoki (Top 25%)'
    elif rev >= q25:
        return 'Sredni (50%)'
    else:
        return 'Niski (Dolne 25%)'
 
country_revenue['Segment'] = country_revenue['Revenue'].apply(segment)
 
print(f"Próg Top 25%:    {q75:,.2f}")
print(f"Próg Dolne 25%:  {q25:,.2f}\n")
print(country_revenue.to_string(index=False))
 
print("\nLiczba krajów w segmentach:")
print(country_revenue['Segment'].value_counts().to_string())
 
# =============================================================================
# ZADANIE 5 – Wnioski (automatycznie wyliczone z danych)
# =============================================================================
 
print("\n" + "=" * 60)
print("ZADANIE 5 – Wnioski")
print("=" * 60)
 
top1_country  = top10.iloc[0]['Country']
top1_revenue  = top10.iloc[0]['Revenue']
total_revenue = country_revenue['Revenue'].sum()
top1_share    = top1_revenue / total_revenue * 100
top3_share    = country_revenue.head(3)['Revenue'].sum() / total_revenue * 100
 
best_month_name  = monthly_totals.index[0]
worst_month_name = monthly_totals.index[-1]
ratio            = monthly_totals.iloc[0] / monthly_totals.iloc[-1]
 
high_seg_count = (country_revenue['Segment'] == 'Wysoki (Top 25%)').sum()
low_seg_count  = (country_revenue['Segment'] == 'Niski (Dolne 25%)').sum()
 
print(f"""
1. Które kraje są kluczowe?
   Dominuje '{top1_country}' z przychodem {top1_revenue:,.0f}
   ({top1_share:.1f}% całkowitej sprzedaży).
   TOP 3 kraje generują łącznie {top3_share:.1f}% przychodu.
   Sprzedaż jest silnie skoncentrowana – {high_seg_count} kraje w segmencie
   wysokim odpowiadają za większość obrotu.
 
2. Czy sprzedaż jest równomierna między krajami?
   Nie. {low_seg_count} krajów należy do segmentu niskiego (<= {q25:,.0f}),
   podczas gdy tylko {high_seg_count} krajów przekracza próg {q75:,.0f}.
   Rozkład jest silnie asymetryczny (długi ogon).
 
3. Czy widać sezonowość?
   Najlepszy miesiąc to {best_month_name} ({monthly_totals.iloc[0]:,.0f}),
   najsłabszy to {worst_month_name} ({monthly_totals.iloc[-1]:,.0f}).
   Stosunek najlepszego do najsłabszego miesiąca wynosi {ratio:.1f}x,
   co wskazuje na wyraźną sezonowość (szczyt sprzedaży w Q4).
""")
 
# =============================================================================
# WYKRESY
# =============================================================================
 
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle('Online Retail – Lab 6: Analiza danych', fontsize=15, fontweight='bold')
 
# 1. Sprzedaż miesięczna (suma po wszystkich krajach)
ax1 = axes[0, 0]
months = [int(m[1:]) for m in monthly_totals.index]
vals   = monthly_totals.values / 1e6
sorted_pairs = sorted(zip(months, vals))
months_s, vals_s = zip(*sorted_pairs)
ax1.bar(months_s, vals_s, color='teal', edgecolor='white')
ax1.set_xlabel('Miesiąc')
ax1.set_ylabel('Revenue (mln)')
ax1.set_title('Zadanie 1 – Sprzedaż wg miesiąca')
ax1.set_xticks(range(1, 13))
ax1.grid(axis='y', alpha=0.3)
 
# 2. TOP 10 krajów
ax2 = axes[0, 1]
bars = ax2.barh(
    top10['Country'][::-1],
    top10['Revenue'][::-1] / 1e6,
    color='steelblue', edgecolor='white'
)
ax2.set_xlabel('Revenue (mln)')
ax2.set_title('Zadanie 2 – TOP 10 krajów')
ax2.bar_label(bars, fmt='%.2f M', padding=3, fontsize=8)
ax2.set_xlim(0, top10['Revenue'].max() / 1e6 * 1.18)
 
# 3. TOP 10 klientów
ax3 = axes[1, 0]
bars3 = ax3.barh(
    top_customers['CustomerID'].astype(str)[::-1],
    top_customers['Revenue'][::-1] / 1e3,
    color='darkorange', edgecolor='white'
)
ax3.set_xlabel('Revenue (tys.)')
ax3.set_title('Zadanie 3 – TOP 10 klientów')
ax3.bar_label(bars3, fmt='%.1f k', padding=3, fontsize=8)
ax3.set_xlim(0, top_customers['Revenue'].max() / 1e3 * 1.18)
 
# 4. Segmentacja – scatter: oś X = przychód, oś Y = segment, etykieta = kraj
ax4 = axes[1, 1]
seg_colors = {
    'Wysoki (Top 25%)': '#2ecc71',
    'Sredni (50%)':     '#3498db',
    'Niski (Dolne 25%)':'#e74c3c',
}
seg_order = ['Niski (Dolne 25%)', 'Sredni (50%)', 'Wysoki (Top 25%)']
y_pos = {s: i for i, s in enumerate(seg_order)}
 
for _, row in country_revenue.iterrows():
    y = y_pos[row['Segment']]
    ax4.scatter(row['Revenue'] / 1e3, y,
                color=seg_colors[row['Segment']], s=60, zorder=3)
    ax4.text(row['Revenue'] / 1e3, y + 0.07, row['Country'],
             ha='center', va='bottom', fontsize=5.5, rotation=45)
 
ax4.set_yticks(range(len(seg_order)))
ax4.set_yticklabels(seg_order, fontsize=8)
ax4.set_xscale('log')
ax4.set_xlabel('Revenue (tys.) – skala logarytmiczna')
ax4.set_title('Zadanie 4 – Segmentacja krajów')
ax4.grid(axis='x', alpha=0.3)
ax4.set_ylim(-0.5, len(seg_order) - 0.3)
 
plt.tight_layout()
plt.savefig('lab6_wykresy.png', dpi=150, bbox_inches='tight')
print("Wykresy zapisane do: lab6_wykresy.png")
plt.close()