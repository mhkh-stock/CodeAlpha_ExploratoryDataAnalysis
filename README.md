# CodeAlpha Tasks 2 & 3 — Exploratory Data Analysis and Data Visualization

A beginner-friendly, reproducible Python project using the **Palmer Penguins** dataset. It investigates penguin body measurements, species, island, and recorded sex while meeting CodeAlpha **Task 2 (EDA)** and **Task 3 (Data Visualization)** requirements.

The CSV is included in this repository, so the project works after cloning and does not need a website or API at run time.

## Project Objectives

Before looking at the data, this project asks these meaningful questions:

1. How is the sample distributed across penguin species and islands?
2. Do body-size measurements differ by species and recorded sex?
3. Which measurements are related to one another?
4. Is average body mass different for penguins recorded as male and female?
5. Are there missing, duplicate, inconsistent, or unusually extreme values that should be reviewed?

## Dataset

- **Name:** Palmer Penguins
- **Included file:** data/penguins.csv
- **Records:** 344 penguins
- **Variables:** 7
- **Source used for this repository:** [Seaborn example-data CSV](https://github.com/mwaskom/seaborn-data/blob/master/penguins.csv)
- **Original documentation:** [Palmer Penguins project](https://allisonhorst.github.io/palmerpenguins/reference/penguins.html)
- **License:** The original Palmer Penguins package is [CC0](https://github.com/allisonhorst/palmerpenguins/blob/main/DESCRIPTION).

The included CSV contains measurements for Adelie, Chinstrap, and Gentoo penguins observed in the Palmer Archipelago, Antarctica. This simplified version has these columns:

| Column | Type when loaded | Meaning |
|---|---|---|
| species | text/category | Penguin species: Adelie, Chinstrap, or Gentoo |
| island | text/category | Island: Biscoe, Dream, or Torgersen |
| bill_length_mm | number | Bill length in millimetres |
| bill_depth_mm | number | Bill depth in millimetres |
| flipper_length_mm | number | Flipper length in millimetres |
| body_mass_g | number | Body mass in grams |
| sex | text/category | Recorded sex: FEMALE or MALE |

## Tools Used

- Python 3.10+
- Pandas and NumPy for loading, cleaning checks, summaries, and calculations
- Matplotlib and Seaborn for visualizations
- SciPy for the Welch independent-samples t-test

## Project Structure

~~~text
codealpha-eda/
├── data/
│   └── penguins.csv                 # Included source dataset
├── outputs/
│   └── .gitkeep                     # Generated charts/tables are saved here
├── src/
│   └── eda_analysis.py              # Complete reproducible EDA
├── .gitignore
├── README.md
└── requirements.txt
~~~

## How to Run

1. Clone or download the repository and open a terminal in its root folder.
2. Create and activate a virtual environment (recommended).

   ~~~bash
   python -m venv .venv
   ~~~

   Windows PowerShell:

   ~~~powershell
   .\.venv\Scripts\Activate.ps1
   ~~~

   macOS/Linux:

   ~~~bash
   source .venv/bin/activate
   ~~~

3. Install the dependencies.

   ~~~bash
   pip install -r requirements.txt
   ~~~

4. Run the analysis.

   ~~~bash
   python src/eda_analysis.py
   ~~~

The script prints the inspection and statistical result to the terminal. It also creates charts, CSV summaries, and outputs/analysis_summary.md. All output files are generated from the local CSV, so a reviewer can reproduce every number.

## Methodology

The analysis script follows this sequence:

1. States the questions before examining the data.
2. Loads data/penguins.csv, confirms its expected column names, prints shape, sample rows, and data types.
3. Checks missing values, exact duplicates, unexpected category labels, and impossible non-positive measurements.
4. Produces descriptive statistics, category counts, species-level summaries, and a correlation matrix.
5. Uses the interquartile-range (IQR) rule to identify numerical values that are unusually far from the middle 50% of the data. These are review candidates, not automatic errors.
6. Creates count plots, histograms, boxplots, a scatterplot, and a correlation heatmap.
7. Tests whether the mean body mass differs between the recorded male and female groups with Welch's t-test.
8. Saves a plain-language findings report and data-quality tables.

## Task 3: Data Visualizations

The project uses several chart types so that each question is shown in an appropriate, readable way. Every chart has a descriptive title, labelled axes with units where relevant, and a legend when multiple groups are shown.

| Output | Chart type | What it shows |
|---|---|---|
| `01_species_distribution.png` | Bar chart | The number of records for each penguin species. |
| `02_measurement_distributions.png` | Histograms with density curves | The distributions of four numerical measurements, separated by species. |
| `03_body_mass_by_species_and_sex.png` | Grouped boxplot | How body mass varies across species and recorded sex groups. |
| `04_bill_length_vs_flipper_length.png` | Scatterplot | The relationship between bill length and flipper length, with species and sex visible. |
| `05_correlation_heatmap.png` | Correlation heatmap | The strength and direction of relationships among numerical measurements. |
| `06_body_mass_by_sex_hypothesis.png` | Boxplot with individual points | The body-mass distributions used to support the hypothesis test. |

Together, the charts communicate categorical composition, distributions, comparisons between groups, relationships between numerical variables, and the statistical-test result. They are generated directly from the included CSV by the same reproducible script used for the EDA.

## Verified Key Findings

All values below were calculated from the included CSV.

- The sample contains **152 Adelie**, **124 Gentoo**, and **68 Chinstrap** records. Biscoe is the most represented island with **168** records.
- Gentoo penguins are clearly larger in this sample: their average body mass is **5,076.0 g** and their average flipper length is **217.2 mm**. Adelie averages **3,700.7 g** and **190.0 mm**; Chinstrap averages **3,733.1 g** and **195.8 mm**.
- Flipper length and body mass have the strongest positive linear relationship among the measurements (**Pearson r = 0.87**). The scatterplot and heatmap show this pattern.
- In records with both fields present, the recorded male group has a mean body mass of **4,545.7 g** (n = 168) and the recorded female group has a mean of **3,862.3 g** (n = 165): a difference of **683.4 g**.
- Welch's t-test gives **t = 8.55**, **df = 323.9**, and **p = 4.79 × 10⁻¹⁶**. Since the p-value is far below 0.05, the sample provides strong evidence that the two recorded-sex groups do not have the same mean body mass.

The test shows an association in this sample; it does **not** prove that sex alone causes the difference. Species is also related to body mass, so comparing sexes within each species would be a sensible next analysis.

## Data-Quality Findings

| Check | Result from the included CSV | Recommended treatment |
|---|---:|---|
| Missing bill length | 2 values | Do not replace with zero; choose a documented strategy if a later task needs this field. |
| Missing bill depth | 2 values | Do not replace with zero. |
| Missing flipper length | 2 values | Do not replace with zero. |
| Missing body mass | 2 values | Exclude only from calculations that require body mass, or justify an imputation later. |
| Missing recorded sex | 11 values | Exclude only from sex-based analysis; do not guess the value. |
| Rows with one or more missing values | 11 rows | Investigate the collection context before further modelling. |
| Exact duplicate records | 0 | No duplicate removal is needed. |
| Unexpected categories / non-positive measurements | 0 flagged | Categories and basic numeric validity checks are consistent. |
| IQR outlier candidates | 0 across the four numeric columns | No global IQR candidates were found; species differences still create real variation. |

## Hypothesis Test Explained Simply

**Question:** Is average body mass the same for penguins recorded as female and male?

- **Null hypothesis (H0):** Their average body mass is the same.
- **Alternative hypothesis (H1):** Their average body mass is different.
- **Test:** Welch's independent two-sample t-test. Welch's version is used because it does not require equal variation in the two groups.
- **Decision rule:** Treat a p-value below 0.05 as statistically significant.
- **Result:** p is much smaller than 0.05, so reject H0 for this dataset.

The script also reports a Levene variance check and creates a boxplot/stripplot to make the group distributions visible. It does not fill missing values with made-up data, and it explains that row independence is a study-design assumption that must be confirmed from collection documentation.

## Generated Outputs

After the script runs, `outputs/` contains the following version-controlled visualizations and reproducible summary files:

- 01_species_distribution.png
- 02_measurement_distributions.png
- 03_body_mass_by_species_and_sex.png
- 04_bill_length_vs_flipper_length.png
- 05_correlation_heatmap.png
- 06_body_mass_by_sex_hypothesis.png
- analysis_summary.md
- CSV tables for missing values, IQR checks, species summaries, correlations, and descriptive statistics

## How This Meets CodeAlpha Task 2 Requirements

| Official requirement | Where it is satisfied |
|---|---|
| Ask meaningful questions before analysis | The five questions appear first in src/eda_analysis.py and in the Project Objectives section. |
| Explore data structure, variables, and types | The script validates column names, reports the 344 × 7 shape, shows sample records, and prints data types. |
| Identify trends, patterns, and anomalies | Species summaries, correlations, IQR checks, and six visualizations reveal size patterns and relationships. |
| Test hypotheses and validate assumptions | The script uses Welch's t-test, reports group sizes and Levene's test, and uses a distribution plot to support interpretation. |
| Detect data issues for further analysis | Missing values, duplicate rows, category consistency, non-positive measurements, and IQR candidates are all checked and saved to tables. |
| Use Pandas, NumPy, and visualizations | Pandas/NumPy are used throughout; Matplotlib/Seaborn create the charts. |
| Document findings without fabrication | Findings in this README are reproducible from the included CSV, and the script writes them again from calculated values. |
| Keep it beginner-friendly | The code is commented, uses clear section headings, and explains the hypothesis test in simple language. |

## How This Meets CodeAlpha Task 3 Requirements

| Data visualization requirement | Where it is satisfied |
|---|---|
| Create meaningful visualizations from a dataset | Six charts are generated from `data/penguins.csv` in `create_visualizations()`. |
| Use Python visualization libraries | Matplotlib and Seaborn are listed in `requirements.txt` and imported in `src/eda_analysis.py`. |
| Use different chart types appropriately | The project includes a bar chart, histograms, boxplots, a scatterplot, a heatmap, and individual data points. |
| Make charts easy to understand | Every chart uses a descriptive title, labelled axes, measurement units, readable colours, and legends where categories are encoded. |
| Draw conclusions from visualizations | The Verified Key Findings section and generated `analysis_summary.md` explain the observed patterns using calculated results. |
| Make the work reproducible and GitHub-ready | The local CSV, source code, requirements, generated charts, and documentation are included in the project. |

## Suggested Next Steps

- Add the study year from the fuller Palmer Penguins dataset if time-based comparisons are needed.
- Compare male and female body mass **within each species** to reduce species as a confounding factor.
- Decide on a documented missing-data approach before building any predictive model.
- Keep this EDA as the first notebook/script in a larger data-analysis portfolio project..
