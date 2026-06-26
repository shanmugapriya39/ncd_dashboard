import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
 
st.set_page_config(page_title="Supporting Evidence – MENA NCD", layout="wide")
 
# ─────────────────────────────────────────────────────────────────
# Constants — mirrored from old 01_MENA_Analysis.py
# ─────────────────────────────────────────────────────────────────
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
    "Lebanon": 422, "Jordan": 400, "Israel": 376, "Malta": 470, "Iraq": 368, "Iran": 364,
    "Yemen": 887, "Syria": 760, "Afghanistan": 4, "Djibouti": 262,
    "Palestine": 275, "Pakistan": 586,
}
 
SUB_REGION_ORDER = ["Gulf", "Levant", "North Africa", "Lower-income MENA"]
INDICATOR_ORDER = ["Blood Pressure", "Diabetes", "Obesity"]
 
SUB_REGION_COLORS = {
    "Gulf": "#1D9E75", "Levant": "#4C78A8",
    "North Africa": "#F58518", "Lower-income MENA": "#E45756",
}
INDICATOR_COLORS = {
    "Blood Pressure": "#4C78A8", "Diabetes": "#E45756", "Obesity": "#F58518",
}
 
# ─────────────────────────────────────────────────────────────────
# Styling
# ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&display=swap');
 
    .se-header {
        background: linear-gradient(135deg, #1a2e4a 0%, #0f1e32 100%);
        border-radius: 18px;
        padding: 30px 36px;
        margin-bottom: 26px;
    }
    .se-header h1 {
        font-family: 'Source Serif 4', Georgia, serif;
        color: #ffffff;
        font-size: 30px;
        font-weight: 700;
        margin: 0 0 10px 0;
    }
    .se-header p {
        color: rgba(255,255,255,0.88);
        font-size: 14.5px;
        line-height: 1.55;
        margin: 0;
        max-width: 820px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #1a2e4a;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12.5px;
        color: #5b5b58;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border-color: #E3E3E0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EBF0F7;
        color: #1a2e4a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ─────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_mena_data():
    df = pd.read_csv("ncd_merged.csv")
    df = df[df["Country"].isin(SUB_REGION.keys())].copy()
    df["Sub_Region"] = df["Country"].map(SUB_REGION)
    df["Income_Tier"] = df["Country"].map(INCOME_TIER)
    df["ISO_numeric"] = df["Country"].map(ISO_NUMERIC)
    df["Pop_sqrt"] = np.sqrt(df["Population"].fillna(df["Population"].median()))
    return df
 
 
df = load_mena_data()
 
# ─────────────────────────────────────────────────────────────────
# Navigation
# ─────────────────────────────────────────────────────────────────
col_nav1, col_nav2, col_nav3, _ = st.columns([1, 1, 1, 5])
with col_nav1:
    if st.button("← GDP Analysis"):
        st.switch_page("pages/02_GDP.py")
with col_nav2:
    if st.button("⌂ Home"):
        st.switch_page("app.py")
 
# ─────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="se-header">
        <h1>Supporting Evidence</h1>
        <p>
            Detailed breakdowns that substantiate the key findings:
            gender disparities in prevalence, country-level ranking by combined NCD burden,
            the relationship between all three metabolic indicators, and how population
            size and sub-regional grouping shape the overall picture.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
 
# ─────────────────────────────────────────────────────────────────
# KPI strip — key numbers referenced in findings
# ─────────────────────────────────────────────────────────────────
kpi_data = [
    ("Egypt obesity gender gap", "+19.0 pts", "Largest gap — women exceed men"),
    ("Malta obesity gender gap", "+0.1 pts", "Smallest gap in region"),
    ("Kuwait diabetes (2014)", "19.6%", "Highest in MENA"),
    ("Kuwait obesity (2014)", "39.6%", "Worst combined metabolic rank"),
]
kpi_cols = st.columns(4)
for col, (label, value, help_txt) in zip(kpi_cols, kpi_data):
    with col.container(border=True):
        st.metric(label, value, help=help_txt)
 
st.write("")
 
# ─────────────────────────────────────────────────────────────────
# ─ FILTER PANEL ──────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────
with st.expander("🔧 Global filters (apply to most charts)", expanded=False):
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        sel_indicator = st.selectbox(
            "Indicator", INDICATOR_ORDER, index=1, key="global_indicator"
        )
    with fc2:
        available_years = sorted(df["Year"].dropna().unique().astype(int).tolist())
        sel_year = st.selectbox(
            "Year", available_years,
            index=available_years.index(2014), key="global_year"
        )
    with fc3:
        sel_subregions = st.multiselect(
            "Sub-regions", SUB_REGION_ORDER, default=SUB_REGION_ORDER, key="global_subregion"
        )
    with fc4:
        sel_sexes = st.multiselect(
            "Sex", ["Men", "Women"], default=["Men", "Women"], key="global_sex"
        )
    if not sel_subregions:
        sel_subregions = SUB_REGION_ORDER
    if not sel_sexes:
        sel_sexes = ["Men", "Women"]
 
# Filtered base dataframe (used by charts that respect global filters)
df_filt = df[
    df["Sub_Region"].isin(sel_subregions) &
    df["Sex"].isin(sel_sexes)
].copy()
 
# ─────────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────────
tab_gender, tab_ranking, tab_triad, tab_population, tab_subregion, tab_medage = st.tabs(
    ["Gender Gap (AQ2)", "Country Ranking (AQ7)", "Metabolic Triad (AQ3)",
     "Population & Prevalence (AQ4)", "Sub-regional Burden (AQ5)", "Median Age (AQ3)"]
)
 
@st.cache_data
def load_median_age_local():
    ma = pd.read_csv("median-age.csv")
    ma = ma[(ma["Year"] >= 1975) & (ma["Year"] <= 2016)][["Entity", "Year", "Median age"]].copy()
    ma.columns = ["Country", "Year", "Median_age"]
    return ma
 
ma_df = load_median_age_local()
 
# ═══════════════════════════════════════════════════════════════
# TAB 1 — Dumbbell chart: gender gap per country (AQ2)
# ═══════════════════════════════════════════════════════════════
with tab_gender:
    with st.container(border=True):
        st.subheader("Where is the gender gap widest across MENA?")
        st.caption(
            "Each row is one country. The left dot shows men's prevalence; "
            "the right dot shows women's. The connecting line length is the gap. "
            "Countries are sorted by gap size (Women − Men), largest at top."
        )
 
        db_col1, db_col2 = st.columns(2)
        with db_col1:
            db_indicator = st.selectbox(
                "Indicator", INDICATOR_ORDER, index=1, key="db_indicator"
            )
        with db_col2:
            db_year = st.selectbox(
                "Year", available_years,
                index=available_years.index(2014), key="db_year"
            )
 
        # Build gender-gap data (all 23 countries, both sexes)
        gap_df = (
            df[
                (df["Year"] == db_year) &
                (df["Indicator"] == db_indicator) &
                (df["Sex"].isin(["Men", "Women"]))
            ]
            .groupby(["Country", "Sub_Region", "Sex"])["Prevalence_pct"]
            .median()
            .reset_index()
        )
 
        gap_wide = gap_df.pivot_table(
            index=["Country", "Sub_Region"], columns="Sex", values="Prevalence_pct"
        ).reset_index()
        gap_wide.columns.name = None
        gap_wide = gap_wide.dropna(subset=["Men", "Women"])
        gap_wide["Gap"] = (gap_wide["Women"] - gap_wide["Men"]).round(1)
        gap_wide = gap_wide.sort_values("Gap", ascending=False)
        country_sort_db = gap_wide["Country"].tolist()
 
        # Melt back to long for Altair
        gap_long = gap_wide.melt(
            id_vars=["Country", "Sub_Region", "Gap"],
            value_vars=["Men", "Women"],
            var_name="Sex",
            value_name="Prevalence_pct",
        )
 
        # Line layer (dumbbell stick)
        dumbbell_lines = (
            alt.Chart(gap_wide)
            .mark_rule(color="#cccccc", strokeWidth=1.8)
            .encode(
                y=alt.Y("Country:N", sort=country_sort_db, title=None,
                         axis=alt.Axis(labelFontSize=11)),
                x=alt.X("Men:Q", title=f"{db_indicator} prevalence (%)"),
                x2="Women:Q",
            )
        )
 
        # Dot layer (one dot per sex)
        dumbbell_dots = (
            alt.Chart(gap_long)
            .mark_point(filled=True, size=80, opacity=0.92)
            .encode(
                y=alt.Y("Country:N", sort=country_sort_db, title=None),
                x=alt.X("Prevalence_pct:Q",
                         title=f"{db_indicator} prevalence (%)",
                         axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8)),
                color=alt.Color(
                    "Sex:N",
                    scale=alt.Scale(
                        domain=["Men", "Women"],
                        range=["#4C78A8", "#E45756"],
                    ),
                    legend=alt.Legend(title="Sex", orient="top"),
                ),
                shape=alt.Shape(
                    "Sex:N",
                    scale=alt.Scale(domain=["Men", "Women"], range=["circle", "diamond"]),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("Country:N"),
                    alt.Tooltip("Sub_Region:N", title="Sub-region"),
                    alt.Tooltip("Sex:N"),
                    alt.Tooltip("Prevalence_pct:Q", title="Prevalence (%)", format=".1f"),
                    alt.Tooltip("Gap:Q", title="Gap (W−M, pts)", format="+.1f"),
                ],
            )
        )
 
        # Gap label on the right side
        gap_labels = (
            alt.Chart(gap_wide)
            .mark_text(align="left", dx=6, fontSize=10, color="#555555")
            .encode(
                y=alt.Y("Country:N", sort=country_sort_db),
                x=alt.X("Women:Q"),
                text=alt.Text("Gap:Q", format="+.1f"),
            )
        )
 
        dumbbell_chart = (
            (dumbbell_lines + dumbbell_dots + gap_labels)
            .properties(
                width=540, height=520,
                title=f"{db_indicator}: gender gap by country, {db_year}",
            )
        )
 
        st.altair_chart(dumbbell_chart, use_container_width=False)
 
    with st.container(border=True):
        st.subheader("Gender gap over time: MENA-wide trend")
        st.caption(
            "MENA-wide median prevalence by sex, with shaded band showing the size of the gap over time."
        )
 
        gg_indicator = st.selectbox(
            "Indicator", INDICATOR_ORDER, index=1, key="gg_indicator"
        )
 
        gender_df = (
            df[df["Sub_Region"].notna() &
               (df["Indicator"] == gg_indicator) &
               df["Sex"].isin(["Men", "Women"])]
            .groupby(["Year", "Sex"])["Prevalence_pct"]
            .median()
            .round(1)
            .reset_index()
        )
 
        gender_wide2 = gender_df.pivot(index="Year", columns="Sex", values="Prevalence_pct").reset_index()
        gender_wide2["lo"] = gender_wide2[["Men", "Women"]].min(axis=1)
        gender_wide2["hi"] = gender_wide2[["Men", "Women"]].max(axis=1)
 
        y_min = gender_df["Prevalence_pct"].min()
        y_max = gender_df["Prevalence_pct"].max()
        y_pad = (y_max - y_min) * 0.10
        y_domain = [max(0, y_min - y_pad), y_max + y_pad]
 
        band = (
            alt.Chart(gender_wide2)
            .mark_area(opacity=0.20, color="#E45756")
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("lo:Q", scale=alt.Scale(domain=y_domain),
                         title=f"{gg_indicator} prevalence (%)"),
                y2="hi:Q",
            )
        )
 
        lines_g = (
            alt.Chart(gender_df)
            .mark_line(strokeWidth=2.5, point=alt.OverlayMarkDef(size=30, filled=True))
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("Prevalence_pct:Q",
                         scale=alt.Scale(domain=y_domain),
                         title=f"{gg_indicator} prevalence (%)"),
                color=alt.Color(
                    "Sex:N",
                    scale=alt.Scale(domain=["Men", "Women"], range=["#4C78A8", "#E45756"]),
                    legend=alt.Legend(title="Sex"),
                ),
                tooltip=[
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("Sex:N"),
                    alt.Tooltip("Prevalence_pct:Q", title="Prevalence (%)", format=".1f"),
                ],
            )
        )
 
        gender_trend_chart = (band + lines_g).properties(
            width=680, height=300,
            title=f"MENA {gg_indicator.lower()} prevalence by sex, 1975–2016",
        )
 
        st.altair_chart(gender_trend_chart, use_container_width=False)
 
 
