
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path
import streamlit as st

st.title("WHO GLASS Dashboard")
st.success("Dashboard script is executing!")
st.write("Testing application rendering...")

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

TABLES_DIR = BASE_DIR / "outputs" / "tables"
PROCESSED_DIR = BASE_DIR / "outputs" / "processed"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"

st.set_page_config(
    page_title="WHO GLASS AMR Surveillance Dashboard",
    page_icon="🧬",
    layout="wide"
)


# ==========================================
# 2. LOAD DATA
# ==========================================

@st.cache_data
def load_csv(path):

    if path.exists():
        return pd.read_csv(path)

    return pd.DataFrame()


master = load_csv(
    PROCESSED_DIR / "AMR_GLASS_MASTER.csv"
)

profile = load_csv(
    TABLES_DIR / "regional_readiness_profile.csv"
)

coverage = load_csv(
    TABLES_DIR / "readiness_reporting_coverage.csv"
)

snapshot = load_csv(
    TABLES_DIR / "regional_readiness_2020.csv"
)

indicator_summary = load_csv(
    TABLES_DIR / "indicator_summary.csv"
)

wilcoxon = load_csv(
    TABLES_DIR / "wilcoxon_results.csv"
)

friedman = load_csv(
    TABLES_DIR / "friedman_results.csv"
)

correlations = load_csv(
    TABLES_DIR / "spearman_correlation_results.csv"
)

correlation_matrix = load_csv(
    TABLES_DIR / "correlation_matrix.csv"
)


# ==========================================
# 3. DASHBOARD HEADER
# ==========================================

st.title("🧬 WHO GLASS AMR Surveillance Dashboard")

st.markdown(
    """
    ### Global Assessment of Antimicrobial Resistance Surveillance Readiness

    Explore regional surveillance infrastructure, laboratory capacity,
    quality assurance and reporting trends from 2017 to 2020.
    """
)

st.caption(
    "Dataset: WHO GLASS | Geographic level: Six WHO regions | Period: 2017–2020"
)

st.divider()


# ==========================================
# 4. CHECK DATA AVAILABILITY
# ==========================================

if master.empty or profile.empty:

    st.error(
        "Required datasets are missing. "
        "Run the data cleaning and readiness profile scripts first."
    )

    st.stop()


# ==========================================
# 5. SIDEBAR FILTERS
# ==========================================

st.sidebar.header("Dashboard Filters")

regions = sorted(
    profile["Region"].dropna().unique().tolist()
)

indicators = sorted(
    profile["IndicatorCode"].dropna().unique().tolist()
)

years = sorted(
    profile["Year"].dropna().unique().tolist()
)

selected_regions = st.sidebar.multiselect(
    "Select WHO Regions",
    options=regions,
    default=regions
)

selected_indicators = st.sidebar.multiselect(
    "Select Indicators",
    options=indicators,
    default=indicators
)

selected_years = st.sidebar.multiselect(
    "Select Years",
    options=years,
    default=years
)


# ==========================================
# 6. FILTER DATA
# ==========================================

filtered = profile[
    profile["Region"].isin(selected_regions)
    & profile["IndicatorCode"].isin(selected_indicators)
    & profile["Year"].isin(selected_years)
].copy()


# ==========================================
# 7. OVERVIEW METRICS
# ==========================================

st.header("1. Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Observations",
        f"{len(master):,}"
    )

with col2:
    st.metric(
        "Indicators",
        master["IndicatorCode"].nunique()
    )

with col3:
    st.metric(
        "WHO Regions",
        master["SpatialDimensionValueCode"].nunique()
    )

with col4:
    st.metric(
        "Study Period",
        "2017–2020"
    )

st.divider()


# ==========================================
# 8. REGIONAL REPORTING COVERAGE
# ==========================================

st.header("2. Regional Reporting Coverage")

