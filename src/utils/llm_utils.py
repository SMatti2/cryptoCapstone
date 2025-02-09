import os
import csv


def initialize_output_file(output_file_path, headers):
    if not os.path.exists(output_file_path):
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
