import mysql.connector
import os
from datetime import datetime
import pytz
from contextlib import contextmanager

class MySQLRepository:

    def __init__(self):
        self.config = {
            "host": os.environ["host"],
            "user": os.environ["user"],
            "password": os.environ["password"],
            "database": os.environ["database"],
        }

    @contextmanager
    def connection(self):
        conn = mysql.connector.connect(**self.config)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def insert_attorney(self, attorney: dict):
        with self.connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now(pytz.timezone("Pacific/Honolulu"))

            sql = """INSERT INTO `HSBA 1-27-2023`
                     (Name, `JD Number`, `License Type`, Employer,
                      Address, AddressLine1, AddressLine2, AddressLine3,
                      AddressLine4, AddressLine5, AddressLine6,
                      Country, Phone, Fax, Email,
                      `Law School`, Graduated, `Admitted HI Bar`,
                      `HSBA ID`, `Internal ID`, Letter, ScrapedTimestamp)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            cursor.execute(sql, (
                attorney.get("Name"),
                attorney.get("JD Number"),
                attorney.get("License Type"),
                attorney.get("Employer"),
                attorney.get("Address"),
                attorney.get("AddressLine1"),
                attorney.get("AddressLine2"),
                attorney.get("AddressLine3"),
                attorney.get("AddressLine4"),
                attorney.get("AddressLine5"),
                attorney.get("AddressLine6"),
                attorney.get("Country"),
                attorney.get("Phone"),
                attorney.get("Fax"),
                attorney.get("Email"),
                attorney.get("Law School"),
                attorney.get("Graduated"),
                attorney.get("Admitted HI Bar"),
                attorney.get("HSBA ID"),
                attorney.get("Internal ID"),
                attorney.get("Letter"),
                timestamp
            ))
