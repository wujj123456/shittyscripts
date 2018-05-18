#!/usr/bin/env python3


import argparse
from collections import namedtuple
from pprint import pprint
import sys
from tabulate import tabulate


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


class ExpTable(object):

    def __init__(self, exp_growth_table):
        self.table = {}
        self._calc_table(exp_growth_table)

    def _calc_table(self, exp_growth_table):
        for e in exp_growth_table:
            for lvl in range(e.base_lvl, e.end_lvl):
                step = lvl - e.base_lvl
                self.table[lvl] = (
                    e.base_exp + step * e.step_base +
                    sum(range(step)) * e.step_growth
                )

    def print_table(self):
        pprint(self.table)


def parse_args(args):
    parser = argparse.ArgumentParser(description='BLHX friendliness calculator')
    parser.add_argument('exp_per_battle', type=int)
    parser.add_argument('--end-level', type=int, default=100)
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    exp = ExpTable(ExpGrowthTable)
    results = []
    for lvl in range(1, args.end_level):
        exp_diff = exp.table[args.end_level] - exp.table[lvl]
        friendiness = exp_diff / args.exp_per_battle / 16
        results.append((lvl, friendiness))
    print(tabulate(results, headers=['level', 'friendiness']))


if __name__ == '__main__':
    sys.exit(main())
