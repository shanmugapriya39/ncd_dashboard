import pandas as pd
import numpy as np
import streamlit as st
 
# ─── Sub-region mapping ───────────────────────────────────────────────────────
SUB_REGION = {
    "Saudi Arabia": "Gulf", "Kuwait": "Gulf", "United Arab Emirates": "Gulf",
    "Qatar": "Gulf", "Bahrain": "Gulf", "Oman": "Gulf",
    "Algeria": "North Africa", "Tunisia": "North Africa", "Libya": "North Africa",
    "Egypt": "North Africa", "Morocco": "North Africa",
    "Lebanon": "Levant", "Jordan": "Levant", "Israel": "Levant",
    "Malta": "Levant", "Iraq": "Levant", "Iran": "Levant",
    "Yemen": "Lower-income MENA", "Syria": "Lower-income MENA",
    "Afghanistan": "Lower-income MENA", "Djibouti": "Lower-income MENA",
    "Palestine": "Lower-income MENA", "Pakistan": "Lower-income MENA",
}
 
INCOME_TIER = {
    "Afghanistan": "Low", "Djibouti": "Low", "Syria": "Low",
    "Yemen": "Low", "Pakistan": "Low", "Palestine": "Low",
    "Morocco": "Medium", "Jordan": "Medium", "Tunisia": "Medium",
    "Egypt": "Medium", "Iraq": "Medium", "Lebanon": "Medium",
    "Algeria": "Medium", "Libya": "Medium", "Iran": "Medium",
    "Malta": "High", "Israel": "High", "Bahrain": "High", "Oman": "High",
    "Saudi Arabia": "High", "United Arab Emirates": "High",
    "Kuwait": "High", "Qatar": "High",
}
 
ISO_NUMERIC = {
    "Saudi Arabia": 682, "Kuwait": 414, "United Arab Emirates": 784,
    "Qatar": 634, "Bahrain": 48, "Oman": 512,
    "Algeria": 12, "Tunisia": 788, "Libya": 434, "Egypt": 818, "Morocco": 504,
    "Lebanon": 422, "Jordan": 400, "Israel": 376, "Malta": 470,
    "Iraq": 368, "Iran": 364,
    "Yemen": 887, "Syria": 760, "Afghanistan": 4, "Djibouti": 262,
    "Palestine": 275, "Pakistan": 586,
}
 
MENA_COUNTRIES = list(SUB_REGION.keys())
 
# ─── Order + colour constants ─────────────────────────────────────────────────
SUB_REGION_ORDER  = ["Gulf", "Levant", "North Africa", "Lower-income MENA"]
INDICATOR_ORDER   = ["Blood Pressure", "Diabetes", "Obesity"]
 
SUB_REGION_COLORS = {
    "Gulf": "#1D9E75", "Levant": "#4C78A8",
    "North Africa": "#F58518", "Lower-income MENA": "#E45756",
}
INDICATOR_COLORS  = {
    "Blood Pressure": "#4C78A8", "Diabetes": "#E45756", "Obesity": "#F58518",
}
 
WB_REGION_COLORS = {
    "MENA": "#1D9E75",
    "North America": "#636363", "East Asia & Pacific": "#969696",
    "Latin America": "#bdbdbd", "Europe & C. Asia": "#d9d9d9",
    "Sub-Saharan Africa": "#f0f0f0", "South Asia": "#cccccc",
}
 
WORLD_110M_URL = "https://cdn.jsdelivr.net/npm/vega-datasets@v1/data/world-110m.json"
WORLD_50M_URL  = "https://cdn.jsdelivr.net/npm/vega-datasets@v1/data/world-50m.json"
 
# ─── Country centroid + label nudge ──────────────────────────────────────────
COUNTRY_CENTROIDS = {
    "Saudi Arabia": (45.0, 24.0), "Kuwait": (47.6, 29.3),
    "United Arab Emirates": (54.0, 24.0), "Qatar": (51.2, 25.3),
    "Bahrain": (50.55, 26.0), "Oman": (57.0, 21.0),
    "Algeria": (3.0, 28.0), "Tunisia": (9.5, 34.0), "Libya": (17.0, 27.0),
    "Egypt": (30.0, 26.5), "Morocco": (-6.0, 32.0),
    "Lebanon": (35.8, 33.9), "Jordan": (36.5, 31.2), "Israel": (34.9, 31.5),
    "Malta": (14.4, 35.9), "Iraq": (44.0, 33.0), "Iran": (53.5, 32.0),
    "Yemen": (47.5, 15.5), "Syria": (38.0, 35.0), "Afghanistan": (66.0, 33.0),
    "Djibouti": (42.6, 11.8), "Palestine": (35.2, 31.9), "Pakistan": (69.5, 30.0),
}
 
