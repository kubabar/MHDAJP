import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")

# zamiana nazwa krajow na kody iso3 (1.3)
ISO3_dict = {"Aruba": "ABW", "Afghanistan": "AFG", "Angola": "AGO", "Anguilla": "AIA", "Åland Islands": "ALA", "Albania": "ALB", "Andorra": "AND", "United Arab Emirates": "ARE", "Argentina": "ARG", "Armenia": "ARM", "American Samoa": "ASM", "Antarctica": "ATA", "French Southern and Antarctic Lands": "ATF", "Antigua and Barbuda": "ATG", "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE", "Burundi": "BDI", "Belgium": "BEL", "Benin": "BEN", "Caribbean Netherlands": "BES", "Burkina Faso": "BFA", "Bangladesh": "BGD", "Bulgaria": "BGR", "Bahrain": "BHR", "The Bahamas": "BHS", "Bosnia and Herzegovina": "BIH", "Saint Barthélemy": "BLM", "Belarus": "BLR", "Belize": "BLZ", "Bermuda": "BMU", "Bolivia": "BOL", "Brazil": "BRA", "Barbados": "BRB", "Brunei": "BRN", "Bhutan": "BTN", "Bouvet Island": "BVT", "Botswana": "BWA", "Central African Republic": "CAF", "Canada": "CAN", "Cocos (Keeling) Islands": "CCK", "Switzerland": "CHE", "Chile": "CHL", "China": "CHN", "Ivory Coast": "CIV", "Cameroon": "CMR", "Democratic Republic of the Congo": "COD", "Republic of the Congo": "COG", "Cook Islands": "COK", "Colombia": "COL", "Comoros": "COM", "Cabo Verde": "CPV", "Costa Rica": "CRI", "Cuba": "CUB", "Curaçao": "CUW", "Christmas Island": "CXR", "Cayman Islands": "CYM", "Cyprus": "CYP", "Czechia": "CZE", "Germany": "DEU", "Djibouti": "DJI", "Dominica": "DMA", "Denmark": "DNK", "Dominican Republic": "DOM", "Algeria": "DZA", "Ecuador": "ECU", "Egypt": "EGY", "Eritrea": "ERI", "Western Sahara": "ESH", "Spain": "ESP", "Estonia": "EST", "Ethiopia": "ETH", "Finland": "FIN", "Fiji": "FJI", "Falkland Islands": "FLK", "France": "FRA", "Faroe Islands": "FRO", "Federated States of Micronesia": "FSM", "Gabon": "GAB", "United Kingdom": "GBR", "Georgia (country)": "GEO", "Bailiwick of Guernsey": "GGY", "Ghana": "GHA", "Gibraltar": "GIB", "Guinea": "GIN", "Guadeloupe": "GLP", "The Gambia": "GMB", "Guinea-Bissau": "GNB", "Equatorial Guinea": "GNQ", "Greece": "GRC", "Grenada": "GRD", "Greenland": "GRL", "Guatemala": "GTM", "French Guiana": "GUF", "Guam": "GUM", "Guyana": "GUY", "Hong Kong": "HKG", "Heard Island and McDonald Islands": "HMD", "Honduras": "HND", "Croatia": "HRV", "Haiti": "HTI", "Hungary": "HUN", "Indonesia": "IDN", "Isle of Man": "IMN", "India": "IND", "British Indian Ocean Territory": "IOT", "Republic of Ireland": "IRL", "Iran, Islamic Republic of": "IRN", "Iraq": "IRQ", "Iceland": "ISL", "Israel": "ISR", "Italy": "ITA", "Jamaica": "JAM", "Jersey": "JEY", "Jordan": "JOR", "Japan": "JPN", "Kazakhstan": "KAZ", "Kenya": "KEN", "Kyrgyzstan": "KGZ", "Cambodia": "KHM", "Kiribati": "KIR", "Saint Kitts and Nevis": "KNA", "South Korea": "KOR", "Kuwait": "KWT", "Laos": "LAO", "Lebanon": "LBN", "Liberia": "LBR", "Libya": "LBY", "Saint Lucia": "LCA", "Liechtenstein": "LIE", "Sri Lanka": "LKA", "Lesotho": "LSO", "Lithuania": "LTU", "Luxembourg": "LUX", "Latvia": "LVA", "Macau": "MAC", "Collectivity of Saint Martin": "MAF", "Morocco": "MAR", "Monaco": "MCO", "Moldova": "MDA", "Madagascar": "MDG", "Maldives": "MDV", "Mexico": "MEX", "Marshall Islands": "MHL", "North Macedonia": "MKD", "Mali": "MLI", "Malta": "MLT", "Myanmar": "MMR", "Montenegro": "MNE", "Mongolia": "MNG", "Northern Mariana Islands": "MNP", "Mozambique": "MOZ", "Mauritania": "MRT", "Montserrat": "MSR", "Martinique": "MTQ", "Mauritius": "MUS", "Malawi": "MWI", "Malaysia": "MYS", "Mayotte": "MYT", "Namibia": "NAM", "New Caledonia": "NCL", "Niger": "NER", "Norfolk Island": "NFK", "Nigeria": "NGA", "Nicaragua": "NIC", "Niue": "NIU", "Kingdom of the Netherlands": "NLD", "Norway": "NOR", "Nepal": "NPL", "Nauru": "NRU", "New Zealand": "NZL", "Oman": "OMN", "Pakistan": "PAK", "Panama": "PAN", "Pitcairn Islands": "PCN", "Peru": "PER", "Philippines": "PHL", "Palau": "PLW", "Papua New Guinea": "PNG", "Poland": "POL", "Puerto Rico": "PRI", "North Korea": "PRK", "Portugal": "PRT", "Paraguay": "PRY", "State of Palestine": "PSE", "French Polynesia": "PYF", "Qatar": "QAT", "Réunion": "REU", "Romania": "ROU", "Russia": "RUS", "Rwanda": "RWA", "Saudi Arabia": "SAU", "Sudan": "SDN", "Senegal": "SEN", "Singapore": "SGP", "South Georgia and the South Sandwich Islands": "SGS", "Saint Helena, Ascension and Tristan da Cunha": "SHN", "Svalbard and Jan Mayen": "SJM", "Solomon Islands": "SLB", "Sierra Leone": "SLE", "El Salvador": "SLV", "San Marino": "SMR", "Somalia": "SOM", "Saint Pierre and Miquelon": "SPM", "Serbia": "SRB", "South Sudan": "SSD", "São Tomé and Príncipe": "STP", "Suriname": "SUR", "Slovakia": "SVK", "Slovenia": "SVN", "Sweden": "SWE", "Eswatini": "SWZ", "Sint Maarten": "SXM", "Seychelles": "SYC", "Syria": "SYR", "Turks and Caicos Islands": "TCA", "Chad": "TCD", "Togo": "TGO", "Thailand": "THA", "Tajikistan": "TJK", "Tokelau": "TKL", "Turkmenistan": "TKM", "East Timor": "TLS", "Tonga": "TON", "Trinidad and Tobago": "TTO", "Tunisia": "TUN", "Turkey": "TUR", "Tuvalu": "TUV", "Taiwan": "TWN", "Tanzania": "TZA", "Uganda": "UGA", "Ukraine": "UKR", "United States Minor Outlying Islands": "UMI", "Uruguay": "URY", "United States": "USA", "Uzbekistan": "UZB", "Vatican City": "VAT", "Saint Vincent and the Grenadines": "VCT", "Venezuela": "VEN", "British Virgin Islands": "VGB", "United States Virgin Islands": "VIR", "Vietnam": "VNM", "Vanuatu": "VUT", "Wallis and Futuna": "WLF", "Samoa": "WSM", "Yemen": "YEM", "South Africa": "ZAF", "Zambia": "ZMB", "Zimbabwe": "ZWE"}

