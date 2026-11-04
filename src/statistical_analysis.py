
import pandas as pd
import numpy as np

from pathlib import Path
from scipy.stats import wilcoxon, friedmanchisquare
from statsmodels.stats.multitest import multipletests


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "outputs" / "processed"
TABLES_DIR = BASE_DIR / "outputs" / "tables"

TABLES_DIR.mkdir(parents=True, exist_ok=True)

MASTER_FILE = PROCESSED_DIR / "AMR_GLASS_MASTER.csv"


# ==========================================
# 2. LOAD DATA
# ==========================================

def load_data():

    df = pd.read_csv(MASTER_FILE)

    df["TimeDim"] = pd.to_numeric(
        df["TimeDim"], errors="coerce"
    )

    df["NumericValue"] = pd.to_numeric(
        df["NumericValue"], errors="coerce"
    )

    print("Statistical analysis dataset loaded")
    print("Shape:", df.shape)

    return df


# ==========================================
# 3. PREPARE REPEATED MEASUREMENTS
# ==========================================

def prepare_data(df):

    data = df.copy()

    # Preserve categories as separate analytical groups.
    data["CategoryCode"] = (
        data["DisaggregatingDimension1ValueCode"]
        .fillna("NOT_DISAGGREGATED")
        .astype(str)
    )

    data["Region"] = (
        data["SpatialDimensionValueCode"].astype(str)
    )

    # One median observation per indicator, category,
    # region and year.
    grouped = data.groupby(
        [
            "IndicatorCode",
            "CategoryCode",
            "Region",
            "TimeDim"
        ],
        dropna=False
    )["NumericValue"].median().reset_index()

    return grouped


# ==========================================
# 4. WILCOXON SIGNED-RANK TEST
# ==========================================

def perform_wilcoxon(data):

    results = []

    print("\nWILCOXON SIGNED-RANK TEST")
    print("=" * 65)

    groups = data.groupby(
        ["IndicatorCode", "CategoryCode"]
    )

    for (indicator, category), group in groups:

        pivot = group.pivot_table(
            index="Region",
            columns="TimeDim",
            values="NumericValue",
            aggfunc="median"
        )

        if 2017 not in pivot.columns or 2020 not in pivot.columns:
            continue

        paired = pivot[[2017, 2020]].dropna()

        if len(paired) < 3:
            continue

        before = paired[2017]
        after = paired[2020]

        differences = after - before

        if np.allclose(differences, 0):
            statistic = 0.0
            p_value = 1.0

        else:

            test = wilcoxon(
                before,
                after,
                alternative="two-sided",
                method="auto"
            )

            statistic = test.statistic
            p_value = test.pvalue

        results.append({

            "Indicator": indicator,
            "Category": category,

            "Paired_Regions": len(paired),

            "Median_2017": before.median(),
            "Median_2020": after.median(),

            "Median_Change": differences.median(),

            "Wilcoxon_Statistic": statistic,
            "P_Value": p_value

        })

    result_df = pd.DataFrame(results)

    if not result_df.empty:

        # Correct for multiple hypothesis testing.
        result_df["Adjusted_P_Value"] = multipletests(
            result_df["P_Value"],
            method="fdr_bh"
        )[1]

        result_df["Significant"] = (
            result_df["Adjusted_P_Value"] < 0.05
        )

    else:

        print("No groups had sufficient paired observations.")

    return result_df


# ==========================================
# 5. FRIEDMAN TEST
# ==========================================

def perform_friedman(data):

    results = []

    print("\nFRIEDMAN TEST")
    print("=" * 65)

    years = [2017, 2018, 2019, 2020]

    groups = data.groupby(
        ["IndicatorCode", "CategoryCode"]
    )

    for (indicator, category), group in groups:

        pivot = group.pivot_table(
            index="Region",
            columns="TimeDim",
            values="NumericValue",
            aggfunc="median"
        )

        if not all(year in pivot.columns for year in years):
            continue

        complete = pivot[years].dropna()

        # Require at least three complete regions.
        if len(complete) < 3:
            continue

        # Friedman test requires some variation.
        if all(
            complete[year].nunique() == 1
            for year in years
        ):
            continue

        test = friedmanchisquare(
            *[complete[year].values for year in years]
        )

        results.append({

            "Indicator": indicator,
            "Category": category,

            "Complete_Regions": len(complete),

            "Friedman_Statistic": test.statistic,

            "P_Value": test.pvalue

        })

    result_df = pd.DataFrame(results)

    if not result_df.empty:

        result_df["Adjusted_P_Value"] = multipletests(
            result_df["P_Value"],
            method="fdr_bh"
        )[1]

        result_df["Significant"] = (
            result_df["Adjusted_P_Value"] < 0.05
        )

    else:

        print("No groups had sufficient complete observations.")

    return result_df


# ==========================================
# 6. REGION-WISE TEMPORAL CHANGE
# ==========================================

def calculate_regional_changes(data):

    pivot = data.pivot_table(

        index=[
            "IndicatorCode",
            "CategoryCode",
            "Region"
        ],

        columns="TimeDim",

        values="NumericValue",

        aggfunc="median"

    ).reset_index()

    if 2017 not in pivot.columns or 2020 not in pivot.columns:

        return pd.DataFrame()

    pivot["Absolute_Change"] = (
        pivot[2020] - pivot[2017]
    )

    pivot["Percentage_Change"] = np.where(
        pivot[2017] != 0,
        (
            (pivot[2020] - pivot[2017])
            / pivot[2017]
        ) * 100,
        np.nan
    )

    return pivot


# ==========================================
# 7. SAVE RESULTS
# ==========================================

def save_results(wilcoxon_results,
                 friedman_results,
                 regional_changes):

    wilcoxon_results.to_csv(
        TABLES_DIR / "wilcoxon_results.csv",
        index=False
    )

    friedman_results.to_csv(
        TABLES_DIR / "friedman_results.csv",
        index=False
    )

    regional_changes.to_csv(
        TABLES_DIR / "regional_temporal_changes.csv",
        index=False
    )

    print("\nRESULT FILES SAVED")
    print("1. wilcoxon_results.csv")
    print("2. friedman_results.csv")
    print("3. regional_temporal_changes.csv")


# ==========================================
# 8. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    print("=" * 65)
    print("WHO GLASS STATISTICAL ANALYSIS")
    print("=" * 65)

    df = load_data()

    data = prepare_data(df)

    print("\nPrepared observations:", len(data))

    wilcoxon_results = perform_wilcoxon(data)

    friedman_results = perform_friedman(data)

    regional_changes = calculate_regional_changes(data)

    save_results(
        wilcoxon_results,
        friedman_results,
        regional_changes
    )

    print("\nWILCOXON RESULTS")
    print(wilcoxon_results.to_string(index=False))

    print("\nFRIEDMAN RESULTS")
    print(friedman_results.to_string(index=False))

    print("\nREGIONAL CHANGES")
    print(regional_changes.head(20).to_string(index=False))

    print("\n" + "=" * 65)
    print("STATISTICAL ANALYSIS COMPLETED")
    print("=" * 65)
