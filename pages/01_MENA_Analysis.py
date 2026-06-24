
import streamlit as st
import pandas as pd
import altair as alt
 
# World boundary topology used by the choropleth below. This is fetched
# by the browser at render time (not by Python), so no extra package
# (vega_datasets) is needed — just an internet connection when viewing
# the dashboard.
WORLD_110M_URL = "https://cdn.jsdelivr.net/npm/vega-datasets@v1/data/world-110m.json"
 
st.set_page_config(page_title="MENA Deep Dive", layout="wide")
 
# ─────────────────────────────────────────────────────────────────
# Page styling (scoped to this page only — app.py is untouched).
# Built around the teal already used for the Gulf sub-region (#1D9E75)
# so the new chrome matches the existing chart palette rather than
# introducing a clashing color.
#
# NOTE: the data-testid selectors below target Streamlit's internal
# DOM structure, which can shift between versions. If a given rule
# doesn't visibly apply on your Streamlit version, it's a harmless
# no-op — the actual layout (tabs + bordered cards) does not depend
# on this CSS to function.
# ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&display=swap');
 
    .mena-header {
        background: linear-gradient(135deg, #1D9E75 0%, #146854 100%);
        border-radius: 18px;
        padding: 30px 36px;
        margin-bottom: 26px;
    }
    .mena-header h1 {
        font-family: 'Source Serif 4', Georgia, serif;
        color: #ffffff;
        font-size: 30px;
        font-weight: 700;
        margin: 0 0 10px 0;
    }
    .mena-header p {
        color: rgba(255,255,255,0.90);
        font-size: 14.5px;
        line-height: 1.55;
        margin: 0;
        max-width: 800px;
    }
 
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border-color: #E3E3E0 !important;
    }
 
    div[data-testid="stMetricValue"] {
        font-size: 25px;
        color: #146854;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12.5px;
        color: #5b5b58;
    }
 
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E9F6F1;
        color: #146854;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ─────────────────────────────────────────────────────────────────
# Locked-in groupings (see project methodology notes).
# Sub-region and income tier are NOT part of ncd_merged.csv — they're
# computed here, on this page only, per the documented decision that
# these groupings are "used ONLY in specific charts, not propagated
# everywhere."
# ─────────────────────────────────────────────────────────────────
SUB_REGION = {
    # Gulf
    "Saudi Arabia": "Gulf", "Kuwait": "Gulf", "United Arab Emirates": "Gulf",
    "Qatar": "Gulf", "Bahrain": "Gulf", "Oman": "Gulf",
    # North Africa
    "Algeria": "North Africa", "Tunisia": "North Africa", "Libya": "North Africa",
    "Egypt": "North Africa", "Morocco": "North Africa",
    # Levant
    "Lebanon": "Levant", "Jordan": "Levant", "Israel": "Levant",
    "Malta": "Levant", "Iraq": "Levant", "Iran": "Levant",
    # Lower-income MENA
    "Yemen": "Lower-income MENA", "Syria": "Lower-income MENA",
    "Afghanistan": "Lower-income MENA", "Djibouti": "Lower-income MENA",
    "Palestine": "Lower-income MENA", "Pakistan": "Lower-income MENA",
}
 
INCOME_TIER = {
    # Low (<$5,000, 2014 GDP)
    "Afghanistan": "Low", "Djibouti": "Low", "Syria": "Low",
    "Yemen": "Low", "Pakistan": "Low", "Palestine": "Low",
    # Medium ($5,000–$20,000)
    "Morocco": "Medium", "Jordan": "Medium", "Tunisia": "Medium",
    "Egypt": "Medium", "Iraq": "Medium", "Lebanon": "Medium",
    "Algeria": "Medium", "Libya": "Medium", "Iran": "Medium",
    # High (>$20,000)
    "Malta": "High", "Israel": "High", "Bahrain": "High", "Oman": "High",
    "Saudi Arabia": "High", "United Arab Emirates": "High",
    "Kuwait": "High", "Qatar": "High",
}
 
# ISO 3166-1 numeric codes — needed for the choropleth's geo-lookup.
# NOTE: low-resolution world topologies sometimes drop very small
# territories (e.g. Palestine, Bahrain, Malta). If a country looks
# missing on the map, that's the likely cause, not a data bug.
ISO_NUMERIC = {
    "Saudi Arabia": 682, "Kuwait": 414, "United Arab Emirates": 784,
    "Qatar": 634, "Bahrain": 48, "Oman": 512,
    "Algeria": 12, "Tunisia": 788, "Libya": 434, "Egypt": 818, "Morocco": 504,
    "Lebanon": 422, "Jordan": 400, "Israel": 376, "Malta": 470, "Iraq": 368, "Iran": 364,
    "Yemen": 887, "Syria": 760, "Afghanistan": 4, "Djibouti": 262,
    "Palestine": 275, "Pakistan": 586,
}
 
