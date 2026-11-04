
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "outputs" / "processed"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"
TABLES_DIR = BASE_DIR / "outputs" / "tables"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

MASTER_FILE = PROCESSED_DIR / "AMR_GLASS_MASTER.csv"


# ==========================================
# 2. LOAD MASTER DATASET
# ==========================================

def load_master_dataset():

    if not MASTER_FILE.exists():
        raise FileNotFoundError(
            f"Master dataset not found: {MASTER_FILE}"
        )

    df = pd.read_csv(MASTER_FILE)

    required_columns = [
        "IndicatorCode",
        "SpatialDimensionValueCode",
        "TimeDim",
        "Value",
        "NumericValue"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df["TimeDim"] = pd.to_numeric(
        df["TimeDim"], errors="coerce"
    )

    df["NumericValue"] = pd.to_numeric(
        df["NumericValue"], errors="coerce"
    )

    df["IndicatorCode"] = (
        df["IndicatorCode"].astype(str).str.strip()
    )

    df["SpatialDimensionValueCode"] = (
        df["SpatialDimensionValueCode"]
        .astype(str).str.strip()
    )

    print("MASTER DATASET LOADED")
    print("Shape:", df.shape)

    return df


# ==========================================
# 3. INDICATOR-WISE ANALYSIS
# ==========================================

def analyze_indicators(df):

    print("\nINDICATOR-WISE ANALYSIS")
    print("=" * 60)

    summary = df.groupby(
        "IndicatorCode"
    ).agg(

        Total_Records=("IndicatorCode", "size"),

        Unique_Regions=(
            "SpatialDimensionValueCode", "nunique"
        ),

        Years_Reported=("TimeDim", "nunique"),

        Numeric_Observations=("NumericValue", "count"),

        Mean_Value=("NumericValue", "mean"),

        Median_Value=("NumericValue", "median"),

        Std_Deviation=("NumericValue", "std"),

        Minimum=("NumericValue", "min"),

        Maximum=("NumericValue", "max")

    ).reset_index()

    summary.to_csv(
        TABLES_DIR / "indicator_summary.csv",
        index=False
    )

    print(summary.to_string(index=False))

    return summary


# ==========================================
# 4. REGION-WISE ANALYSIS
# ==========================================

def analyze_regions(df):

    print("\nREGIONAL ANALYSIS")
    print("=" * 60)

    summary = df.groupby(
        "SpatialDimensionValueCode"
    ).agg(

        Total_Records=("IndicatorCode", "size"),

        Indicators_Reported=("IndicatorCode", "nunique"),

        Years_Reported=("TimeDim", "nunique")

    ).reset_index()

    summary.rename(
        columns={
            "SpatialDimensionValueCode": "Region_Code"
        },
        inplace=True
    )

    summary.to_csv(
        TABLES_DIR / "regional_coverage.csv",
        index=False
    )

    print(summary.to_string(index=False))

    return summary


# ==========================================
# 5. YEAR-WISE ANALYSIS
# ==========================================

def analyze_years(df):

    print("\nYEAR-WISE ANALYSIS")
    print("=" * 60)

    summary = df.groupby("TimeDim").agg(

        Total_Records=("IndicatorCode", "size"),

        Indicators_Reported=("IndicatorCode", "nunique"),

        Regions_Reported=(
            "SpatialDimensionValueCode", "nunique"
        )

    ).reset_index()

    summary.to_csv(
        TABLES_DIR / "yearly_summary.csv",
        index=False
    )

    print(summary.to_string(index=False))

    return summary


# ==========================================
# 6. INDICATOR-REGION-YEAR SUMMARY
# ==========================================

def analyze_indicator_region_year(df):

    summary = df.groupby(
        [
            "IndicatorCode",
            "SpatialDimensionValueCode",
            "TimeDim"
        ],
        dropna=False
    ).agg(

        Observation_Count=("NumericValue", "count"),

        Median_Value=("NumericValue", "median"),

        Mean_Value=("NumericValue", "mean")

    ).reset_index()

    summary.to_csv(
        TABLES_DIR / "indicator_region_year.csv",
        index=False
    )

    print("\nINDICATOR-REGION-YEAR SUMMARY")
    print("Total grouped observations:", len(summary))

    return summary


# ==========================================
# 7. VALUE DISTRIBUTION ANALYSIS
# ==========================================

def analyze_value_distribution(df):

    distribution = df.groupby(
        ["IndicatorCode", "Value"],
        dropna=False
    ).size().reset_index(name="Frequency")

    distribution.to_csv(
        TABLES_DIR / "value_distribution.csv",
        index=False
    )

    print("\nVALUE DISTRIBUTION")
    print(distribution.head(30).to_string(index=False))

    return distribution


# ==========================================
# 8. DATA COMPLETENESS ANALYSIS
# ==========================================

def analyze_completeness(df):

    summary = pd.DataFrame({

        "Column": df.columns,

        "Missing_Count": [
            df[col].isnull().sum()
            for col in df.columns
        ],

        "Completeness_Percent": [
            df[col].notnull().mean() * 100
            for col in df.columns
        ]

    })

    summary.to_csv(
        TABLES_DIR / "data_completeness.csv",
        index=False
    )

    print("\nDATA COMPLETENESS")
    print(summary.to_string(index=False))

    return summary


# ==========================================
# 9. VISUALIZATION: INDICATOR RECORDS
# ==========================================

def plot_indicator_distribution(summary):

    plt.figure(figsize=(12, 6))

    plt.bar(
        summary["IndicatorCode"],
        summary["Total_Records"]
    )

    plt.title("Record Distribution Across AMR Indicators")
    plt.xlabel("Indicator Code")
    plt.ylabel("Number of Records")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "indicator_distribution.png",
        dpi=300
    )

    plt.close()


