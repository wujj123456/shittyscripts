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


def color_table(table, value_key, value_efficiency_key):
    """ If level up gains no value, color red. If level up gains more
    value above benchmark, color green. If level up gains more value
    but below benchmark, color blue. The benchmark is the highest
    efficiency across all ship types at max level
    """

    def _format(val):
        if isinstance(val, float):
            return '{:4.1f}'.format(val)
        elif isinstance(val, int):
            return '{:3}'.format(val)
        else:
            return str(val)

    # find benchmark
    max_lvl = max(table.keys())
    benchmark = max(v[value_efficiency_key] for v in table[max_lvl])
    colored_table = defaultdict(list)
    for lvl, effs in table.items():
        for i, value in enumerate(effs):
            color = 'green'
            if lvl > 1:
                if value[value_key] == table[lvl-1][i][value_key]:
                    # no additional gain
                    color = 'red'
                elif value[value_efficiency_key] < benchmark:
                    # efficiency below benchmark
                    color = 'blue'
            colored_table[lvl].append(
                colored(' '.join([_format(v) for v in value.values()]), color),
            )
    return colored_table


def calc_retire_efficiency(exp_table, value_table, multiplier, max_lvl):
    headers = []
    lvl_to_value = defaultdict(list)
    for ship_type, val in value_table.items():
        headers.append(ship_type)
        base = (value_table[ship_type] + 30) // 10
        for lvl in range(1, max_lvl + 1):
            exp = exp_table.table[lvl]
            value = (lvl * value_table[ship_type] + 30) // 10
            # value per exp when leveling up to this level
            value_per_exp = 0.0
            if lvl > 1:
                value_per_exp = ((value - base) / exp) * multiplier
            lvl_to_value[lvl].append({
                'value': value,
                'value per {} exp'.format(multiplier): value_per_exp,
            })
    return headers, lvl_to_value


def splitter():
    print('====================')


def print_retire_efficiency(headers, lvl_to_value):
    rows = []
    headers = ['level'] + headers
    for lvl, v in lvl_to_value.items():
        rows.append([lvl] + v)
    print(tabulate(rows, headers=headers))


def print_retire_table(args, exp_table, name, retire_table, multiplier):
    if args.rank and args.comfort:
        exp_per_fuel = HomeExp(
            rank=args.rank,
            comfort=args.comfort,
            multiplier=args.multiplier,
        ).base_exp_per_fuel

    headers, lvl_to_resource = calc_retire_efficiency(
        exp_table,
        retire_table,
        multiplier,
        args.max_level,
    )
    if args.rank and args.comfort:
        for lvl, data in lvl_to_resource.items():
            for entry in data:
                entry['value per fuel'] = (
                    entry['value per {} exp'.format(multiplier)] /
                    multiplier * exp_per_fuel
                )
    title = lvl_to_resource[1][0].keys()
    lvl_to_resource = color_table(
        lvl_to_resource,
        'value',
        'value per {} exp'.format(multiplier),
    )
    print()
    splitter()
    print('{} ({})'.format(name, ', '.join(title)))
    splitter()
    print()
    print_retire_efficiency(headers, lvl_to_resource)
    print()


def print_retire(args):

    exp = ExpTable()
    splitter()
    print('EXP')
    splitter()
    print()
    exp.print_table(args.max_level)
    print()

    print_retire_table(args, exp, 'RESOURCE', RETIRE_RESOURCE, 100)
    print_retire_table(args, exp, 'FUEL', RETIRE_FUEL, 1000)

# home

class HomeExp(object):

    SHIP_MULTIPLIER = {
        1: 1,
        2: 1.8,
        3: 2.4,
        4: 2.8,
        5: 3.2,
    }
    BASE_FUEL_PER_SEC = 1/3
    BASE_FUEL_PER_HOUR = BASE_FUEL_PER_SEC * 3600

    def __init__(self, rank, comfort, multiplier=1.0):
        self.rank = rank
        self.comfort = comfort
        self.multiplier = multiplier
        # exp per hour with single ship, including boost multiplier
        self.base_exp_per_hour = self._base_exp_per_hour()
        # per unit of fuel equals to 100 units of food
        self.base_exp_per_fuel = (
            100 * self.base_exp_per_hour / self.BASE_FUEL_PER_HOUR
        )
        self.exp_per_hour = {}
        self._calculate()

    def _base_exp_per_hour(self):
        comfort = 1 + self.comfort / (self.comfort + 100)
        commander = (240 + self.rank * 12)
        return commander * comfort * self.multiplier

    def _calculate_exp_per_hour_ship(self, count):
        ships = self.SHIP_MULTIPLIER[count] / count
        return self.base_exp_per_hour * ships

    def _calculate(self):
        for i in range(1, 6):
            exp_per_hour_ship = self._calculate_exp_per_hour_ship(i)
            self.exp_per_hour[i] = (
                exp_per_hour_ship,
                exp_per_hour_ship * i,
            )

    def print_exp_table(self):
        print(tabulate(
            [(k, *v) for k, v in self.exp_per_hour.items()],
            headers=['ships', 'exp / (h * ship)', 'exp / h'],
        ))


def print_home(args):
    home_exp = HomeExp(args.rank, args.comfort)
    print('Exp per fuel: {}\n'.format(home_exp.base_exp_per_fuel))
    home_exp.print_exp_table()


def get_home_parsers(required):
    home_parser = argparse.ArgumentParser(add_help=False)
    home_parser.add_argument(
        '--rank',
        type=int,
        required=required,
        help='Commander Rank',
    )
    home_parser.add_argument(
        '--comfort',
        type=int,
        required=required,
        help='Comfort rating',
    )
    home_parser.add_argument('--multiplier', type=float, default=1.0)
    return home_parser

def parse_args(args):
    parser = argparse.ArgumentParser(description='BLHX calculator')
    parser.add_argument('-d', '--debug', action='store_true')
    subparsers = parser.add_subparsers()

    friendiness_parser = subparsers.add_parser(
        'love',
        help='Calculate friendliness gain per level',
    )
    friendiness_parser.add_argument('exp_per_battle', type=int)
    friendiness_parser.add_argument('--start-level', type=int, default=60)
    friendiness_parser.add_argument('--end-level', type=int, default=100)
    friendiness_parser.set_defaults(func=print_friendiness)

    home_parser = subparsers.add_parser(
        'home',
        parents=[get_home_parsers(required=True)],
        help='Calculate XP growth rate at home',
    )
    home_parser.set_defaults(func=print_home)

    retire_parser = subparsers.add_parser(
        'retire',
        parents=[get_home_parsers(required=False)],
        help='Calculate resource/fuel value for retirement',
    )
    retire_parser.add_argument('--max-level', type=int, default=15)
    retire_parser.set_defaults(func=print_retire)

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
