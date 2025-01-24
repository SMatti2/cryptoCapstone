import numpy as np


def create_sequences(features, target, seq_length=30):
    X, y = [], []
    for i in range(len(features) - seq_length):

        seq = features.iloc[i : i + seq_length]
        label = target.iloc[i + seq_length]
        X.append(seq.values)
        y.append(label)

    return np.array(X), np.array(y)
