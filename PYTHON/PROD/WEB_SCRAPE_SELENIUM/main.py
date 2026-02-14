# main.py
import logging
from config import ScraperConfig
from browser import create_driver
from persistence import CSVWriter
from scraper import HSBAScraper


def main():
    logging.basicConfig(level=logging.INFO)

    config = ScraperConfig()
    driver = create_driver()
    writer = CSVWriter(config.output_path)

    scraper = HSBAScraper(driver, config, writer)
    scraper.run()


if __name__ == "__main__":
    main()
