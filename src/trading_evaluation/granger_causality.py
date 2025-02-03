import pandas as pd
import numpy as np
import warnings

from statsmodels.tsa.stattools import grangercausalitytests
from config import config


def granger_causality_tests(
    df: pd.DataFrame,
    crypto_symbol: str,
    target: str,
    variables_to_exclude: list[str] = config.EXCLUDE_VARIABLES,
    max_lag: int = 30,
    alpha: float = 0.05,
):
    exclude_vars = set(variables_to_exclude + [target])
    predictors = [col for col in df.columns if col not in exclude_vars]
    results = {}

    print(f"\nGranger Causality Test for {crypto_symbol} '{target}'s")
    print("-" * 50)

    for predictor in predictors:
        data = df[[target, predictor]].dropna()
        if len(data) < max_lag * 2:
            print(f"Skipped {predictor}: insufficient data")
            continue

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)

                test_result = grangercausalitytests(data, maxlag=max_lag, verbose=False)
                p_values = [
                    test_result[lag][0]["ssr_ftest"][1] for lag in range(1, max_lag + 1)
                ]
                min_p = np.min(p_values)
                opt_lag = np.argmin(p_values) + 1

                if min_p < alpha:
                    results[predictor] = {"p_value": min_p, "lag": opt_lag}
                    print(f"✓ {predictor} (lag {opt_lag}, p={min_p:.2e})")
                else:
                    print(f"✗ {predictor} (best p={min_p:.2e})")
        except Exception as e:
            print(f"Error testing {predictor}: {str(e)[:50]}")

    print("\nSignificant Predictors:")
    for pred, res in results.items():
        print(f"{pred}: lag {res['lag']} (p={res['p_value']:.2e})")

    return results
