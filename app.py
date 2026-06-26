
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import (
    load_ncd, load_global, SUB_REGION_ORDER, SUB_REGION_COLORS,
    INDICATOR_ORDER, INDICATOR_COLORS, SHARED_CSS, WB_REGION_COLORS
)
 
st.set_page_config(page_title="MENA NCD Dashboard", layout="wide", page_icon="🏥")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
header[data-testid="stHeader"] {display: none;}
</style>""", unsafe_allow_html=True)
df = load_ncd()
gdf = load_global()
 
# ─── Navigation ───────────────────────────────────────────────────────────────
n1, n2, n3, n4, _ = st.columns([1.2, 1.4, 1.3, 1.5, 4])
with n1:
    if st.button(" Global Overview"):
        st.switch_page("pages/01_Global.py")
with n2:
    if st.button(" GDP Analysis"):
        st.switch_page("pages/02_GDP.py")
with n3:
    if st.button(" Supporting Evidence"):
        st.switch_page("pages/03_Evidence.py")
 
# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div>
    <h1>MENA NCD Dashboard — Executive Overview</h1>
    <p>Does GDP explain NCD prevalence in MENA? · 23 countries · 1975–2016 · 
       NCD-RisC + World Bank + UN Population data</p>
  </div>
  <div><span class="badge">CST4245 · Coursework 1</span></div>
</div>
""", unsafe_allow_html=True)
 
# ─── KPI cards ────────────────────────────────────────────────────────────────
d14 = df[df["Year"] == 2014]
gulf_gdp = d14[d14["Sub_Region"]=="Gulf"]["GDP_per_capita"].median()
low_gdp  = d14[d14["Sub_Region"]=="Lower-income MENA"]["GDP_per_capita"].median()
k_ob = d14[(d14["Country"]=="Kuwait")&(d14["Indicator"]=="Obesity")]["Prevalence_pct"].median()
y_bp = d14[(d14["Country"]=="Yemen")&(d14["Indicator"]=="Blood Pressure")]["Prevalence_pct"].median()
eg_gap = (
    d14[(d14["Country"]=="Egypt")&(d14["Indicator"]=="Obesity")&(d14["Sex"]=="Women")]["Prevalence_pct"].median() -
    d14[(d14["Country"]=="Egypt")&(d14["Indicator"]=="Obesity")&(d14["Sex"]=="Men")]["Prevalence_pct"].median()
)
 
k1,k2,k3,k4,k5 = st.columns(5)
for col,val,lbl in [
    (k1, "#1 globally",       "MENA diabetes rank since 1985"),
    (k2, f"${gulf_gdp/1000:.0f}k vs ${low_gdp/1000:.1f}k", "Gulf vs Lower-income GDP, 2014"),
    (k3, f"{k_ob:.1f}%",      "Kuwait obesity — worst combined burden"),
    (k4, f"{y_bp:.1f}%",      "Yemen blood pressure — highest in MENA"),
    (k5, f"+{eg_gap:.1f} pts","Egypt gender obesity gap — widest in MENA"),
]:
    col.markdown(f'<div class="kpi"><div class="v">{val}</div>'
                 f'<div class="l">{lbl}</div></div>', unsafe_allow_html=True)
 
st.write("")
 
# ─── Key insights panel ───────────────────────────────────────────────────────
st.markdown("**Key Findings**")
ic1, ic2, ic3 = st.columns(3)
 
with ic1:
    st.markdown("""
    <div class="insight-box">
      <div class="title">Income shapes NCDs in opposite directions</div>
      <div class="body">Higher GDP → more diabetes and obesity but <em>less</em> blood pressure.
      The obesity–BP correlation reversed from r = +0.85 (1980) to r = −0.71 (2014).</div>
    </div>""", unsafe_allow_html=True)
 
with ic2:
    st.markdown("""
    <div class="insight-box">
      <div class="title">The crossover: obesity overtook BP in 2010</div>
      <div class="body">Obesity rose from 9.3% (1975) to 28.8% (2016).
      Blood pressure fell from 32.9% to 23.8% over the same period.</div>
    </div>""", unsafe_allow_html=True)
 
