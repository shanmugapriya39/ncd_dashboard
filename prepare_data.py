import pandas as pd
import streamlit as slt
import altair as alt
mena_ncd = [
    'Saudi Arabia', 'Kuwait', 'United Arab Emirates', 'Qatar', 'Bahrain', 'Oman',
    'Israel', 'Malta', 'Iran', 'Iraq', 'Lebanon', 'Jordan',
    'Algeria', 'Tunisia', 'Libya', 'Egypt', 'Morocco', 'Yemen',
    'Syrian Arab Republic', 'Djibouti', 'Occupied Palestinian Territory',
    'Pakistan', 'Afghanistan'
]

mena_wb = [
    'Saudi Arabia', 'Kuwait', 'United Arab Emirates', 'Qatar', 'Bahrain', 'Oman',
    'Israel', 'Malta', 'Iran, Islamic Rep.', 'Iraq', 'Lebanon', 'Jordan',
    'Algeria', 'Tunisia', 'Libya', 'Egypt, Arab Rep.', 'Morocco', 'Yemen, Rep.',
    'Syrian Arab Republic', 'Djibouti', 'West Bank and Gaza',
    'Pakistan', 'Afghanistan'
]

mena_owid = [
    'Saudi Arabia', 'Kuwait', 'United Arab Emirates', 'Qatar', 'Bahrain', 'Oman',
    'Israel', 'Malta', 'Iran', 'Iraq', 'Lebanon', 'Jordan',
    'Algeria', 'Tunisia', 'Libya', 'Egypt', 'Morocco', 'Yemen',
    'Syria', 'Djibouti', 'Palestine', 'Pakistan', 'Afghanistan'
]

# A single "clean" display name for each country, in the same order as the lists above
clean_names = [
    'Saudi Arabia', 'Kuwait', 'United Arab Emirates', 'Qatar', 'Bahrain', 'Oman',
    'Israel', 'Malta', 'Iran', 'Iraq', 'Lebanon', 'Jordan',
    'Algeria', 'Tunisia', 'Libya', 'Egypt', 'Morocco', 'Yemen',
    'Syria', 'Djibouti', 'Palestine', 'Pakistan', 'Afghanistan'
]
ncd_to_clean = dict(zip(mena_ncd, clean_names))
wb_to_clean  = dict(zip(mena_wb, clean_names))
owid_to_clean = dict(zip(mena_owid, clean_names))
bp  = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Raised Blood Pressure")
bmi = pd.read_excel("cw1 -dataset.xlsx", sheet_name="BMI")
dia = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Diabetes")

bp.columns  = ['Country', 'Sex', 'Year', 'Prevalence']
bmi.columns = ['Country', 'Sex', 'Year', 'Prevalence']
dia.columns = ['Country', 'Sex', 'Year', 'Prevalence']

bp['Indicator']  = 'Blood Pressure'
bmi['Indicator'] = 'Obesity'
dia['Indicator'] = 'Diabetes'

ncd = pd.concat([bp, bmi, dia], ignore_index=True)

# Filter to MENA only, using the NCD-RisC naming list
ncd = ncd[ncd['Country'].isin(mena_ncd)].copy()

# Translate to clean names
ncd['Country'] = ncd['Country'].map(ncd_to_clean)

# Convert to percentage
ncd['Prevalence_pct'] = (ncd['Prevalence'] * 100).round(1)

print(f"NCD data: {ncd.shape}")
print(f"Countries: {ncd['Country'].nunique()}")
pop = pd.read_csv(r"C:\Users\Shanm\OneDrive\Desktop\CW1\ncd_dashboard\API_SP.POP.TOTL_DS2_EN_csv_v2_327505.csv")
pop = pop[pop['Country Name'].isin(mena_wb)].copy()
pop['Country'] = pop['Country Name'].map(wb_to_clean)

# Convert from wide (one column per year) to long (one row per country-year)
year_cols = [str(y) for y in range(1975, 2017) if str(y) in pop.columns]
pop_long = pop.melt(
    id_vars=['Country'],
    value_vars=year_cols,
    var_name='Year',
    value_name='Population'
)
pop_long['Year'] = pop_long['Year'].astype(int)

