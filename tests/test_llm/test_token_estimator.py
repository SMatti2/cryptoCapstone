import pytest

from src.llm.token_estimator import estimate_tokens_and_cost


def test_empty_list():
    result = estimate_tokens_and_cost([])
    assert result["total_texts"] == 0, "Should have 0 texts"
    assert result["total_tokens"] == 0, "Should have 0 tokens"
    assert result["estimated_cost"] == 0.0, "Cost should be 0 for no tokens"


def test_single_short_text():
    texts = ["Hello world"]
    result = estimate_tokens_and_cost(texts)
    assert result["total_texts"] == 1
    assert result["total_tokens"] == 2, "Expected 2 tokens for 'Hello world'"
    assert result["estimated_cost"] == 0.0, "Default cost is 0"


def test_multiple_texts_with_custom_cost():
    texts = [
        "Bitcoin surges again",
        "Ethereum hits new all-time high",
        "Is this the beginning of a bull run?",
    ]
    result = estimate_tokens_and_cost(texts, cost_per_million_tokens=5.0)

    assert result["total_texts"] == 3
    assert result["total_tokens"] == 22, "Check total token calculation"


def test_custom_word_in_tokens():
    texts = ["One two three", "Another test line"]
    result = estimate_tokens_and_cost(texts, word_in_tokens=2.0)

    assert result["total_tokens"] == 12, "Check custom word_in_tokens factor"
