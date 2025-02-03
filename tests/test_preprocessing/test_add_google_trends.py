import os
import pandas as pd
import pytest
from datetime import datetime

from src.preprocessing.add_google_trends import insert_google_trends_data_in_df


def test_insert_google_trends_data_in_df():
    dates = pd.date_range(start="2023-01-01", end="2023-01-31", freq="D")
    # mock data
    df = pd.DataFrame({"date": dates, "value": range(len(dates))})
    # so we can insert a "useless row" before the actual header.
    csv_content = """This is a useless row that we want to skip
Month,gTrendsBitcoin
2023-01-01,100
"""

    # savea temporary CSV file
    temp_file_path = os.path.join(os.getcwd(), "temp_google_trends.csv")
    with open(temp_file_path, "w") as f:
        f.write(csv_content)

    result_df = insert_google_trends_data_in_df(
        temp_file_path, df, "gTrendsBitcoin", is_monthly=True, rows_to_skip=1
    )

    assert "gTrendsBitcoin" in result_df.columns
    assert result_df["gTrendsBitcoin"].iloc[0] == 100
    assert result_df["gTrendsBitcoin"].iloc[30] == 100
    assert result_df.index.name == "date"

    # remove temporary file
    os.remove(temp_file_path)
