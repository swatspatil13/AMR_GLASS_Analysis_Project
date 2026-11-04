# Global Assessment of Antimicrobial Resistance (AMR) Surveillance Readiness Using WHO GLASS Data

## Project Overview

This project analyzes the World Health Organization's Global Antimicrobial Resistance and Use Surveillance System (WHO GLASS) data to assess regional AMR surveillance infrastructure and reporting capacity between 2017 and 2020.

The analysis focuses on six WHO regions and evaluates indicators related to:

- National AMR coordination centres
- National reference laboratories
- External quality assurance (EQA)
- Antimicrobial susceptibility testing (AST) standards
- Hospital and outpatient surveillance sites
- Clinical laboratory participation in surveillance

The project applies data preprocessing, exploratory data analysis, statistical testing, correlation analysis and interactive visualization to identify regional patterns and changes in surveillance infrastructure.

## Research Objectives

1. Examine regional differences in AMR surveillance infrastructure.
2. Analyze temporal trends in WHO GLASS indicators from 2017 to 2020.
3. Evaluate regional reporting coverage across the ten indicators.
4. Apply statistical tests to investigate changes over time.
5. Explore associations between regional changes in surveillance indicators.
6. Develop an interactive dashboard for exploring the findings.

## Dataset Description

**Source:** WHO Global Antimicrobial Resistance and Use Surveillance System (GLASS).

The dataset contains ten indicator files and four metadata files.

### Indicators analyzed

| Category | Indicator codes | Description |
|---|---|---|
| Coordination | COORD02 | Establishment of National Coordination Centre |
| Coordination | COORD04 | Establishment of National Reference Laboratory |
| Quality Assurance | QA01 | EQA provided to NRL |
| Quality Assurance | QA03 | EQA provided to participating local laboratories |
| Quality Assurance | QA05 | AST standards followed |
| Surveillance | SURVL01 | Hospital surveillance sites |
| Surveillance | SURVL02 | Outpatient surveillance sites |
| Surveillance | SURVL03 | Local clinical laboratories supporting surveillance |
| Surveillance | SURVL04 | Inpatient and outpatient surveillance sites |
| Surveillance | SURVL05 | Total surveillance sites reporting to GLASS |

**Geographical coverage:** Six WHO regions.

**Time period:** 2017–2020.

**Total observations:** 666.

**Important:** The dataset contains regional surveillance infrastructure and capacity indicators. It does not directly measure bacterial antibiotic resistance prevalence.

## Methodology

### 1. Data Loading
- Loaded ten WHO GLASS indicator datasets.
- Imported four metadata and lookup files.
- Examined data dimensions, column types and missing values.

### 2. Data Cleaning
- Standardized column names and data formats.
- Converted numerical and date fields.
- Checked and removed duplicate records where applicable.
- Combined the indicator datasets into a master dataset.
- Preserved missing values without automatically replacing them with zero.

### 3. Exploratory Data Analysis
- Indicator-wise descriptive statistics.
- Regional reporting coverage.
- Year-wise reporting patterns.
- Indicator-specific temporal trends.
- Data completeness assessment.

### 4. Statistical Analysis
- Wilcoxon signed-rank test for paired regional comparisons between 2017 and 2020.
- Friedman test for repeated observations across 2017–2020.
- Benjamini–Hochberg false discovery rate correction for multiple testing.
- Regional absolute and percentage change calculations.

### 5. Correlation Analysis
- Spearman rank correlation.
- Analysis of regional changes between 2017 and 2020.
- Correlation matrix and heatmap visualization.

### 6. Regional Readiness Profiling
- Mapping official WHO indicator descriptions.
- Mapping indicator category definitions.
- Generating regional indicator profiles.
- Comparing 2020 regional observations.
- Examining reporting coverage and temporal trends.

No composite readiness score or regional ranking is calculated because the indicators have different meanings, measurement scales and denominators.

## Technology Stack

