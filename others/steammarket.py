#!/usr/bin/env python3


from urllib.request import urlopen
import urllib.error
from tabulate import tabulate
import json
import time
import threading
from collections import namedtuple


GameGroup = namedtuple('GameGroup', ['name', 'pack', 'cards', 'gems'])


class MarketPrice(object):
    def __init__(self, name, lowest, median, volume):
        self.name = name
        self.lowest = lowest
        self.median = median
        self.volume = volume

    def __str__(self):
        return ', '.join([self.lowest, self.median, self.volume])


trade_items = {
    'nekopara_vol0': GameGroup(
        name='Nekopara Vol. 0',
        pack='385800-NEKOPARA%20Vol.%200%20Booster%20Pack',
        cards=[
            '385800-Coconut',
            '385800-Cinnamon',
            '385800-Azuki',
            '385800-Chocola',
            '385800-Shigure',
            '385800-Vanilla',
            '385800-Maple',
            '385800-Minaduki%20Family',
        ],
        gems=750,
    ),
    'nekopara_vol1': GameGroup(
        name='Nekopara Vol. 1',
        pack='333600-NEKOPARA%20Vol.%201%20Booster%20Pack',
        cards=[
            '333600-Coconut',
            '333600-Azuki',
            '333600-Cinnamon',
            '333600-Shigure',
            '333600-Maple',
            '333600-Chocola',
            '333600-Vanilla',
            '333600-Chocola',
         ],
        gems=750,
    ),
    'nekopara_vol2': GameGroup(
        name='Nekopara Vol. 2',
        pack='420110-NEKOPARA%20Vol.%202%20Booster%20Pack',
        cards=[
            '420110-Azuki',
            '420110-Cinnamon',
            '420110-Milk',
            '420110-Chocola',
            '420110-Vanilla',
            '420110-Shigure',
            '420110-Maple',
            '420110-Coconut',
        ],
        gems=750,
    ),
    'hyperdimension_rebirth2': GameGroup(
        name='Hyperdimension Neptunia Re;Birth2',
        pack='351710-Hyperdimension%20Neptunia%20Re%3BBirth2%20Sisters%20Generation%20Booster%20Pack',
        cards=[
            '351710-Histoire',
            '351710-Maid',
            '351710-Wedding%20Dress',
            '351710-Main%20Package',
            '351710-Nepgear%2C%20Uni%2C%20Rom%2C%20and%20Ram',
            '351710-Cosplay',
            '351710-Sleepover%20Party',
            '351710-PJ',
        ],
        gems=750,
    ),
    'hyperdimension_rebirth3': GameGroup(
        name='Hyperdimension Neptunia Re;Birth3',
        pack='353270-Hyperdimension%20Neptunia%20Re%3BBirth3%20V%20Generation%20Booster%20Pack',
        cards=[
            '353270-Noire%20%26%20Uni',
            '353270-Peashy',
            '353270-Neptune%20%26%20Nepgear',
            '353270-Nepgear',
            '353270-Plutia%20%26%20Histoire',
            '353270-The%20three',
            '353270-Plutia%20and%20the%20kids',
            '353270-Party',
        ],
        gems=750,
    ),
}


# market appid = 753
# currency: USD->1, RMB->23
def item_url(name):
    return construct_url('753', '23', name)


def get_price(item, ret_list=None):
    url = item_url(item)
    result = None
    for i in range(5):
        try:
            result = urlopen(url).read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3)
                continue
            else:
                print(e.code, e.reason)
                continue
        break
    if result:
        data = dict(json.loads(result.decode('utf-8')))
        result = MarketPrice(
            item,
            data['lowest_price'],
            data['median_price'],
            data['volume'],
        )

    if ret_list is not None:
        ret_list.append(result)
    return result


def construct_url(appid, currency, name):
    return (
        'https://steamcommunity.com/market/priceoverview/?'
        'appid={appid}&currency={currency}&market_hash_name={name}'
        .format(**locals())
    )


def print_item_prices(game_group):
    price_list = []
    item_list = [game_group.pack] + game_group.cards
    for s in item_list:
        t = threading.Thread(target=get_price, args=(s, price_list))
        t.start()
        t.join()
    print(game_group.name)
    print(tabulate(zip(item_list, price_list)))


def main():
    print_item_prices(trade_items['nekopara_vol0'])


if __name__ == '__main__':
    main()
