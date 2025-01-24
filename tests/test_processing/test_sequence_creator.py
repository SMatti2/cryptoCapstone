import unittest
import pandas as pd
import numpy as np
from src.processing.sequence_creator import create_sequences


class TestCreateSequences(unittest.TestCase):
    def test_create_sequences(self):
        # create sample
        features = pd.DataFrame({"feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        target = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

        seq_length = 3
        X, y = create_sequences(features, target, seq_length)

        # check output shapes
        self.assertEqual(
            X.shape, (len(features) - seq_length, seq_length, features.shape[1])
        )
        self.assertEqual(y.shape, (len(features) - seq_length,))

        # check if the first sequence and label are correct
        self.assertTrue(np.array_equal(X[0], np.array([[1], [2], [3]])))
        self.assertEqual(y[0], 40)

        # check if the last sequence and label are correct
        self.assertTrue(np.array_equal(X[-1], np.array([[7], [8], [9]])))
        self.assertEqual(y[-1], 100)
