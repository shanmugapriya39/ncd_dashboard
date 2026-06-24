
import streamlit as st
import pandas as pd
import altair as alt
 
st.set_page_config(page_title="MENA NCD Dashboard", layout="wide")
 
st.title("Non-Communicable Diseases in the MENA Region")
st.markdown("Analysing obesity, diabetes, and hypertension across 23 countries (1975–2016).")
 
# ── Load data ─────────────────────────────────────────────────
# Expects:
#   cw1 -dataset.xlsx        sheets: "Raised Blood Pressure", "BMI", "Diabetes"
#   CLASS_2025_10_07.xlsx    sheet:  "List of economies" (World Bank region/income classification)
@st.cache_data
def load_data():
    bp = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Raised Blood Pressure")
    bmi = pd.read_excel("cw1 -dataset.xlsx", sheet_name="BMI")
    dia = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Diabetes")
 
    bp.columns = ["Country", "Sex", "Year", "Prevalence"]
    bmi.columns = ["Country", "Sex", "Year", "Prevalence"]
    dia.columns = ["Country", "Sex", "Year", "Prevalence"]
 
    bp["Indicator"] = "Blood Pressure"
    bmi["Indicator"] = "Obesity"
    dia["Indicator"] = "Diabetes"
 
    df = pd.concat([bp, bmi, dia], ignore_index=True)
    df["Prevalence_pct"] = (df["Prevalence"] * 100).round(1)
 
    wb = pd.read_excel("CLASS_2025_10_07.xlsx", sheet_name="List of economies")
    wb = wb[["Economy", "Region", "Income group"]].dropna(subset=["Region"])
    wb.columns = ["Country", "WB_Region", "Income_group"]
 
    df = df.merge(wb, on="Country", how="left")
    df["WB_Region"] = df["WB_Region"].fillna("Unknown")
 
    return df
 
 
df = load_data()
 
region_names = {
    "Middle East, North Africa, Afghanistan & Pakistan": "MENA",
    "Europe & Central Asia": "Europe & C. Asia",
    "East Asia & Pacific": "East Asia & Pacific",
    "Latin America & Caribbean": "Latin America",
    "Sub-Saharan Africa": "Sub-Saharan Africa",
    "South Asia": "South Asia",
    "North America": "North America",
}
 
# ═══════════════════════════════════════════════════════════════
# OVERVIEW — KPI cards
# ═══════════════════════════════════════════════════════════════
st.divider()
st.subheader("Global overview")
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Countries analysed", df["Country"].nunique())
col2.metric("Data points", f"{len(df):,}")
col3.metric("Study period", "1975–2016")
col4.metric("MENA diabetes median", "13.7%")
 
# ═══════════════════════════════════════════════════════════════
# OVERVIEW — Regional comparison (all regions, all indicators)
# ═══════════════════════════════════════════════════════════════
st.divider()
st.subheader("Global NCD burden by region (2014)")
st.caption("Median prevalence across countries within each region. Excludes unmatched country names.")
 
regional_summary = (
    df[(df["Year"] == 2014) & (df["WB_Region"] != "Unknown")]
    .groupby(["WB_Region", "Indicator"])["Prevalence_pct"]
    .median()
    .round(1)
    .reset_index()
)
regional_summary["WB_Region"] = regional_summary["WB_Region"].replace(region_names)
 
chart = (
    alt.Chart(regional_summary)
    .mark_bar()
    .encode(
        x=alt.X("Prevalence_pct:Q", title="Median prevalence (%)"),
        y=alt.Y("WB_Region:N", sort="-x", title=None),
        color=alt.Color(
            "Indicator:N",
            scale=alt.Scale(
                domain=["Blood Pressure", "Obesity", "Diabetes"],
                range=["#4C78A8", "#F58518", "#E45756"],
            ),
            legend=None,
        ),
        facet=alt.Facet("Indicator:N", columns=3, header=alt.Header(labelFontSize=13, labelFontWeight="bold")),
        tooltip=[
            alt.Tooltip("WB_Region:N", title="Region"),
            alt.Tooltip("Indicator:N", title="Indicator"),
            alt.Tooltip("Prevalence_pct:Q", title="Median prevalence (%)", format=".1f"),
        ],
    )
    .properties(width=300, height=200)
)
 
