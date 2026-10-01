"""Exploratory Data Analysis for the Palmer Penguins dataset.

Run from the project root:
    python src/eda_analysis.py

The script reads the CSV included in data/, saves reproducible charts and
reports to outputs/, and prints a beginner-friendly summary to the terminal.
"""

from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib

# A non-interactive backend makes the script work on a terminal/CI server.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "penguins.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

EXPECTED_COLUMNS = [
    "species",
    "island",
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
    "sex",
]
NUMERIC_COLUMNS = [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]
CATEGORICAL_COLUMNS = ["species", "island", "sex"]
VALID_CATEGORIES = {
    "species": {"Adelie", "Chinstrap", "Gentoo"},
    "island": {"Biscoe", "Dream", "Torgersen"},
    "sex": {"FEMALE", "MALE"},
}


def heading(title: str) -> None:
    """Print a clearly separated terminal section."""
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def save_figure(filename: str) -> None:
    """Save the current Matplotlib figure consistently."""
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=180, bbox_inches="tight")
    plt.close()


def iqr_outlier_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return IQR fences and candidate-outlier counts for each numeric column.

    The IQR rule marks values far from the middle 50% of a variable. These are
    candidates for review, not automatic data errors.
    """
    rows = []
    for column in NUMERIC_COLUMNS:
        values = df[column].dropna()
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        candidates = values[(values < lower_fence) | (values > upper_fence)]
        rows.append(
            {
                "variable": column,
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_fence": lower_fence,
                "upper_fence": upper_fence,
                "outlier_candidates": len(candidates),
                "candidate_min": candidates.min() if not candidates.empty else np.nan,
                "candidate_max": candidates.max() if not candidates.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def suspicious_value_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Check category consistency and impossible non-positive measurements."""
    checks = []
    for column in CATEGORICAL_COLUMNS:
        observed = set(df[column].dropna().unique())
        unexpected = sorted(observed - VALID_CATEGORIES[column])
        checks.append(
            {
                "check": f"Unexpected values in {column}",
                "result": "None found" if not unexpected else ", ".join(unexpected),
                "records_flagged": 0
                if not unexpected
                else int(df[column].isin(unexpected).sum()),
            }
        )

    for column in NUMERIC_COLUMNS:
        non_positive = int((df[column].dropna() <= 0).sum())
        checks.append(
            {
                "check": f"Non-positive values in {column}",
                "result": "None found" if non_positive == 0 else "Review needed",
                "records_flagged": non_positive,
            }
        )
    return pd.DataFrame(checks)


def welch_test_by_sex(df: pd.DataFrame) -> dict[str, float]:
    """Test whether mean body mass differs between recorded male and female birds.

    Welch's t-test is used because it does not assume equal group variances.
    Rows with missing sex or body mass are excluded only from this test.
    """
    sex_mass = df.dropna(subset=["sex", "body_mass_g"])
    male = sex_mass.loc[sex_mass["sex"] == "MALE", "body_mass_g"]
    female = sex_mass.loc[sex_mass["sex"] == "FEMALE", "body_mass_g"]
    test = stats.ttest_ind(male, female, equal_var=False)
    levene = stats.levene(male, female, center="median")

    mean_difference = male.mean() - female.mean()
    standard_error = np.sqrt(male.var(ddof=1) / len(male) + female.var(ddof=1) / len(female))
    degrees_of_freedom = (
        (male.var(ddof=1) / len(male) + female.var(ddof=1) / len(female)) ** 2
        / (
            (male.var(ddof=1) / len(male)) ** 2 / (len(male) - 1)
            + (female.var(ddof=1) / len(female)) ** 2 / (len(female) - 1)
        )
    )
    margin = stats.t.ppf(0.975, degrees_of_freedom) * standard_error

    return {
        "male_n": len(male),
        "female_n": len(female),
        "male_mean": male.mean(),
        "female_mean": female.mean(),
        "mean_difference": mean_difference,
        "t_statistic": test.statistic,
        "p_value": test.pvalue,
        "degrees_of_freedom": degrees_of_freedom,
        "ci_lower": mean_difference - margin,
        "ci_upper": mean_difference + margin,
        "levene_p_value": levene.pvalue,
    }


