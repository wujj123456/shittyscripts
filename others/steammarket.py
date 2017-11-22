#!/usr/bin/env python3

from urllib.request import urlopen
import urllib.error
from tabulate import tabulate
import json, time, threading

#import pprint
#pp = pprint.PrettyPrinter(indent=4)

nekopara_vol0 = ['385800-Coconut',
                 '385800-Cinnamon',
                 '385800-Azuki',
                 '385800-Chocola',
                 '385800-Shigure',
                 '385800-Vanilla',
                 '385800-Maple',
                 '385800-Minaduki%20Family',
                 ]
nekopara_vol1 = ['333600-Coconut',
                 '333600-Azuki',
                 '333600-Cinnamon',
                 '333600-Shigure',
                 '333600-Maple',
                 '333600-Chocola',
                 '333600-Vanilla',
                 '333600-Chocola',
                 ]
nekopara_vol2 = ['420110-Azuki',
                 '420110-Cinnamon',
                 '420110-Milk',
                 '420110-Chocola',
                 '420110-Vanilla',
                 '420110-Shigure',
                 '420110-Maple',
                 '420110-Coconut',
                 ]
hyperdimension_2 = ['351710-Histoire',
                    '351710-Maid',
                    '351710-Wedding%20Dress',
                    '351710-Main%20Package',
                    '351710-Nepgear%2C%20Uni%2C%20Rom%2C%20and%20Ram',
                    '351710-Cosplay',
                    '351710-Sleepover%20Party',
                    '351710-PJ',
                    ]
hyperdimension_3 = ['353270-Noire%20%26%20Uni',
                    '353270-Peashy',
                    '353270-Neptune%20%26%20Nepgear',
                    '353270-Nepgear',
                    '353270-Plutia%20%26%20Histoire',
                    '353270-The%20three',
                    '353270-Plutia%20and%20the%20kids',
                    '353270-Party',
                    ]
booster_packs = ['385800-NEKOPARA%20Vol.%200%20Booster%20Pack',
                 '333600-NEKOPARA%20Vol.%201%20Booster%20Pack',
                 '420110-NEKOPARA%20Vol.%202%20Booster%20Pack',
                 '351710-Hyperdimension%20Neptunia%20Re%3BBirth2%20Sisters%20Generation%20Booster%20Pack',
                 '353270-Hyperdimension%20Neptunia%20Re%3BBirth3%20V%20Generation%20Booster%20Pack',
                 ]

def get_lowest_price(url, ret_list):
    result = None
    for i in range(5):
        try:
            result = urlopen(url).read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5)
                continue
            else:
                print(e.code, e.reason)
                continue
        break
    if result:
        data = dict(json.loads(result.decode('utf-8')))
        ret_list.append((data['lowest_price'], data['volume']))
    else:
        ret_list.append(('timedout', '0'))

def construct_url(appid, currency, name):
    return 'https://steamcommunity.com/market/priceoverview/?appid=' \
           + appid + '&currency=' + currency + '&market_hash_name=' \
           + name

# market appid = 753
# currency: USD->1, RMB->23
def card_url(name):
    return construct_url('753', '23', name)

def print_card_group(title, group):
    table = []
    for s in group:
        url = card_url(s)
        t = threading.Thread(target=get_lowest_price, args=(url, table))
        t.start()
        t.join()
    print(title)
    print(tabulate(zip(group, table)))

def main():
    print_card_group('Booster Packs', booster_packs)
#    print_card_group('Nekopara Vol.0', nekopara_vol0)
    print_card_group('Nekopara Vol.2', nekopara_vol2)
    print_card_group('Nekopara Vol.1', nekopara_vol1)
#    print_card_group('Hyperdimension 2', hyperdimension_2)
#    print_card_group('Hyperdimension 3', hyperdimension_3)

if __name__ == '__main__':
    main()