# wczytanie z pliku (0.1), dla lepszego dzialania zalecam podmiane na plik sales_raw_extended.csv, ktory pokaze wszystkie mozliwosci tego skryptu
df = pd.read_csv("sales_raw.csv")

# usuniecie duplikatow (1.1)
df = df.drop_duplicates()

# utworzenie kolumny total_value (0.2)
df["total_value"] = df["quantity"] * df["unit_price"]

# utworzenie kolumny total_price (duplikat niezgodny z zasadami norm., istnieje juz total_value) (1.2)
df["total_price"] = df["quantity"] * df["unit_price"]

# konwersja na datetime
df["order_date"] = pd.to_datetime(df["order_date"])

# rozbicie daty (1.4)
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month
df["day"] = df["order_date"].dt.day

# dodanie kwartalu (2.2)
df["quarter"] = df["order_date"].dt.to_period("Q")

# dodanie kodow iso3 na podstawie nazwy (1.3)
df["country_code"] = df["country"].map(ISO3_dict).fillna("UNKNOWN")

print(f"{df}\n")

# laczna wartosc sprzedazy dla kazdego kraju i produktu (0.3)
sales_by_country = df.groupby("country")["total_value"].sum()
sales_by_product = df.groupby("product_name")["total_value"].sum()

print(f"wartosc laczna sprzedazy wg kraju:\n{sales_by_country}\n\n")
print(f"wartosc laczna sprzedazy wg produktu:\n{sales_by_product}\n\n")

