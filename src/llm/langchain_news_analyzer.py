import os, csv
import pandas as pd
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from datetime import datetime
from config import config


class CryptoNewsSentimentAnalyzer:
    def __init__(self, verbose=False, output_file_path=None):
        self.verbose = verbose
        self.output_file_path = (
            output_file_path or config.DATA_DIR / "temp" / "output.csv"
        )
        self.chain = self._create_chain()
        self._initialize_output_file()

    def _initialize_output_file(self):
        if not os.path.exists(self.output_file_path):
            with open(self.output_file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "title", "subtitle", "score"])

    def _create_chain(self):
        prompt = ChatPromptTemplate.from_template(
            """
            You are a financial news sentiment analyst with expertise in cryptocurrency. You will receive an article with two parts: a "title" and a "subtitle". Your task is to analyze the article and decide if it is directly relevant to cryptocurrency financial news.

            For each article, do the following:
            1. If the article does not discuss topics that directly impact cryptocurrency investments (for example, unrelated general news or non-financial subjects), output exactly: 0
            2. If the article is relevant, output a sentiment score as a number between 1 and 10, where:
                - 10 means the article is extremely bullish for crypto investments,
                - 1 means the article is extremely bearish for crypto investments.

            Respond with ONLY a single number (the sentiment score or 0) and nothing else.

            Example:
            Title: "Bitcoin ETF approval could spark institutional buying"
            Subtitle: "Experts predict a significant bullish trend in crypto markets."
            Output: 10

            Remember: Analyze only the direct financial implications for crypto markets. Do not include any additional text in your response.

            Title: {title}
            Subtitle: {subtitle}
            Analysis:
            """
        )

        llm = ChatOpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=config.DEEPSEEK_API_KEY,
            model="deepseek-chat",
            temperature=0.4,
            max_tokens=5,
        )

        return prompt | llm | StrOutputParser()

    def classify_article(self, title: str, subtitle: str) -> float:
        try:
            response = self.chain.invoke({"title": title, "subtitle": subtitle}).strip()
            if response == "0":
                return np.nan
            return float(response) if 1 <= float(response) <= 10 else np.nan
        except Exception as e:
            if self.verbose:
                print(f"Classification error: {e}")
            return np.nan

    def analyze_articles_in_range(
        self, df: pd.DataFrame, start_date: str, end_date: str
    ):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        date_filter = (df["date"] >= datetime.strptime(start_date, "%Y-%m-%d")) & (
            df["date"] <= datetime.strptime(end_date, "%Y-%m-%d")
        )
        filtered_df = df[date_filter]

        if filtered_df.empty:
            print("No articles in date range") if self.verbose else None
            return pd.DataFrame(columns=["date", "average_score"])

        results = []
        with self.output_file_path.open("a") as f:
            writer = csv.writer(f)

            for idx, row in filtered_df.iterrows():
                score = self.classify_article(row["title"], row["subtitle"])
                writer.writerow(
                    [
                        row["date"].strftime("%Y-%m-%d"),
                        row["title"],
                        row["subtitle"],
                        score,
                    ]
                )

                if self.verbose:
                    print(
                        f"Processed article {idx} | Date: {row['date'].date()} | Score: {score} | Title: {row['title']}"
                    )

                results.append({"date": row["date"], "score": score})

        return self._aggregate_results(pd.DataFrame(results))

    def _aggregate_results(self, results_df: pd.DataFrame) -> pd.DataFrame:
        if results_df.empty:
            return pd.DataFrame(columns=["date", "average_score"])

        results_df["date"] = pd.to_datetime(results_df["date"])
        grouped = (
            results_df.groupby(pd.Grouper(key="date", freq="D"))
            .agg(
                average_score=("score", "mean"),
                article_count=("score", "size"),
                valid_scores=("score", "count"),
            )
            .reset_index()
        )

        if self.verbose:
            for _, row in grouped.iterrows():
                print(f"Date: {row['date'].date()}")
                print(
                    f"  Articles: {row['article_count']} | Valid: {row['valid_scores']}"
                )
                print(f"  Average: {row['average_score']:.2f}\n")

        return grouped[["date", "average_score"]]
