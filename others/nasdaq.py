#!/usr/bin/env python3

from urllib.request import urlopen
import urllib.error
from tabulate import tabulate
import re, threading

#import pprint
#pp = pprint.PrettyPrinter(indent=4)

symbols = set([
    'AAPL',
    'AMD',
    'AMZN',
    'ATVI',
    'BILI',
    'EA',
	'EBAY',
    'FB',
    'GOOG',
    'IBM',
    'INTC',
    'MRVL',
    'MSFT',
    'MU',
    'NFLX',
    'NVDA',
    'PYPL',
    'QCOM',
	'SNAP',
    'SNE',
    'STX',
    'TSLA',
    'TTWO',
    'TWTR',
    'WD',
    'YELP',
])
dates = {}

report_patterns = [
    re.compile(
        '.*(?P<type>(expected|estimated)).*to report earnings '
        'on\s+(?P<date>[\d/]*)\s+(?P<time>(before|after)) market.*'
    ),
    re.compile(
        '.*(?P<type>(expected|estimated)).*to report earnings '
        'on\s+(?P<date>[\d/]*).*'
    ),
]
ex_div_pattern = re.compile(
    '.*<span id="quotes_content_left_dividendhistoryGrid_exdate_0">'
    '(?P<date>[\d/]+)</span>.*'
    '<span id="quotes_content_left_dividendhistoryGrid_CashAmount_0">'
    '(?P<amount>[\d.]+)</span>.*'
)

def get_report_date(symbol):
    url = 'http://www.nasdaq.com/earnings/report/' + symbol.lower()
    dates[symbol] = {
        'report': 'unknown',
        'type': 'unknown',
    }
    try:
        result = urlopen(url).read()
    except urllib.error.HTTPError as e:
        print(e.code, e.reason)
        return
    for p in report_patterns:
        g = p.match(str(result))
        if g:
            d = g.groupdict()
            dates[symbol] = {
                'report': d['date'],
                'type': d['type'],
            }
            if 'time' in d:
                dates[symbol]['report'] = '{} {} market'.format(
                    d['date'], d['time'],
                )
            break

def get_div_date(symbol):
    url = 'http://www.nasdaq.com/symbol/{}/dividend-history'.format(symbol)
    dates[symbol]['div_date'] = None
    try:
        result = urlopen(url).read()
    except urllib.error.HTTPError as e:
        print(e.code, e.reason)
        return
    g = ex_div_pattern.match(str(result))
    if g:
        dates[symbol]['div_date'] = '{} ${}'.format(
            g.groupdict()['date'],
            g.groupdict()['amount'],
        )

def print_dates():
    data = [
        (sym, v['report'], v['type'], v['div_date'])
        for sym, v in dates.items()
    ]
    data = sorted(data, key=lambda s:s[1])
    print(tabulate(
        data,
        headers=['symbol', 'report date', 'type', 'div date'],
    ))

def get_data(func):
    threads = []
    for s in symbols:
        t = threading.Thread(target=func, args=[s])
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def main():
    get_data(get_report_date)
    get_data(get_div_date)
    print_dates()

if __name__ == '__main__':
    main()
