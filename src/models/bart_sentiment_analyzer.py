import numpy as np
import pandas as pd
import csv, time, torch

from typing import List, Optional
from datetime import datetime
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch.nn.functional import softmax

from src.utils.llm_utils import initialize_output_file, limit_words


class UniversalSentimentAnalyzer:
    def __init__(
        self,
        text_columns: List[str],
        hypotheses: List[str],
        date_column: str = "date",
        device: str = "cpu",
        threshold: float = 0.25,
        batch_size: int = 8,
        verbose: bool = False,
        output_path: Optional[str] = None,
        output_columns: Optional[List[str]] = None,
        max_words: int = 200,
    ):
        self.text_columns = text_columns
        self.hypotheses = hypotheses
        self.date_column = date_column
        self.device = device
        self.threshold = threshold
        self.batch_size = batch_size
        self.verbose = verbose
        self.output_path = output_path
        self.output_columns = output_columns or ["date", "score"]
        self.max_words = max_words

        # init model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "facebook/bart-large-mnli"
        )
        self.model.to(self.device).eval()

        if self.output_path:
            initialize_output_file(self.output_path, self.output_columns)

    def _prepare_texts(self, df: pd.DataFrame) -> List[str]:
        combined_series = df[self.text_columns].apply(
            lambda row: ". ".join(str(cell) for cell in row if pd.notna(cell)),
            axis=1,
        )
        return combined_series.apply(lambda x: limit_words(x, self.max_words)).tolist()

    def _batch_classify(self, texts: List[str]) -> np.ndarray:
        pairs = [[text, hypothesis] for text in texts for hypothesis in self.hypotheses]

        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            logits = self.model(**inputs).logits
            logits = logits.view(len(texts), len(self.hypotheses), -1)
            return softmax(logits[..., [0, 2]], dim=-1)[..., 1].cpu().numpy()

    def _calculate_scores(
        self, bull_probs: np.ndarray, bear_probs: np.ndarray
    ) -> np.ndarray:

        relevant_mask = np.maximum(bull_probs, bear_probs) > self.threshold
        net_sentiment = np.where(relevant_mask, bull_probs - bear_probs, 0.0)
        scaled_scores = (net_sentiment + 1) * 4.5 + 1
        return np.clip(np.where(relevant_mask, scaled_scores, np.nan), 1, 10).round(1)

    def analyze(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        df[self.date_column] = pd.to_datetime(df[self.date_column], errors="coerce")
        date_mask = (df[self.date_column] >= start_dt) & (
            df[self.date_column] <= end_dt
        )
        filtered_df = df[date_mask].sort_values(self.date_column)

        if filtered_df.empty:
            if self.verbose:
                print(f"No data found between {start_date} and {end_date}")
            return pd.DataFrame(columns=[self.date_column, "score"])

        # Get unique dates for progress tracking
        unique_dates = filtered_df[self.date_column].dt.date.unique()
        if self.verbose:
            print(
                f"Found {len(unique_dates)} days to process between {start_date} and {end_date}"
            )

        texts = self._prepare_texts(filtered_df)
        scores = np.full(len(texts), np.nan)
        current_month = None

        for batch_idx in range(0, len(texts), self.batch_size):
            batch_start = batch_idx
            batch_end = batch_idx + self.batch_size
            batch_texts = texts[batch_start:batch_end]

            batch_dates = filtered_df.iloc[batch_start:batch_end][self.date_column]
            min_date = batch_dates.min().date()
            max_date = batch_dates.max().date()
            # sleep for 1 minute every month
            if current_month is not None and min_date.month != current_month:
                if self.verbose:
                    print(f"Month changed. Waiting for 1 minute before proceeding...")
                time.sleep(10)

            current_month = min_date.month

            if self.verbose:
                print(
                    f"Processing batch {batch_idx//self.batch_size + 1}: "
                    f"Dates {min_date} to {max_date} "
                    f"({len(batch_texts)} entries)"
                )

            # inference
            probs = self._batch_classify(batch_texts)
            batch_scores = self._calculate_scores(probs[:, 0], probs[:, 1])
            scores[batch_start:batch_end] = batch_scores

            if self.output_path:
                self._save_batch_results(
                    filtered_df.iloc[batch_start:batch_end], batch_scores
                )

        filtered_df["score"] = scores
        return filtered_df

    def _save_batch_results(self, batch_df: pd.DataFrame, scores: np.ndarray):
        batch_df.loc[:, "score"] = scores.astype(float)

        with open(self.output_path, "a", newline="") as f:
            batch_df[self.output_columns].to_csv(
                f, header=False, index=False, float_format="%.1f", mode="a"
            )
