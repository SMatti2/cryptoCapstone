import pandas as pd
import pandas_ta as ta
import numpy as np

from config import config


# BUG with pandas_ta MFI (https://github.com/twopirllc/pandas-ta/issues/731)
def calculate_mfi(high, low, close, volume, period):
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume
    mf_sign = np.where(typical_price > np.roll(typical_price, shift=1), 1, -1)

    signed_mf = money_flow * mf_sign

    # Calculate gain and loss using vectorized operations
    positive_mf = np.maximum(signed_mf, 0)
    negative_mf = np.maximum(-signed_mf, 0)

    mf_avg_gain = (
        np.convolve(positive_mf, np.ones(period), mode="full")[: len(positive_mf)]
        / period
    )
    mf_avg_loss = (
        np.convolve(negative_mf, np.ones(period), mode="full")[: len(negative_mf)]
        / period
    )

    epsilon = 1e-10  # Small epsilon value to avoid division by zero
    mfi = 100 - 100 / (1 + mf_avg_gain / (mf_avg_loss + epsilon))
    return mfi


def create_log_price_change(df):
    df["logPriceChange"] = np.log(df["close"] / df["close"].shift(1))
    df["priceMovement"] = (df["logPriceChange"] > 0).astype(int)
    df.dropna(inplace=True)


def create_local_extrema(df, periods: [int], price_column: str):
    for period in periods:
        df[f"localMin_{period}"] = (
            df[price_column] == df[price_column].rolling(period, min_periods=1).min()
        ).astype(int)
        df[f"localMax_{period}"] = (
            df[price_column] == df[price_column].rolling(period, min_periods=1).max()
        ).astype(int)


def create_day_of_week_sin_cos(df):
    # Extract day of the week (Monday=0, Sunday=6)
    day_of_week = df.index.dayofweek

    # Compute sine and cosine transformations
    df["dayOfWeek_Sin"] = np.sin(2 * np.pi * day_of_week / 7)
    df["dayOfWeek_Cos"] = np.cos(2 * np.pi * day_of_week / 7)

    return df


