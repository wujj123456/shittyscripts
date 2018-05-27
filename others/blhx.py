#!/usr/bin/env python3


import argparse
from collections import namedtuple, defaultdict
import sys


from tabulate import tabulate
from termcolor import colored, cprint


# friendliness

class ExpTable(object):

    ExpGrowth = namedtuple(
        'ExpGrowth',
        [
            'base_lvl',
            'end_lvl',
            'step_base',
            'step_growth',
            'base_exp',
        ],
    )

    ExpGrowthTable = [
        ExpGrowth(1, 40, 100, 100, 0),
        ExpGrowth(40, 60, 4000, 200, 78000),
        ExpGrowth(60, 70, 8000, 300, 196000),
        ExpGrowth(70, 80, 11000, 400, 289500),
        ExpGrowth(80, 90, 15000, 500, 417500),
        ExpGrowth(90, 91, 0, 0, 590000),
        ExpGrowth(91, 92, 0, 0, 610000),
        ExpGrowth(92, 93, 0, 0, 631000),
        ExpGrowth(93, 94, 0, 0, 653000),
        ExpGrowth(94, 95, 0, 0, 677000),
        ExpGrowth(95, 96, 0, 0, 703000),
        ExpGrowth(96, 97, 0, 0, 733000),
        ExpGrowth(97, 98, 0, 0, 768000),
        ExpGrowth(98, 99, 0, 0, 808000),
        ExpGrowth(99, 100, 0, 0, 868000),
        ExpGrowth(100, 105, 70000, 2000, 1000000),
        ExpGrowth(104, 106, 78000, 7000, 1292000),
        ExpGrowth(106, 110, 97000, 12000, 1455000),
        ExpGrowth(110, 115, 145000, 18000, 1915000),
        ExpGrowth(115, 121, 235000, 21000, 2820000),
    ]

    def __init__(self):
        self.table = {}
        self._calc_table()

    def _calc_table(self):
        for e in self.ExpGrowthTable:
            for lvl in range(e.base_lvl, e.end_lvl):
                step = lvl - e.base_lvl
                self.table[lvl] = (
                    e.base_exp + step * e.step_base +
                    sum(range(step)) * e.step_growth
                )

    def print_table(self, max_level=None):
        rows = [
            (k, v) for k, v in self.table.items()
            if not max_level or k <= max_level
        ]
        print(tabulate(rows, headers=['level', 'total exp']))


def print_friendiness(args):
    exp = ExpTable()
    if args.debug:
        exp.print_table()

    results = []
    for lvl in range(args.start_level, args.end_level):
        exp_diff = exp.table[args.end_level] - exp.table[lvl]
        friendiness = exp_diff / args.exp_per_battle / 16
        results.append((lvl, friendiness))
    print(tabulate(results, headers=['level', 'friendiness gain']))


# retire

RETIRE_RESOURCE = {
    'DD': 15,
    'CL': 35,
    'CA': 60,
    'BC': 70,
    'BB': 85,
    'CVL': 40,
    'CV': 65,
    'BM': 30,
    'AR': 15,
}

RETIRE_FUEL = {
    'DD': 2,
    'CL': 3,
    'CA': 5,
    'BC': 8,
    'BB': 10,
    'CVL': 5,
    'CV': 8,
    'BM': 3,
    'AR': 3,
}


def _color_table(table):
    """ If level up gains no value, color red. If level up gains more
    value above benchmark, color green. If level up gains more value
    but below benchmark, color blue. The benchmark is the highest
    efficiency across all ship types at max level
    """
    # find benchmark
    max_lvl = max(table.keys())
    benchmark = max(eff for _, eff in table[max_lvl])
    colored_table = defaultdict(list)
    for lvl, effs in table.items():
        for i, value in enumerate(effs):
            color = 'green'
            if lvl > 1:
                if value[0] == table[lvl-1][i][0]:
                    # no additional gain
                    color = 'red'
                elif value[1] < benchmark:
                    # efficiency below benchmark
                    color = 'blue'
            colored_table[lvl].append(
                colored('{} {:.2f}'.format(*value), color),
            )
    return colored_table


def calc_retire_efficiency(exp_table, gain_table, multiplier, max_lvl):
    headers = []
    lvl_to_gain = defaultdict(list)
    for ship_type, val in gain_table.items():
        headers.append(ship_type)
        for lvl in range(1, max_lvl + 1):
            exp = exp_table.table[lvl]
            gain = (lvl * gain_table[ship_type] + 30) // 10
            # gain per exp when leveling up to this level
            gain_per_exp = 0
            if lvl > 1:
                gain_per_exp = (gain / exp) * multiplier
            lvl_to_gain[lvl].append((gain, gain_per_exp))
    lvl_to_gain = _color_table(lvl_to_gain)
    return headers, lvl_to_gain


def print_retire_efficiency(headers, lvl_to_gain):
    rows = []
    headers = ['level'] + headers
    for lvl, v in lvl_to_gain.items():
        rows.append([lvl] + v)
    print(tabulate(rows, headers=headers))


def print_retire(args):
    exp = ExpTable()
    print('==========\nEXP\n==========\n')
    exp.print_table(args.max_level)

    multiplier = 100
    print('\n==========\nRESOURCE (value, value per 100 xp)\n==========\n')
    print_retire_efficiency(
        *calc_retire_efficiency(exp, RETIRE_RESOURCE, 100, args.max_level),
    )
    print('\n==========\nFUEL (value, value per 1000 xp)\n==========\n')
    print_retire_efficiency(
        *calc_retire_efficiency(exp, RETIRE_FUEL, 1000, args.max_level),
    )
    return


def parse_args(args):
    parser = argparse.ArgumentParser(description='BLHX calculator')
    parser.add_argument('-d', '--debug', action='store_true')
    subparsers = parser.add_subparsers()

    friendiness_parser = subparsers.add_parser('love')
    friendiness_parser.add_argument('exp_per_battle', type=int)
    friendiness_parser.add_argument('--start-level', type=int, default=60)
    friendiness_parser.add_argument('--end-level', type=int, default=100)
    friendiness_parser.set_defaults(func=print_friendiness)

    retire_parser = subparsers.add_parser('retire')
    retire_parser.add_argument('--max-level', type=int, default=15)
    retire_parser.set_defaults(func=print_retire)
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
