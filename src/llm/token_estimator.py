import numpy as np
from typing import List, Dict


def estimate_tokens_and_cost(
    texts: List[str],
    cost_per_million_tokens: float = 0.0,
    word_in_tokens: float = 1.4,
):

    token_counts = []
    for text in texts:
        word_count = len(text.split())
        estimated_tokens = int(word_count * word_in_tokens)
        token_counts.append(estimated_tokens)

    total_tokens = sum(token_counts)

    stats = {
        "total_texts": len(texts),
        "total_tokens": total_tokens,
        "estimated_cost": total_tokens * cost_per_million_tokens / 1_000_000,
    }

    return stats