def calculate_technical_indicators(df):
    """
    Calculate technical indicators for cryptocurrency price data using pandas_ta.

    Parameters:
    - df (pd.DataFrame): DataFrame containing 'open', 'high', 'low', 'close', 'volume' columns.

    Returns:
    - pd.DataFrame: DataFrame with added technical indicator columns using pandas_ta.
    """

    # 1. Exponential Moving Averages (EMA)
    df["EMA_12"] = df.ta.ema(close="close", length=12)
    df["EMA_26"] = df.ta.ema(close="close", length=26)

    # 2. Relative Strength Index (RSI)
    df["RSI_14"] = df.ta.rsi(close="close", length=14)

    # 4. Bollinger Bands (BB)
    bb = df.ta.bbands(close="close", length=20, std=2)
    df["BB_Middle"] = bb["BBM_20_2.0"]
    df["BB_Upper"] = bb["BBU_20_2.0"]
    df["BB_Lower"] = bb["BBL_20_2.0"]

    # 5. On-Balance Volume (OBV)
    df["OBV"] = df.ta.obv(close="close", volume="volume")

    df["AO"] = df.ta.ao(high="high", low="low")
    df["KAMA"] = df.ta.kama(close="close")

    ppo = df.ta.ppo(close="close")
    df["PPO"] = ppo["PPO_12_26_9"]
    df["PPO_Signal"] = ppo["PPOs_12_26_9"]
    df["PPO_Histogram"] = ppo["PPOh_12_26_9"]

    pvo = df.ta.pvo(volume="volume")
    df["PVO"] = pvo["PVO_12_26_9"]
    df["PVO_Signal"] = pvo["PVOs_12_26_9"]
    df["PVO_Histogram"] = pvo["PVOh_12_26_9"]

    df["ROC"] = df.ta.roc(close="close")
    df["RSI"] = df.ta.rsi(close="close")

    stoch_rsi = df.ta.stochrsi(close="close")
    df["Stoch_RSI_K"] = stoch_rsi["STOCHRSIk_14_14_3_3"]
    df["Stoch_RSI_D"] = stoch_rsi["STOCHRSId_14_14_3_3"]

    stoch = df.ta.stoch(high="high", low="low", close="close")
    df["Stoch_K"] = stoch["STOCHk_14_3_3"]
    df["Stoch_D"] = stoch["STOCHd_14_3_3"]

    tsi = df.ta.tsi(close="close")
    df["TSI"] = tsi["TSI_13_25_13"]

    df["Ultimate_Oscillator"] = df.ta.uo(high="high", low="low", close="close")
    df["WilliamsR"] = df.ta.willr(high="high", low="low", close="close")
    df["ADI"] = df.ta.ad(high="high", low="low", close="close", volume="volume")

    df["CMF"] = df.ta.cmf(high="high", low="low", close="close", volume="volume")
    df["EMV"] = df.ta.eom(high="high", low="low", volume="volume")
    # Force Index
    df["FI"] = df.ta.efi(close="close", volume="volume")
    # Money Flow Index
    df["MFI"] = calculate_mfi(
        df["high"], df["low"], df["close"], df["volume"], period=14
    )
    # Negative Volume Index
    df["NVI"] = df.ta.nvi(close="close", volume="volume")

    # Volume Price Trend
    df["VPT"] = df.ta.pvol(close="close", volume="volume")

    bb = df.ta.bbands(close="close")
    df["BBM"] = bb["BBM_5_2.0"]
    df["BBW"] = (bb["BBU_5_2.0"] - bb["BBL_5_2.0"]) / bb["BBM_5_2.0"]

    dc = df.ta.donchian(close="close")
    df["DCM"] = dc["DCM_20_20"]
    df["DCW"] = dc["DCU_20_20"] - dc["DCL_20_20"]

    # Keltner Channel (KC)
    kc = df.ta.kc()
    df["KCM"] = kc["KCBe_20_2"]
    df["KCW"] = kc["KCUe_20_2"] - kc["KCLe_20_2"]

    # Ultimate Oscillator (UI)
    df["UI"] = df.ta.uo()

    # Aroon Oscillator
    aroon = df.ta.aroon()
    df["Aroon_down"] = aroon["AROOND_14"]
    df["Aroon_up"] = aroon["AROONU_14"]

    # Commodity Channel Index (CCI)
    df["CCI"] = df.ta.cci()

    # Detrended Price Oscillator (DPO)
    df["DPO"] = df.ta.dpo()

    # Ichimoku Cloud
    ichimoku_df = df.ta.ichimoku(include_leading_span=False)

    df["Ichimoku_A"] = ichimoku_df["ISA_9"]
    df["Ichimoku_B"] = ichimoku_df["ISB_26"]
    df["Ichimoku_Base"] = ichimoku_df["IKS_26"]
    df["Ichimoku_Conversion"] = ichimoku_df["ITS_9"]

    # Know Sure Thing (KST)
    df["KST"] = df.ta.kst()["KST_10_15_20_30_10_10_10_15"]

    # MACD
    macd = df.ta.macd(close="close")
    df["MACD"] = macd["MACD_12_26_9"]
    df["MACD_Signal"] = macd["MACDs_12_26_9"]

    # # Mass Index (MI)
    df["MI"] = df.ta.massi()

    # TRIX
    df["TRIX"] = df.ta.trix(length=30)["TRIX_30_9"]

    # Vortex Indicator (VI)
    vi = df.ta.vortex()
    df["Vortex_down"] = vi["VTXM_14"]
    df["Vortex_up"] = vi["VTXP_14"]

    # Weighted Moving Average (WMA)
    df["WMA"] = df.ta.wma(close="close", length=10)

    # Chande Momentum Oscillator (CR)
    df["CR"] = df.ta.cmo()

    # Parabolic Stop and Reverse (PSAR)
    psar = df.ta.psar()
    df["PSAR_down"] = psar["PSARs_0.02_0.2"].notnull().astype(int)
    df["PSAR_up"] = psar["PSARl_0.02_0.2"].notnull().astype(int)

    return df


def create_variables(df):
    create_log_price_change(df)
    create_local_extrema(df, [7, 14, 21], "close")
    create_day_of_week_sin_cos(df)
    calculate_technical_indicators(df)
    return df


if __name__ == "__main__":
    from config import dtype_dict

    df = pd.read_csv(
        "data/processed/crypto_prices/btc.csv",
        parse_dates=["date"],
        index_col="date",
        dtype=dtype_dict,
    )
    df = create_variables(df)
    df.to_csv(config.DATA_DIR / "processed" / "crypto_prices" / "btc.csv")

    print(df.head(80))
