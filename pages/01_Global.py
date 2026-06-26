import streamlit.components.v1 as components
import os
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import (
    load_ncd, SUB_REGION_ORDER, SUB_REGION_COLORS,
    INDICATOR_ORDER, INDICATOR_COLORS, SHARED_CSS, WB_REGION_COLORS,
    WORLD_110M_URL
)

st.set_page_config(page_title="Global Overview", layout="wide", page_icon="🌍")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
header[data-testid="stHeader"] {display: none;}
</style>""", unsafe_allow_html=True)

df = load_ncd()

@st.cache_data
def load_global_direct():
    bp = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Raised Blood Pressure")
    bmi = pd.read_excel("cw1 -dataset.xlsx", sheet_name="BMI")
    dia = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Diabetes")

    for d, ind in [(bp, "Blood Pressure"), (bmi, "Obesity"), (dia, "Diabetes")]:
        d.columns = ["Country", "Sex", "Year", "Prevalence"]
        d["Indicator"] = ind

    g = pd.concat([bp, bmi, dia], ignore_index=True)
    g["Prevalence_pct"] = (g["Prevalence"] * 100).round(1)

    wb = pd.read_excel("CLASS_2025_10_07.xlsx", sheet_name="List of economies")
    wb = wb[["Economy", "Region", "Income group"]].dropna(subset=["Region"])
    wb.columns = ["Country", "WB_Region", "Income_group"]

    g = g.merge(wb, on="Country", how="left")
    g["WB_Region"] = g["WB_Region"].fillna("Unknown")

    return g


gdf = load_global_direct()

# Navigation
n1, n2, n3, _ = st.columns([1.2, 1.4, 1.5, 5])

with n1:
    if st.button("← Executive"):
        st.switch_page("app.py")

with n2:
    if st.button(" GDP Analysis"):
        st.switch_page("pages/02_GDP.py")

with n3:
    if st.button(" Supporting Evidence"):
        st.switch_page("pages/03_Evidence.py")

# Header
st.markdown("""
<div class="page-header">
  <div>
    <h1>Global Overview — Why Investigate MENA?</h1>
    <p>Regional comparison across 7 World Bank regions · Global NCD trends · MENA highlighted throughout</p>
  </div>
  <div><span class="badge">Page 2 of 4</span></div>