if not coverage.empty:

    coverage_filtered = coverage[
        coverage["Region"].isin(selected_regions)
        & coverage["Year"].isin(selected_years)
    ]

    fig = px.line(
        coverage_filtered,
        x="Year",
        y="Indicators_Reported",
        color="Region",
        markers=True,
        title="Number of Indicators Reported by WHO Region",
        labels={
            "Year": "Year",
            "Indicators_Reported": "Indicators Reported"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        coverage_filtered,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("Reporting coverage data is unavailable.")


st.divider()


# ==========================================
# 9. INDICATOR TRENDS
# ==========================================

st.header("3. Indicator-Wise Trends")

if not filtered.empty:

    selected_indicator = st.selectbox(
        "Choose an indicator for detailed analysis",
        options=sorted(
            filtered["IndicatorCode"].unique()
        )
    )

    trend_data = filtered[
        filtered["IndicatorCode"] == selected_indicator
    ]

    description = trend_data[
        "IndicatorDescription"
    ].iloc[0]

    st.info(f"Official indicator definition: {description}")

    fig = px.line(
        trend_data,
        x="Year",
        y="Regional_Value",
        color="Region",
        markers=True,
        title=f"Regional Trend: {selected_indicator}",
        labels={
            "Year": "Year",
            "Regional_Value": "Reported Value"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Underlying observations")

    st.dataframe(
        trend_data,
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning(
        "No observations match the selected filters."
    )


st.divider()


# ==========================================
# 10. 2020 REGIONAL SNAPSHOT
# ==========================================

st.header("4. Regional Readiness Profile – 2020")

if not snapshot.empty:

    snapshot_filtered = snapshot[
        snapshot["Region"].isin(selected_regions)
        & snapshot["IndicatorCode"].isin(selected_indicators)
    ]

    st.markdown(
        """
        This section displays the reported 2020 values for each
        indicator and category. Values retain their original
        indicator-specific meaning.
        """
    )

    st.dataframe(
        snapshot_filtered,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("2020 snapshot is unavailable.")


st.divider()


# ==========================================
# 11. STATISTICAL ANALYSIS
# ==========================================

st.header("5. Statistical Analysis")

tab1, tab2 = st.tabs([
    "Wilcoxon Test",
    "Friedman Test"
])


with tab1:

    st.subheader("2017 vs 2020")

    if not wilcoxon.empty:

        st.markdown(
            "Paired regional comparison of 2017 and 2020 values."
        )

        st.dataframe(
            wilcoxon,
            use_container_width=True,
            hide_index=True
        )

        if "Adjusted_P_Value" in wilcoxon.columns:

            significant = wilcoxon[
                wilcoxon["Significant"] == True
            ]

            st.metric(
                "Significant results after FDR correction",
                len(significant)
            )

    else:
        st.info("Wilcoxon results are unavailable or empty.")


with tab2:

    st.subheader("2017–2020")

    if not friedman.empty:

        st.markdown(
            "Repeated-measures comparison across four years."
        )

        st.dataframe(
            friedman,
            use_container_width=True,
            hide_index=True
        )

        if "Adjusted_P_Value" in friedman.columns:

            significant = friedman[
                friedman["Significant"] == True
            ]

            st.metric(
                "Significant results after FDR correction",
                len(significant)
            )

    else:
        st.info("Friedman results are unavailable or empty.")


st.divider()


# ==========================================
# 12. CORRELATION ANALYSIS
# ==========================================

st.header("6. Correlation Analysis")

st.markdown(
    """
    Spearman correlation of regional indicator changes
    between 2017 and 2020.
    """
)

if not correlations.empty:

    st.dataframe(
        correlations,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No eligible indicator pairs were available "
        "for correlation analysis."
    )


if not correlation_matrix.empty:

    st.subheader("Correlation Matrix")

    matrix = correlation_matrix.set_index(
        correlation_matrix.columns[0]
    )

    fig = px.imshow(
        matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        title="Spearman Correlation Matrix"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()


# ==========================================
# 13. INDICATOR SUMMARY
# ==========================================

st.header("7. Indicator Summary")

if not indicator_summary.empty:

    st.dataframe(
        indicator_summary,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("Indicator summary is unavailable.")


st.divider()


# ==========================================
# 14. DOWNLOAD REPORTS
# ==========================================

st.header("8. Download Analysis Results")

download_files = {
    "Regional Readiness Profile": profile,
    "2020 Regional Snapshot": snapshot,
    "Reporting Coverage": coverage,
    "Wilcoxon Results": wilcoxon,
    "Friedman Results": friedman,
    "Correlation Results": correlations,
    "Indicator Summary": indicator_summary
}

for label, dataframe in download_files.items():

    if not dataframe.empty:

        st.download_button(
            label=f"Download {label}",
            data=dataframe.to_csv(index=False).encode("utf-8"),
            file_name=label.lower().replace(" ", "_") + ".csv",
            mime="text/csv",
            key=label
        )


# ==========================================
# 15. FOOTER
# ==========================================

st.divider()

st.caption(
    """
    WHO GLASS AMR Surveillance Analysis | 2017–2020

    This dashboard presents regional surveillance infrastructure
    and reporting indicators. It does not estimate antimicrobial
    resistance prevalence or establish causal relationships.

    No composite readiness score or regional ranking is calculated.
    """
)
