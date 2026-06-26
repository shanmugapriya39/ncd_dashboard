import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import (
    load_ncd, load_median_age, SUB_REGION_ORDER, SUB_REGION_COLORS,
    INDICATOR_ORDER, INDICATOR_COLORS, SHARED_CSS
)
 
st.set_page_config(page_title="GDP Analysis", layout="wide", page_icon="📊")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
header[data-testid="stHeader"] {display: none;}
</style>""", unsafe_allow_html=True)
 
df  = load_ncd()
ma  = load_median_age()
 
# ─── Navigation ───────────────────────────────────────────────────────────────
n1, n2, n3, n4, _ = st.columns([1.2, 1.4, 1.3, 1.5, 4])
with n1:
    if st.button("← Executive"): st.switch_page("app.py")
with n2:
    if st.button(" Global Overview"): st.switch_page("pages/01_Global.py")
with n3:
    if st.button(" Supporting Evidence"): st.switch_page("pages/03_Evidence.py")
 
# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div>
    <h1>GDP & NCD Analysis — The Core Question</h1>
    <p>Does GDP per capita explain NCD prevalence within MENA? · 
       Scatter plots · Country trajectories · Correlation over time</p>
  </div>
  <div><span class="badge">Page 3 of 4</span></div>
</div>
""", unsafe_allow_html=True)
 
# ─── Controls ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    indicator = st.selectbox("Indicator:", INDICATOR_ORDER, key="gdp_indicator")
with c2:
    sel_year = st.slider("Year:", 1975, 2016, 2014, key="gdp_year")
with c3:
    sub_filter = st.selectbox("Sub-region filter:",
                               ["All sub-regions"] + SUB_REGION_ORDER, key="gdp_sub")
 
st.divider()
 
# ─── Shared data prep ─────────────────────────────────────────────────────────
scatter_df = (
    df[(df["Year"] == sel_year) & (df["Indicator"] == indicator) &
       df["Sub_Region"].notna() & df["GDP_per_capita"].notna()]
    .groupby(["Country","Sub_Region"])
    .agg(Prevalence_pct=("Prevalence_pct","median"),
         GDP_per_capita=("GDP_per_capita","median"),
         Population=("Population","median"))
    .reset_index()
)
scatter_df["Pop_sqrt"] = np.sqrt(scatter_df["Population"].fillna(0))
 
# Merge median age
ma_yr = ma[ma["Year"] == sel_year][["Country","Median_age"]]
scatter_df = scatter_df.merge(ma_yr, on="Country", how="left")
 
if sub_filter != "All sub-regions":
    scatter_df = scatter_df[scatter_df["Sub_Region"] == sub_filter]
 
# Country highlight selection — click to highlight across charts
country_sel = alt.selection_point(fields=["Country"], on="click",
                                   empty=True, name="country_highlight")
 
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Scatter: GDP vs Prevalence (colour = sub-region)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"**GDP per capita vs {indicator} prevalence, MENA {sel_year}**")
st.caption("Bubble size = population (√-scaled). Click a bubble to highlight that country. "
           "Drag to brush-select multiple countries.")
 
# Brush selection for lasso/rectangle
brush = alt.selection_interval(empty=True, name="brush_sel")
 
scatter = (
    alt.Chart(scatter_df).mark_circle(opacity=0.85)
    .encode(
        x=alt.X("GDP_per_capita:Q", title="GDP per capita (log scale, US$)",
                 scale=alt.Scale(type="log"),
                 axis=alt.Axis(grid=False)),
        y=alt.Y("Prevalence_pct:Q", title=f"{indicator} prevalence (%)",
                 scale=alt.Scale(zero=False),
                 axis=alt.Axis(grid=True, gridColor="#e8e8e8")),
        size=alt.Size("Pop_sqrt:Q", legend=None, scale=alt.Scale(range=[80,1500])),
        color=alt.Color("Sub_Region:N", title="Sub-region",
            scale=alt.Scale(domain=SUB_REGION_ORDER,
                            range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER])),
        opacity=alt.condition(brush | country_sel, alt.value(0.9), alt.value(0.2)),
        stroke=alt.condition(country_sel, alt.value("#333"), alt.value(None)),
        strokeWidth=alt.condition(country_sel, alt.value(2), alt.value(0)),
        tooltip=[
            alt.Tooltip("Country:N"),
            alt.Tooltip("Sub_Region:N", title="Sub-region"),
            alt.Tooltip("GDP_per_capita:Q", title="GDP per capita ($)", format=",.0f"),
            alt.Tooltip("Prevalence_pct:Q", title=f"{indicator} (%)", format=".1f"),
            alt.Tooltip("Population:Q", title="Population", format=",.0f"),
            alt.Tooltip("Median_age:Q", title="Median age (yrs)", format=".1f"),
        ],
    )
    .add_params(brush, country_sel)
    .properties(width=680, height=380)
)
 