# Approximate country centroids (lon, lat) — used only to place text labels
# on the choropleth. Rough geographic centers, not precise centroids.
COUNTRY_CENTROIDS = {
    "Saudi Arabia": (45.0, 24.0), "Kuwait": (47.6, 29.3), "United Arab Emirates": (54.0, 24.0),
    "Qatar": (51.2, 25.3), "Bahrain": (50.55, 26.0), "Oman": (57.0, 21.0),
    "Algeria": (3.0, 28.0), "Tunisia": (9.5, 34.0), "Libya": (17.0, 27.0),
    "Egypt": (30.0, 26.5), "Morocco": (-6.0, 32.0),
    "Lebanon": (35.8, 33.9), "Jordan": (36.5, 31.2), "Israel": (34.9, 31.5),
    "Malta": (14.4, 35.9), "Iraq": (44.0, 33.0), "Iran": (53.5, 32.0),
    "Yemen": (47.5, 15.5), "Syria": (38.0, 35.0), "Afghanistan": (66.0, 33.0),
    "Djibouti": (42.6, 11.8), "Palestine": (35.2, 31.9), "Pakistan": (69.5, 30.0),
}
 
# Pixel nudge offsets (dx, dy) applied on top of centroid positions.
# Small Gulf/Levant states cluster tightly — offsets spread their labels
# outward so they don't overlap each other on the Mercator projection.
LABEL_NUDGE = {
    "Kuwait":              ( 18, -10),
    "Qatar":               ( 18,   4),
    "Bahrain":             ( 18,  14),
    "United Arab Emirates":( 10,  14),
    "Israel":              (-18, -10),
    "Palestine":           (-22,   4),
    "Lebanon":             (-22,  14),
    "Jordan":              (-10,  18),
    "Djibouti":            ( 18,   0),
    "Malta":               (-18,   0),
}
 
SUB_REGION_ORDER = ["Gulf", "Levant", "North Africa", "Lower-income MENA"]
TIER_ORDER = ["Low", "Medium", "High"]
INDICATOR_ORDER = ["Blood Pressure", "Diabetes", "Obesity"]
 
SUB_REGION_COLORS = {
    "Gulf": "#1D9E75", "Levant": "#4C78A8",
    "North Africa": "#F58518", "Lower-income MENA": "#E45756",
}
INDICATOR_COLORS = {
    "Blood Pressure": "#4C78A8", "Diabetes": "#E45756", "Obesity": "#F58518",
}
 
# ─────────────────────────────────────────────────────────────────
# Load data
# Expects ncd_merged.csv (built by prepare_data.py) with at least:
#   Country, Sex, Year, Indicator, Prevalence_pct, GDP_per_capita, Population
# If your prepare_data.py uses different column names, rename them
# here rather than touching the chart code below.
# ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_mena_data():
    df = pd.read_csv("ncd_merged.csv")
    df = df[df["Country"].isin(SUB_REGION.keys())].copy()
    df["Sub_Region"] = df["Country"].map(SUB_REGION)
    df["Income_Tier"] = df["Country"].map(INCOME_TIER)
    df["ISO_numeric"] = df["Country"].map(ISO_NUMERIC)
    return df
 
 
df = load_mena_data()
 
# ─────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────
if st.button("← Back to Global Overview"):
    st.switch_page("app.py")
 
