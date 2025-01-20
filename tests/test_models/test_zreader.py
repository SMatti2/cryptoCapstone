import unittest, os, json, tempfile
import zstandard as zstd
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO

from src.models.zreader import Zreader


class TestZreader(unittest.TestCase):

    def setUp(self):
        # We'll just use a placeholder path that won't be actually opened
        # because we'll be mocking os.path.getsize & reading methods
        self.mock_file_path = "fake.zst"

    @patch("os.path.getsize", return_value=12345)
    @patch("builtins.open", new_callable=mock_open)
    def test_file_overview(self, mock_open_file, mock_getsize):
        # We'll mock the readlines method to return a known set of lines
        z = Zreader(self.mock_file_path)

        with patch.object(z, "readlines", return_value=["{}", "{}", ""]):
            overview = z.file_overview()
            self.assertEqual(overview["file_size_bytes"], 12345)
            self.assertEqual(overview["json_items_count"], 2)  # 2 non-empty lines
        z.close()

    @patch("builtins.open", new_callable=mock_open)
    def test_reset_reader(self, mock_open_file):
        z = Zreader(self.mock_file_path)
        z.reader = MagicMock()
        z.reader.read.side_effect = [b"line1\nlin", b"e2\n", b""]
        lines = list(z.readlines())  # ["line1", "line2"]
        self.assertEqual(lines, ["line1", "line2"])
        z.reset_reader()
        self.assertEqual(z.buffer, "")
        z.close()

    @patch("builtins.open", new_callable=mock_open)
    def test_print_header_success(self, mock_open_file):
        z = Zreader(self.mock_file_path)
        with patch.object(z, "readlines", return_value=iter(['{"hello":"world"}'])):
            header = z.print_header()
            self.assertEqual(header, {"hello": "world"})
        z.close()

    @patch("builtins.open", new_callable=mock_open)
    def test_print_header_invalid_json(self, mock_open_file):
        z = Zreader(self.mock_file_path)
        with patch.object(z, "readlines", return_value=iter(["{not_valid_json}"])):

            header = z.print_header()
            self.assertIsNone(header)
        z.close()

    @patch("builtins.open", new_callable=mock_open)
    def test_readlines_multi_chunks(self, mock_open_file):
        z = Zreader(self.mock_file_path)
        z.reader = MagicMock()
        z.reader.read.side_effect = [
            b'{"val":1}\n{"val":2}',  # first chunk
            b"\n",  # second chunk
            b'{"val":3}\n{"val":4}\n{"val":5}',  # third chunk
            b"",  # end
        ]
        lines = list(z.readlines())
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0], '{"val":1}')
        self.assertEqual(lines[-1], '{"val":5}')
        z.close()


if __name__ == "__main__":
    unittest.main()
