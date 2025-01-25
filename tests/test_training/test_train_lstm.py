import unittest
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input

from src.training.lstm_training import train_lstm


class TestLSTMTraining(unittest.TestCase):
    def setUp(self):
        # create dummy data
        self.X_train = np.random.rand(
            100, 10, 5
        )  # 100 samples, 10 timesteps, 5 features
        self.y_train = np.random.rand(100, 1)
        self.X_val = np.random.rand(20, 10, 5)
        self.y_val = np.random.rand(20, 1)

        self.params = {
            "num_lstm_layers": 2,
            "lstm_units": [64, 32],
            "dropout_rates": [0.2, 0.3],
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10,
            "clipvalue": 0.5,
        }

    def test_model_architecture(self):
        model, _ = train_lstm(
            self.X_train, self.y_train, self.X_val, self.y_val, self.params
        )

        # check the number of LSTM layers
        lstm_layers = [layer for layer in model.layers if isinstance(layer, LSTM)]
        self.assertEqual(len(lstm_layers), self.params["num_lstm_layers"])

        # check the number of units
        for i, layer in enumerate(lstm_layers):
            self.assertEqual(layer.units, self.params["lstm_units"][i])

        # check number of Dropout layers
        dropout_layers = [layer for layer in model.layers if isinstance(layer, Dropout)]
        self.assertEqual(len(dropout_layers), self.params["num_lstm_layers"])

        # check if the output layer is a Dense layer
        self.assertIsInstance(model.layers[-1], Dense)
        self.assertEqual(model.layers[-1].units, 1)

    def test_training_process(self):
        model, history = train_lstm(
            self.X_train, self.y_train, self.X_val, self.y_val, self.params
        )

        # check if the model was trained for the correct number of epochs
        self.assertEqual(len(history.history["loss"]), self.params["epochs"])

        # check if the model returns a history object with the expected keys
        self.assertIn("loss", history.history)
        self.assertIn("val_loss", history.history)

    def test_output_shape(self):
        model, _ = train_lstm(
            self.X_train, self.y_train, self.X_val, self.y_val, self.params
        )
        output = model.predict(self.X_train[:1])

        # check if the model's output shape matches the expected shape
        self.assertEqual(output.shape, (1, 1))  # Batch size of 1, output of 1 value


if __name__ == "__main__":
    unittest.main()