# filtrowanie transakcji o wysokiej wartosci (0.4)
df_high_value = df[df["total_value"] > 1000]

# zapis transakcji o wysokiej wartosci do pliku (0.4)
df_high_value.to_csv("high_value_sales.csv", index=False)

# liczba transakcji w kazdym kraju w zbiorze high value (0.5)
sales_count_high_value = df_high_value.groupby("country")["order_id"].count()

print(f"liczba transakcji high value wg kraju:\n{sales_count_high_value}\n\n")

# podsumowanie liczby transakcji w kazdym kraju (0.5)
sales_count_by_country = df.groupby("country")["order_id"].count()

print(f"liczba sprzedazy wg kraju:\n{sales_count_by_country}\n\n")

# suma total_price i quantity dla kazdego miesiaca i kraju (2.1)
monthly_country_summary = df.groupby(["country_code", "year", "month"])[["total_price", "quantity"]].sum()

print(f"suma miesieczna total_price i quantity:\n{monthly_country_summary}\n\n")

# srednia cena jednostkowa produktu w kwartale (2.2)
quarterly_avg_price = df.groupby(["product_name", "quarter"])["unit_price"].mean()

print(f"srednia cena jednostkowa w kwartale:\n{quarterly_avg_price}\n\n")

# top 3 klientow wg sumy zakupow w kazdym kraju (3.1)
top_customers = (
    df.groupby(["country", "customer_name"])["total_price"]
    .sum()
    .groupby(level=0, group_keys=False)
    .nlargest(3)
)

print(f"top 3 klientow wg kraju:\n{top_customers}\n\n")

# ranking produktow w kazdej kategorii (3.2)
product_ranking = (
    df.groupby(["category", "product_name"])["total_price"]
    .sum()
    .groupby(level=0, group_keys=False)
    .rank(method="dense", ascending=False)
)

print(f"ranking produktow w kategorii:\n{product_ranking}\n\n")

# udzial procentowy kategorii w sprzedazy (3.3)
category_share = df.groupby("category")["total_price"].sum()
category_share_pct = category_share / category_share.sum() * 100

print(f"udzial procentowy kategorii:\n{category_share_pct}\n\n")

# srednia liczba produktow w zamowieniu (4.1)
avg_products_per_order = df.groupby("order_id")["product_name"].count().mean()

print(f"srednia liczba produktow w zamowieniu: {avg_products_per_order}\n")

# korelacja cena vs ilosc sprzedanych (4.1)
price_quantity_corr = df["unit_price"].corr(df["quantity"])

print(f"korelacja cena vs ilosc sprzedanych: {price_quantity_corr}\n")

# srednia liczba produktow w zamowieniu (4.2)
products_per_order = (
    df.groupby("order_id")["product_name"]
    .count()
)

# hierarchia produktow (4.4)
product_hierarchy = (
    df.groupby(["category", "product_name"])
    .agg(
        total_sales=("total_price", "sum"),
        total_quantity=("quantity", "sum")
    )
    .sort_values(["category", "total_sales"], ascending=[True, False])
)

print(f"hierarchia produktow:\n{product_hierarchy}\n")


# struktura slownikowa hierarchii
hierarchy_dict = (
    df.groupby("category")["product_name"]
    .unique()
    .to_dict()
)

print(f"struktura hierarchii:\n{hierarchy_dict}\n")


# wykrycie nietypowych cen metoda zscore (1.5)
mean_price = df["unit_price"].mean()
std_price = df["unit_price"].std(ddof=0)

df["price_zscore"] = (df["unit_price"] - mean_price) / std_price

