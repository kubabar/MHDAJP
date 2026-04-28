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
df2 = pd.read_csv('online_retail_II.csv', sep=';', encoding='ISO-8859-1', decimal=',')
df = pd.concat([df1, df2]).drop_duplicates()

print("=== Wczytane dane ===")
print(f"Łączna liczba wierszy: {len(df)}")
print(f"Kolumny: {list(df.columns)}\n")
 
# =============================================================================
# CZYSZCZENIE DANYCH
# =============================================================================
 
customer_col = 'Customer ID' if 'Customer ID' in df.columns else 'CustomerID'
price_col    = 'Price'       if 'Price'       in df.columns else 'UnitPrice'
 
df = df.dropna(subset=[customer_col])
df = df[df['Quantity'] > 0]
df['TotalPrice'] = df['Quantity'] * df[price_col]
 
# =============================================================================
# CZAS JAKO WYMIAR
# =============================================================================
 
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%d.%m.%Y %H:%M', dayfirst=True)
df['Year']  = df['InvoiceDate'].dt.year
df['Month'] = df['InvoiceDate'].dt.month
 
country_col = 'Country'
 
print("=== Po czyszczeniu ===")
print(f"Liczba wierszy: {len(df)}")
print(f"Zakres dat: {df['InvoiceDate'].min()} – {df['InvoiceDate'].max()}\n")
 
# =============================================================================
# ZADANIE 1 – Top 10 krajów pod względem sprzedaży
# =============================================================================
 
print("=" * 60)
print("ZADANIE 1 – Top 10 krajów pod względem sprzedaży")
print("=" * 60)
 
top10_countries = (
    df.groupby(country_col)['TotalPrice']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={'TotalPrice': 'Sprzedaz_total'})
)
top10_countries['Sprzedaz_total'] = top10_countries['Sprzedaz_total'].round(2)
print(top10_countries.to_string(index=False))
 
# =============================================================================
# ZADANIE 2 – Miesiąc o największej sprzedaży
# =============================================================================
 
print("\n" + "=" * 60)
print("ZADANIE 2 – Miesiąc o największej sprzedaży")
print("=" * 60)
 
monthly_sales = (
    df.groupby(['Year', 'Month'])['TotalPrice']
    .sum()
    .reset_index()
    .rename(columns={'TotalPrice': 'Sprzedaz_total'})
)
best_month = monthly_sales.loc[monthly_sales['Sprzedaz_total'].idxmax()]
print(f"Rok: {int(best_month['Year'])}, Miesiąc: {int(best_month['Month'])}, "
      f"Sprzedaż: {best_month['Sprzedaz_total']:,.2f}")
 
print("\nDrill-down – top 10 miesięcy:")
print(monthly_sales.sort_values('Sprzedaz_total', ascending=False).head(10).to_string(index=False))
 
# =============================================================================
# ZADANIE 3 – Kostka: wiersze=kraj, kolumny=miesiąc, wartości=sprzedaż
# =============================================================================
 
print("\n" + "=" * 60)
print("ZADANIE 3 – Kostka (kraj × miesiąc)")
print("=" * 60)
 
pivot_kraj_miesiac = pd.pivot_table(
    df,
    values='TotalPrice',
    index=country_col,
    columns='Month',
    aggfunc='sum',
    fill_value=0
)
pivot_kraj_miesiac.columns = [f'M{int(m):02d}' for m in pivot_kraj_miesiac.columns]
pivot_kraj_miesiac = pivot_kraj_miesiac.round(2)
print(pivot_kraj_miesiac.head(15).to_string())
print(f"\n... ({len(pivot_kraj_miesiac)} krajów łącznie)")
 
# =============================================================================
# ZADANIE 4 – Dla każdego kraju rok z najwyższą sprzedażą
# =============================================================================
 
print("\n" + "=" * 60)
print("ZADANIE 4 – Najlepszy rok sprzedażowy dla każdego kraju")
print("=" * 60)
 
country_year = (
    df.groupby([country_col, 'Year'])['TotalPrice']
    .sum()
    .reset_index()
    .rename(columns={'TotalPrice': 'Sprzedaz_total'})
)
best_year_per_country = (
    country_year.loc[
        country_year.groupby(country_col)['Sprzedaz_total'].idxmax()
    ]
    .reset_index(drop=True)
    .sort_values('Sprzedaz_total', ascending=False)
)
best_year_per_country['Sprzedaz_total'] = best_year_per_country['Sprzedaz_total'].round(2)
print(best_year_per_country.to_string(index=False))
 
# =============================================================================
# ZADANIE 5 (CHALLENGE) – Top 5 produktów w każdym kraju
# =============================================================================
 
print("\n" + "=" * 60)
print("ZADANIE 5 – Top 5 produktów w każdym kraju")
print("=" * 60)
 
