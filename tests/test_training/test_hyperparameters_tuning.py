import unittest
import numpy as np
from src.training.hyperparameters_tuning import objective, tune_hyperparameters
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam


# mock train_lstm
def mock_train_lstm(X_train, y_train, X_val, y_val, params):
    model = Sequential()
    model.add(Input(shape=(X_train.shape[1], X_train.shape[2])))

    # LSTM layers
    for i, units in enumerate(params["lstm_units"]):
        return_sequences = i < len(params["lstm_units"]) - 1
        model.add(LSTM(units, return_sequences=return_sequences))
        model.add(Dropout(params["dropout_rate"]))

    # Dense layers
    for units in params["dense_units"]:
        model.add(Dense(units, activation="relu"))
        model.add(Dropout(params["dropout_rate"]))

    # Output layer
    model.add(Dense(1, activation="linear"))

    # compile
    model.compile(
        optimizer=Adam(learning_rate=params["learning_rate"]),
        loss="mean_squared_error",
        metrics=["mae"],
    )

    # mock training history
    history = {
        "val_loss": [0.5, 0.4, 0.3, 0.2, 0.1],
    }

    return model, history


# mock Optuna trial class
class MockTrial:
    def __init__(self, trial_params):
        self.trial_params = trial_params

    def suggest_int(self, name, low, high, step=None):
        return self.trial_params[name]

    def suggest_float(self, name, low, high, step=None, log=False):
        return self.trial_params[name]

    def suggest_categorical(self, name, choices):
        return self.trial_params[name]


class TestHyperparameterTuning(unittest.TestCase):
    def setUp(self):
        # dummy data for testing
        self.X_train = np.random.rand(100, 10, 5)
        self.y_train = np.random.rand(100, 1)
        self.X_val = np.random.rand(20, 10, 5)
        self.y_val = np.random.rand(20, 1)

    def test_objective_function(self):
        trial_params = {
            "num_lstm_layers": 3,
            "lstm_units_1": 64,
            "lstm_units_2": 128,
            "lstm_units_3": 256,
            "num_dense_layers": 1,
            "dense_units_1": 64,
            "dense_units_2": 128,
            "dense_units_3": 256,
            "dropout_rate": 0.2,
            "learning_rate": 0.001,
            "batch_size": 32,
        }

        mock_trial = MockTrial(trial_params)
        val_loss = objective(
            mock_trial,
            self.X_train,
            self.y_train,
            self.X_val,
            self.y_val,
            mock_train_lstm,
        )

        # assert val loss is returned
        self.assertIsInstance(val_loss, float)
        self.assertGreaterEqual(val_loss, 0.0)

    def test_tune_hyperparameters(self):
        # test the tune_hyperparameters function
        study = tune_hyperparameters(
            self.X_train,
            self.y_train,
            self.X_val,
            self.y_val,
            mock_train_lstm,
            n_trials=5,
        )

        # assert the study object is returned
        self.assertIsNotNone(study)
        self.assertTrue(hasattr(study, "best_trial"))
        self.assertTrue(hasattr(study.best_trial, "value"))
        self.assertTrue(hasattr(study.best_trial, "params"))


if __name__ == "__main__":
    unittest.main()
