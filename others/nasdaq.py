#!/usr/bin/env python3

import argparse
from collections import OrderedDict
from html.parser import HTMLParser
from urllib.request import urlopen
import urllib.error
from tabulate import tabulate


symbols = [
    "AAPL",
    "AKAM",
    "AMD",
    "AMZN",
    "ATVI",
    "BILI",
    "EA",
    "EBAY",
    "FB",
    "GOOGL",
    "INTC",
    "MSFT",
    "MU",
    "NET",
    "NFLX",
    "NVDA",
    "PYPL",
    "QCOM",
    "SNE",
    "STX",
    "TSLA",
    "TSM",
    "TTWO",
    "TWTR",
    "WDC",
]


class YahooFinanceHTMLParser(HTMLParser):

    FIELDS = OrderedDict(
        {
            "close": "Previous Close",
            "report_date": "Earnings Date",
            "dividend": "Forward Dividend & Yield",
            "dividend_date": "Ex-Dividend Date",
        }
    )

    def __init__(self, symbol, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self.data = {}
        self.record = None

        self.symbol = symbol
        self.url = f"https://finance.yahoo.com/quote/{self.symbol}"

    def get_raw_html(self):
        try:
            result = urlopen(self.url).read()
        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
            return
        return result.decode("utf-8")

    def handle_data(self, data):
        if self.record:
            self.data[self.record] = data
            self.record = None

        for k, v in self.FIELDS.items():
            if data == v:
                self.record = k

    def query(self):
        self.feed(self.get_raw_html())


def get_data_for_symbols(symbols):
    result = OrderedDict()
    for symbol in symbols:
        html_parser = YahooFinanceHTMLParser(symbol)
        html_parser.query()
        result[symbol] = html_parser.data
    return result

def get_sort_index(sort_by):
    if not sort_by:
        return 0
    for i, k in enumerate(YahooFinanceHTMLParser.FIELDS.keys()):
        if k == sort_by:
            return i + 1
    return 0

def tabulate_output(data, sort_by=None):
    rows = []
    for symbol, info in data.items():
        row = [symbol]
        for k in YahooFinanceHTMLParser.FIELDS:
            row.append(info[k])
        rows.append(row)
    headers = ["Symbol"] + [v for v in YahooFinanceHTMLParser.FIELDS.values()]
    sort_index = get_sort_index(sort_by)
    print(tabulate(sorted(rows, key=lambda x:x[sort_index]), headers=headers))


def parse_args():
    parser = argparse.ArgumentParser(description="Script to get earning info")
    parser.add_argument(
        "--symbols", nargs="+", default=symbols, help="List of symbols to query for"
    )
    parser.add_argument(
        "--sort-by",
        default="report_date",
        choices=list(YahooFinanceHTMLParser.FIELDS.keys()),
        help="Sort by selected field",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    results = get_data_for_symbols(args.symbols)
    tabulate_output(results, args.sort_by)


if __name__ == "__main__":
    main()
