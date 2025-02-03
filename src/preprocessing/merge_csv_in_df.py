import pandas as pd
from datetime import datetime, timedelta


def merge_csv_by_date(
    file_path, df, value_col, date_col="date", is_monthly=False, rows_to_skip=0
):

    df_to_add = pd.read_csv(file_path, skiprows=rows_to_skip)

    if is_monthly:
        df_to_add.columns = ["Month", value_col]
        df_to_add["Month"] = pd.to_datetime(df_to_add["Month"])
        trends_daily = pd.DataFrame()

        for index, row in df_to_add.iterrows():
            month_start = row["Month"]
            month_end = month_start + pd.offsets.MonthEnd(0)
            date_range = pd.date_range(start=month_start, end=month_end, freq="D")
            data = pd.DataFrame({date_col: date_range, value_col: row[value_col]})
            trends_daily = pd.concat([trends_daily, data]).reset_index(drop=True)

        df_to_add = trends_daily
    else:
        # daily data
        df_to_add.columns = [date_col, value_col]
        df_to_add[date_col] = pd.to_datetime(df_to_add[date_col])

    merged_df = pd.merge(df, df_to_add, on=date_col, how="left").set_index(date_col)

    return merged_df
