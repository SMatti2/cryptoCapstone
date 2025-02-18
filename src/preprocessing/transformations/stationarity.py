import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tools.sm_exceptions import InterpolationWarning
from arch.unitroot import PhillipsPerron


def adf_test(series, alpha):
    """Augmented Dickey-Fuller test"""
    result = adfuller(series, autolag="AIC")
    return {
        "Test Statistic": result[0],
        "p-value": result[1],
        "Stationary": result[1] < alpha,
    }


def pp_test(series, alpha):
    """Phillips-Perron test"""
    result = PhillipsPerron(series)
    return {
        "Test Statistic": result.stat,
        "p-value": result.pvalue,
        "Stationary": result.pvalue < alpha,
    }


def kpss_test(series, alpha):
    """KPSS test"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InterpolationWarning)
        result = kpss(series, regression="c", nlags="auto")
    return {
        "Test Statistic": result[0],
        "p-value": result[1],
        "Stationary": result[1] >= alpha,
    }


def difference_non_stationary_features(
    df,
    target="logPriceChange",
    variables_to_exclude=None,
    alpha=0.05,
    verbose=False,
):
    df
    differenced_columns = []

    if variables_to_exclude is None:
        variables_to_exclude = []

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cols_to_process = [
        c for c in numeric_cols if c not in variables_to_exclude and c != target
    ]

    for col in cols_to_process:
        # Original series with potential NaNs
        original_series = df[col]

        # Forward-fill NaNs and track changes
        filled_series = original_series.ffill()
        n_filled = original_series.isna().sum() - filled_series.isna().sum()
        n_leading_dropped = filled_series.isna().sum()

        # Remove any remaining leading NaNs
        clean_series = filled_series.dropna()

        if verbose:
            print(f"\nColumn: {col}")
            print(f"Original NaNs: {original_series.isna().sum()}")
            print(f"NaNs filled by forward-fill: {n_filled}")
            print(f"Leading NaNs dropped: {n_leading_dropped}")
            print(f"Clean data points remaining: {len(clean_series)}")

        # Skip columns with insufficient data after cleaning
        if len(clean_series) < 2:
            if verbose:
                print("Skipping - insufficient data after cleaning")
            continue

        # check stationarity
        tests = {
            "ADF": adf_test(clean_series, alpha),
            "PP": pp_test(clean_series, alpha),
            "KPSS": kpss_test(clean_series, alpha),
        }

        non_stationary_votes = sum(
            [
                not tests["ADF"]["Stationary"],
                not tests["PP"]["Stationary"],
                not tests["KPSS"]["Stationary"],
            ]
        )

        if non_stationary_votes >= 2:
            differenced = clean_series.diff()

            # Preserve original index structure
            df.loc[clean_series.index, col] = differenced
            differenced_columns.append(col)

    df = df.dropna()

    if verbose:
        print(f"\nColumn: {col}")
        print(f"Original NaNs: {original_series.isna().sum()}")
        print(f"NaNs filled by forward-fill: {n_filled}")
        print(f"Leading NaNs dropped: {n_leading_dropped}")
        print(f"Clean data points remaining: {len(clean_series)}")

    return df, differenced_columns