print(f"Population data: {pop_long.shape}")
print(f"Countries: {pop_long['Country'].nunique()}")
# Temporary check — which MENA country is missing?
found_countries = set(ncd['Country'].unique())
expected_countries = set(clean_names)
missing = expected_countries - found_countries
print(f"Missing country: {missing}")
# ── Load GDP per capita data ────────────────────────────────
gdp = pd.read_csv(r"C:\Users\Shanm\OneDrive\Desktop\CW1\ncd_dashboard\gdp-per-capita-maddison-project-database.csv")
gdp = gdp[(gdp['Year'] >= 1975) & (gdp['Year'] <= 2016)].copy()
gdp = gdp[gdp['Entity'].isin(mena_owid)].copy()
gdp['Country'] = gdp['Entity'].map(owid_to_clean)

gdp_clean = gdp[['Country', 'Year', 'GDP per capita']].copy()
gdp_clean.columns = ['Country', 'Year', 'GDP_per_capita']

print(f"GDP data: {gdp_clean.shape}")
print(f"Countries: {gdp_clean['Country'].nunique()}")
gdp_found = set(gdp_clean['Country'].unique())
gdp_missing = set(clean_names) - gdp_found
print(f"GDP missing countries: {gdp_missing}")
# ── Load Income classification data ─────────────────────────
income_raw = pd.read_excel(
    "OGHIST_2026_03_10.xlsx",
    sheet_name="Country Analytical History",
    header=5,
    skiprows=[6,7,8,9,10]
)

income_raw = income_raw.rename(columns={
    'Unnamed: 0': 'ISO3',
    'Data for calendar year :': 'Country'
})

income = income_raw[income_raw['Country'].isin(mena_wb)].copy()
income['Country'] = income['Country'].map(wb_to_clean)

# Convert from wide (years as columns) to long (one row per country-year)
year_cols = [c for c in income.columns if str(c).isdigit() and 1975 <= int(c) <= 2016]

income_long = income.melt(
    id_vars=['Country'],
    value_vars=year_cols,
    var_name='Year',
    value_name='Income_group'
)
income_long['Year'] = income_long['Year'].astype(int)

# Replace ".." (missing) with proper NaN, and expand codes to full names
income_long['Income_group'] = income_long['Income_group'].replace('..', None)
income_map = {'L': 'Low income', 'LM': 'Lower middle income', 
              'UM': 'Upper middle income', 'H': 'High income'}
income_long['Income_group'] = income_long['Income_group'].map(income_map)

print(f"Income data: {income_long.shape}")
print(f"Countries: {income_long['Country'].nunique()}")
income_found = set(income_long['Country'].unique())
income_missing = set(clean_names) - income_found
print(f"Income missing countries: {income_missing}")
# ── Load Region classification data ─────────────────────────
region_raw = pd.read_excel("CLASS_2025_10_07.xlsx", sheet_name="List of economies")
region_raw = region_raw[['Economy', 'Region']].dropna(subset=['Region'])
region_raw.columns = ['Country_WB', 'Region']

region = region_raw[region_raw['Country_WB'].isin(mena_wb)].copy()
region['Country'] = region['Country_WB'].map(wb_to_clean)
region = region[['Country', 'Region']]

print(f"Region data: {region.shape}")
print(f"Countries: {region['Country'].nunique()}")

region_found = set(region['Country'].unique())
region_missing = set(clean_names) - region_found
print(f"Region missing countries: {region_missing}")
# ── Merge everything together ────────────────────────────────
merged = ncd.merge(pop_long, on=['Country', 'Year'], how='left')
merged = merged.merge(gdp_clean, on=['Country', 'Year'], how='left')
merged = merged.merge(income_long, on=['Country', 'Year'], how='left')
merged = merged.merge(region, on='Country', how='left')

# Compute absolute counts
merged['Absolute_count'] = (merged['Prevalence'] * merged['Population'])

print(f"\nFinal merged shape: {merged.shape}")
print(f"Countries: {merged['Country'].nunique()}")
print(f"\nSample row:")
print(merged.head(3).to_string())

# Save the result
merged.to_csv("ncd_merged.csv", index=False)
print(f"\n✓ Saved ncd_merged.csv")
import altair as alt

df = pd.read_csv(r"C:\Users\Shanm\OneDrive\Desktop\CW1\ncd_dashboard\ncd_merged.csv")

boxplot = alt.Chart(df).mark_boxplot(extent='min-max', size=40).encode(
    x=alt.X('Indicator:N', title=None),
    y=alt.Y('Prevalence_pct:Q', title='Prevalence (%)'),
    color=alt.Color('Indicator:N', legend=None,
        scale=alt.Scale(
            domain=['Blood Pressure', 'Obesity', 'Diabetes'],
            range=['#4C78A8', '#F58518', '#E45756']
        )
    )
).properties(
    width=400,
    height=350,
    title='Distribution of NCD prevalence values across MENA (outlier check)'
)

boxplot