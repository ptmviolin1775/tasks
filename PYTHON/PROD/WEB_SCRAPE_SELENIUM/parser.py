# parser.py
from bs4 import BeautifulSoup
import re
from typing import Dict

def normalize_address(value: str) -> str:
    return re.sub(r'\n\s*\n', '\n', value)

def break_apart_address(address: str) -> Dict[str, str]:
    lines = address.split("\n")
    address_lines = {f"AddressLine{i}": None for i in range(1, 7)}

    for i, line in enumerate(lines[:6]):
        address_lines[f"AddressLine{i+1}"] = line.strip()

    return address_lines

def parse_profile(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    main_div = soup.find("div", id="ctl01_TemplateBody_WebPartManager1_gwpciDirectoryResults_ciDirectoryResults__Body")
    rows = main_div.find_all("div", class_="ReadOnly PanelField Left")

    data = {}

    for row in rows:
        label = row.find("span", class_="Label").text.strip()
        value = row.find("div", class_="PanelFieldValue").get_text(separator="\n").strip()

        if label == "Address":
            value = normalize_address(value)

        data[label] = value

    if "Address" in data:
        data.update(break_apart_address(data["Address"]))

    return data