outliers = df[df["price_zscore"].abs() > 1.5]

print(f"nietypowe ceny:\n{outliers[['product_name','unit_price','price_zscore']]}\n")

# analiza olap sprzedaz wg kraju i kategorii (5.4)
olap_country_category = df.pivot_table(
    values="total_price",
    index="country_code",
    columns="category",
    aggfunc="sum"
)

print(f"olap sprzedaz wg kraju i kategorii:\n{olap_country_category}\n")


# wymiar customer (5.1)
dim_customer = (
    df[["customer_name", "country", "country_code"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

dim_customer["customer_id"] = dim_customer.index + 1

print(f"wymiar customer:\n{dim_customer}\n")


# wymiar product (5.2)
dim_product = (
    df[["product_name", "category"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

dim_product["product_id"] = dim_product.index + 1

print(f"wymiar product:\n{dim_product}\n")


# wymiar time (5.5)
dim_time = (
    df[["order_date", "year", "month", "quarter"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

dim_time["time_id"] = dim_time.index + 1

print(f"wymiar time:\n{dim_time}\n")


# polaczenie kluczy do faktow
df_fact = df.merge(
    dim_customer[["customer_id", "customer_name"]],
    on="customer_name",
    how="left"
).merge(
    dim_product[["product_id", "product_name"]],
    on="product_name",
    how="left"
).merge(
    dim_time[["time_id", "order_date"]],
    on="order_date",
    how="left"
)

fact_sales = df_fact[[
    "order_id",
    "customer_id",
    "product_id",
    "time_id",
    "quantity",
    "unit_price",
    "total_price"
]].copy()

fact_sales["fact_id"] = range(1, len(fact_sales) + 1)

print(f"fakt sales:\n{fact_sales}\n")


# analiza kwartalna sprzedaz wg kraju (5.5)
quarterly_analysis = (
    df.groupby(["country_code", "quarter"])["total_price"]
    .sum()
    .reset_index()
)

print(f"analiza kwartalna wg kraju:\n{quarterly_analysis}\n")


# suma zakupow klienta w czasie rocznym (3.4)
customer_yearly = (
    df.groupby(["customer_name", "year"])["total_price"]
    .sum()
    .reset_index()
    .sort_values(["customer_name", "year"])
)

# obliczenie wzrostu rok do roku (3.4)
customer_yearly["growth"] = (
    customer_yearly
    .groupby("customer_name")["total_price"]
    .diff()
)

# klient z najwiekszym wzrostem (3.4)
if customer_yearly["growth"].notna().any():
    max_growth_row = customer_yearly.loc[
        customer_yearly["growth"].idxmax()
    ]
    print(f"klient z najwiekszym wzrostem zakupow:\n{max_growth_row}\n")
else:
    print("Brak danych do obliczenia wzrostu rok do roku (wszyscy klienci mają tylko 1 rok danych).")


# filtrowanie laptopow w polsce i niemczech
df_laptops = df[
    (df["product_name"].str.contains("laptop", case=False, na=False)) &
    (df["country"].isin(["Poland", "Germany"]))
]

# agregacja miesieczna
laptop_trend = (
    df_laptops
    .groupby(["year", "month", "country"])["total_price"]
    .sum()
    .reset_index()
)

# utworzenie kolumny data miesieczna
laptop_trend["date"] = pd.to_datetime(
    laptop_trend["year"].astype(str) + "-" +
    laptop_trend["month"].astype(str) + "-01"
)

# pivot do wykresu
laptop_pivot = laptop_trend.pivot(
    index="date",
    columns="country",
    values="total_price"
)

# wykres trendu
plt.figure()
laptop_pivot.plot()
plt.xlabel("data")
plt.ylabel("sprzedaz")
plt.title("trend sprzedazy laptopow pl vs de")
plt.tight_layout()
plt.savefig("laptop_trend.png")
plt.close()


# wykrywanie sezonowosci na podstawie sredniej miesiecznej
seasonality = (
    df.groupby("month")["total_price"]
    .mean()
)

plt.figure()
seasonality.plot(kind="bar")
plt.xlabel("miesiac")
plt.ylabel("srednia wartosc sprzedazy")
plt.title("sezonowosc miesieczna")
plt.tight_layout()
plt.savefig("seasonality.png")
plt.close()