import os
import csv
import numpy as np
import pandas as pd
import torch

from typing import List, Dict
from torch.nn.functional import softmax
from datetime import datetime
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.utils.llm_utils import (
    initialize_output_file,
    append_news_scores_to_csv,
    add_daily_aggregates,
)
from config import config


class CryptoNewsAnalyzer:
    def __init__(
        self,
        device: str = "cpu",
        threshold: float = 0.25,
        batch_size: int = 8,
        verbose: bool = False,
        output_file_path: str = None,
    ):
        self.device = device
        self.threshold = threshold
        self.batch_size = batch_size
        self.verbose = verbose
        self.output_file_path = output_file_path

        # init model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "facebook/bart-large-mnli"
        )
        self.model.to(self.device).eval()

        # hypotheses
        self.hypotheses = [
            "This example is bullish for cryptocurrency prices.",
            "This example is bearish for cryptocurrency prices.",
        ]

        if self.output_file_path:
            initialize_output_file(
                self.output_file_path, ["date", "title", "subtitle", "score"]
            )

    def _prepare_texts(self, titles: List[str], subtitles: List[str]):
        return [
            f"{title}. {subtitle}".strip() for title, subtitle in zip(titles, subtitles)
        ]

    def _batch_classify(self, articles_batch: List[str]):
        # create premise-hypothesis pairs
        pairs = [
            [text, hypothesis]
            for text in articles_batch
            for hypothesis in self.hypotheses
        ]

        # tokenize
        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(self.device)
        # inference
        with torch.no_grad():
            logits = self.model(**inputs).logits
            # reshape into (batch_size, #hypotheses, 3)
            # 3 is [contradiction/bearish, neutral, entailment/bullish]
            logits = logits.view(len(articles_batch), len(self.hypotheses), -1)
            # we convert contradiction and entailment to probabilities that sum to 1
            probs = softmax(logits[..., [0, 2]], dim=-1)[..., 1]

            return probs.cpu().numpy()

    def _calculate_scores(self, bull_probs: np.ndarray, bear_probs: np.ndarray):
        relevant_mask = np.maximum(bull_probs, bear_probs) > self.threshold
        net_sentiment = bull_probs - bear_probs
        net_sentiment = np.where(relevant_mask, net_sentiment, 0.0)
        scaled_scores = (net_sentiment + 1) * 4.5 + 1

        # set 0 values to nan
        scaled_scores = np.where(relevant_mask, scaled_scores, np.nan)

        # make sure scores are between 1 and 10
        return np.clip(scaled_scores, 1, 10).round(1)

    def analyze_articles(self, df: pd.DataFrame, start_date: str, end_date: str):
        """
        analyze news articles within a specified date range and calculate sentiment scores. it returns a df and creates a csv file
        """
        # filter data by date
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        date_mask = (df["date"] >= start_dt) & (df["date"] <= end_dt)
        data_df = df[date_mask].copy()

        if data_df.empty:
            if self.verbose:
                print(f"No articles found between {start_dt} and {end_dt}.")
            return pd.DataFrame(
                columns=["date", "average_score", "article_count", "relevant_articles"]
            )
        if self.verbose:
            print(
                f"Processing {len(data_df)} articles from {start_date} to {end_date} in batches of {self.batch_size}."
            )
        if self.output_file_path:
            initialize_output_file(
                self.output_file_path, ["date", "title", "subtitle", "score"]
            )

        titles = data_df["title"].tolist()
        subtitles = data_df["subtitle"].tolist()
        texts = self._prepare_texts(titles, subtitles)

        # we'll store final scores in an array so we can add them to data_df
        final_scores = np.empty(len(texts))
        final_scores.fill(np.nan)

        # process batches and append each set to the csv
        for start_idx in range(0, len(texts), self.batch_size):
            end_idx = start_idx + self.batch_size
            batch_texts = texts[start_idx:end_idx]

            # analyze this batch
            ent_probs = self._batch_classify(batch_texts)
            bull_probs = ent_probs[:, 0]
            bear_probs = ent_probs[:, 1]

            # convert probabilities to scores
            scores = self._calculate_scores(bull_probs, bear_probs)

            final_scores[start_idx:end_idx] = scores

            # use the same indexes so we are aligned with original df
            sub_df = data_df.iloc[start_idx:end_idx].copy()
            sub_df["score"] = scores

            if self.output_file_path:
                append_news_scores_to_csv(
                    self.output_file_path,
                    sub_df[["date", "title", "subtitle", "score"]],
                )

            if self.verbose:
                print(f"Processed batch {start_idx} to {end_idx} and appended to CSV.")

        data_df["score"] = final_scores

        return add_daily_aggregates(data_df)
