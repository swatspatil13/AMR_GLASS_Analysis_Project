
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "outputs" / "processed"
TABLES_DIR = BASE_DIR / "outputs" / "tables"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"
CODES_DIR = BASE_DIR / "codes"

MASTER_FILE = PROCESSED_DIR / "AMR_GLASS_MASTER.csv"
GHO_FILE = CODES_DIR / "GHO.csv"
CATEGORY_FILE = CODES_DIR / "AMRGLASSCATEGORY.csv"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD DATA AND METADATA
# ==========================================

def load_data():

    for file in [MASTER_FILE, GHO_FILE, CATEGORY_FILE]:

        if not file.exists():
            raise FileNotFoundError(
                f"Required file not found: {file}"
            )

    data = pd.read_csv(MASTER_FILE)
    indicators = pd.read_csv(GHO_FILE)
    categories = pd.read_csv(CATEGORY_FILE)

    data["TimeDim"] = pd.to_numeric(
        data["TimeDim"], errors="coerce"
    )

    data["NumericValue"] = pd.to_numeric(
        data["NumericValue"], errors="coerce"
    )

    print("Master dataset loaded:", data.shape)
    print("Indicator metadata loaded:", indicators.shape)
    print("Category metadata loaded:", categories.shape)

    return data, indicators, categories


# ==========================================
# 3. MAP OFFICIAL INDICATOR DEFINITIONS
# ==========================================

def map_indicator_definitions(data, indicators):

    indicator_map = indicators[
        ["Code", "Title"]
    ].drop_duplicates()

    indicator_map = indicator_map.rename(
        columns={
            "Code": "IndicatorCode",
            "Title": "IndicatorDescription"
        }
    )

    result = data.merge(
        indicator_map,
        on="IndicatorCode",
        how="left"
    )

    result["IndicatorDescription"] = (
        result["IndicatorDescription"]
        .fillna("Definition unavailable in metadata")
    )

    return result


# ==========================================
# 4. MAP CATEGORY DESCRIPTIONS
# ==========================================

def map_category_definitions(data, categories):

    category_map = categories[
        ["Code", "Title"]
    ].drop_duplicates()

    category_map = category_map.rename(
        columns={
            "Code": "DisaggregatingDimension1ValueCode",
            "Title": "CategoryDescription"
        }
    )

    result = data.merge(
        category_map,
        on="DisaggregatingDimension1ValueCode",
        how="left"
    )

    result["CategoryDescription"] = (
        result["CategoryDescription"]
        .fillna("Not disaggregated or unavailable")
    )

    return result


# ==========================================
# 5. GENERATE REGIONAL READINESS PROFILE
# ==========================================

def generate_regional_profile(data):

    profile = data.dropna(
        subset=[
            "IndicatorCode",
            "SpatialDimensionValueCode",
            "TimeDim",
            "NumericValue"
        ]
    ).copy()

    profile = profile.rename(
        columns={
            "SpatialDimensionValueCode": "Region",
            "TimeDim": "Year"
        }
    )

    # Retain indicator-specific categories.
    grouped = profile.groupby(
        [
            "IndicatorCode",
            "IndicatorDescription",
            "DisaggregatingDimension1ValueCode",
            "CategoryDescription",
            "Region",
            "Year"
        ],
        dropna=False
    ).agg(
        Regional_Value=("NumericValue", "median"),
        Observation_Count=("NumericValue", "count")
    ).reset_index()

    grouped.to_csv(
        TABLES_DIR / "regional_readiness_profile.csv",
        index=False
    )

    print("\nRegional readiness profile generated")
    print("Rows:", len(grouped))

    return grouped


# ==========================================
# 6. GENERATE 2020 REGIONAL SNAPSHOT
# ==========================================

def generate_2020_snapshot(profile):

    snapshot = profile[
        profile["Year"] == 2020
    ].copy()

    snapshot.to_csv(
        TABLES_DIR / "regional_readiness_2020.csv",
        index=False
    )

    print("\n2020 regional snapshot generated")
    print("Rows:", len(snapshot))

    return snapshot


# ==========================================
# 7. REGIONAL REPORTING COVERAGE
# ==========================================

def generate_coverage(profile):

    coverage = profile.groupby(
        ["Region", "Year"]
    ).agg(
        Indicators_Reported=("IndicatorCode", "nunique"),
        Total_Observations=("Observation_Count", "sum")
    ).reset_index()

    coverage.to_csv(
        TABLES_DIR / "readiness_reporting_coverage.csv",
        index=False
    )

    return coverage


# ==========================================
# 8. INDICATOR-WISE TREND VISUALIZATION
# ==========================================

def plot_indicator_trends(profile):

    indicators = profile[
        "IndicatorCode"
    ].dropna().unique()

    for indicator in indicators:

        subset = profile[
            profile["IndicatorCode"] == indicator
        ]

        plt.figure(figsize=(9, 5))

        sns.lineplot(
            data=subset,
            x="Year",
            y="Regional_Value",
            hue="Region",
            marker="o",
            errorbar=None
        )

        description = subset[
            "IndicatorDescription"
        ].iloc[0]

        plt.title(
            f"{indicator}\n{description}",
            fontsize=10
        )

        plt.xlabel("Year")
        plt.ylabel("Reported indicator value")

        plt.xticks([2017, 2018, 2019, 2020])

        plt.grid(alpha=0.3)
        plt.legend(title="WHO Region")

        plt.tight_layout()

        output_path = (
            FIGURES_DIR /
            f"readiness_trend_{indicator}.png"
        )

        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

    print("\nIndicator-wise trend plots generated.")


# ==========================================
# 9. SAVE INDICATOR DEFINITIONS
# ==========================================

def save_indicator_dictionary(indicators):

    dictionary = indicators[
        ["Code", "Title"]
    ].copy()

    dictionary = dictionary.rename(
        columns={
            "Code": "IndicatorCode",
            "Title": "OfficialDefinition"
        }
    )

    dictionary.to_csv(
        TABLES_DIR / "indicator_dictionary.csv",
        index=False
    )

    print("Indicator dictionary saved.")


# ==========================================
# 10. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    print("=" * 65)
    print("WHO GLASS REGIONAL READINESS PROFILE")
    print("=" * 65)

    data, indicators, categories = load_data()

    data = map_indicator_definitions(
        data, indicators
    )

    data = map_category_definitions(
        data, categories
    )

    profile = generate_regional_profile(data)

    snapshot = generate_2020_snapshot(profile)

    coverage = generate_coverage(profile)

    save_indicator_dictionary(indicators)

    plot_indicator_trends(profile)

    print("\n2020 SNAPSHOT PREVIEW")
    print(snapshot.head(15).to_string(index=False))

    print("\nREPORTING COVERAGE")
    print(coverage.to_string(index=False))

    print("\n" + "=" * 65)
    print("READINESS PROFILE COMPLETED")
    print("=" * 65)
