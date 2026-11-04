
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
PROCESSED_DIR = OUTPUT_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. INDICATOR FILES
# ==========================================

DATA_FILES = [
    "AMRGLASS_COORD02.csv",
    "AMRGLASS_COORD04.csv",
    "AMRGLASS_QA01.csv",
    "AMRGLASS_QA03.csv",
    "AMRGLASS_QA05.csv",
    "AMRGLASS_SURVL01.csv",
    "AMRGLASS_SURVL02.csv",
    "AMRGLASS_SURVL03.csv",
    "AMRGLASS_SURVL04.csv",
    "AMRGLASS_SURVL05.csv"
]

NUMERIC_COLUMNS = [
    "Value",
    "NumericValue",
    "Low",
    "High",
    "TimeDim",
    "TimeDimensionValue"
]

DATE_COLUMNS = [
    "Date",
    "TimeDimensionBegin",
    "TimeDimensionEnd"
]


# ==========================================
# 3. CLEAN INDIVIDUAL DATASET
# ==========================================

def clean_dataset(df, filename):

    df = df.copy()

    print(f"\nCleaning: {filename}")

    original_rows = len(df)

    # Standardise column names
    df.columns = df.columns.str.strip()

    # Remove whitespace from text columns
    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:

        df[column] = df[column].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

        df[column] = df[column].replace("", np.nan)

    # Convert numerical columns
    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Convert date columns
    for column in DATE_COLUMNS:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # Remove exact duplicate records only
    duplicate_count = df.duplicated().sum()

    df = df.drop_duplicates().copy()

    # Check invalid numeric values
    invalid_values = {}

    for column in ["Value", "NumericValue"]:

        if column in df.columns:

            invalid_values[column] = int(
                (df[column] < 0).sum()
            )

    # Missing value report
    missing_count = int(df.isnull().sum().sum())

    cleaned_rows = len(df)

    print("Original rows:", original_rows)
    print("Duplicate rows removed:", duplicate_count)
    print("Final rows:", cleaned_rows)
    print("Total missing cells:", missing_count)
    print("Negative values:", invalid_values)

    return df


# ==========================================
# 4. LOAD AND CLEAN ALL DATASETS
# ==========================================

def clean_all_datasets():

    cleaned_datasets = []

    cleaning_summary = []

    print("=" * 60)
    print("WHO GLASS DATA CLEANING")
    print("=" * 60)

    for filename in DATA_FILES:

        file_path = DATA_DIR / filename

        if not file_path.exists():

            print(f"WARNING: Missing file {filename}")
            continue

        try:

            df = pd.read_csv(file_path)

            original_rows = len(df)

            cleaned_df = clean_dataset(
                df,
                filename
            )

            # Add source information
            cleaned_df["SourceFile"] = filename

            # Save individual cleaned file
            output_name = filename.replace(
                ".csv",
                "_cleaned.csv"
            )

            cleaned_df.to_csv(
                PROCESSED_DIR / output_name,
                index=False
            )

            cleaned_datasets.append(cleaned_df)

            cleaning_summary.append({

                "Dataset": filename,

                "Original_Rows": original_rows,

                "Cleaned_Rows": len(cleaned_df),

                "Duplicates_Removed":
                    original_rows - len(cleaned_df),

                "Missing_Cells":
                    int(cleaned_df.isnull().sum().sum())

            })

        except Exception as error:

            print(f"ERROR cleaning {filename}: {error}")

    return cleaned_datasets, cleaning_summary


# ==========================================
# 5. COMBINE CLEANED DATASETS
# ==========================================

def combine_datasets(cleaned_datasets):

    if not cleaned_datasets:

        raise ValueError("No datasets were successfully cleaned.")

    combined_df = pd.concat(
        cleaned_datasets,
        ignore_index=True,
        sort=False
    )

    output_path = PROCESSED_DIR / "AMR_GLASS_MASTER.csv"

    combined_df.to_csv(
        output_path,
        index=False
    )

    print("\nMASTER DATASET CREATED")

    print("Total rows:", len(combined_df))

    print("Total columns:", len(combined_df.columns))

    print("Saved at:", output_path)

    return combined_df


# ==========================================
# 6. SAVE CLEANING SUMMARY
# ==========================================

def save_cleaning_summary(summary):

    summary_df = pd.DataFrame(summary)

    output_path = PROCESSED_DIR / "cleaning_summary.csv"

    summary_df.to_csv(
        output_path,
        index=False
    )

    print("\nCLEANING SUMMARY")

    print(summary_df.to_string(index=False))

    print("\nSummary saved at:", output_path)


# ==========================================
# 7. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    cleaned_datasets, summary = clean_all_datasets()

    if len(cleaned_datasets) != len(DATA_FILES):

        print("\nWARNING: Not all 10 datasets were cleaned.")

    if cleaned_datasets:

        master_df = combine_datasets(
            cleaned_datasets
        )

        save_cleaning_summary(summary)

        print("\n" + "=" * 60)

        print("DATA CLEANING COMPLETED")

        print("=" * 60)

        print("Datasets cleaned:", len(cleaned_datasets))

        print("Total records:", len(master_df))

        print(
            "Remaining exact duplicates:",
            master_df.duplicated().sum()
        )
