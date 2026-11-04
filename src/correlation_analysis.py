
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from scipy.stats import spearmanr


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

TABLES_DIR = BASE_DIR / "outputs" / "tables"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = TABLES_DIR / "regional_temporal_changes.csv"


# ==========================================
# 2. LOAD REGIONAL CHANGE DATA
# ==========================================

def load_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print("Regional temporal change data loaded")
    print("Dataset shape:", df.shape)

    return df


# ==========================================
# 3. PREPARE CORRELATION DATA
# ==========================================

def prepare_correlation_data(df):

    required_columns = [
        "IndicatorCode",
        "Region",
        "CategoryCode",
        "Absolute_Change"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # Compare only non-disaggregated regional observations.
    # Different indicator categories may have different meanings.
    data = df[
        df["CategoryCode"] == "NOT_DISAGGREGATED"
    ].copy()

    data["Absolute_Change"] = pd.to_numeric(
        data["Absolute_Change"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["IndicatorCode", "Region", "Absolute_Change"]
    )

    # One change value per indicator and region.
    data = data.groupby(
        ["Region", "IndicatorCode"]
    )["Absolute_Change"].median().reset_index()

    if data.empty:
        raise ValueError(
            "No non-disaggregated regional observations found. "
            "Check the CategoryCode values in regional_temporal_changes.csv."
        )

    pivot = data.pivot(
        index="Region",
        columns="IndicatorCode",
        values="Absolute_Change"
    )

    print("\nCorrelation dataset prepared")
    print("Regions:", len(pivot))
    print("Indicators:", len(pivot.columns))

    print("\nIndicators included:")
    print(list(pivot.columns))

    return pivot


# ==========================================
# 4. SPEARMAN CORRELATION ANALYSIS
# ==========================================

def calculate_correlations(pivot):

    results = []

    indicators = pivot.columns.tolist()

    print("\nSPEARMAN CORRELATION ANALYSIS")
    print("=" * 65)

    for i in range(len(indicators)):

        for j in range(i + 1, len(indicators)):

            indicator_1 = indicators[i]
            indicator_2 = indicators[j]

            paired = pivot[
                [indicator_1, indicator_2]
            ].dropna()

            n = len(paired)

            # Require at least four paired regions.
            if n < 4:
                continue

            x = paired[indicator_1]
            y = paired[indicator_2]

            # Correlation is undefined for constant variables.
            if x.nunique() < 2 or y.nunique() < 2:
                continue

            result = spearmanr(x, y)

            if not np.isfinite(result.statistic):
                continue

            rho = result.statistic

            if abs(rho) >= 0.7:
                strength = "Strong"
            elif abs(rho) >= 0.4:
                strength = "Moderate"
            else:
                strength = "Weak"

            direction = (
                "Positive" if rho > 0
                else "Negative" if rho < 0
                else "No association"
            )

            results.append({

                "Indicator_1": indicator_1,
                "Indicator_2": indicator_2,
                "Regions_Compared": n,
                "Spearman_Rho": rho,
                "Direction": direction,
                "Strength": strength

            })

    result_df = pd.DataFrame(results)

    if result_df.empty:
        print(
            "No indicator pairs had sufficient variation "
            "and paired regional observations."
        )
    else:
        result_df = result_df.sort_values(
            "Spearman_Rho",
            key=lambda x: x.abs(),
            ascending=False
        )

    return result_df


# ==========================================
# 5. CORRELATION MATRIX
# ==========================================

def create_correlation_matrix(pivot):

    correlation_matrix = pivot.corr(
        method="spearman",
        min_periods=4
    )

    return correlation_matrix


# ==========================================
# 6. VISUALIZE CORRELATION MATRIX
# ==========================================

def plot_correlation_matrix(correlation_matrix):

    if correlation_matrix.empty:
        print("Correlation matrix is empty.")
        return

    plt.figure(figsize=(12, 9))

    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        linewidths=0.5
    )

    plt.title(
        "Spearman Correlation of Regional Indicator Changes (2017–2020)"
    )

    plt.xlabel("AMR Indicators")
    plt.ylabel("AMR Indicators")

    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    plt.tight_layout()

    output_path = FIGURES_DIR / "indicator_correlation_matrix.png"

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("\nCorrelation heatmap saved:")
    print(output_path)


# ==========================================
# 7. SAVE RESULTS
# ==========================================

def save_results(result_df, correlation_matrix):

    pair_file = TABLES_DIR / "spearman_correlation_results.csv"

    matrix_file = TABLES_DIR / "correlation_matrix.csv"

    result_df.to_csv(
        pair_file,
        index=False
    )

    correlation_matrix.to_csv(
        matrix_file
    )

    print("\nRESULT FILES SAVED")
    print("=" * 65)

    print(pair_file)
    print(matrix_file)

    print("Pairwise correlation rows:", len(result_df))


# ==========================================
# 8. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    print("=" * 65)
    print("WHO GLASS CORRELATION ANALYSIS")
    print("=" * 65)

    df = load_data()

    pivot = prepare_correlation_data(df)

    correlation_results = calculate_correlations(pivot)

    correlation_matrix = create_correlation_matrix(pivot)

    save_results(
        correlation_results,
        correlation_matrix
    )

    plot_correlation_matrix(correlation_matrix)

    print("\nPAIRWISE CORRELATION RESULTS")

    if not correlation_results.empty:
        print(
            correlation_results.to_string(index=False)
        )
    else:
        print("No eligible indicator pairs found.")

    print("\nCORRELATION MATRIX")
    print(correlation_matrix)

    print("\n" + "=" * 65)
    print("CORRELATION ANALYSIS COMPLETED")
    print("=" * 65)