st.altair_chart(chart, use_container_width=False)
 
# ═══════════════════════════════════════════════════════════════
# OVERVIEW — Ranking table (details on demand)
# ═══════════════════════════════════════════════════════════════
st.markdown("**Which region leads across the metabolic triad?**")
 
ranking_table = regional_summary.copy()
ranking_table["Rank"] = ranking_table.groupby("Indicator")["Prevalence_pct"].rank(ascending=False).astype(int)
 
pivot = ranking_table.pivot(index="WB_Region", columns="Indicator", values="Rank")
pivot = pivot.sort_values("Diabetes")
pivot.columns.name = None
pivot.index.name = "Region"
 
st.dataframe(pivot, use_container_width=True)
 
# ═══════════════════════════════════════════════════════════════
# RELATE — MENA's ranking over time (verifies the pattern is consistent)
# ═══════════════════════════════════════════════════════════════
st.divider()
st.subheader("MENA's global NCD ranking over time")
st.caption(
    "MENA highlighted in green across all three indicators. "
    "The contrast across panels is the core finding: MENA pulls clearly ahead "
    "for Diabetes and Obesity, but sits mid-pack for Blood Pressure — "
    "confirming that MENA's elevated NCD burden is specifically metabolic, "
    "not uniform across all three indicators."
)
 
time_trend_all = (
    df[df["WB_Region"] != "Unknown"]
    .groupby(["Year", "WB_Region", "Indicator"])["Prevalence_pct"]
    .median()
    .round(1)
    .reset_index()
)
time_trend_all["WB_Region"] = time_trend_all["WB_Region"].replace(region_names)
 
region_domain = ["MENA", "North America", "East Asia & Pacific",
                 "Latin America", "Europe & C. Asia", "Sub-Saharan Africa", "South Asia"]
region_range  = ["#1D9E75", "#636363", "#969696",
                 "#bdbdbd", "#d9d9d9", "#f0f0f0", "#cccccc"]
 
line_chart = (
    alt.Chart(time_trend_all)
    .mark_line(strokeWidth=2)
    .encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Prevalence_pct:Q", title="Median prevalence (%)"),
        color=alt.Color(
            "WB_Region:N",
            scale=alt.Scale(domain=region_domain, range=region_range),
            legend=alt.Legend(title="Region"),
        ),
        opacity=alt.condition(
            alt.datum.WB_Region == "MENA", alt.value(1.0), alt.value(0.35)
        ),
        strokeWidth=alt.condition(
            alt.datum.WB_Region == "MENA", alt.value(3), alt.value(1.2)
        ),
        facet=alt.Facet(
            "Indicator:N",
            columns=3,
            sort=["Blood Pressure", "Diabetes", "Obesity"],
            header=alt.Header(labelFontSize=13, labelFontWeight="bold"),
        ),
        tooltip=[
            alt.Tooltip("Year:O", title="Year"),
            alt.Tooltip("WB_Region:N", title="Region"),
            alt.Tooltip("Indicator:N", title="Indicator"),
            alt.Tooltip("Prevalence_pct:Q", title="Prevalence (%)", format=".1f"),
        ],
    )
    .properties(width=260, height=260)
)
 
st.altair_chart(line_chart, use_container_width=False)
 
# ═══════════════════════════════════════════════════════════════
# ZOOM AND FILTER — navigate to MENA deep dive
# ═══════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    "MENA consistently ranks among the top regions globally for "
    "diabetes and obesity. The next page zooms into the 23 MENA "
    "countries to examine why."
)
 
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔍 Explore MENA Deep Dive →", use_container_width=True):
        st.switch_page("pages/01_MENA_Analysis.py")