# ═══════════════════════════════════════════════════════════════
# TAB 2 — Country ranking heatmap (AQ7)
# ═══════════════════════════════════════════════════════════════
with tab_ranking:
    with st.container(border=True):
        st.subheader("Which MENA country carries the most severe combined NCD profile?")
        st.caption(
            "Countries sorted by combined rank score — the sum of each country's rank "
            "across all three indicators, where rank 1 = highest prevalence. "
            "Darker = higher prevalence. A country dark across all columns has a broad burden."
        )
 
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            ranking_year = st.selectbox(
                "Year",
                available_years,
                index=available_years.index(2014),
                key="ranking_year",
            )
        with r_col2:
            ranking_color = st.selectbox(
                "Colour scale",
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
 
        ranking_df = (
            df[(df["Year"] == ranking_year) & df["Sub_Region"].notna()]
            .groupby(["Country", "Sub_Region", "Indicator"])["Prevalence_pct"]
            .median()
            .unstack("Indicator")
            .reset_index()
        )
 
        available_indicators = [i for i in ["Blood Pressure", "Diabetes", "Obesity"]
                                 if i in ranking_df.columns and ranking_df[i].notna().any()]
 
        for ind in available_indicators:
            ranking_df[f"{ind}_rank"] = ranking_df[ind].rank(
                ascending=False, na_option="bottom"
            ).astype(int)
 
        rank_cols = [f"{ind}_rank" for ind in available_indicators]
        ranking_df["Combined_rank"] = ranking_df[rank_cols].sum(axis=1).astype(int)
        ranking_df = ranking_df.sort_values("Combined_rank")
        country_sort_r = ranking_df["Country"].tolist()
 
        heatmap_long = ranking_df.melt(
            id_vars=["Country", "Sub_Region"],
            value_vars=available_indicators,
            var_name="Indicator",
            value_name="Prevalence_pct",
        )
 
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
                    sort=country_sort_r,
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
            .properties(width=340, height=540,
                        title=f"NCD prevalence heatmap, MENA {ranking_year}")
        )
 
        SUBREGION_ABBREV = {
            "Gulf": "Gulf", "Levant": "Levant",
            "North Africa": "N. Africa", "Lower-income MENA": "Low-inc.",
        }
        subregion_df = ranking_df[["Country", "Sub_Region"]].drop_duplicates().copy()
        subregion_df["Label"] = (
            subregion_df["Country"] + "  ·  " +
            subregion_df["Sub_Region"].map(SUBREGION_ABBREV)
        )
 
        country_labels = (
            alt.Chart(subregion_df)
            .mark_text(align="right", dx=-4, fontSize=10, color="#333333")
            .encode(
                y=alt.Y("Country:N", sort=country_sort_r, axis=None),
                text="Label:N",
            )
            .properties(width=180, height=540, title=" ")
        )
 
        combined_heatmap = (
            alt.hconcat(country_labels, heatmap)
            .resolve_scale(color="independent")
            .configure_view(strokeWidth=0)
        )
 
        st.altair_chart(combined_heatmap, use_container_width=False)
 
    with st.container(border=True):
        st.subheader("Ranked table")
        st.caption(
            "Rank 1 = highest prevalence. Combined rank = sum of individual ranks; "
            "lower = worse overall burden."
        )
        table_cols = ["Country", "Sub_Region"]
        rename_map = {"Country": "Country", "Sub_Region": "Sub-region"}
 
        for ind in available_indicators:
            table_cols += [ind, f"{ind}_rank"]
            short = "BP" if ind == "Blood Pressure" else ind
            rename_map[ind] = f"{short} (%)"
            rename_map[f"{ind}_rank"] = f"{short} rank"
 
        table_cols.append("Combined_rank")
        rename_map["Combined_rank"] = "Combined rank"
 
        table_display = ranking_df[table_cols].copy()
        table_display.columns = [rename_map[c] for c in table_cols]
        for col in table_display.columns:
            if "(%)" in col:
                table_display[col] = table_display[col].round(1)
 
        st.dataframe(table_display, use_container_width=True, hide_index=True)
 
 
