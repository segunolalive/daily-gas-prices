import os
import logging
import traceback
import datetime

import requests
from bs4 import BeautifulSoup


class GasPrice:
    """
    a suite of utilities to generate csv version of daily gas prices from www.eia.gov
    """

    URL = "https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm"
    OUTPUT_DIR = "public/"
    DAILY_PRICES = OUTPUT_DIR + "daily_prices.csv"
    html = None
    data = None
    formatted_data = []

    def get_daily_prices_csv(self):
        """
        write CSV file containing cleaned gas prices and corresponding dates
        """
        self.__get_page().__extract_rows().__format_prices()

        directory = os.path.join(os.getcwd(), self.OUTPUT_DIR)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(self.DAILY_PRICES, "w") as csv_file:
            csv_file.write("date,price \n")
            for day in self.formatted_data:
                csv_file.write(",".join(day))
                csv_file.write("\n")

        logging.info(
            "SUCCESS! Daily Gas Prices Generated at {0}".format(
                os.path.join(os.getcwd(), self.DAILY_PRICES)
            )
        )

    def __get_page(self):
        """
        method for fetching the gas prices html page
        """
        try:
            req = requests.get(self.URL)
            if req.status_code == 200:
                self.html = req.content
                logging.info("HTML page fetched successfully...")
                return self
            else:
                message = "ERROR. Server returned a status code of " + str(
                    req.status_code
                )
                logging.warning(message)
        except Exception as e:
            message = "An Error occured while fetching the html page. " + str(e)
            logging.error(message)
            logging.error(traceback.format_exc())

    def __extract_rows(self):
        data = {"dates": [], "prices": []}
        summary = "Henry Hub Natural Gas Spot Price (Dollars per Million Btu)"
        soup = BeautifulSoup(self.html, "html.parser")
        table = soup.find(summary=summary)
        table_rows = table.find_all("tr")
        for row in table_rows:
            date_cell = row.find("td", {"class": "B6"})
            price_cells = row.find_all("td", {"class": "B3"})
            if date_cell:
                data.get("dates").append(date_cell)
            if len(price_cells):
                data.get("prices").append(price_cells)
        self.data = data
        return self

    def __format_prices(self):
        dates = self.data.get("dates")
        prices = self.data.get("prices")
        for i, date in enumerate(dates):
            start_date = self.__get_start_date(date)
            day_offset = 0
            for price in prices[i]:
                if not price.text:
                    continue
                current_date = start_date + datetime.timedelta(days=day_offset)
                current_date = current_date.strftime("%b %d %Y")
                self.formatted_data.append([current_date, price.text])
                day_offset += 1
        return self

    def __get_start_date(self, string):
        start_date = (
            string.text.replace("\xa0\xa0", "")
            .replace("- ", " ")
            .replace("-", " ")
            .split(" ")[0:3]
        )
        start_date.reverse()
        return self.normalise_date(start_date)

    def normalise_date(self, date):
        return datetime.datetime.strptime(" ".join(date), "%d %b %Y")


def main():
    logging.basicConfig(level=logging.DEBUG)

    gas_prices = GasPrice()
    gas_prices.get_daily_prices_csv()


if __name__ == "__main__":
    main()
