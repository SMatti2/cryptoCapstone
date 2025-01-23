import numpy as np
from statsmodels.tsa.stattools import adfuller


def adf_test(series, alpha):
    """Augmented Dickey-Fuller test"""
    adf_result = adfuller(series, autolag="AIC")
    p_value = adf_result[1]
    return {
        "Test Statistic": adf_result[0],
        "p-value": p_value,
        "Stationary": p_value < alpha,
    }