def create_visualizations(df: pd.DataFrame) -> None:
    """Create charts that answer the project questions."""
    sns.set_theme(style="whitegrid", context="notebook")
    palette = {"Adelie": "#4C78A8", "Chinstrap": "#F58518", "Gentoo": "#54A24B"}

    plt.figure(figsize=(8, 5))
    order = df["species"].value_counts().index
    ax = sns.countplot(data=df, x="species", order=order, hue="species", palette=palette, legend=False)
    ax.set(title="Records by Penguin Species", xlabel="Species", ylabel="Number of records")
    for container in ax.containers:
        ax.bar_label(container, padding=3)
    save_figure("01_species_distribution.png")

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, column in zip(axes.flat, NUMERIC_COLUMNS):
        sns.histplot(data=df, x=column, hue="species", palette=palette, kde=True, ax=ax)
        ax.set_title(f"Distribution of {column.replace('_', ' ')}")
        ax.set_xlabel(column.replace("_", " "))
    save_figure("02_measurement_distributions.png")

    plt.figure(figsize=(10, 6))
    ax = sns.boxplot(
        data=df,
        x="species",
        y="body_mass_g",
        hue="sex",
        order=["Adelie", "Chinstrap", "Gentoo"],
        palette={"FEMALE": "#E45756", "MALE": "#4C78A8"},
    )
    ax.set(
        title="Body Mass by Species and Recorded Sex",
        xlabel="Species",
        ylabel="Body mass (g)",
    )
    ax.legend(title="Recorded sex")
    save_figure("03_body_mass_by_species_and_sex.png")

    plt.figure(figsize=(9, 6))
    ax = sns.scatterplot(
        data=df,
        x="bill_length_mm",
        y="flipper_length_mm",
        hue="species",
        style="sex",
        palette=palette,
        s=70,
        alpha=0.85,
    )
    ax.set(
        title="Bill Length and Flipper Length by Species",
        xlabel="Bill length (mm)",
        ylabel="Flipper length (mm)",
    )
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    save_figure("04_bill_length_vs_flipper_length.png")

    plt.figure(figsize=(8, 6))
    corr = df[NUMERIC_COLUMNS].corr()
    ax = sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0, square=True)
    ax.set_title("Correlation Between Numerical Measurements")
    save_figure("05_correlation_heatmap.png")

    plt.figure(figsize=(7, 5))
    ax = sns.boxplot(
        data=df.dropna(subset=["sex", "body_mass_g"]),
        x="sex",
        y="body_mass_g",
        order=["FEMALE", "MALE"],
        hue="sex",
        palette={"FEMALE": "#E45756", "MALE": "#4C78A8"},
        legend=False,
    )
    sns.stripplot(
        data=df.dropna(subset=["sex", "body_mass_g"]),
        x="sex",
        y="body_mass_g",
        order=["FEMALE", "MALE"],
        color="black",
        alpha=0.30,
        jitter=0.18,
        size=3,
        ax=ax,
    )
    ax.set(
        title="Body Mass by Recorded Sex (Hypothesis-Test Groups)",
        xlabel="Recorded sex",
        ylabel="Body mass (g)",
    )
    save_figure("06_body_mass_by_sex_hypothesis.png")


