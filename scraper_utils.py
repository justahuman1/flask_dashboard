from __future__ import print_function

import sys
import datetime
from pyquery import PyQuery as pq
from requests import get


def get_url_data(url):
    try:
        response = get(url)
        return response
    except Exception as e:
        if hasattr(e, "message"):
            print("Error message (get_url_data) :", e.message)
        else:
            print("Error message (get_url_data) :", e)
        sys.exit(1)


def get_coin_id(coin_code):
    try:
        url = "https://coinmarketcap.com/all/views/all/"

        html = get_url_data(url).text
        raw_data = pq(html)

        coin_code = coin_code.upper()

        for _row in raw_data("tr")[1:]:
            symbol = _row.cssselect("td.text-left.col-symbol")[0].text_content()
            coin_id = _row.values()[0].split("id-")[1]
            if symbol == coin_code:
                return coin_id
        raise InvalidCoinCode('This coin code is unavailable on "coinmarketcap.com"')
    except Exception as e:
        raise e


def download_coin_data(coin_code, start_date, end_date):
    if start_date is None:
        start_date = "28-4-2013"

    if end_date is None:
        yesterday = datetime.date.today() - datetime.timedelta(1)
        end_date = yesterday.strftime("%d-%m-%Y")

    coin_id = get_coin_id(coin_code)

    start_date = datetime.datetime.strptime(start_date, "%d-%m-%Y").strftime("%Y%m%d")
    end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y%m%d")

    url = f"http://coinmarketcap.com/currencies/{coin_id}/historical-data/?start={start_date}&end={end_date}"

    try:
        html = get_url_data(url).text
        return html
    except Exception as e:
        print(
            f"Error fetching price data for {coin_code} for interval '{start_date}' and '{end_date}'"
        )

        if hasattr(e, "message"):
            print("Error message (download_data) :", e.message)
        else:
            print("Error message (download_data) :", e)


def _native_type(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def _replace(s, bad_chars):
    if sys.version_info > (3, 0):
        # For Python 3
        without_bad_chars = str.maketrans("", "", bad_chars)
        return s.translate(without_bad_chars)
    else:
        # For Python 2
        import string

        identity = string.maketrans("", "")
        return s.translate(identity, bad_chars)


def extract_data(html):
    raw_data = pq(html)

    headers = [col.text_content().strip("*") for col in raw_data("table:first>thead>tr>th")]

    rows = []

    for _row in raw_data("table:first>tbody>tr"):
        row = [
            _native_type(_replace(col.text_content().strip(), ",-*?"))
            for col in _row.findall("td")
        ]

        # change format of date ('Aug 24 2017' to '24-08-2017')
        row[0] = datetime.datetime.strptime(row[0], "%b %d %Y").strftime("%d-%m-%Y")

        rows.append(row)

    end_date, start_date = rows[0][0], rows[-1][0]

    return end_date, start_date, headers, rows


class InvalidParameters(ValueError):
    """Passed parameters are invalid."""


class InvalidCoinCode(NotImplementedError):
    """This coin code is unavailable on 'coinmarketcap.com'"""
