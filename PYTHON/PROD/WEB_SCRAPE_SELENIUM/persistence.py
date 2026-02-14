# persistence.py
import csv
import os
from typing import List, Dict

class CSVWriter:

    def __init__(self, filepath: str):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def write(self, records: List[Dict]):
        if not records:
            return

        file_exists = os.path.exists(self.filepath)

        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(records)
