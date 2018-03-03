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
        return ', '.join([
            str(self.median),
            str(self.lowest),
            str(self.volume),
        ])


SACK_OF_GEMS = '753-Sack%20of%20Gems'
GEMS_PER_SACK = 1000
CARDS_PER_PACK = 3

trade_items = [
#    GameGroup(
#        name='Nekopara Vol. 0',
#        pack='385800-NEKOPARA%20Vol.%200%20Booster%20Pack',
#        cards=[
#            '385800-Coconut',
#            '385800-Cinnamon',
#            '385800-Azuki',
#            '385800-Chocola',
#            '385800-Shigure',
#            '385800-Vanilla',
#            '385800-Maple',
#            '385800-Minaduki%20Family',
#        ],
#        gems=750,
#    ),
#    GameGroup(
#        name='Nekopara Vol. 1',
#        pack='333600-NEKOPARA%20Vol.%201%20Booster%20Pack',
#        cards=[
#            '333600-Coconut',
#            '333600-Azuki',
#            '333600-Cinnamon',
#            '333600-Shigure',
#            '333600-Maple',
#            '333600-Chocola',
#            '333600-Vanilla',
#            '333600-Chocola',
#         ],
#        gems=750,
#    ),
#    GameGroup(
#        name='Nekopara Vol. 2',
#        pack='420110-NEKOPARA%20Vol.%202%20Booster%20Pack',
#        cards=[
#            '420110-Azuki',
#            '420110-Cinnamon',
#            '420110-Milk',
#            '420110-Chocola',
#            '420110-Vanilla',
#            '420110-Shigure',
#            '420110-Maple',
#            '420110-Coconut',
#        ],
#        gems=750,
#    ),
#    GameGroup(
#        name='Nekopara Vol. 3',
#        pack='602520-NEKOPARA%20Vol.%203%20Booster%20Pack',
#        cards=[
#            '602520-Maple',
#            '602520-Shigure',
#            '602520-Soleil',
#            '602520-Azuki',
#            '602520-Cinnamon',
#            '602520-Chocola',
#            '602520-Coconut',
#            '602520-Vanilla',
#        ],
#        gems=750,
#    ),
#    GameGroup(
#        name='Nekopara OVA',
#        pack='758230-NEKOPARA%20OVA%20Booster%20Pack',
#        cards=[
#            '758230-Cinnamon',
#            '758230-Coconut',
#            '758230-Vanilla',
#            '758230-Azuki',
#            '758230-Shigure',
#            '758230-Maple',
#            '758230-Soleil',
#            '758230-Chocola',
#        ],
#        gems=750,
#    ),
#    GameGroup(
#        name='Hyperdimension Neptunia Re;Birth2',
#        pack='351710-Hyperdimension%20Neptunia%20Re%3BBirth2%20Sisters%20Generation%20Booster%20Pack',
#        cards=[
#            '351710-Histoire',
#            '351710-Maid%20Look',
#            '351710-Wedding%20Dress',
#            '351710-Main%20Package',
#            '351710-Nepgear%2C%20Uni%2C%20Rom%2C%20and%20Ram',
#            '351710-Cosplay',
#            '351710-Sleepover%20Party',
#            '351710-PJ',
#        ],
#        gems=750,
#    ),
#    GameGroup(
#        name='Hyperdimension Neptunia Re;Birth3',
#        pack='353270-Hyperdimension%20Neptunia%20Re%3BBirth3%20V%20Generation%20Booster%20Pack',
#        cards=[
#            '353270-Noire%20%26%20Uni',
#            '353270-Peashy',
#            '353270-Neptune%20%26%20Nepgear',
#            '353270-Nepgear',
#            '353270-Plutia%20%26%20Histoire',
#            '353270-The%20three',
#            '353270-Plutia%20and%20the%20kids',
#            '353270-Party',
#        ],
#        gems=750,
#    ),
#    GameGroup(
#        name='Megadimension Neptunia VII',
#        pack='460120-Megadimension%20Neptunia%20VII%20Booster%20Pack',
#        cards=[
#            '460120-Purple%20Heart%20from%20Neptunia%20VII',
#            '460120-Megadimension%20Neptunia%20VII%20Main%20Theme',
#            '460120-Neptune%20Main%20Theme',
#            '460120-Adult%20Neptune%20of%20Zero%20Dimension',
#            '460120-The%204%20original%20CPUs%20and%20Uzume',
#            '460120-Orange%20Heart',
#            '460120-Adult%20Neptune%20and%20Uzume',
#        ],
#        gems=857,
#    ),
#    GameGroup(
#        name='Hyperdimension Neptunia U: Action Unleashed',
#        pack='387340-Hyperdimension%20Neptunia%20U%3A%20Action%20Unleashed%20Booster%20Pack',
#        cards=[
#            '387340-Joyful%20Neptune%21',
#            '387340-Purple%20Heart%20Highlight',
#            '387340-All%20Stars',
#            '387340-The%20Goddesses',
#            '387340-4%20CPU%20Candidates',
#        ],
#        gems=1200,
#    ),
#    GameGroup(
#        name='Superdimension Neptune VS Sega Hard Girls',
#        pack='571530-Superdimension%20Neptune%20VS%20Sega%20Hard%20Girls%20Booster%20Pack',
#        cards=[
#            '571530-Sega%20Saturn%20and%20Purple%20Heart',
#            '571530-Sega%20Saturn%20and%20Neptune',
#            '571530-Segami%20and%20IF',
#            '571530-Iris%20Heart',
#            '571530-Nepgear%20and%20Game%20Gear',
#            '571530-Segami%2C%20IF%20and%20Mega%20Drive',
#        ],
#        gems=1000,
#    ),
    GameGroup(
        name='Cyberdimension Neptunia: 4 Goddesses Online',
        pack='632350-Cyberdimension%20Neptunia%3A%204%20Goddesses%20Online%20Booster%20Pack',
        cards=[
            '632350-The%20Four%20Goddesses',
            '632350-The%20Four%20CPUs',
            '632350-The%20Four%20CPUs%20Closeup',
            '632350-The%20Four%20CPU%20Candidates',
            '632350-The%20Four%20CPU%20Candidates%20Closeup',
        ],
        gems=1200,
    ),
]


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
                time.sleep(10)
                continue
            else:
                print(e.code, e.reason)
                continue
        break

    if not result:
        raise RuntimeError('Failed to get price for {}'.format(item))

    data = dict(json.loads(result.decode('utf-8')))
    if not data['success']:
        raise RuntimeError('Failed to get price for {}'.format(item))

    result = MarketPrice(
        item,
        data.get('lowest_price', 0),
        data.get('median_price', 0),
        data.get('volume', 0),
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


def get_prices(items):
    prices = []
    for s in items:
        t = threading.Thread(target=get_price, args=(s, prices))
        t.start()
        t.join()
    return prices


def to_float(price):
    try:
        return float(price)
    except ValueError:
        return float(price.split()[1])
    raise ValueError('Failed to convert {}'.format(price))


def assess_game_market(game_groups):
    # get price per gem
    gem_price = get_price(SACK_OF_GEMS)
    print('Cost per sack of gem: {}'.format(gem_price.median))
    gem_price = to_float(gem_price.median) / GEMS_PER_SACK

    for idx, group in enumerate(game_groups):
        cost = gem_price * group.gems

        # pack value
        pack = get_price(group.pack)
        if pack.median or pack.lowest:
            pack_sale = min(
                v for v in [
                    to_float(pack.median),
                    to_float(pack.lowest),
                ] if v != 0
            )
            pack_sale *= 0.87
        else:
            pack_sale = 0
        pack_margin = (pack_sale - cost) / cost * 100

        # unpack value
        cards = get_prices(group.cards)
        avg_medium = sum([to_float(p.median) for p in cards]) / len(cards)
        avg_medium *= CARDS_PER_PACK
        avg_lowest = sum([to_float(p.lowest) for p in cards]) / len(cards)
        avg_lowest *= CARDS_PER_PACK
        unpack_sale = min(avg_lowest, avg_medium)
        unpack_sale *= 0.87
        unpack_margin = (unpack_sale - cost) / cost * 100

        print(group.name)
        print(tabulate(zip(
            [group.pack] + group.cards +
            ['Unpack value', 'Cost', 'Pack margin', 'Unpack margin'],
            [pack] + cards +
            [
                ', '.join('{:.2f}'.format(v) for v in [avg_medium, avg_lowest]),
                '{:.2f}'.format(cost),
                '{:.2f} %'.format(pack_margin),
                '{:.2f} %'.format(unpack_margin),
            ],
        )))
        # there seems to be throttling for API
        if idx != len(game_groups) - 1:
            time.sleep(20)


def main():
    assess_game_market(trade_items)


if __name__ == '__main__':
    main()