LABEL_NUDGE = {
    "Kuwait": (18, -10), "Qatar": (18, 4), "Bahrain": (18, 14),
    "United Arab Emirates": (10, 14), "Israel": (-18, -10),
    "Palestine": (-22, 4), "Lebanon": (-22, 14), "Jordan": (-10, 18),
    "Djibouti": (18, 0), "Malta": (-18, 0),
}
 
# ─── Shared CSS ──────────────────────────────────────────────────────────────
SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.2rem !important; }
.page-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    border-radius: 12px; padding: 22px 28px; margin-bottom: 18px;
    display: flex; align-items: center; justify-content: space-between;
}
.page-header h1 { color:#fff; font-size:22px; font-weight:700; margin:0 0 4px 0; }
.page-header p  { color:rgba(255,255,255,0.65); font-size:12px; margin:0; }
.page-header .badge {
    background:rgba(29,158,117,0.25); border:1px solid #1D9E75;
    color:#1D9E75; font-size:10px; font-weight:700; letter-spacing:1px;
    text-transform:uppercase; padding:4px 10px; border-radius:20px;
}
.kpi { background:#fff; border:1px solid #e8e8e8; border-radius:10px;
       padding:14px 16px; border-top:3px solid #1D9E75; }
.kpi .v { font-size:22px; font-weight:700; color:#1a1a2e; line-height:1; margin-bottom:4px; }
.kpi .l { font-size:11px; color:#777; line-height:1.35; }
.insight-box {
    background:#f0fdf9; border:1px solid #1D9E75; border-radius:8px;
    padding:12px 16px; margin-bottom:8px;
}
.insight-box .title { font-size:11px; font-weight:700; color:#1D9E75;
    text-transform:uppercase; letter-spacing:0.8px; margin-bottom:4px; }
.insight-box .body  { font-size:13px; color:#1a1a2e; line-height:1.5; }
</style>
"""
 
# ─── Data loader (cached) ─────────────────────────────────────────────────────
@st.cache_data
def load_ncd():
    df = pd.read_csv("ncd_merged.csv")
    df = df[df["Country"].isin(MENA_COUNTRIES)].copy()
    df["Sub_Region"]  = df["Country"].map(SUB_REGION)
    df["Income_Tier"] = df["Country"].map(INCOME_TIER)
    df["ISO_numeric"] = df["Country"].map(ISO_NUMERIC)
    df["Pop_sqrt"]    = np.sqrt(df["Population"].fillna(0))
    return df
 
@st.cache_data
def load_global():
    """Full NCD dataset for global comparisons (all World Bank regions)."""
    bp  = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Raised Blood Pressure")
    bmi = pd.read_excel("cw1 -dataset.xlsx", sheet_name="BMI")
    dia = pd.read_excel("cw1 -dataset.xlsx", sheet_name="Diabetes")
    bp.columns  = ["Country","Sex","Year","Prevalence"]
    bmi.columns = ["Country","Sex","Year","Prevalence"]
    dia.columns = ["Country","Sex","Year","Prevalence"]
    bp["Indicator"]  = "Blood Pressure"
    bmi["Indicator"] = "Obesity"
    dia["Indicator"] = "Diabetes"
    df = pd.concat([bp, bmi, dia], ignore_index=True)
    df["Prevalence_pct"] = (df["Prevalence"] * 100).round(1)
    wb = pd.read_excel("CLASS_2025_10_07.xlsx", sheet_name="List of economies")
    wb = wb[["Economy","Region","Income group"]].dropna(subset=["Region"])
    wb.columns = ["Country","WB_Region","Income_group"]
    df = df.merge(wb, on="Country", how="left")
    df["WB_Region"] = df["WB_Region"].fillna("Unknown")
    return df
 
@st.cache_data
def load_life_expectancy():
    le = pd.read_csv("life-expectancy.csv")
    le.columns = ["Country", "Code", "Year", "Life_expectancy"]
    return le[["Country", "Year", "Life_expectancy"]]
 
@st.cache_data
def load_median_age():
    ma = pd.read_csv("median-age.csv")
    ma.columns = ["Country", "Code", "Year", "Median_age", "Median_age_proj"]
    return ma[["Country", "Year", "Median_age"]]
 
def ax_clean(grid=False, label_size=10):
    """Return standard axis config — no grid by default."""
    import altair as alt
    return alt.Axis(grid=grid, gridColor="#e8e8e8", gridWidth=0.8,
                    labelFontSize=label_size)
 