# Country labels
labels = (
    alt.Chart(scatter_df).mark_text(fontSize=9, dy=-12, color="#444")
    .encode(
        x=alt.X("GDP_per_capita:Q", scale=alt.Scale(type="log")),
        y=alt.Y("Prevalence_pct:Q", scale=alt.Scale(zero=False)),
        text="Country:N",
        opacity=alt.condition(brush | country_sel, alt.value(0.9), alt.value(0.1)),
    )
)
st.altair_chart(scatter + labels, use_container_width=False)

st.divider()
 
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Country trajectories (connected scatter)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"**Country trajectories — how GDP and {indicator} moved together over time**")
st.caption("Each line traces one country from 1975 to 2016 as GDP grew. "
           "An upward-right trajectory means both GDP and prevalence rose together.")
 
default_countries = {
    "Low income":    "Afghanistan",
    "Medium income": "Iran",
    "High income":   "United Arab Emirates",
}
 
tc1, tc2, tc3 = st.columns(3)
c_low  = tc1.selectbox("Low income country:",
    df[df["Income_Tier"]=="Low"]["Country"].dropna().unique().tolist(),
    index=0, key="traj_low")
c_med  = tc2.selectbox("Medium income country:",
    df[df["Income_Tier"]=="Medium"]["Country"].dropna().unique().tolist(),
    index=list(df[df["Income_Tier"]=="Medium"]["Country"].dropna().unique()).index("Iran") if "Iran" in df[df["Income_Tier"]=="Medium"]["Country"].dropna().unique().tolist() else 0,
    key="traj_med")
c_high = tc3.selectbox("High income country:",
    df[df["Income_Tier"]=="High"]["Country"].dropna().unique().tolist(),
    index=list(df[df["Income_Tier"]=="High"]["Country"].dropna().unique()).index("United Arab Emirates") if "United Arab Emirates" in df[df["Income_Tier"]=="High"]["Country"].dropna().unique().tolist() else 0,
    key="traj_high")
 
traj_countries = [c_low, c_med, c_high]
traj_colors    = {
    c_low:  SUB_REGION_COLORS.get(df[df["Country"]==c_low]["Sub_Region"].iloc[0] if len(df[df["Country"]==c_low])>0 else "Gulf", "#E45756"),
    c_med:  SUB_REGION_COLORS.get(df[df["Country"]==c_med]["Sub_Region"].iloc[0] if len(df[df["Country"]==c_med])>0 else "Levant", "#F58518"),
    c_high: SUB_REGION_COLORS.get(df[df["Country"]==c_high]["Sub_Region"].iloc[0] if len(df[df["Country"]==c_high])>0 else "Gulf", "#1D9E75"),
}
 
traj_df = (
    df[df["Country"].isin(traj_countries) & (df["Indicator"]==indicator) &
       df["GDP_per_capita"].notna()]
    .groupby(["Country","Year"])[["Prevalence_pct","GDP_per_capita"]]
    .median().reset_index()
)
 
# Add year labels at start and end
traj_ends = pd.concat([
    traj_df.sort_values("Year").groupby("Country").first().reset_index().assign(label_pos="start"),
    traj_df.sort_values("Year").groupby("Country").last().reset_index().assign(label_pos="end"),
])
 
traj_chart = (
    alt.Chart(traj_df).mark_line(point=alt.OverlayMarkDef(size=25))
    .encode(
        x=alt.X("GDP_per_capita:Q", title="GDP per capita (log scale, US$)",
                 scale=alt.Scale(type="log"), axis=alt.Axis(grid=False)),
        y=alt.Y("Prevalence_pct:Q", title=f"{indicator} prevalence (%)",
                 scale=alt.Scale(zero=False),
                 axis=alt.Axis(grid=True, gridColor="#e8e8e8")),
        order="Year:O",
        color=alt.Color("Country:N", legend=alt.Legend(orient="bottom"),
            scale=alt.Scale(domain=traj_countries,
                            range=[traj_colors[c] for c in traj_countries])),
        tooltip=[alt.Tooltip("Country:N"), alt.Tooltip("Year:O"),
                 alt.Tooltip("GDP_per_capita:Q", format=",.0f", title="GDP ($)"),
                 alt.Tooltip("Prevalence_pct:Q", format=".1f", title=f"{indicator} (%)")],
    ).properties(width=680, height=360)
)
 