st.markdown(
    """
    <div class="mena-header">
        <h1>MENA Region – Deep Dive</h1>
        <p>
            Zooming into the 23 MENA countries to examine which countries carry the
            highest NCD burden and why. This page explores how the region's NCD burden
            is distributed across sub-regions, how it relates to national income,
            when the current trends began, and how prevalence differs by sex over
            time and across countries.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
 
# ═══════════════════════════════════════════════════════════════
# KPI cards
# ═══════════════════════════════════════════════════════════════
gdp_2014 = df[df["Year"] == 2014][["Country", "Sub_Region", "GDP_per_capita"]].drop_duplicates()
 
gulf_gdp = gdp_2014.loc[gdp_2014["Sub_Region"] == "Gulf", "GDP_per_capita"].median()
levant_gdp = gdp_2014.loc[gdp_2014["Sub_Region"] == "Levant", "GDP_per_capita"].median()
na_gdp = gdp_2014.loc[gdp_2014["Sub_Region"] == "North Africa", "GDP_per_capita"].median()
low_gdp = gdp_2014.loc[gdp_2014["Sub_Region"] == "Lower-income MENA", "GDP_per_capita"].median()
 
dia_2014 = df[(df["Year"] == 2014) & (df["Indicator"] == "Diabetes")]
dia_by_subregion = dia_2014.groupby("Sub_Region")["Prevalence_pct"].median()
diabetes_gap = dia_by_subregion.get("Gulf", float("nan")) - dia_by_subregion.get("Lower-income MENA", float("nan"))
 
income_ratio = gulf_gdp / low_gdp
 
kpi_info = [
    ("Gulf median GDP (2014)", f"${gulf_gdp:,.0f}"),
    ("Lower-income MENA median GDP", f"${low_gdp:,.0f}"),
    ("Gulf vs. Lower-income diabetes gap", f"{diabetes_gap:.1f} pts"),
    ("Income ratio (Gulf : Lower-income)", f"{income_ratio:.0f}×"),
]
 
kpi_cols = st.columns(4)
for col, (label, value) in zip(kpi_cols, kpi_info):
    with col.container(border=True):
        st.metric(label, value)
 
st.write("")
 
# ═══════════════════════════════════════════════════════════════
# Tabs — group the charts into logical sections instead of one
# long vertical scroll.
# ═══════════════════════════════════════════════════════════════
tab_subregion, tab_income, tab_trends, tab_triad, tab_population, tab_ranking, tab_gender = st.tabs(
    ["Sub-Regional Burden", "Income & GDP", "Trends Over Time", "Metabolic Triad", "Population & Prevalence", "Country Ranking", "Gender & Geography"]
)
 
# ───────────────────────────────────────────────────────────────
# Tab 1 — Sub-regional comparison (AQ5)
# ───────────────────────────────────────────────────────────────
with tab_subregion:
    with st.container(border=True):
        st.subheader("Sub-regional comparison: is MENA's NCD burden evenly distributed?")
        # NOTE: every literal "$" below is escaped as "\$" — Streamlit/KaTeX treats
        # unescaped pairs of "$" as inline LaTeX, which mangles dollar figures.
        st.caption(
            f"Median prevalence by sub-region, 2014. Groupings reflect median GDP per capita: "
            f"Gulf (\\${gulf_gdp:,.0f}) > Levant (\\${levant_gdp:,.0f}) > "
            f"North Africa (\\${na_gdp:,.0f}) > Lower-income MENA (\\${low_gdp:,.0f})."
        )
 
        subregional = (
            df[(df["Year"] == 2014) & (df["Sub_Region"].notna())]
            .groupby(["Sub_Region", "Indicator"])["Prevalence_pct"]
            .median()
            .round(1)
            .reset_index()
        )
 
        chart_subregion = (
            alt.Chart(subregional)
            .mark_bar()
            .encode(
                x=alt.X("Prevalence_pct:Q", title="Median prevalence (%)"),
                y=alt.Y("Sub_Region:N", sort=SUB_REGION_ORDER, title=None),
                color=alt.Color(
                    "Sub_Region:N",
                    scale=alt.Scale(domain=SUB_REGION_ORDER, range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER]),
                    legend=None,
                ),
                facet=alt.Facet("Indicator:N", columns=3, header=alt.Header(labelFontSize=13, labelFontWeight="bold"), sort=INDICATOR_ORDER),
                tooltip=[
                    alt.Tooltip("Sub_Region:N", title="Sub-region"),
                    alt.Tooltip("Indicator:N", title="Indicator"),
                    alt.Tooltip("Prevalence_pct:Q", title="Median prevalence (%)", format=".1f"),
                ],
            )
            .properties(width=220, height=220)
        )
 
        st.altair_chart(chart_subregion, use_container_width=False)
 
# ───────────────────────────────────────────────────────────────
# Tab 2 — Gapminder scatter (AQ1) + Country trajectories (AQ1+AQ6)
# ───────────────────────────────────────────────────────────────
with tab_income:
    with st.container(border=True):
        st.subheader("Income and NCD prevalence within MENA")
        st.caption("Each point is one MENA country. Bubble size encodes population, scaled by square root to prevent large-population countries (Pakistan, 214M) from visually dominating small ones (Bahrain, 1.4M) — rank ordering is preserved. Drag the slider to see how the relationship changes over time.")
 
        gapminder_df = df[df["Sub_Region"].notna() & df["GDP_per_capita"].notna() & df["Population"].notna()].copy()
        # Square-root scale population for bubble area — raw population values
        # cause Pakistan's bubble to dominate; sqrt compression preserves rank
        # ordering while giving all countries a legible bubble size.
        import numpy as np
        gapminder_df["Pop_sqrt"] = np.sqrt(gapminder_df["Population"])
 
        year_slider = alt.binding_range(min=1975, max=2016, step=1, name="Year: ")
        year_select = alt.selection_point(fields=["Year"], bind=year_slider, value=2014)
 
        gapminder_chart = (
            alt.Chart(gapminder_df)
            .mark_circle(opacity=0.75)
            .encode(
                x=alt.X("GDP_per_capita:Q", title="GDP per capita (log scale, US$)",
                         scale=alt.Scale(type="log"),
                         axis=alt.Axis(grid=False)),
                y=alt.Y("Prevalence_pct:Q", title="Prevalence (%)",
                         axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8)),
                size=alt.Size("Pop_sqrt:Q", title="Population (√-scaled)",
                               scale=alt.Scale(range=[50, 1500]), legend=None),
                color=alt.Color(
                    "Sub_Region:N",
                    title="Sub-region",
                    scale=alt.Scale(domain=SUB_REGION_ORDER, range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER]),
                ),
                facet=alt.Facet("Indicator:N", columns=3, header=alt.Header(labelFontSize=13, labelFontWeight="bold"), sort=INDICATOR_ORDER),
                tooltip=[
                    alt.Tooltip("Country:N"),
                    alt.Tooltip("Indicator:N"),
                    alt.Tooltip("GDP_per_capita:Q", title="GDP per capita ($)", format=",.0f"),
                    alt.Tooltip("Prevalence_pct:Q", title="Prevalence (%)", format=".1f"),
                    alt.Tooltip("Population:Q", title="Population", format=",.0f"),
                ],
            )
            .add_params(year_select)
            .transform_filter(year_select)
            .properties(width=220, height=300)
        )
 
        st.altair_chart(gapminder_chart, use_container_width=False)
 
    with st.container(border=True):
        st.subheader("Country trajectories by income tier")
        st.caption(
            "Income tiers defined by 2014 GDP per capita breakpoints: Low (<\\$5,000), "
            "Medium (\\$5,000–\\$20,000), High (>\\$20,000). Choose one country from each "
            "tier to compare how GDP and NCD prevalence have moved together since 1975."
        )
 
        low_countries = sorted(c for c, t in INCOME_TIER.items() if t == "Low")
        medium_countries = sorted(c for c, t in INCOME_TIER.items() if t == "Medium")
        high_countries = sorted(c for c, t in INCOME_TIER.items() if t == "High")
 
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            default_low = low_countries.index("Yemen") if "Yemen" in low_countries else 0
            low_country = st.selectbox("Low income country:", low_countries, index=default_low)
        with c2:
            default_med = medium_countries.index("Algeria") if "Algeria" in medium_countries else 0
            medium_country = st.selectbox("Medium income country:", medium_countries, index=default_med)
        with c3:
            default_high = high_countries.index("Bahrain") if "Bahrain" in high_countries else 0
            high_country = st.selectbox("High income country:", high_countries, index=default_high)
        with c4:
            traj_indicator = st.selectbox("Choose indicator:", INDICATOR_ORDER)
 
        selected_countries = [low_country, medium_country, high_country]
        traj_colors = {low_country: "#E45756", medium_country: "#F58518", high_country: "#1D9E75"}
 
        traj_df = (
            df[df["Country"].isin(selected_countries) & (df["Indicator"] == traj_indicator) & df["GDP_per_capita"].notna()]
            .groupby(["Country", "Year"])[["Prevalence_pct", "GDP_per_capita"]]
            .median()
            .reset_index()
        )
 
        trajectory_chart = (
            alt.Chart(traj_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("GDP_per_capita:Q", title="GDP per capita (log scale, US$)",
                         scale=alt.Scale(type="log"),
                         axis=alt.Axis(grid=False)),
                y=alt.Y("Prevalence_pct:Q", title=f"{traj_indicator} prevalence (%)",
                         axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8)),
                order="Year:O",
                color=alt.Color(
                    "Country:N",
                    scale=alt.Scale(domain=selected_countries, range=[traj_colors[c] for c in selected_countries]),
                ),
                tooltip=[
                    alt.Tooltip("Country:N"),
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("GDP_per_capita:Q", title="GDP per capita ($)", format=",.0f"),
                    alt.Tooltip("Prevalence_pct:Q", title=f"{traj_indicator} (%)", format=".1f"),
                ],
            )
            .properties(width=700, height=400, title=f"{traj_indicator}: trajectories by income tier, 1975–2016")
        )
 
        st.altair_chart(trajectory_chart, use_container_width=False)
 
# ───────────────────────────────────────────────────────────────
# Tab 3 — Diverging trends, all 3 indicators (AQ6)
# ───────────────────────────────────────────────────────────────
with tab_trends:
    with st.container(border=True):
        st.subheader("Diverging trends: metabolic disease vs. blood pressure over time")
        st.caption(
            "MENA-wide median prevalence over time, 1975–2016. Diabetes and obesity rise "
            "while blood pressure declines — a clear divergence in trajectory."
        )
 
        mena_trend = (
            df[df["Sub_Region"].notna()]
            .groupby(["Year", "Indicator"])["Prevalence_pct"]
            .median()
            .round(1)
            .reset_index()
        )
 
        # Hover selection — when user mouses over a line, that indicator
        # thickens to 4px; others fade to 0.3 opacity. nearest=True snaps
        # the selection to the closest point on hover.
        hover = alt.selection_point(fields=["Indicator"], on="mouseover",
                                    nearest=False, empty=True)
 
        lines = (
            alt.Chart(mena_trend)
            .mark_line()
            .encode(
                x=alt.X("Year:O", title="Year",
                         axis=alt.Axis(grid=False)),
                y=alt.Y("Prevalence_pct:Q", title="Median prevalence (%)",
                         axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8)),
                color=alt.Color(
                    "Indicator:N",
                    title="Indicator",
                    scale=alt.Scale(domain=INDICATOR_ORDER, range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER]),
                    legend=None,
                ),
                strokeWidth=alt.condition(hover, alt.value(4), alt.value(2)),
                opacity=alt.condition(hover, alt.value(1.0), alt.value(0.6)),
                tooltip=[
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("Indicator:N"),
                    alt.Tooltip("Prevalence_pct:Q", title="Median prevalence (%)", format=".1f"),
                ],
            )
            .add_params(hover)
        )
 
        # End-of-line labels — take the LAST available year per indicator
        # (BP ends 2015, Diabetes ends 2014, Obesity ends 2016 — different
        # end years mean a single global max only captures Obesity)
        end_labels_df = (
            mena_trend.sort_values("Year")
            .groupby("Indicator")
            .last()
            .reset_index()
        )
 
        end_labels = (
            alt.Chart(end_labels_df)
            .mark_text(align="left", dx=6, fontSize=11, fontWeight="bold")
            .encode(
                x=alt.X("Year:O"),
                y=alt.Y("Prevalence_pct:Q"),
                text=alt.Text("Indicator:N"),
                color=alt.Color(
                    "Indicator:N",
                    scale=alt.Scale(domain=INDICATOR_ORDER, range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER]),
                    legend=None,
                ),
            )
        )
 
        # Value labels — show the actual prevalence number at line end
        end_values = (
            alt.Chart(end_labels_df)
            .mark_text(align="left", dx=6, dy=13, fontSize=10, color="#666666")
            .encode(
                x=alt.X("Year:O"),
                y=alt.Y("Prevalence_pct:Q"),
                text=alt.Text("Prevalence_pct:Q", format=".1f"),
            )
        )
 
        diverging_chart = (
            (lines + end_labels + end_values)
            .properties(width=680, height=350, title="MENA-wide NCD trends, 1975–2016")
        )
 
        st.altair_chart(diverging_chart, use_container_width=False)
 
# ───────────────────────────────────────────────────────────────
# Tab 4 — Metabolic triad: relationship between the three indicators (AQ3)
# ───────────────────────────────────────────────────────────────
with tab_triad:
    with st.container(border=True):
        st.subheader("How are blood pressure, diabetes, and obesity related within MENA?")
        st.caption(
            "Each point is one MENA country. Position shows obesity (x-axis) and diabetes "
            "(y-axis) prevalence; colour shows blood pressure prevalence. Drag the slider to "
            "see how the relationship changes over time."
        )
 
        # Wide-format table: one row per country-year, one column per indicator,
        # so the three indicators can be plotted against each other directly.
        triad_wide = (
            df[df["Sub_Region"].notna()]
            .groupby(["Country", "Sub_Region", "Year", "Indicator"])["Prevalence_pct"]
            .median()
            .unstack("Indicator")
            .reset_index()
            .dropna(subset=["Blood Pressure", "Diabetes", "Obesity"])
        )
 
        # Join population so bubble size can encode it (sqrt-scaled, same
        # rationale as the Gapminder scatter — raw values let Pakistan dominate)
        pop_lookup = (
            df[df["Population"].notna()]
            .groupby(["Country", "Year"])["Population"]
            .median()
            .reset_index()
        )
        triad_wide = triad_wide.merge(pop_lookup, on=["Country", "Year"], how="left")
        import numpy as np
        triad_wide["Pop_sqrt"] = np.sqrt(triad_wide["Population"].fillna(triad_wide["Population"].median()))
 
        triad_year_slider = alt.binding_range(min=1975, max=2016, step=1, name="Year: ")
        triad_year_select = alt.selection_point(fields=["Year"], bind=triad_year_slider, value=2014)
 
        triad_chart = (
            alt.Chart(triad_wide)
            .mark_circle(size=120, opacity=0.85)
            .encode(
                x=alt.X("Obesity:Q", title="Obesity prevalence (%)",
                         scale=alt.Scale(zero=False),
                         axis=alt.Axis(grid=False)),
                y=alt.Y("Diabetes:Q", title="Diabetes prevalence (%)",
                         scale=alt.Scale(zero=False),
                         axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8)),
                color=alt.Color(
                    "Blood Pressure:Q",
                    title="Blood Pressure (%)",
                    scale=alt.Scale(scheme="redblue", reverse=True),
                ),
                tooltip=[
                    alt.Tooltip("Country:N"),
                    alt.Tooltip("Sub_Region:N", title="Sub-region"),
                    alt.Tooltip("Obesity:Q", title="Obesity (%)", format=".1f"),
                    alt.Tooltip("Diabetes:Q", title="Diabetes (%)", format=".1f"),
                    alt.Tooltip("Blood Pressure:Q", title="Blood Pressure (%)", format=".1f"),
                ],
            )
            .add_params(triad_year_select)
            .transform_filter(triad_year_select)
            .properties(width=680, height=420, title="Metabolic triad: Obesity, Diabetes, and Blood Pressure, MENA")
        )
 
        st.altair_chart(triad_chart, use_container_width=False)
 
        # Pearson correlation coefficients, fixed to 2014 for consistency with the
        # rest of the dashboard's static-year comparisons (e.g. the KPI cards and
        # sub-regional chart) — gives an exact, citable number for the report
        # rather than a visual read of the scatter above.
        corr_year = 2014
        corr_input = triad_wide.loc[triad_wide["Year"] == corr_year, ["Country", "Blood Pressure", "Diabetes", "Obesity"]]
        corr_matrix = corr_input[["Blood Pressure", "Diabetes", "Obesity"]].corr(method="pearson").round(2)
 
        n_countries = len(corr_input)
        missing_countries = sorted(set(SUB_REGION.keys()) - set(corr_input["Country"]))
 
        st.caption(
            f"Pearson correlation coefficients across {n_countries} MENA countries, {corr_year} "
            f"(country-level median of Men/Women)."
        )
        if missing_countries:
            st.caption(
                f"Note: excluded from this correlation due to a missing value in at least one "
                f"indicator for {corr_year}: {', '.join(missing_countries)}."
            )
        st.dataframe(corr_matrix, use_container_width=False)
 
        st.divider()
        st.markdown("**Has this relationship changed over time?**")
        st.caption(
            "Pearson correlation between each pair of indicators, computed separately for "
            "every year with at least 5 countries of complete data. A line crossing the "
            "dashed zero-line indicates the direction of that relationship has reversed "
            "over the study period, rather than being a fixed, stable relationship."
        )
 
        yearly_corr_rows = []
        for yr, group in triad_wide.groupby("Year"):
            if len(group) >= 5:
                yearly_corr_rows.append(
                    {
                        "Year": yr,
                        "Obesity vs Blood Pressure": group["Obesity"].corr(group["Blood Pressure"]),
                        "Diabetes vs Blood Pressure": group["Diabetes"].corr(group["Blood Pressure"]),
                        "Obesity vs Diabetes": group["Obesity"].corr(group["Diabetes"]),
                    }
                )
 
        yearly_corr_df = pd.DataFrame(yearly_corr_rows).melt(
            id_vars="Year", var_name="Indicator pair", value_name="Pearson r"
        )
 
        corr_trend_chart = (
            alt.Chart(yearly_corr_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("Pearson r:Q", title="Pearson r", scale=alt.Scale(domain=[-1, 1])),
                color=alt.Color("Indicator pair:N", title="Indicator pair"),
                tooltip=[
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("Indicator pair:N"),
                    alt.Tooltip("Pearson r:Q", format=".2f"),
                ],
            )
        )
 
        zero_line = (
            alt.Chart(pd.DataFrame({"y": [0]}))
            .mark_rule(strokeDash=[4, 4], color="#999999")
            .encode(y="y:Q")
        )
 
        st.altair_chart(
            (corr_trend_chart + zero_line).properties(
                width=700, height=320, title="Correlation between indicator pairs, by year"
            ),
            use_container_width=False,
        )
 
# ───────────────────────────────────────────────────────────────
# ───────────────────────────────────────────────────────────────
# Tab 5 — Population and prevalence (AQ4)
# ───────────────────────────────────────────────────────────────
with tab_population:
    with st.container(border=True):
        st.subheader("Does NCD prevalence track population size?")
        st.caption(
            "Each point is one MENA country. Population on a log scale "
            "(range: 1.4 million — 214 million across MENA). If larger countries "
            "showed higher prevalence, points would trend upward left to right. "
            "The absence of any such trend justifies using prevalence rates rather "
            "than absolute counts as the primary measure throughout this dashboard. "
            "Drag the slider to confirm the pattern holds across all study years."
        )
 
        pop_all = (
            df[df["Sub_Region"].notna() & df["Population"].notna()]
            .groupby(["Country", "Sub_Region", "Year", "Indicator"])
            .agg(Prevalence_pct=("Prevalence_pct", "median"), Population=("Population", "median"))
            .reset_index()
        )
 
        pop_year_slider = alt.binding_range(min=1975, max=2016, step=1, name="Year: ")
        pop_year_select = alt.selection_point(fields=["Year"], bind=pop_year_slider, value=2014)
 
        pop_chart = (
            alt.Chart(pop_all)
            .mark_circle(opacity=0.8, size=90)
            .encode(
                x=alt.X(
                    "Population:Q",
                    title="Population (log scale)",
                    scale=alt.Scale(type="log"),
                    axis=alt.Axis(format="~s", grid=False),
                ),
                y=alt.Y("Prevalence_pct:Q", title="Prevalence (%)",
                         axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8)),
                color=alt.Color(
                    "Sub_Region:N",
                    title="Sub-region",
                    scale=alt.Scale(
                        domain=SUB_REGION_ORDER,
                        range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER],
                    ),
                ),
                facet=alt.Facet(
                    "Indicator:N",
                    columns=3,
                    header=alt.Header(labelFontSize=13, labelFontWeight="bold"),
                    sort=INDICATOR_ORDER,
                ),
                tooltip=[
                    alt.Tooltip("Country:N"),
                    alt.Tooltip("Sub_Region:N", title="Sub-region"),
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("Population:Q", title="Population", format=",.0f"),
                    alt.Tooltip("Prevalence_pct:Q", title="Prevalence (%)", format=".1f"),
                ],
            )
            .add_params(pop_year_select)
            .transform_filter(pop_year_select)
            .properties(width=230, height=270)
        )
 
        st.altair_chart(pop_chart, use_container_width=False)
 
 
# ───────────────────────────────────────────────────────────────
# ───────────────────────────────────────────────────────────────
# Tab 6 — Country ranking: worst combined NCD profile (AQ7)
# ───────────────────────────────────────────────────────────────
with tab_ranking:
    with st.container(border=True):
        st.subheader("Which MENA country carries the most severe combined NCD profile?")
        st.caption(
            "Countries sorted by combined rank score — the sum of each country's rank "
            "across all three indicators, where rank 1 = highest prevalence. "
            "A country dark across all three columns has a broad burden; "
            "dark in only one column indicates a concentrated profile."
        )
 
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            ranking_year = st.selectbox(
                "Choose year:",
                sorted(df["Year"].dropna().unique().astype(int).tolist()),
                index=sorted(df["Year"].dropna().unique().astype(int).tolist()).index(2014),
                key="ranking_year",
            )
        with r_col2:
            ranking_color = st.selectbox(
                "Colour scale:",
                ["Combined (orangered)", "Blood Pressure (blues)", "Diabetes (reds)", "Obesity (oranges)"],
                key="ranking_color",
            )
 
        color_scheme_map = {
            "Combined (orangered)": "orangered",
            "Blood Pressure (blues)": "blues",
            "Diabetes (reds)": "reds",
            "Obesity (oranges)": "oranges",
        }
        chosen_scheme = color_scheme_map[ranking_color]
 
        # Build country × indicator prevalence table (sex-averaged)
        ranking_df = (
            df[(df["Year"] == ranking_year) & df["Sub_Region"].notna()]
            .groupby(["Country", "Sub_Region", "Indicator"])["Prevalence_pct"]
            .median()
            .unstack("Indicator")
            .reset_index()
        )
 
        # Only keep indicators that have data for this year
        available_indicators = [i for i in ["Blood Pressure", "Diabetes", "Obesity"]
                                 if i in ranking_df.columns and ranking_df[i].notna().any()]
 
        # Rank each available indicator (1 = highest prevalence)
        for ind in available_indicators:
            ranking_df[f"{ind}_rank"] = ranking_df[ind].rank(ascending=False, na_option="bottom").astype(int)
 
        # Combined rank = sum of available indicator ranks; lower = worse overall burden
        rank_cols = [f"{ind}_rank" for ind in available_indicators]
        ranking_df["Combined_rank"] = ranking_df[rank_cols].sum(axis=1).astype(int)
 
        # Sort countries worst first
        ranking_df = ranking_df.sort_values("Combined_rank")
        country_sort = ranking_df["Country"].tolist()
 
        # Melt to long format for heatmap
        heatmap_long = ranking_df.melt(
            id_vars=["Country", "Sub_Region"],
            value_vars=available_indicators,
            var_name="Indicator",
            value_name="Prevalence_pct",
        )
 
        # Add sub-region colour as a column for the heatmap tooltip
        heatmap_long["Sub_Region_color"] = heatmap_long["Sub_Region"].map(SUB_REGION_COLORS)
 
        heatmap = (
            alt.Chart(heatmap_long)
            .mark_rect(stroke="white", strokeWidth=0.5)
            .encode(
                x=alt.X(
                    "Indicator:N",
                    title=None,
                    sort=INDICATOR_ORDER,
                    axis=alt.Axis(labelFontSize=11, labelAngle=0, orient="top"),
                ),
                y=alt.Y(
                    "Country:N",
                    sort=country_sort,
                    title=None,
                    axis=None,
                ),
                color=alt.Color(
                    "Prevalence_pct:Q",
                    title="Prevalence (%)",
                    scale=alt.Scale(scheme=chosen_scheme),
                    legend=alt.Legend(orient="right"),
                ),
                tooltip=[
                    alt.Tooltip("Country:N"),
                    alt.Tooltip("Sub_Region:N", title="Sub-region"),
                    alt.Tooltip("Indicator:N"),
                    alt.Tooltip("Prevalence_pct:Q", title="Prevalence (%)", format=".1f"),
                ],
            )
            .properties(
                width=340, height=540,
                title=f"NCD prevalence heatmap, MENA {ranking_year}",
            )
        )
 
        # Country + sub-region labels on the left — sub-region shown as
        # abbreviated text in a muted colour so it doesn't compete with
        # the heatmap's prevalence colour channel.
        SUBREGION_ABBREV = {
            "Gulf": "Gulf", "Levant": "Levant",
            "North Africa": "N. Africa", "Lower-income MENA": "Low-inc."
        }
        subregion_df = ranking_df[["Country", "Sub_Region"]].drop_duplicates().copy()
        subregion_df["Label"] = subregion_df["Country"] + "  ·  " + subregion_df["Sub_Region"].map(SUBREGION_ABBREV)
 
        country_labels = (
            alt.Chart(subregion_df)
            .mark_text(align="right", dx=-4, fontSize=10, color="#333333")
            .encode(
                y=alt.Y("Country:N", sort=country_sort, axis=None),
                text="Label:N",
            )
            .properties(width=180, height=540, title=" ")
        )
 
        combined_chart = (
            alt.hconcat(country_labels, heatmap)
            .resolve_scale(color="independent")
            .configure_view(strokeWidth=0)
        )
 
        st.altair_chart(combined_chart, use_container_width=False)
 
    with st.container(border=True):
        st.subheader("Ranked table: combined NCD burden by country")
        st.caption(
            "Rank 1 = highest prevalence for that indicator. "
            "Combined rank = sum of individual ranks; lower = worse overall burden across all three indicators."
        )
 
        # Build clean display table with only available indicators
        table_cols = ["Country", "Sub_Region"]
        rename_map = {"Country": "Country", "Sub_Region": "Sub-region"}
        gradient_cols = {}
 
        for ind in available_indicators:
            table_cols += [ind, f"{ind}_rank"]
            short = "BP" if ind == "Blood Pressure" else ind
            rename_map[ind] = f"{short} (%)"
            rename_map[f"{ind}_rank"] = f"{short} rank"
            cmap = "Blues" if ind == "Blood Pressure" else ("Reds" if ind == "Diabetes" else "Oranges")
            gradient_cols[f"{short} (%)"] = cmap
 
        table_cols.append("Combined_rank")
        rename_map["Combined_rank"] = "Combined rank"
 
        table_display = ranking_df[table_cols].copy()
        table_display.columns = [rename_map[c] for c in table_cols]
 
        # Round prevalence columns
        for col in table_display.columns:
            if "(%)" in col:
                table_display[col] = table_display[col].round(1)
 
        st.dataframe(table_display, use_container_width=True, hide_index=True)
 
 
# ───────────────────────────────────────────────────────────────
# Tab 7 — Gender gap over time (AQ2) + Choropleth (AQ2 extension)
# ───────────────────────────────────────────────────────────────
with tab_gender:
    with st.container(border=True):
        st.subheader("Gender gap in prevalence over time")
 
        gender_indicator = st.selectbox("Choose indicator:", INDICATOR_ORDER, key="gender_indicator")
 
        st.caption(
            f"MENA-wide median {gender_indicator.lower()} prevalence by sex, 1975–2016. Shaded area shows "
            f"the size of the gender gap."
        )
 
        gender_df = (
            df[df["Sub_Region"].notna() & (df["Indicator"] == gender_indicator) & df["Sex"].isin(["Men", "Women"])]
            .groupby(["Year", "Sex"])["Prevalence_pct"]
            .median()
            .round(1)
            .reset_index()
        )
 
        gender_wide = gender_df.pivot(index="Year", columns="Sex", values="Prevalence_pct").reset_index()
        gender_wide["lo"] = gender_wide[["Men", "Women"]].min(axis=1)
        gender_wide["hi"] = gender_wide[["Men", "Women"]].max(axis=1)
 
        # Dynamic y-axis: scale to actual data range with 10% padding on each
        # side, rather than forcing zero. Blood Pressure data sits 20–35% so
        # a zero baseline wastes half the chart height; Obesity starts near 5%
        # in 1975 so zero is also not a meaningful anchor. Padding of 10% of
        # the range prevents data points touching the chart edge.
        y_min = gender_df["Prevalence_pct"].min()
        y_max = gender_df["Prevalence_pct"].max()
        y_pad = (y_max - y_min) * 0.10
        y_domain = [max(0, y_min - y_pad), y_max + y_pad]
 
        band = (
            alt.Chart(gender_wide)
            .mark_area(opacity=0.25, color="#E45756")
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("lo:Q", title=f"{gender_indicator} prevalence (%)",
                         scale=alt.Scale(domain=y_domain)),
                y2="hi:Q",
            )
        )
 
        lines = (
            alt.Chart(gender_df)
            .mark_line(strokeWidth=2.5, point=alt.OverlayMarkDef(size=30, filled=True))
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("Prevalence_pct:Q", title=f"{gender_indicator} prevalence (%)",
                         scale=alt.Scale(domain=y_domain)),
                color=alt.Color("Sex:N", title="Sex", scale=alt.Scale(domain=["Men", "Women"], range=["#4C78A8", "#E45756"])),
                tooltip=[
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("Sex:N"),
                    alt.Tooltip("Prevalence_pct:Q", title=f"{gender_indicator} prevalence (%)", format=".1f"),
                ],
            )
        )
 
        gender_chart = (band + lines).properties(
            width=700, height=350, title=f"MENA {gender_indicator.lower()} prevalence by sex, with gender gap shaded"
        )
 
        st.altair_chart(gender_chart, use_container_width=False)
 
    with st.container(border=True):
        st.subheader("Where is the gender gap widest?")
        st.caption(
            "Gender gap in prevalence (Women minus Men). Darker red indicates "
            "women's prevalence exceeds men's; darker blue indicates the reverse. "
            "Grey indicates no data."
        )
 
        available_years = sorted(df["Year"].dropna().unique().astype(int).tolist())
        default_year_idx = available_years.index(2014) if 2014 in available_years else len(available_years) - 1
 
        map_col1, map_col2 = st.columns(2)
        with map_col1:
            map_indicator = st.selectbox("Choose indicator:", INDICATOR_ORDER, key="map_indicator")
        with map_col2:
            map_year = st.selectbox("Choose year:", available_years, index=default_year_idx, key="map_year")
 
        map_data = (
            df[(df["Year"] == map_year) & (df["Indicator"] == map_indicator) & df["Sex"].isin(["Men", "Women"])]
            .pivot_table(index=["Country", "ISO_numeric"], columns="Sex", values="Prevalence_pct")
            .reset_index()
        )
        map_data["Gap"] = map_data["Women"] - map_data["Men"]
 
        # Attach label coordinates and per-country pixel nudge offsets.
        # Small states (Kuwait, Qatar, Bahrain, Israel, Palestine, Lebanon)
        # cluster tightly on the Mercator projection — offsets spread their
        # labels outward so they don't overlap each other.
        label_data = map_data.copy()
        label_data["lon"] = label_data["Country"].map(lambda c: COUNTRY_CENTROIDS.get(c, (None, None))[0])
        label_data["lat"] = label_data["Country"].map(lambda c: COUNTRY_CENTROIDS.get(c, (None, None))[1])
        label_data["dx"]  = label_data["Country"].map(lambda c: LABEL_NUDGE.get(c, (0, 0))[0])
        label_data["dy"]  = label_data["Country"].map(lambda c: LABEL_NUDGE.get(c, (0, 0))[1])
        label_data = label_data.dropna(subset=["lon", "lat"])
 
        world = alt.topo_feature(WORLD_110M_URL, "countries")
 
        choropleth_base = (
            alt.Chart(world)
            .mark_geoshape(stroke="white", strokeWidth=0.5)
            .encode(
                color=alt.Color("Gap:Q", title="Gap (pts)", scale=alt.Scale(scheme="redblue", reverse=True, domainMid=0)),
                tooltip=[alt.Tooltip("Country:N"), alt.Tooltip("Gap:Q", title="Gap (pts)", format=".1f")],
            )
            .transform_lookup(lookup="id", from_=alt.LookupData(map_data, "ISO_numeric", ["Country", "Gap"]))
        )
 
        # Build one text layer per country so each can carry its own dx/dy.
        # Two passes: white halo first, black text on top — keeps labels
        # legible over both dark-red and dark-blue choropleth fills.
        label_layers = []
        for _, row in label_data.iterrows():
            single = pd.DataFrame([row])
            for color, stroke, sw in [("white", "white", 3), ("black", None, 0)]:
                kwargs = dict(fontSize=9, fontWeight="bold", color=color,
                              dx=int(row["dx"]), dy=int(row["dy"]))
                if stroke:
                    kwargs["stroke"] = stroke
                    kwargs["strokeWidth"] = sw
                label_layers.append(
                    alt.Chart(single)
                    .mark_text(**kwargs)
                    .encode(longitude="lon:Q", latitude="lat:Q", text="Country:N")
                )
 
        choropleth = (
            alt.layer(choropleth_base, *label_layers)
            .project(type="mercator", center=[47, 27], scale=700)
            .properties(width=700, height=420, title=f"{map_indicator}: gender gap by country, MENA, {map_year}")
        )
 
        st.altair_chart(choropleth, use_container_width=False)