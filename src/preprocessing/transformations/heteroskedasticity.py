import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_white, het_breuschpagan, het_goldfeldquandt
from sklearn.preprocessing import PowerTransformer
from config import config


def check_heteroskedasticity(series, alpha=0.05):
    """Check heteroskedasticity in a single feature's own time series"""
    X = sm.add_constant(np.arange(len(series)))  # Time trend
    model = sm.OLS(series, X).fit()
    residuals = model.resid

    # White Test
    _, white_p, _, _ = het_white(residuals, X)

    # Breusch-Pagan Test
    _, bp_p, _, _ = het_breuschpagan(residuals, X)

    # Goldfeld-Quandt Test
    gq_p = het_goldfeldquandt(series, X)[1]

    return {
        "White": white_p < alpha,
        "Breusch-Pagan": bp_p < alpha,
        "Goldfeld-Quandt": gq_p < alpha,
        "needs_transform": sum([white_p < alpha, bp_p < alpha, gq_p < alpha]) >= 2,
    }


def log_heteroskedastic_vars(
    df,
    target="logPriceChange",
    variables_to_exclude=config.EXCLUDE_VARIABLES,
    alpha=0.05,
    verbose=False,
):
    """
    Heteroskedasticity-focused preprocessing:
    1. Checks each feature's variance stability
    2. Applies transformations where needed
    """
    processed_df = df.copy()

    for col in df.columns:
        if col == target or col in variables_to_exclude:
            continue

        series = df[col].dropna()
        if len(series) < 10:  # Minimum observations check
            if verbose:
                print(f"Skipped {col} - insufficient data")
            continue

        # Check heteroskedasticity on original series
        het_result = check_heteroskedasticity(series, alpha)

        if het_result["needs_transform"]:
            if (series > 0).all():
                # Apply log transform for positive-definite series
                processed_df[col] = np.log(series)
                if verbose:
                    print(f"Applied log transform to {col}")
            else:
                # Use Yeo-Johnson for series with negatives/zeros
                pt = PowerTransformer(method="yeo-johnson")
                processed_df[col] = pt.fit_transform(
                    series.values.reshape(-1, 1)
                ).ravel()
                if verbose:
                    print(f"Applied Yeo-Johnson to {col}")

    # Preserve target and excluded columns
    processed_df[target] = df[target]
    for col in variables_to_exclude:
        if col in df.columns:
            processed_df[col] = df[col]

    return processed_df


# Usage example
if __name__ == "__main__":
    # Load raw data
    df = (
        pd.read_csv(
            "data/processed/crypto_prices/eth.csv",
            parse_dates=["date"],
            index_col="date",
        )
        .dropna()
        .sort_index()
    )

    # Handle heteroskedasticity only
    processed_df = log_heteroskedastic_vars(df, verbose=True)

    # Save results
    processed_df.to_csv("data/processed/crypto_prices/heteroskedasticity_processed.csv")
