#!/usr/bin/env python3

import argparse
import calendar
from collections import OrderedDict
import datetime
from html.parser import HTMLParser
import re
import sys
from tabulate import tabulate
from urllib.request import urlopen
import urllib.error


class YahooFinanceHTMLParser(HTMLParser):

    FIELDS = OrderedDict(
        {
            "close": "Previous Close",
            "report_date": "Earnings Date",
            "dividend": "Forward Dividend & Yield",
            "dividend_date": "Ex-Dividend Date",
        }
    )
    MONTH_ABBR_TO_NUM = {m: i for i, m in enumerate(calendar.month_abbr) if m}
    DATE_REGEX = re.compile("(?P<m>[a-zA-Z]+) (?P<d>\d+), (?P<y>\d+)")

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
            if "date" in self.record:
                data = self.format_date(data)
            self.data[self.record] = data
            self.record = None

        for k, v in self.FIELDS.items():
            if data == v:
                self.record = k

    def query(self):
        self.feed(self.get_raw_html())

    def format_date(self, date_str):
        m = re.match(self.DATE_REGEX, date_str)
        if not m:
            return date_str

        d = m.groupdict()
        month = self.MONTH_ABBR_TO_NUM[d["m"]]
        date = datetime.date(int(d["y"]), month, int(d["d"]))
        return date.isoformat()


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
    print(tabulate(sorted(rows, key=lambda x: x[sort_index]), headers=headers))


def parse_args():
    parser = argparse.ArgumentParser(description="Script to get earning info")
    symbol_parser = parser.add_mutually_exclusive_group(required=True)
    symbol_parser.add_argument(
        "--symbols", nargs="+", help="List of symbols to query for"
    )
    symbol_parser.add_argument(
        "--stdin", action="store_true", help="Parse symbols from stdin. One per line"
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

    if args.stdin:
        args.symbols = sys.stdin.readlines()

    if not args.symbols:
        print("No symbols passed in. Exiting")
        return
    results = get_data_for_symbols(args.symbols)
    tabulate_output(results, args.sort_by)


if __name__ == "__main__":
    main()
