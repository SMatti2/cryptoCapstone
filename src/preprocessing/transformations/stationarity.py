import pandas as pd

import warnings
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tools.sm_exceptions import InterpolationWarning
from arch.unitroot import PhillipsPerron


def adf_test(series, alpha):
    """Augmented Dickey-Fuller test"""
    adf_result = adfuller(series, autolag="AIC")
    p_value = adf_result[1]
    return {
        "Test Statistic": adf_result[0],
        "p-value": p_value,
        "Stationary": p_value < alpha,
    }


def pp_test(series, alpha):
    """Phillips-Perron test"""
    pp_result = PhillipsPerron(series)
    p_value = pp_result.pvalue
    return {
        "Test Statistic": pp_result.stat,
        "p-value": p_value,
        "Stationary": p_value < alpha,
    }


def kpss_test(series, alpha):
    """KPSS test"""
    kpss_stat = kpss(series, regression="c", nlags="auto")
    p_value = kpss_stat[1]
    return {
        "Test Statistic": kpss_stat,
        "p-value": p_value,
        "Stationary": p_value >= alpha,
    }
