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