# ==========================================
# 10. VISUALIZATION: REGIONAL COVERAGE
# ==========================================

def plot_regional_coverage(summary):

    plt.figure(figsize=(10, 6))

    plt.bar(
        summary["Region_Code"],
        summary["Total_Records"]
    )

    plt.title("AMR Surveillance Reporting by WHO Region")
    plt.xlabel("Region Code")
    plt.ylabel("Number of Records")

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "regional_coverage.png",
        dpi=300
    )

    plt.close()


# ==========================================
# 11. VISUALIZATION: YEARLY RECORDS
# ==========================================

def plot_yearly_records(summary):

    plt.figure(figsize=(9, 5))

    plt.plot(
        summary["TimeDim"],
        summary["Total_Records"],
        marker="o",
        linewidth=2
    )

    plt.title("AMR Indicator Reporting Over Time")
    plt.xlabel("Year")
    plt.ylabel("Number of Records")

    plt.xticks(summary["TimeDim"].dropna().unique())

    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "yearly_reporting.png",
        dpi=300
    )

    plt.close()


# ==========================================
# 12. VISUALIZATION: INDIVIDUAL INDICATOR TRENDS
# ==========================================

def plot_indicator_trends(df):

    indicators = df["IndicatorCode"].dropna().unique()

    for indicator in indicators:

        subset = df[
            df["IndicatorCode"] == indicator
        ].copy()

        trend = subset.groupby(
            "TimeDim"
        )["NumericValue"].median().dropna()

        # Do not plot if there is insufficient variation
        if len(trend) < 2 or trend.nunique() < 2:
            print(
                f"Skipping trend chart for {indicator}: "
                "insufficient variation."
            )
            continue

        plt.figure(figsize=(8, 5))

        plt.plot(
            trend.index,
            trend.values,
            marker="o",
            linewidth=2
        )

        plt.title(
            f"Yearly Median NumericValue - {indicator}"
        )

        plt.xlabel("Year")
        plt.ylabel("Median NumericValue")

        plt.xticks(trend.index)
        plt.grid(alpha=0.3)
        plt.tight_layout()

        plt.savefig(
            FIGURES_DIR / f"trend_{indicator}.png",
            dpi=300
        )

        plt.close()


# ==========================================
# 13. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    print("=" * 60)
    print("WHO GLASS EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    df = load_master_dataset()

    indicator_summary = analyze_indicators(df)

    regional_summary = analyze_regions(df)

    yearly_summary = analyze_years(df)

    analyze_indicator_region_year(df)

    analyze_value_distribution(df)

    analyze_completeness(df)

    # Generate visualizations

    plot_indicator_distribution(indicator_summary)

    plot_regional_coverage(regional_summary)

    plot_yearly_records(yearly_summary)

    plot_indicator_trends(df)

    print("\n" + "=" * 60)
    print("EXPLORATORY DATA ANALYSIS COMPLETED")
    print("=" * 60)

    print("Total records analysed:", len(df))

    print("Unique indicators:",
          df["IndicatorCode"].nunique())

    print("Unique regions:",
          df["SpatialDimensionValueCode"].nunique())

    print("Years:",
          sorted(df["TimeDim"].dropna().unique()))