# Year labels at start and end — two separate layers
traj_start = traj_ends[traj_ends["label_pos"] == "start"]
traj_end   = traj_ends[traj_ends["label_pos"] == "end"]
 
year_labels_start = (
    alt.Chart(traj_start)
    .mark_text(fontSize=9, color="#666", dx=-8, align="right")
    .encode(
        x=alt.X("GDP_per_capita:Q", scale=alt.Scale(type="log")),
        y=alt.Y("Prevalence_pct:Q", scale=alt.Scale(zero=False)),
        text="Year:O",
    )
)
year_labels_end = (
    alt.Chart(traj_end)
    .mark_text(fontSize=9, color="#666", dx=8, align="left")
    .encode(
        x=alt.X("GDP_per_capita:Q", scale=alt.Scale(type="log")),
        y=alt.Y("Prevalence_pct:Q", scale=alt.Scale(zero=False)),
        text="Year:O",
    )
)
 
st.altair_chart(traj_chart + year_labels_start + year_labels_end, use_container_width=False)
 
st.divider()
 
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Pearson correlation over time
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("**GDP–NCD correlation over time — how has the relationship changed?**")
st.caption("Pearson r computed between GDP per capita and prevalence across all 23 MENA countries "
           "for each year. r > 0 means richer countries have higher prevalence; r < 0 means the opposite.")
 
from scipy.stats import pearsonr
 
corr_rows = []
for yr in sorted(df["Year"].dropna().unique()):
    for ind in INDICATOR_ORDER:
        sub = (
            df[(df["Year"]==yr) & (df["Indicator"]==ind) &
               df["GDP_per_capita"].notna() & df["Sub_Region"].notna()]
            .groupby("Country")
            .agg(Prevalence_pct=("Prevalence_pct","median"),
                 GDP_per_capita=("GDP_per_capita","median"))
            .dropna()
        )
        if len(sub) >= 5:
            r, _ = pearsonr(sub["GDP_per_capita"], sub["Prevalence_pct"])
            corr_rows.append({"Year": yr, "Indicator": ind, "r": round(r,3)})
 
corr_df = pd.DataFrame(corr_rows)
 
hover_corr = alt.selection_point(fields=["Indicator"], on="mouseover", empty=True)
 
corr_chart = (
    alt.Chart(corr_df).mark_line(strokeWidth=2.5, point=True)
    .encode(
        x=alt.X("Year:Q", title="Year",
                 axis=alt.Axis(grid=False, format="d")),
        y=alt.Y("r:Q", title="Pearson r (GDP vs prevalence)",
                 scale=alt.Scale(zero=False),
                 axis=alt.Axis(grid=True, gridColor="#e8e8e8")),
        color=alt.Color("Indicator:N", legend=alt.Legend(orient="right"),
            scale=alt.Scale(domain=INDICATOR_ORDER,
                            range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER])),
        strokeWidth=alt.condition(hover_corr, alt.value(4), alt.value(2)),
        opacity=alt.condition(hover_corr, alt.value(1.0), alt.value(0.6)),
        tooltip=[alt.Tooltip("Year:Q", format="d"), alt.Tooltip("Indicator:N"),
                 alt.Tooltip("r:Q", title="Pearson r", format=".3f")],
    )
    .add_params(hover_corr)
)
 
# Zero reference line
zero_line = (
    alt.Chart(pd.DataFrame({"y":[0]}))
    .mark_rule(color="#999", strokeDash=[4,2], strokeWidth=1)
    .encode(y="y:Q")
)
 
# End labels
corr_end = corr_df.sort_values("Year").groupby("Indicator").last().reset_index()
corr_labels = (
    alt.Chart(corr_end).mark_text(align="left", dx=6, fontSize=10, fontWeight="bold")
    .encode(x="Year:Q", y="r:Q", text=alt.Text("r:Q", format=".2f"),
        color=alt.Color("Indicator:N", legend=None,
            scale=alt.Scale(domain=INDICATOR_ORDER,
                            range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER])))
)
 
st.altair_chart(
    (corr_chart + zero_line + corr_labels)
    .properties(width=760, height=320,
                title="Pearson r: GDP per capita vs NCD prevalence, MENA 1975–2016"),
    use_container_width=False
)
st.caption("r > 0 = richer countries have higher prevalence. "
           "r < 0 = richer countries have lower prevalence. "
           "Hover a line to highlight it.")
 
st.divider()
st.caption(
    "Data: NCD-RisC (2016a, 2016b, 2017) · World Bank GDP per capita · "
    "UN World Population Prospects (median age). "
    "Pearson r computed across 23 MENA countries per year (Field, 2018)."
)
