import unittest
import numpy as np
from src.training.hyperparameters_tuning import objective, tune_hyperparameters


# mock train_lstm function
def mock_train_lstm(X_train, y_train, X_val, y_val, params):
    history = type(
        "obj", (object,), {"history": {"val_loss": [0.5, 0.4, 0.3, 0.2, 0.1]}}
    )
    return None, history


# mock trial class
class MockTrial:
    def __init__(self, trial_params):
        self.trial_params = trial_params

    def suggest_int(self, name, low, high, step=None):
        return self.trial_params.get(name, low)

    def suggest_float(self, name, low, high, step=None, log=False):
        return self.trial_params.get(name, low)

    def suggest_categorical(self, name, choices):
        return self.trial_params.get(name, choices[0])


class TestHyperparameterTuning(unittest.TestCase):
    def setUp(self):
        self.X_train = np.random.rand(100, 10, 5)
        self.y_train = np.random.rand(100, 1)
        self.X_val = np.random.rand(20, 10, 5)
        self.y_val = np.random.rand(20, 1)

    def test_objective_function(self):
        trial_params = {
            "num_lstm_layers": 2,
            "lstm_units_1": 64,
            "num_dense_layers": 1,
            "dense_units_1": 64,
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

        self.assertIsInstance(val_loss, float)
        self.assertGreaterEqual(val_loss, 0.0)

    def test_tune_hyperparameters(self):
        study = tune_hyperparameters(
            self.X_train,
            self.y_train,
            self.X_val,
            self.y_val,
            mock_train_lstm,
            n_trials=2,
        )

        self.assertIsNotNone(study)
        self.assertTrue(hasattr(study, "best_trial"))
        self.assertTrue(hasattr(study.best_trial, "value"))
        self.assertTrue(hasattr(study.best_trial, "params"))
