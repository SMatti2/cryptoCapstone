import pandas as pd

from sklearn.preprocessing import StandardScaler


def scale_features(X_train, X_val, X_test):
    scaler = StandardScaler()

    return (
        pd.DataFrame(scaler.fit_transform(X_train), X_train.index, X_train.columns),
        pd.DataFrame(scaler.transform(X_val), X_val.index, X_val.columns),
        pd.DataFrame(scaler.transform(X_test), X_test.index, X_test.columns),
        scaler,
    )