| Component | Technologies |
|---|---|
| Programming | Python |
| Data manipulation | Pandas, NumPy |
| Statistical analysis | SciPy, Statsmodels |
| Visualization | Matplotlib, Seaborn, Plotly |
| Interactive dashboard | Streamlit |
| Development environment | Visual Studio Code |
| Version control | Git and GitHub |

## Project Structure

```text
AMR_GLASS_Analysis_Project/
│
├── codes/
│   ├── AMRGLASSCATEGORY.csv
│   ├── COUNTRY.csv
│   ├── GHO.csv
│   └── REGION.csv
│
├── data/
│   ├── AMRGLASS_COORD02.csv
│   ├── AMRGLASS_COORD04.csv
│   ├── AMRGLASS_QA01.csv
│   ├── AMRGLASS_QA03.csv
│   ├── AMRGLASS_QA05.csv
│   ├── AMRGLASS_SURVL01.csv
│   ├── AMRGLASS_SURVL02.csv
│   ├── AMRGLASS_SURVL03.csv
│   ├── AMRGLASS_SURVL04.csv
│   └── AMRGLASS_SURVL05.csv
│
├── src/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── exploratory_analysis.py
│   ├── statistical_analysis.py
│   ├── correlation_analysis.py
│   └── readiness_index.py
│
├── outputs/
│   ├── processed/
│   ├── tables/
│   ├── figures/
│   └── reports/
│
├── app.py
├── run_analysis.py
├── requirements.txt
└── README.md
```

## Installation and Execution

### 1. Clone the repository

```bash
git clone https://github.com/swatspatil13/AMR_GLASS_Analysis_Project.git

cd AMR_GLASS_Analysis_Project
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Run the analysis modules

Execute the modules in the following order:

```bash
python src/data_loader.py

python src/data_cleaning.py

python src/exploratory_analysis.py

python src/statistical_analysis.py

python src/correlation_analysis.py

python src/readiness_index.py
```

### 4. Launch the interactive dashboard

```bash
python -m streamlit run app.py
```

The dashboard will be available locally at:

`http://localhost:8501`

## Generated Outputs

### Statistical tables
- Indicator summary
- Regional coverage
- Yearly reporting summary
- Wilcoxon test results
- Friedman test results
- Regional temporal changes
- Spearman correlation results
- Correlation matrix
- Regional readiness profile
- 2020 regional snapshot

### Visualizations
- Indicator distributions
- Regional reporting coverage
- Yearly reporting trends
- Individual indicator trends
- Correlation heatmap
- Regional readiness trend plots

## Key Findings

The exploratory analysis identified:

- Six WHO regions represented in the dataset.
- Ten surveillance infrastructure and capacity indicators.
- 666 observations across 2017–2020.
- Differences in indicator reporting coverage across regions and years.
- Variations in reported coordination, laboratory quality assurance and surveillance infrastructure indicators.

The statistical and correlation analyses are exploratory. Their results must be interpreted in view of the small number of geographical units and incomplete paired observations.

## Limitations

1. The dataset provides regional rather than country-level measurements.
2. Only six WHO regions are available for geographical comparisons.
3. The study period covers four years (2017–2020).
4. Indicators have different units, scales and definitions.
5. Missing observations and differences in reporting coverage may influence comparisons.
6. Correlation does not establish causation.
7. Surveillance infrastructure indicators cannot be interpreted as direct measurements of AMR prevalence.

## Future Scope

- Incorporation of more recent WHO GLASS datasets.
- Country-level surveillance capacity assessment, subject to data availability.
- Integration of antimicrobial resistance prevalence datasets.
- Development of a validated composite readiness framework.
- Advanced predictive modelling and longitudinal analysis.
- Expansion of the interactive dashboard.

## Acknowledgements

Data source: World Health Organization (WHO), Global Antimicrobial Resistance and Use Surveillance System (GLASS).

## Author

**Atreyee Bhattacharyya** and
**Swati Patil**

Medical Electronics Engineering

Ramaiah Institute of Technology

GitHub: [@swatspatil13](https://github.com/swatspatil13)

---

*This project is intended for research and analytical purposes. Findings should not be interpreted as clinical recommendations or direct estimates of antimicrobial resistance prevalence.*