desc_col = 'Description' if 'Description' in df.columns else 'StockCode'
top5_per_country = (
    df.groupby([country_col, desc_col])['TotalPrice']
    .sum()
    .reset_index()
    .rename(columns={'TotalPrice': 'Sprzedaz'})
    .sort_values([country_col, 'Sprzedaz'], ascending=[True, False])
    .groupby(country_col)
    .head(5)
    .reset_index(drop=True)
)
top5_per_country['Sprzedaz'] = top5_per_country['Sprzedaz'].round(2)
 
for kraj in top5_per_country[country_col].unique()[:5]:
    print(f"\n  {kraj}:")
    for _, row in top5_per_country[top5_per_country[country_col] == kraj].iterrows():
        print(f"    {str(row[desc_col])[:50]:<50}  {row['Sprzedaz']:>12,.2f}")
 
# =============================================================================
# BONUS – Wizualizacje (matplotlib only)
# =============================================================================
 
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Online Retail – Analiza OLAP', fontsize=16, fontweight='bold')
 
# --- 1. Słupkowy poziomy – Top 10 krajów ---
ax1 = axes[0, 0]
bars = ax1.barh(
    top10_countries[country_col][::-1],
    top10_countries['Sprzedaz_total'][::-1] / 1e6,
    color='steelblue', edgecolor='white'
)
ax1.set_xlabel('Sprzedaż (mln)')
ax1.set_title('Top 10 krajów – łączna sprzedaż')
ax1.bar_label(bars, fmt='%.2f M', padding=3, fontsize=8)
ax1.set_xlim(0, top10_countries['Sprzedaz_total'].max() / 1e6 * 1.18)
 
# --- 2. Liniowy – sprzedaż miesięczna wg roku ---
ax2 = axes[0, 1]
for year, grp in monthly_sales.groupby('Year'):
    ax2.plot(grp['Month'], grp['Sprzedaz_total'] / 1e6,
             marker='o', label=str(int(year)), linewidth=2)
ax2.set_xlabel('Miesiąc')
ax2.set_ylabel('Sprzedaż (mln)')
ax2.set_title('Sprzedaż miesięczna wg roku')
ax2.set_xticks(range(1, 13))
ax2.legend()
ax2.grid(alpha=0.3)
 
# --- 3. Heatmap – Top 15 krajów × miesiąc (imshow) ---
ax3 = axes[1, 0]
top15_idx = (
    df.groupby(country_col)['TotalPrice'].sum()
    .nlargest(15).index
)
heatmap_data = pivot_kraj_miesiac.loc[
    pivot_kraj_miesiac.index.isin(top15_idx)
].copy() / 1e3  # tysiące
 
im = ax3.imshow(heatmap_data.values, aspect='auto', cmap='YlOrRd')
ax3.set_xticks(range(len(heatmap_data.columns)))
ax3.set_xticklabels(heatmap_data.columns, fontsize=8)
ax3.set_yticks(range(len(heatmap_data.index)))
ax3.set_yticklabels(heatmap_data.index, fontsize=8)
plt.colorbar(im, ax=ax3, label='Sprzedaż (tys.)')
vmax = heatmap_data.values.max()
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        val = heatmap_data.values[i, j]
        if val > 0:
            color = 'white' if val > vmax * 0.6 else 'black'
            ax3.text(j, i, f'{val:.0f}', ha='center', va='center',
                     fontsize=5, color=color)
ax3.set_title('Heatmap: kraj × miesiąc (top 15, tys.)')
ax3.set_xlabel('Miesiąc')
ax3.set_ylabel('Kraj')
 
# --- 4. Słupkowy – najlepszy rok dla top 10 krajów ---
ax4 = axes[1, 1]
top10_names = top10_countries[country_col].tolist()
bpy = best_year_per_country[best_year_per_country[country_col].isin(top10_names)]
palette = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f']
year_colors = {yr: palette[i % len(palette)]
               for i, yr in enumerate(sorted(bpy['Year'].unique()))}
for _, row in bpy.iterrows():
    ax4.bar(row[country_col], row['Sprzedaz_total'] / 1e6,
            color=year_colors.get(row['Year'], 'gray'),
            label=str(int(row['Year'])))
ax4.set_xlabel('Kraj')
ax4.set_ylabel('Sprzedaż (mln)')
ax4.set_title('Najlepszy rok sprzedażowy (top 10 krajów)')
ax4.tick_params(axis='x', rotation=45)
handles, labels = ax4.get_legend_handles_labels()
ax4.legend(dict(zip(labels, handles)).values(),
           dict(zip(labels, handles)).keys(), title='Rok')
 
plt.tight_layout()
plt.savefig('olap_wykresy.png', dpi=150, bbox_inches='tight')
print("\n\nWykresy zapisane do: olap_wykresy.png")
plt.close()
