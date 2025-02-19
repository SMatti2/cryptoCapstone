# Deep Learning & Sentiment-Driven Trading Price Predictor

This repository contains a capstone project focused on forecasting cryptocurrency prices using deep learning techniques. The project explores various modeling approaches to predict the daily log price change of major cryptocurrencies—Bitcoin (BTC) and Ethereum (ETH)—by integrating traditional price data with external features such as technical indicators, market metrics, and sentiment signals from news and social media

## Table of Contents

- [Project Overview](#project-overview)
- [Installation](#installation)
- [Project Structure](#project-structure)

## Project Overview

This repository demonstrates different approaches to forecasting daily logarithmic price changes of cryptocurrencies. Three main models were developed:

1. **HLOC-only Model**: Uses daily High, Low, Open, and Close (HLOC) values, alongside standard technical indicators (e.g., moving averages, momentum indicators)

2. **Multi-source Model (News & Trends)**: Extends the HLOC model by adding Google Trends data (keywords like “bitcoin,” “blockchain,” “cryptocurrency,” “ethereum,” “investing”), gold prices, US inflation data, S&P 500 values, and sentiment scores derived from Google News headlines and subtitles.

3. **Multi-source Model (News, Trends & Reddit)**: Further includes Reddit-based features (daily posts, comments, authors, average post scores, and average sentiment of the top five posts). However, this dataset had a two-month gap between July and August 2022, which might have weakened the model’s performance due to missing or incomplete data.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/smatti2/cryptoCapstone/
cd cryptoCapstone
```

2. (Optional) Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```
