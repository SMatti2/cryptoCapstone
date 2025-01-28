import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping


def train_lstm(X_train, y_train, X_val, y_val, params):

    lstm_units = params["lstm_units"]
    dense_units = params.get("dense_units", [])
    dropout_rate = params.get("dropout_rate", 0.2)

    model = Sequential()
    model.add(Input(shape=(X_train.shape[1], X_train.shape[2])))

    for i, units in enumerate(lstm_units):
        return_sequences = i < len(lstm_units) - 1
        model.add(LSTM(units, return_sequences=return_sequences))
        model.add(Dropout(dropout_rate))

    for units in dense_units:
        model.add(Dense(units, activation="relu"))
        model.add(Dropout(dropout_rate))

    model.add(Dense(1, activation="linear"))

    model.compile(
        optimizer=Adam(learning_rate=params.get("learning_rate", 0.001)),
        loss="mean_squared_error",
        metrics=["mae"],
    )

    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=params.get("epochs", 100),
        batch_size=params.get("batch_size", 32),
        callbacks=[EarlyStopping(patience=10, restore_best_weights=True)],
        shuffle=False,
        verbose=1,
    )

    return model, history
