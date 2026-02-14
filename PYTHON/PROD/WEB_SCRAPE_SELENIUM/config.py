# config.py
from dataclasses import dataclass
from datetime import date
import os
import string

@dataclass
class ScraperConfig:
    base_url: str = "https://hsba.org/HSBA_2020/For_the_Public/Find_a_Lawyer/HSBA_2020/Public/Find_a_Lawyer.aspx"
    output_dir: str = "HSBA_Directories"
    letters: list = tuple(string.ascii_uppercase)
    timeout: int = 60

    @property
    def filename(self) -> str:
        today = date.today().strftime("%Y-%m-%d")
        return f"HSBA_{today}.csv"

    @property
    def output_path(self) -> str:
        return os.path.join(self.output_dir, self.filename)