</div>
""", unsafe_allow_html=True)

# Year filter
f1, _ = st.columns([1, 3])

with f1:
    sel_year = st.slider(
        "Reference year:",
        1975,
        2016,
        2014,
        key="global_year"
    )

# Prepare data
region_names = {
    "Middle East & North Africa": "MENA",
    "Middle East, North Africa, Afghanistan & Pakistan": "MENA",
    "Europe & Central Asia": "Europe & C. Asia",
    "East Asia & Pacific": "East Asia & Pacific",
    "Latin America & Caribbean": "Latin America",
    "Sub-Saharan Africa": "Sub-Saharan Africa",
    "South Asia": "South Asia",
    "North America": "North America",
}

gdf2 = gdf.copy()
gdf2["WB_Region"] = gdf2["WB_Region"].replace(region_names)
gdf2 = gdf2[gdf2["WB_Region"].isin(region_names.values())]

region_domain = [
    "MENA",
    "North America",
    "East Asia & Pacific",
    "Latin America",
    "Europe & C. Asia",
    "Sub-Saharan Africa",
    "South Asia",
]

region_range = [
    "#00C896",
    "#E45756",
    "#4C78A8",
    "#F58518",
    "#9B59B6",
    "#E8C32A",
    "#E91E8C",
]

# Regional medians
reg_year = (
    gdf2[gdf2["Year"] == sel_year]
    .groupby(["WB_Region", "Indicator"])["Prevalence_pct"]
    .median()
    .round(1)
    .reset_index()
)

rank_tbl = (
    reg_year
    .pivot(index="WB_Region", columns="Indicator", values="Prevalence_pct")
    .reset_index()
)

for ind in INDICATOR_ORDER:
    if ind in rank_tbl.columns:
        rank_tbl[f"{ind}_rank"] = rank_tbl[ind].rank(ascending=False).astype(int)

st.divider()

# Regional comparison
st.markdown(f"**Regional NCD comparison ({sel_year}) — click a region to highlight**")

region_click = alt.selection_point(fields=["WB_Region"], empty=True)

reg_bar = (
    alt.Chart(reg_year)
    .mark_bar()
    .encode(
        x=alt.X(
            "Prevalence_pct:Q",
            title="Median prevalence (%)",
            axis=alt.Axis(grid=True, gridColor="#e8e8e8")
        ),
        y=alt.Y(
            "WB_Region:N",
            sort="-x",
            title=None,
            axis=alt.Axis(labelFontSize=10)
        ),
        color=alt.condition(
            alt.datum.WB_Region == "MENA",
            alt.value("#1D9E75"),
            alt.value("#9ECAE1")
        ),
        opacity=alt.condition(region_click, alt.value(1.0), alt.value(0.5)),
        facet=alt.Facet(
            "Indicator:N",
            columns=3,
            sort=INDICATOR_ORDER,
            header=alt.Header(labelFontSize=12, labelFontWeight="bold")
        ),
        tooltip=[
            alt.Tooltip("WB_Region:N", title="Region"),
            alt.Tooltip("Indicator:N", title="Indicator"),
            alt.Tooltip("Prevalence_pct:Q", title="Prevalence (%)", format=".1f"),
        ],
    )
    .add_params(region_click)
    .properties(width=240, height=220)
)

st.altair_chart(reg_bar, use_container_width=False)

st.caption(
    "MENA highlighted in green. Click any bar to highlight that region across all three panels."
)

st.divider()

# Global trends
st.markdown("**Global NCD trends by region 1975–2016 — MENA highlighted**")

trend_all = (
    gdf2[gdf2["WB_Region"].notna() & (gdf2["WB_Region"] != "Unknown")]
    .groupby(["Year", "WB_Region", "Indicator"])["Prevalence_pct"]
    .median()
    .round(1)
    .reset_index()
    .rename(columns={
        "WB_Region": "Region",
        "Prevalence_pct": "Median_prevalence"
    })
)

trend_ind = "Blood Pressure"

trend_plot = trend_all[trend_all["Indicator"] == trend_ind].copy()


def global_trend_chart(d, indicator):
    hover = alt.selection_point(
        fields=["Year"],
        nearest=True,
        on="mouseover",
        empty=False,
        clear="mouseout"
    )

    base = alt.Chart(d).encode(
        x=alt.X(
            "Year:Q",
            axis=alt.Axis(
                title="Year",
                values=[1975, 1985, 1995, 2005, 2015],
                format="d"
            )
        )
    )

    line = base.mark_line(interpolate="monotone").encode(
        y=alt.Y("Median_prevalence:Q", title="Median prevalence (%)"),
        color=alt.Color(
            "Region:N",
            scale=alt.Scale(domain=region_domain, range=region_range),
            legend=alt.Legend(title="Region", orient="right")
        ),
        strokeWidth=alt.condition(
            alt.datum.Region == "MENA",
            alt.value(4),
            alt.value(2)
        ),
        opacity=alt.condition(
            alt.datum.Region == "MENA",
            alt.value(1),
            alt.value(0.35)
        )
    )

    selectors = base.mark_point(size=100, opacity=0).encode(
        y="Median_prevalence:Q"
    ).add_params(hover)

    points = base.mark_circle(size=100).encode(
        y="Median_prevalence:Q",
        color=alt.Color(
            "Region:N",
            scale=alt.Scale(domain=region_domain, range=region_range),
            legend=None
        ),
        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
        tooltip=[
            alt.Tooltip("Year:Q", title="Year", format="d"),
            alt.Tooltip("Region:N", title="Region"),
            alt.Tooltip("Median_prevalence:Q", title=f"{indicator} (%)", format=".1f"),
        ]
    )

    rule = base.mark_rule(
        color="#555555",
        strokeDash=[5, 3],
        strokeWidth=1.5
    ).encode(
        opacity=alt.condition(hover, alt.value(1), alt.value(0))
    ).transform_filter(hover)

    last_year = d["Year"].max()

    mena_label = (
        alt.Chart(d[(d["Year"] == last_year) & (d["Region"] == "MENA")])
        .mark_text(align="left", dx=8, fontSize=12, fontWeight="bold")
        .encode(
            x="Year:Q",
            y="Median_prevalence:Q",
            text="Region:N",
            color=alt.value("#00C896")
        )
    )

    return (
        (line + selectors + points + rule + mena_label)
        .properties(
            width=850,
            height=380,
            title=alt.TitleParams(
                f"{indicator} prevalence by region, 1975–2016",
                fontSize=16,
                anchor="start"
            )
        )
        .configure_view(strokeWidth=0)
        .configure_axis(
            grid=True,
            gridOpacity=0.18,
            labelFontSize=11,
            titleFontSize=12
        )
    )

_chart_path = os.path.join(os.path.dirname(__file__), "..", "global_trend_chart.html")
with open(_chart_path, encoding="utf-8") as _f:
    components.html(_f.read(), height=500, scrolling=False)

st.caption(
    "Hover over the vertical rule to inspect all regional values for a selected year. "
    "MENA line is always thicker and teal."
)

# Year summary table
st.markdown("**Inspect a specific year — all regions ranked**")

sel_year2 = st.slider(
    "Select year:",
    1975,
    2016,
    2014,
    key="trend_year_slider"
)

year_summary = (
    trend_plot[trend_plot["Year"] == sel_year2]
    .sort_values("Median_prevalence", ascending=False)
    [["Region", "Median_prevalence"]]
    .rename(columns={"Median_prevalence": f"{trend_ind} (%)"})
    .reset_index(drop=True)
)

def highlight_mena_row(row):
    if row["Region"] == "MENA":
        return ["background-color:#e8f8f2; font-weight:bold"] * len(row)
    return [""] * len(row)

st.dataframe(
    year_summary.style.apply(highlight_mena_row, axis=1),
    use_container_width=True,
    hide_index=False
)

st.divider()

# Ranking table
st.markdown(f"**Regional ranking by indicator ({sel_year}) — rank 1 = highest prevalence**")

display_cols = ["WB_Region"]
rename = {"WB_Region": "Region"}

for ind in INDICATOR_ORDER:
    if ind in rank_tbl.columns:
        display_cols += [ind, f"{ind}_rank"]
        short = "BP" if ind == "Blood Pressure" else ind
        rename[ind] = f"{short} (%)"
        rename[f"{ind}_rank"] = f"{short} rank"

tbl_show = rank_tbl[display_cols].rename(columns=rename).round(1)

def highlight_mena(row):
    if row["Region"] == "MENA":
        return ["background-color:#e8f8f2; font-weight:bold"] * len(row)
    return [""] * len(row)

st.dataframe(
    tbl_show.style.apply(highlight_mena, axis=1),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "MENA row highlighted. MENA ranks #1 for diabetes, #2 for obesity, "
    "but only #4 for blood pressure — confirming the metabolic specificity of its NCD burden."
)

st.divider()

st.caption(
    "Data: NCD-RisC (2016a, 2016b, 2017) · World Bank GDP, population & income classification. "
    "Global dataset covers 200 countries across 7 World Bank regions."
)
