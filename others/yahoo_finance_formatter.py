#!/usr/bin/env python3

import argparse
import csv
from dataclasses import dataclass
from typing import List


@dataclass
class Position:
    """ The minimal format Yahoo Finance takes for positions """

    symbol: str
    trade_date: str  # 20202221
    purchase_price: float
    quantity: float

    @classmethod
    def header(self) -> str:
        return "Symbol,Trade Date,Purchase Price,Quantity"

    def row(self) -> str:
        return f"{self.symbol},{self.trade_date},{self.purchase_price},{self.quantity}"


class YahooFinanceExporter:

    def __init__(self, positions: List[Position]):
        self.positions = positions

    def export(self):
        print(Position.header())
        for p in self.positions:
            print(p.row())


class Importer:

    COLUMN_MAPPING = {
        "symbol": "Symbol",
        "trade_date": "Trade Date",
        "purchase_price": "Purchase Price",
        "quantity": "Quantity",
    }
    EXCLUDED_SYMBOLS = set()

    def __init__(self, filename: str):
        self.filename = filename

    def _read_field(self, row, name: str) -> str:
        if name in self.COLUMN_MAPPING:
            return row[self.COLUMN_MAPPING[name]]
        else:
            return ""

    def date_formatter(self, date: str) -> str:
        return date

    def parse(self) -> List[Position]:
        positions = []
        with open(self.filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                symbol = row[self.COLUMN_MAPPING["symbol"]]
                if not symbol or symbol in self.EXCLUDED_SYMBOLS:
                    continue
                if len(row) == 0:
                    break
                positions.append(
                    Position(
                        symbol=self._read_field(row, "symbol"),
                        trade_date=self.date_formatter(
                            self._read_field(row, "trade_date")
                        ),
                        purchase_price=self._read_field(row, "purchase_price"),
                        quantity=self._read_field(row, "quantity"),
                    )
                )
        return positions


class ChaseImporter(Importer):

    COLUMN_MAPPING = {
        "symbol": "Ticker",
        "trade_date": "Pricing Date",
        "purchase_price": "Unit Cost",
        "quantity": "Quantity",
    }
    EXCLUDED_SYMBOLS = {"QACDS"}

    def date_formatter(self, date) -> str:
        date = date.split(" ")[0]
        month, day, year = date.split("/")
        return f"{year}{month}{day}"


class M1Importer(Importer):

    COLUMN_MAPPING = {
        "symbol": "Symbol",
        "trade_date": "Trade Date",
        "purchase_price": "Unit Price",
        "quantity": "Quantity",
    }

    def date_formatter(self, date) -> str:
        month, day, year = date.split("/")
        return f"{year}{month}{day}"


class EtradeImporter(Importer):

    COLUMN_MAPPING = {
        "symbol": "Symbol",
        "purchase_price": "Price Paid $",
        "quantity": "Quantity",
    }
    EXCLUDED_SYMBOLS = {"CASH", "TOTAL"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Format portfolio data into Yahoo Finance format"
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=["yahoo", "chase", "m1", "etrade"],
        help="Where the input data was exported from",
    )
    parser.add_argument(
        "csv", help="CSV file showing header and positions"
    )
    return parser.parse_args()


def get_importer(source):
    source_to_class = {
        "yahoo": Importer,
        "chase": ChaseImporter,
        "m1": M1Importer,
        "etrade": EtradeImporter,
    }
    return source_to_class[source]


def main():
    args = parse_args()
    importer = get_importer(args.source)(args.csv)
    YahooFinanceExporter(importer.parse()).export()


if __name__ == "__main__":
    main()