# ═══════════════════════════════════════════════════════════════
# TAB 3 — Metabolic triad scatter (AQ3)
# ═══════════════════════════════════════════════════════════════
with tab_triad:
    with st.container(border=True):
        st.subheader("How are blood pressure, diabetes, and obesity related within MENA?")
        st.caption(
            "Each point is one MENA country. X-axis = obesity, Y-axis = diabetes, "
            "colour encodes blood pressure. Drag the slider to see how the relationship changes over time."
        )
 
        triad_wide = (
            df[df["Sub_Region"].notna()]
            .groupby(["Country", "Sub_Region", "Year", "Indicator"])["Prevalence_pct"]
            .median()
            .unstack("Indicator")
            .reset_index()
            .dropna(subset=["Blood Pressure", "Diabetes", "Obesity"])
        )
 
        pop_lookup = (
            df[df["Population"].notna()]
            .groupby(["Country", "Year"])["Population"]
            .median()
            .reset_index()
        )
        triad_wide = triad_wide.merge(pop_lookup, on=["Country", "Year"], how="left")
        triad_wide["Pop_sqrt"] = np.sqrt(
            triad_wide["Population"].fillna(triad_wide["Population"].median())
        )
 
        triad_year_slider = alt.binding_range(min=1975, max=2016, step=1, name="Year: ")
        triad_year_select = alt.selection_point(
            fields=["Year"], bind=triad_year_slider, value=2014
        )
 
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
                size=alt.Size("Pop_sqrt:Q", title="Population (√-scaled)",
                               scale=alt.Scale(range=[60, 1200]), legend=None),
                color=alt.Color(
                    "Blood Pressure:Q",
                    title="Blood Pressure (%)",
                    scale=alt.Scale(scheme="redblue", reverse=True),
                    legend=alt.Legend(orient="right"),
                ),
                tooltip=[
                    alt.Tooltip("Country:N"),
                    alt.Tooltip("Sub_Region:N", title="Sub-region"),
                    alt.Tooltip("Obesity:Q", title="Obesity (%)", format=".1f"),
                    alt.Tooltip("Diabetes:Q", title="Diabetes (%)", format=".1f"),
                    alt.Tooltip("Blood Pressure:Q", title="Blood Pressure (%)", format=".1f"),
                    alt.Tooltip("Year:O"),
                ],
            )
            .add_params(triad_year_select)
            .transform_filter(triad_year_select)
            .properties(
                width=660, height=420,
                title="Metabolic triad: Obesity, Diabetes, and Blood Pressure, MENA",
            )
        )
 
        st.altair_chart(triad_chart, use_container_width=False)
 
        # Pearson correlation matrix (fixed 2014)
        corr_year = 2014
        corr_input = triad_wide.loc[
            triad_wide["Year"] == corr_year,
            ["Country", "Blood Pressure", "Diabetes", "Obesity"],
        ]
        corr_matrix = corr_input[["Blood Pressure", "Diabetes", "Obesity"]].corr(
            method="pearson"
        ).round(2)
        n_countries = len(corr_input)
        missing_countries = sorted(
            set(SUB_REGION.keys()) - set(corr_input["Country"])
        )
 
        st.caption(
            f"Pearson correlation coefficients across {n_countries} MENA countries, {corr_year} "
            f"(country-level median of Men/Women)."
        )
        if missing_countries:
            st.caption(
                f"Note: excluded due to missing data in {corr_year}: "
                f"{', '.join(missing_countries)}."
            )
        st.dataframe(corr_matrix, use_container_width=False)
 
    with st.container(border=True):
        st.subheader("Correlation between indicator pairs over time")
        st.caption(
            "Pearson r computed per year for each indicator pair. A line crossing "
            "zero indicates the direction of the relationship has reversed — notably "
            "Obesity vs Blood Pressure crossed zero around 1995."
        )
 
        yearly_corr_rows = []
        for yr, group in triad_wide.groupby("Year"):
            if len(group) >= 5:
                yearly_corr_rows.append({
                    "Year": yr,
                    "Obesity vs Blood Pressure": group["Obesity"].corr(group["Blood Pressure"]),
                    "Diabetes vs Blood Pressure": group["Diabetes"].corr(group["Blood Pressure"]),
                    "Obesity vs Diabetes": group["Obesity"].corr(group["Diabetes"]),
                })
 
        yearly_corr_df = pd.DataFrame(yearly_corr_rows).melt(
            id_vars="Year", var_name="Indicator pair", value_name="Pearson r"
        )
 
        corr_hover = alt.selection_point(
            fields=["Indicator pair"], on="mouseover", nearest=False, empty=True
        )
 
        corr_trend_chart = (
            alt.Chart(yearly_corr_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("Pearson r:Q",
                         scale=alt.Scale(zero=False),
                         axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8)),
                color=alt.Color(
                    "Indicator pair:N",
                    legend=alt.Legend(title="Indicator pair", orient="top"),
                ),
                strokeWidth=alt.condition(corr_hover, alt.value(3), alt.value(1.5)),
                opacity=alt.condition(corr_hover, alt.value(1.0), alt.value(0.6)),
                tooltip=[
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("Indicator pair:N"),
                    alt.Tooltip("Pearson r:Q", format=".2f"),
                ],
            )
            .add_params(corr_hover)
        )
 
        zero_line = (
            alt.Chart(pd.DataFrame({"y": [0]}))
            .mark_rule(strokeDash=[5, 4], color="#999999", strokeWidth=1.2)
            .encode(y="y:Q")
        )
 
        # End-of-line r value labels
        end_corr = (
            yearly_corr_df.sort_values("Year")
            .groupby("Indicator pair")
            .last()
            .reset_index()
        )
        corr_end_labels = (
            alt.Chart(end_corr)
            .mark_text(align="left", dx=6, fontSize=10, fontWeight="bold")
            .encode(
                x=alt.X("Year:O"),
                y=alt.Y("Pearson r:Q"),
                text=alt.Text("Pearson r:Q", format=".2f"),
                color=alt.Color("Indicator pair:N", legend=None),
            )
        )
 
        st.altair_chart(
            (corr_trend_chart + zero_line + corr_end_labels).properties(
                width=680, height=320,
                title="Pearson correlation between indicator pairs, by year",
            ),
            use_container_width=False,
        )
 
 
