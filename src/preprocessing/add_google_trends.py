import pandas as pd
from datetime import datetime, timedelta


def insert_google_trends_data_in_df(file_path, df, value_col, date_col="date"):

    monthly_data = pd.read_csv(file_path, skiprows=1)
    monthly_data.columns = ["Month", value_col]
    monthly_data["Month"] = pd.to_datetime(monthly_data["Month"])

    trends_daily = pd.DataFrame()

    for index, row in monthly_data.iterrows():
        month_start = row["Month"]
        month_end = month_start + pd.offsets.MonthEnd(0)
        date_range = pd.date_range(start=month_start, end=month_end, freq="D")

        data = pd.DataFrame({date_col: date_range, value_col: row[value_col]})
        trends_daily = pd.concat([trends_daily, data]).reset_index(drop=True)
    # Debug: Print DataFrames before merging
    print("DF DataFrame:\n", df.head())
    print("Trends Daily DataFrame:\n", trends_daily.head())
    merged_df = pd.merge(df, trends_daily, on=date_col, how="left").set_index(date_col)

    return merged_df