with ic3:
    st.markdown("""
    <div class="insight-box">
      <div class="title">One region, two epidemics</div>
      <div class="body">Gulf states carry a metabolic burden (high obesity + diabetes).
      Lower-income MENA carries a vascular burden (high blood pressure).
      A single policy cannot address both.</div>
    </div>""", unsafe_allow_html=True)
 
st.divider()
 
# ─── Two-column summary charts ────────────────────────────────────────────────
left, right = st.columns(2)
 
# Left — Diverging NCD trends (MENA-wide)
with left:
    st.markdown("**MENA-wide NCD trends 1975–2016**")
    trend = (
        df[df["Sub_Region"].notna()]
        .groupby(["Year","Indicator"])["Prevalence_pct"]
        .median().round(1).reset_index()
    )
    hover = alt.selection_point(fields=["Indicator"], on="mouseover", empty=True)
    end_df = trend.sort_values("Year").groupby("Indicator").last().reset_index()
 
    lines = (
        alt.Chart(trend).mark_line(strokeWidth=2.5)
        .encode(
            x=alt.X("Year:O", title=None,
                     axis=alt.Axis(grid=False, labelFontSize=9, tickCount=8)),
            y=alt.Y("Prevalence_pct:Q", title="Median prevalence (%)",
                     axis=alt.Axis(grid=True, gridColor="#e8e8e8")),
            color=alt.Color("Indicator:N", legend=None,
                scale=alt.Scale(domain=INDICATOR_ORDER,
                                range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER])),
            strokeWidth=alt.condition(hover, alt.value(4), alt.value(2)),
            opacity=alt.condition(hover, alt.value(1.0), alt.value(0.6)),
            tooltip=[alt.Tooltip("Year:O"), alt.Tooltip("Indicator:N"),
                     alt.Tooltip("Prevalence_pct:Q", format=".1f", title="Prevalence (%)")],
        ).add_params(hover)
    )
    end_labels = (
        alt.Chart(end_df).mark_text(align="left", dx=5, fontSize=10, fontWeight="bold")
        .encode(x="Year:O", y="Prevalence_pct:Q", text="Indicator:N",
            color=alt.Color("Indicator:N", legend=None,
                scale=alt.Scale(domain=INDICATOR_ORDER,
                                range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER])))
    )
    end_vals = (
        alt.Chart(end_df).mark_text(align="left", dx=5, dy=13, fontSize=9, color="#888")
        .encode(x="Year:O", y="Prevalence_pct:Q",
                text=alt.Text("Prevalence_pct:Q", format=".1f"))
    )
    st.altair_chart((lines + end_labels + end_vals)
                    .properties(width=420, height=280), use_container_width=False)
 
# Right — Sub-regional comparison 2014
with right:
    st.markdown("**NCD burden by sub-region (2014)**")
    subr = (
        df[(df["Year"]==2014) & df["Sub_Region"].notna()]
        .groupby(["Sub_Region","Indicator"])["Prevalence_pct"]
        .median().round(1).reset_index()
    )
    sub_chart = (
        alt.Chart(subr).mark_bar()
        .encode(
            x=alt.X("Prevalence_pct:Q", title="Median prevalence (%)",
                     axis=alt.Axis(grid=True, gridColor="#e8e8e8")),
            y=alt.Y("Sub_Region:N", sort=SUB_REGION_ORDER, title=None),
            color=alt.Color("Indicator:N",
                scale=alt.Scale(domain=INDICATOR_ORDER,
                                range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER]),
                legend=alt.Legend(orient="bottom", labelFontSize=10)),
            xOffset=alt.XOffset("Indicator:N", sort=INDICATOR_ORDER),
            tooltip=[alt.Tooltip("Sub_Region:N"), alt.Tooltip("Indicator:N"),
                     alt.Tooltip("Prevalence_pct:Q", format=".1f", title="Prevalence (%)")],
        ).properties(width=420, height=280)
    )
    st.altair_chart(sub_chart, use_container_width=False)
 
st.divider()
st.caption(
    "Data: NCD-RisC (2016a, 2016b, 2017) · World Bank GDP, population & income classification · "
    "UN World Population Prospects (2024) · WHO GHO Life Expectancy. "
    "23 MENA countries · age-standardised prevalence · country-equal median. "
    "Built with Streamlit + Altair (Satyanarayan et al., 2017)."
)
