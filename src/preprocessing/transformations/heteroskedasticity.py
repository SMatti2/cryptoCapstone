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

        # copy column
        series = df[col].copy()

        # Check heteroskedasticity on non-null values
        non_null_series = series.dropna()
        het_result = check_heteroskedasticity(non_null_series, alpha)

        if het_result["needs_transform"]:
            # Create mask for non-null values
            mask = series.notna()

            if (series[mask] > 0).all():
                # Apply log transform to non-null values
                processed_df.loc[mask, col] = np.log(series[mask])
                if verbose:
                    print(f"Applied log transform to {col}")
            else:
                # Apply Yeo-Johnson to non-null values
                pt = PowerTransformer(method="yeo-johnson")
                transformed = pt.fit_transform(
                    series[mask].values.reshape(-1, 1)
                ).ravel()
                processed_df.loc[mask, col] = transformed
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
    df = pd.read_csv(
        "data/processed/crypto_prices/eth.csv",
        parse_dates=["date"],
        index_col="date",
    )

    processed_df = log_heteroskedastic_vars(df, verbose=True)
    processed_df.to_csv("data/processed/crypto_prices/heteroskedasticity_processed.csv")