def write_report(
    df: pd.DataFrame,
    missing: pd.Series,
    duplicates: int,
    suspicious: pd.DataFrame,
    outliers: pd.DataFrame,
    species_summary: pd.DataFrame,
    correlation: pd.DataFrame,
    test: dict[str, float],
) -> None:
    """Write a concise Markdown report using values calculated in this run."""
    p_value_text = "< 0.001" if test["p_value"] < 0.001 else f"= {test['p_value']:.4f}"
    hypothesis_result = (
        "reject the null hypothesis"
        if test["p_value"] < 0.05
        else "do not reject the null hypothesis"
    )
    missing_rows = int(df.isna().any(axis=1).sum())
    high_corr = correlation.where(np.triu(np.ones(correlation.shape), k=1).astype(bool)).stack()
    strongest_pair = high_corr.abs().idxmax()
    strongest_r = high_corr[strongest_pair]
    largest_species = df["species"].value_counts().idxmax()
    largest_species_count = int(df["species"].value_counts().max())

    report = f"""# Palmer Penguins EDA — Results

This report is generated by src/eda_analysis.py from data/penguins.csv.

## Dataset snapshot

- **Rows:** {len(df)}
- **Columns:** {len(df.columns)}
- **Exact duplicate rows:** {duplicates}
- **Rows with at least one missing value:** {missing_rows}

## Questions explored

1. How is the sample distributed across species and islands?
2. How do physical measurements vary by species and recorded sex?
3. Which measurements move together?
4. Is mean body mass different for recorded male and female penguins?
5. Are there missing, duplicate, inconsistent, or unusually extreme values that need review?

## Key Findings

- **{largest_species}** is the most frequently represented species ({largest_species_count} of {len(df)} records).
- The species-level body-mass summaries and the boxplot show that **Gentoo** penguins are generally heavier and have longer flippers than the other sampled species. This is a pattern in this sample, not a claim about every penguin population.
- The strongest linear measurement relationship is **{strongest_pair[0]} and {strongest_pair[1]}** (Pearson r = {strongest_r:.2f}). The correlation heatmap and scatterplot help show the direction and strength of this relationship.
- Recorded males average **{test['mean_difference']:.0f} g** more body mass than recorded females in the usable rows ({test['male_mean']:.0f} g vs {test['female_mean']:.0f} g).
- A Welch two-sample t-test gives t = {test['t_statistic']:.2f}, p {p_value_text}; at a 5% significance level, we **{hypothesis_result}** that male and female mean body mass is the same in this dataset.

## Hypothesis test in plain language

**Question:** Is the average body mass the same for penguins recorded as male and female?

- **Null hypothesis (H0):** their average body mass is the same.
- **Alternative hypothesis (H1):** their average body mass is different.
- **Method:** Welch's independent two-sample t-test. It uses {int(test['male_n'])} male and {int(test['female_n'])} female records with non-missing body mass.
- **Result:** t({test['degrees_of_freedom']:.1f}) = {test['t_statistic']:.2f}, p {p_value_text}; estimated male-minus-female difference = {test['mean_difference']:.1f} g (95% CI: {test['ci_lower']:.1f} to {test['ci_upper']:.1f} g).

Because the p-value is below 0.05, the observed difference would be unlikely if the two population means were truly equal. This shows an association in this sample; it does not prove that sex alone causes the difference. Species is also related to body mass, so a later analysis could compare sexes within each species.

### Assumption checks

- Each row is treated as one independent penguin record; independence cannot be proven from this CSV alone and should be confirmed from collection documentation.
- The groups are reasonably large ({int(test['male_n'])} and {int(test['female_n'])} records), and 06_body_mass_by_sex_hypothesis.png lets the reader inspect spread and shape.
- Levene's median-based variance test has p = {test['levene_p_value']:.4f}. Welch's test was selected because it does not require equal variances.
- Missing sex/body-mass records are excluded from this one test only, rather than being filled with invented values.

## Data-quality findings and follow-up actions

{missing.to_frame("missing_values").to_markdown()}

{suspicious.to_markdown(index=False)}

{outliers.to_markdown(index=False, floatfmt=".2f")}

There are {missing_rows} rows with at least one missing value. Missing numerical values should be handled deliberately in later modeling: inspect why they are absent, avoid treating them as zero, and choose complete-case analysis or a documented imputation method only when appropriate. The data contains {duplicates} exact duplicate rows. IQR candidates are unusual observations to review, not values to delete automatically; biological variation may be real.

## Supporting tables

### Species-level numerical summary

{species_summary.to_markdown(index=False, floatfmt=".2f")}

### Pearson correlation matrix

{correlation.to_markdown(floatfmt=".2f")}
"""
    (OUTPUT_DIR / "analysis_summary.md").write_text(report, encoding="utf-8")


