
import pandas as pd
from pathlib import Path

# -----------------------------------
# 1. Define project paths
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CODES_DIR = BASE_DIR / "codes"

# -----------------------------------
# 2. List the dataset files
# -----------------------------------

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

CODE_FILES = [
    "AMRGLASSCATEGORY.csv",
    "COUNTRY.csv",
    "GHO.csv",
    "REGION.csv"
]

# -----------------------------------
# 3. Load CSV files
# -----------------------------------

def load_csv_files(folder, filenames):

    datasets = {}

    for filename in filenames:

        file_path = folder / filename

        if not file_path.exists():
            print(f"ERROR: File not found: {filename}")
            continue

        try:
            df = pd.read_csv(file_path)

            dataset_name = filename.replace(".csv", "")

            datasets[dataset_name] = df

            print(f"Loaded: {filename}")
            print(f"Rows: {df.shape[0]}")
            print(f"Columns: {df.shape[1]}")
            print("-" * 45)

        except Exception as error:
            print(f"Error loading {filename}: {error}")

    return datasets


# -----------------------------------
# 4. Examine dataset structure
# -----------------------------------

def inspect_datasets(datasets):

    print("\nDATASET STRUCTURE ANALYSIS")
    print("=" * 55)

    for name, df in datasets.items():

        print(f"\nDataset: {name}")

        print("Shape:", df.shape)

        print("Column names:")
        print(df.columns.tolist())

        print("\nMissing values:")
        print(df.isnull().sum().to_string())

        print("\nDuplicate rows:")
        print(df.duplicated().sum())

        if "TimeDim" in df.columns:
            print("\nAvailable years:")
            print(sorted(df["TimeDim"].dropna().unique()))

        if "SpatialDimension" in df.columns:
            print("\nSpatial dimensions:")
            print(df["SpatialDimension"].value_counts().to_string())

        print("=" * 55)


# -----------------------------------
# 5. Main execution
# -----------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("WHO GLASS DATA LOADING")
    print("=" * 55)

    print("\nLoading indicator datasets...\n")

    data_datasets = load_csv_files(
        DATA_DIR,
        DATA_FILES
    )

    print("\nLoading metadata datasets...\n")

    code_datasets = load_csv_files(
        CODES_DIR,
        CODE_FILES
    )

    print("\nTotal indicator datasets loaded:",
          len(data_datasets))

    print("Total metadata datasets loaded:",
          len(code_datasets))

    print("\nTotal indicator records:",
          sum(len(df) for df in data_datasets.values()))

    print("\nInspecting indicator datasets...")

    inspect_datasets(data_datasets)

    print("\nDATA LOADING COMPLETED")
