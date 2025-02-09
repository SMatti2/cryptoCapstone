import os
import csv
import tempfile
import unittest
from src.utils.llm_utils import initialize_output_file


class TestLLMUtils(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # delete temporary dirs and files
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_initialize_output_file(self):
        test_file = os.path.join(
            self.test_dir, "nested", "directory", "test_output.csv"
        )
        headers = ["column1", "column2", "column3"]

        initialize_output_file(test_file, headers)

        # check if file exists and contains correct headers
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, "r") as f:
            reader = csv.reader(f)
            file_headers = next(reader)
            self.assertEqual(headers, file_headers)

    def test_initialize_output_file_existing(self):
        test_file = os.path.join(self.test_dir, "existing_file.csv")

        # create an existing file
        with open(test_file, "w") as f:
            f.write("existing content")

        headers = ["new_column1", "new_column2"]
        initialize_output_file(test_file, headers)

        # check if we do not overwrite existing file
        with open(test_file, "r") as f:
            content = f.read()
            self.assertEqual(content, "existing content")


if __name__ == "__main__":
    unittest.main()
