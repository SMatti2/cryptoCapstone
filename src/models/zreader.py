import os
import json
import zstandard as zstd


class Zreader:
    def __init__(self, file_path, chunk_size=16384):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.fh = open(file_path, "rb")  # file handle
        self.dctx = zstd.ZstdDecompressor()
        self.reader = self.dctx.stream_reader(self.fh)
        self.buffer = ""

    def readlines(self):
        while True:
            chunk = self.reader.read(self.chunk_size)
            if not chunk:
                break
            text = chunk.decode("utf-8", errors="ignore")
            lines = (self.buffer + text).split("\n")
            for line in lines[:-1]:
                yield line
            self.buffer = lines[-1]

        # After no more chunks, if there's leftover text in buffer, yield it:
        if self.buffer:
            yield self.buffer
            self.buffer = ""

    def file_overview(self):
        """
        Returns a dictionary with the file size in bytes and the count of JSON lines.
        (Resets the reader afterwards.)
        """
        file_size = os.path.getsize(self.file_path)
        count = sum(1 for line in self.readlines() if line.strip())
        self.reset_reader()
        return {"file_size_bytes": file_size, "json_items_count": count}

    def print_header(self):
        """
        Prints and returns the first JSON object in the file.
        Resets the reader after reading the first line.
        """
        header_line = next(self.readlines(), None)
        if header_line:
            try:
                header_dict = json.loads(header_line)
                print("Header (parsed):", header_dict)
                self.reset_reader()
                return header_dict
            except json.JSONDecodeError as e:
                print("Failed to decode JSON. Error:", e)
                print("Invalid JSON content:", header_line)
        else:
            print("No data to read.")
        self.reset_reader()
        return None

    def reset_reader(self):
        """
        Resets the file handle and the decompression stream back to start.
        """
        self.fh.seek(0)
        self.reader = self.dctx.stream_reader(self.fh)
        self.buffer = ""

    def close(self):
        """
        Closes the underlying file handle. No further reading possible afterward.
        """
        self.fh.close()
