# scraper.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import time

from parser import parse_profile


class HSBAScraper:

    def __init__(self, driver, config, writer):
        self.driver = driver
        self.config = config
        self.writer = writer
        self.logger = logging.getLogger(__name__)
        self.internal_id = 1

    def run(self):
        self.driver.get(self.config.base_url)

        for letter in self.config.letters:
            self.logger.info(f"Processing letter {letter}")
            records = self._scrape_letter(letter)
            self.writer.write(records)

        self.driver.quit()

    def _scrape_letter(self, letter):
        self._search_letter(letter)
        urls = self._extract_profile_links()

        records = []
        for url in urls:
            record = self._scrape_profile(url, letter)
            records.append(record)

        return records

    def _search_letter(self, letter):
        wait = WebDriverWait(self.driver, self.config.timeout)

        wait.until(EC.presence_of_element_located((By.ID, "txtDirectorySearchLastName"))).clear()
        wait.until(EC.presence_of_element_located((By.ID, "txtDirectorySearchLastName"))).send_keys(letter)
        wait.until(EC.presence_of_element_located((By.ID, "btnDirectorySearch"))).click()

        wait.until(EC.presence_of_element_located(
            (By.ID, "ctl01_TemplateBody_WebPartManager1_gwpciNewQueryMenuCommon_ciNewQueryMenuCommon_ResultsGrid_Grid1_ctl00")
        ))

    def _extract_profile_links(self):
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        table = soup.find("table", id="ctl01_TemplateBody_WebPartManager1_gwpciNewQueryMenuCommon_ciNewQueryMenuCommon_ResultsGrid_Grid1_ctl00")
        rows = table.find_all("tr")[1:]

        links = []
        for row in rows:
            tag = row.find("a")
            if tag:
                links.append("https://hsba.org" + tag["href"])

        return links

    def _scrape_profile(self, url, letter):
        self.driver.get(url)

        WebDriverWait(self.driver, self.config.timeout).until(
            EC.presence_of_element_located(
                (By.ID, "ctl01_TemplateBody_WebPartManager1_gwpciDirectoryResults_ciDirectoryResults__Body")
            )
        )

        data = parse_profile(self.driver.page_source)

        data["HSBA ID"] = url.split("ID=")[-1]
        data["Internal ID"] = str(self.internal_id)
        data["Letter"] = letter

        self.internal_id += 1
        return data
