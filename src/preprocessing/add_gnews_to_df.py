import json
import pandas as pd
from pathlib import Path


def load_and_process_news_data(json_file_path):
    with open(json_file_path, "r") as f:
        data = json.load(f)

    rows = []
    for date_str, articles_list in data.items():
        for article in articles_list:
            rows.append(
                {
                    "date": date_str,
                    "title": article["title"],
                    "subtitle": article["subtitle"],
                }
            )

    df_news = pd.DataFrame(rows)
    df_news["date"] = pd.to_datetime(df_news["date"])
    df_news["complete_text"] = df_news["title"] + " " + df_news["subtitle"]

    df_news["word_count"] = df_news["complete_text"].apply(lambda x: len(x.split()))

    df_news.sort_values("date", inplace=True)
    df_news.set_index("date", inplace=True)

    return df_news