# ═══════════════════════════════════════════════════════════════
# TAB 4 — Population scatter (AQ4)
# ═══════════════════════════════════════════════════════════════
with tab_population:
    with st.container(border=True):
        st.subheader("Does NCD prevalence track population size?")
        st.caption(
            "Each point is one MENA country. Population on a log scale "
            "(range: 1.4 million – 214 million). If larger countries showed "
            "higher prevalence, points would trend upward left to right. "
            "The absence of any such trend justifies using prevalence rates "
            "rather than absolute counts. Drag the slider across all study years."
        )
 
        pop_all = (
            df[df["Sub_Region"].notna() & df["Population"].notna()]
            .groupby(["Country", "Sub_Region", "Year", "Indicator"])
            .agg(
                Prevalence_pct=("Prevalence_pct", "median"),
                Population=("Population", "median"),
            )
            .reset_index()
        )
 
        pop_year_slider = alt.binding_range(min=1975, max=2016, step=1, name="Year: ")
        pop_year_select = alt.selection_point(
            fields=["Year"], bind=pop_year_slider, value=2014
        )
 
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
                y=alt.Y(
                    "Prevalence_pct:Q",
                    title="Prevalence (%)",
                    axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8),
                ),
                color=alt.Color(
                    "Sub_Region:N",
                    title="Sub-region",
                    scale=alt.Scale(
                        domain=SUB_REGION_ORDER,
                        range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER],
                    ),
                    legend=alt.Legend(title="Sub-region", orient="top"),
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
 
 
# ═══════════════════════════════════════════════════════════════
# TAB 5 — Sub-regional bar chart (AQ5)
# ═══════════════════════════════════════════════════════════════
with tab_subregion:
    with st.container(border=True):
        st.subheader("Sub-regional comparison: is MENA's NCD burden evenly distributed?")
 
        gdp_2014 = df[df["Year"] == 2014][
            ["Country", "Sub_Region", "GDP_per_capita"]
        ].drop_duplicates()
 
        gulf_gdp = gdp_2014.loc[gdp_2014["Sub_Region"] == "Gulf", "GDP_per_capita"].median()
        levant_gdp = gdp_2014.loc[gdp_2014["Sub_Region"] == "Levant", "GDP_per_capita"].median()
        na_gdp = gdp_2014.loc[gdp_2014["Sub_Region"] == "North Africa", "GDP_per_capita"].median()
        low_gdp = gdp_2014.loc[gdp_2014["Sub_Region"] == "Lower-income MENA", "GDP_per_capita"].median()
 
        st.caption(
            f"Median prevalence by sub-region, {sel_year}. "
            f"Groupings reflect median GDP per capita: "
            f"Gulf (\\${gulf_gdp:,.0f}) > Levant (\\${levant_gdp:,.0f}) > "
            f"North Africa (\\${na_gdp:,.0f}) > Lower-income MENA (\\${low_gdp:,.0f})."
        )
 
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            sub_year = st.selectbox(
                "Year", available_years,
                index=available_years.index(sel_year), key="sub_year"
            )
        with sub_col2:
            sub_sex = st.selectbox(
                "Sex", ["Both (median)", "Men", "Women"], key="sub_sex"
            )
 
        sub_df_source = df[df["Sub_Region"].notna() & (df["Year"] == sub_year)]
        if sub_sex != "Both (median)":
            sub_df_source = sub_df_source[sub_df_source["Sex"] == sub_sex]
 
        subregional = (
            sub_df_source
            .groupby(["Sub_Region", "Indicator"])["Prevalence_pct"]
            .median()
            .round(1)
            .reset_index()
        )
 
        bar_hover = alt.selection_point(
            fields=["Sub_Region"], on="mouseover", nearest=False, empty=True
        )
 
        chart_subregion = (
            alt.Chart(subregional)
            .mark_bar()
            .encode(
                x=alt.X("Prevalence_pct:Q", title="Median prevalence (%)"),
                y=alt.Y(
                    "Sub_Region:N",
                    sort=SUB_REGION_ORDER,
                    title=None,
                    axis=alt.Axis(labelFontSize=11),
                ),
                color=alt.Color(
                    "Sub_Region:N",
                    scale=alt.Scale(
                        domain=SUB_REGION_ORDER,
                        range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER],
                    ),
                    legend=None,
                ),
                opacity=alt.condition(bar_hover, alt.value(1.0), alt.value(0.75)),
                facet=alt.Facet(
                    "Indicator:N",
                    columns=3,
                    header=alt.Header(labelFontSize=13, labelFontWeight="bold"),
                    sort=INDICATOR_ORDER,
                ),
                tooltip=[
                    alt.Tooltip("Sub_Region:N", title="Sub-region"),
                    alt.Tooltip("Indicator:N"),
                    alt.Tooltip("Prevalence_pct:Q", title="Median prevalence (%)", format=".1f"),
                ],
            )
            .add_params(bar_hover)
            .properties(width=220, height=220)
        )
 
        st.altair_chart(chart_subregion, use_container_width=False)
 
    with st.container(border=True):
        st.subheader("Sub-regional trends over time")
        st.caption(
            "Each sub-region's median prevalence, 1975–2016. Hover a line to highlight it."
        )
 
        trend_indicator = st.selectbox(
            "Indicator", INDICATOR_ORDER, index=1, key="sr_trend_indicator"
        )
 
        sr_trend = (
            df[df["Sub_Region"].notna() & (df["Indicator"] == trend_indicator)]
            .groupby(["Year", "Sub_Region"])["Prevalence_pct"]
            .median()
            .round(1)
            .reset_index()
        )
 
        sr_hover = alt.selection_point(
            fields=["Sub_Region"], on="mouseover", nearest=False, empty=True
        )
 
        sr_lines = (
            alt.Chart(sr_trend)
            .mark_line()
            .encode(
                x=alt.X("Year:O", title="Year", axis=alt.Axis(grid=False)),
                y=alt.Y(
                    "Prevalence_pct:Q",
                    title=f"Median {trend_indicator} prevalence (%)",
                    axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8),
                ),
                color=alt.Color(
                    "Sub_Region:N",
                    scale=alt.Scale(
                        domain=SUB_REGION_ORDER,
                        range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER],
                    ),
                    legend=alt.Legend(title="Sub-region", orient="top"),
                ),
                strokeWidth=alt.condition(sr_hover, alt.value(3.5), alt.value(1.5)),
                opacity=alt.condition(sr_hover, alt.value(1.0), alt.value(0.55)),
                tooltip=[
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("Sub_Region:N", title="Sub-region"),
                    alt.Tooltip("Prevalence_pct:Q", title="Prevalence (%)", format=".1f"),
                ],
            )
            .add_params(sr_hover)
        )
 
        # End-of-line labels
        sr_end = (
            sr_trend.sort_values("Year")
            .groupby("Sub_Region")
            .last()
            .reset_index()
        )
        sr_end_labels = (
            alt.Chart(sr_end)
            .mark_text(align="left", dx=6, fontSize=10, fontWeight="bold")
            .encode(
                x=alt.X("Year:O"),
                y=alt.Y("Prevalence_pct:Q"),
                text=alt.Text("Sub_Region:N"),
                color=alt.Color(
                    "Sub_Region:N",
                    scale=alt.Scale(
                        domain=SUB_REGION_ORDER,
                        range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER],
                    ),
                    legend=None,
                ),
            )
        )
 
        sr_chart = (sr_lines + sr_end_labels).properties(
            width=680, height=320,
            title=f"Sub-regional {trend_indicator} trends, 1975–2016",
        )
 
        st.altair_chart(sr_chart, use_container_width=False)
 