def main() -> None:
    """Run the full exploratory analysis."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    heading("1. Meaningful Questions Before Analysis")
    print(
        textwrap.dedent(
            """
            1. How is the sample distributed across penguin species and islands?
            2. Do body size measurements differ by species and recorded sex?
            3. Which measurements are related to one another?
            4. Is average body mass different for recorded male and female penguins?
            5. Are there missing, duplicate, inconsistent, or unusually extreme values?
            """
        ).strip()
    )

    df = pd.read_csv(DATA_PATH)
    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            "Unexpected CSV schema. Expected columns: "
            f"{EXPECTED_COLUMNS}; found: {list(df.columns)}"
        )

    heading("2. Data Structure and First Look")
    print(f"Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("\nSample records:")
    print(df.head().to_string(index=False))
    print("\nColumn data types:")
    print(df.dtypes.to_string())

    heading("3. Data Quality Checks")
    missing = df.isna().sum()
    duplicates = int(df.duplicated().sum())
    suspicious = suspicious_value_checks(df)
    outliers = iqr_outlier_summary(df)
    print("Missing values by column:")
    print(missing.to_string())
    print(f"\nExact duplicate rows: {duplicates}")
    print("\nInconsistent or impossible-value checks:")
    print(suspicious.to_string(index=False))
    print("\nIQR outlier candidates (review; not automatic errors):")
    print(outliers.to_string(index=False, float_format=lambda value: f"{value:.2f}"))

    heading("4. Descriptive Statistics and Patterns")
    print("Numerical summary:")
    print(df[NUMERIC_COLUMNS].describe().round(2).to_string())
    print("\nCategorical counts:")
    for column in CATEGORICAL_COLUMNS:
        print(f"\n{column}:")
        print(df[column].value_counts(dropna=False).to_string())

    species_summary = (
        df.groupby("species", dropna=False)
        .agg(
            records=("species", "size"),
            mean_bill_length_mm=("bill_length_mm", "mean"),
            mean_flipper_length_mm=("flipper_length_mm", "mean"),
            mean_body_mass_g=("body_mass_g", "mean"),
        )
        .reset_index()
        .sort_values("mean_body_mass_g", ascending=False)
    )
    correlation = df[NUMERIC_COLUMNS].corr()
    print("\nSpecies-level summary:")
    print(species_summary.round(2).to_string(index=False))
    print("\nNumerical correlation matrix:")
    print(correlation.round(2).to_string())

    heading("5. Hypothesis Test: Body Mass by Recorded Sex")
    test = welch_test_by_sex(df)
    print("H0: Mean body mass is the same for recorded male and female penguins.")
    print("H1: Mean body mass differs between the two recorded-sex groups.")
    print(
        f"Male mean = {test['male_mean']:.1f} g (n={int(test['male_n'])}); "
        f"Female mean = {test['female_mean']:.1f} g (n={int(test['female_n'])})"
    )
    print(
        f"Welch t-test: t = {test['t_statistic']:.2f}, p = {test['p_value']:.3g}; "
        f"male - female = {test['mean_difference']:.1f} g"
    )
    print(
        "Interpretation: "
        + (
            "the p-value is below 0.05, so the data provides evidence of a difference."
            if test["p_value"] < 0.05
            else "the p-value is not below 0.05, so this sample does not provide enough evidence of a difference."
        )
    )

    heading("6. Creating Charts and Reproducible Report")
    create_visualizations(df)
    df[NUMERIC_COLUMNS].describe().round(2).to_csv(OUTPUT_DIR / "numeric_summary.csv")
    df[CATEGORICAL_COLUMNS].describe().to_csv(OUTPUT_DIR / "categorical_summary.csv")
    missing.rename("missing_values").to_csv(OUTPUT_DIR / "missing_values.csv")
    suspicious.to_csv(OUTPUT_DIR / "suspicious_value_checks.csv", index=False)
    outliers.to_csv(OUTPUT_DIR / "iqr_outlier_candidates.csv", index=False)
    species_summary.to_csv(OUTPUT_DIR / "species_summary.csv", index=False)
    correlation.to_csv(OUTPUT_DIR / "correlation_matrix.csv")
    write_report(
        df, missing, duplicates, suspicious, outliers, species_summary, correlation, test
    )
    print(f"Saved charts and tables to: {OUTPUT_DIR}")
    print("Open outputs/analysis_summary.md for the concise written findings.")


if __name__ == "__main__":
    main()