# ═══════════════════════════════════════════════════════════════
# TAB 6 — Median Age vs Prevalence scatter (AQ3)
# ═══════════════════════════════════════════════════════════════
with tab_medage:
    with st.container(border=True):
        st.subheader("Does population ageing drive higher NCD prevalence in MENA?")
        st.caption(
            "Each point is one MENA country in the selected year. "
            "X-axis = median age of the national population (UN WPP). "
            "A positive trend means older countries tend to have higher prevalence. "
            "Use the year slider to watch how the relationship shifts over time."
        )
 
        ma_col1, ma_col2, ma_col3 = st.columns(3)
        with ma_col1:
            ma_indicator = st.selectbox(
                "Indicator", INDICATOR_ORDER, index=1, key="ma_indicator"
            )
        with ma_col2:
            ma_year = st.selectbox(
                "Year", available_years,
                index=available_years.index(2014), key="ma_year"
            )
        with ma_col3:
            ma_subregion = st.multiselect(
                "Sub-regions", SUB_REGION_ORDER, default=SUB_REGION_ORDER, key="ma_subregion"
            )
        if not ma_subregion:
            ma_subregion = SUB_REGION_ORDER
 
        # Build scatter data
        ncd_yr = (
            df[
                (df["Year"] == ma_year) &
                (df["Indicator"] == ma_indicator) &
                df["Sub_Region"].notna()
            ]
            .groupby(["Country", "Sub_Region"])["Prevalence_pct"]
            .median()
            .reset_index()
        )
 
        ma_yr_data = ma_df[ma_df["Year"] == ma_year][["Country", "Median_age"]]
        scatter_ma = ncd_yr.merge(ma_yr_data, on="Country", how="inner")
        scatter_ma = scatter_ma[scatter_ma["Sub_Region"].isin(ma_subregion)]
 
        if scatter_ma.empty:
            st.warning("No data for this combination.")
        else:
            # OLS trend line data
            from numpy.polynomial import polynomial as P
            x = scatter_ma["Median_age"].values
            y = scatter_ma["Prevalence_pct"].values
            if len(x) >= 3:
                coef = np.polyfit(x, y, 1)
                x_line = np.linspace(x.min(), x.max(), 50)
                y_line = np.polyval(coef, x_line)
                trend_data = pd.DataFrame({"Median_age": x_line, "Prevalence_pct": y_line})
                r = np.corrcoef(x, y)[0, 1]
            else:
                trend_data = pd.DataFrame()
                r = None
 
            # Scatter
            ma_scatter = (
                alt.Chart(scatter_ma)
                .mark_circle(size=110, opacity=0.88)
                .encode(
                    x=alt.X(
                        "Median_age:Q",
                        title="Median age (years)",
                        scale=alt.Scale(zero=False),
                        axis=alt.Axis(grid=False),
                    ),
                   y=alt.Y(
    "Prevalence_pct:Q",
    title=f"{ma_indicator} prevalence (%)",
    scale=alt.Scale(zero=False, padding=20),
                        axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8),
                    ),
                    color=alt.Color(
                        "Sub_Region:N",
                        title="Sub-region",
                        scale=alt.Scale(
                            domain=SUB_REGION_ORDER,
                            range=[SUB_REGION_COLORS[s] for s in SUB_REGION_ORDER],
                        ),
                        legend=alt.Legend(orient="top"),
                    ),
                    tooltip=[
                        alt.Tooltip("Country:N"),
                        alt.Tooltip("Sub_Region:N", title="Sub-region"),
                        alt.Tooltip("Median_age:Q", title="Median age (yrs)", format=".1f"),
                        alt.Tooltip("Prevalence_pct:Q", title=f"{ma_indicator} (%)", format=".1f"),
                    ],
                )
            )
 
            # Country labels
            ma_labels = (
                alt.Chart(scatter_ma)
                .mark_text(fontSize=9, dy=-10, color="#555")
                .encode(
                    x=alt.X("Median_age:Q", scale=alt.Scale(zero=False)),
                    y=alt.Y("Prevalence_pct:Q", scale=alt.Scale(zero=False)),
                    text="Country:N",
                )
            )
 
            # OLS trend line
            if not trend_data.empty:
                ma_trend = (
                    alt.Chart(trend_data)
                    .mark_line(strokeDash=[5, 4], color="#888888", strokeWidth=1.5)
                    .encode(
                        x=alt.X("Median_age:Q"),
                        y=alt.Y("Prevalence_pct:Q"),
                    )
                )
                ma_chart = (ma_scatter + ma_labels + ma_trend).properties(
                    width=680, height=400,
                    title=f"Median age vs {ma_indicator} prevalence, MENA {ma_year}",
                )
            else:
                ma_chart = (ma_scatter + ma_labels).properties(
                    width=680, height=400,
                    title=f"Median age vs {ma_indicator} prevalence, MENA {ma_year}",
                )
 
            st.altair_chart(ma_chart, use_container_width=False)
 
            if r is not None:
                direction = "positive" if r > 0 else "negative"
                strength = "strong" if abs(r) > 0.5 else ("moderate" if abs(r) > 0.3 else "weak")
                st.caption(
                    f"Pearson r = {r:.2f} ({strength} {direction} correlation). "
                    f"Dashed line = OLS trend. n = {len(scatter_ma)} MENA countries, {ma_year}."
                )
 
    with st.container(border=True):
        st.subheader("Pearson r: median age vs NCD prevalence over time")
        st.caption(
            "How has the correlation between population median age and NCD prevalence "
            "changed across 1975–2016? Hover a line to highlight it."
        )
 
        corr_ma_rows = []
        for yr in available_years:
            ncd_yr_all = (
                df[df["Sub_Region"].notna() & (df["Year"] == yr)]
                .groupby(["Country", "Indicator"])["Prevalence_pct"]
                .median()
                .reset_index()
            )
            ma_yr_all = ma_df[ma_df["Year"] == yr][["Country", "Median_age"]]
            merged_yr = ncd_yr_all.merge(ma_yr_all, on="Country", how="inner").dropna()
            for ind in INDICATOR_ORDER:
                sub = merged_yr[merged_yr["Indicator"] == ind]
                if len(sub) >= 5:
                    r_val = np.corrcoef(sub["Median_age"], sub["Prevalence_pct"])[0, 1]
                    corr_ma_rows.append({"Year": yr, "Indicator": ind, "Pearson_r": round(r_val, 3)})
 
        corr_ma_df = pd.DataFrame(corr_ma_rows)
 
        hover_ma = alt.selection_point(
            fields=["Indicator"], on="mouseover", nearest=False, empty=True
        )
 
        corr_ma_lines = (
            alt.Chart(corr_ma_df)
            .mark_line(strokeWidth=2.5, point=True)
            .encode(
                x=alt.X("Year:O", title="Year", axis=alt.Axis(grid=False)),
                y=alt.Y(
                    "Pearson_r:Q",
                    title="Pearson r (Median age vs prevalence)",
                    scale=alt.Scale(zero=False),
                    axis=alt.Axis(grid=True, gridColor="#e8e8e8", gridWidth=0.8),
                ),
                color=alt.Color(
                    "Indicator:N",
                    scale=alt.Scale(
                        domain=INDICATOR_ORDER,
                        range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER],
                    ),
                    legend=alt.Legend(title="Indicator", orient="top"),
                ),
                strokeWidth=alt.condition(hover_ma, alt.value(3.5), alt.value(1.8)),
                opacity=alt.condition(hover_ma, alt.value(1.0), alt.value(0.6)),
                tooltip=[
                    alt.Tooltip("Year:O"),
                    alt.Tooltip("Indicator:N"),
                    alt.Tooltip("Pearson_r:Q", title="Pearson r", format=".2f"),
                ],
            )
            .add_params(hover_ma)
        )
 
        zero_ma = (
            alt.Chart(pd.DataFrame({"y": [0]}))
            .mark_rule(strokeDash=[5, 4], color="#999999", strokeWidth=1.2)
            .encode(y="y:Q")
        )
 
        end_ma = (
            corr_ma_df.sort_values("Year")
            .groupby("Indicator")
            .last()
            .reset_index()
        )
        end_labels_ma = (
            alt.Chart(end_ma)
            .mark_text(align="left", dx=6, fontSize=10, fontWeight="bold")
            .encode(
                x=alt.X("Year:O"),
                y=alt.Y("Pearson_r:Q"),
                text=alt.Text("Pearson_r:Q", format=".2f"),
                color=alt.Color(
                    "Indicator:N",
                    scale=alt.Scale(
                        domain=INDICATOR_ORDER,
                        range=[INDICATOR_COLORS[i] for i in INDICATOR_ORDER],
                    ),
                    legend=None,
                ),
            )
        )
 
        st.altair_chart(
            (corr_ma_lines + zero_ma + end_labels_ma).properties(
                width=680, height=300,
                title="Pearson r: median age vs NCD prevalence, MENA 1975–2016",
            ),
            use_container_width=False,
        )
        st.caption(
            "r > 0 = older countries have higher prevalence. "
            "r < 0 = older countries have lower prevalence. "
            "Hover a line to highlight it."
        )
