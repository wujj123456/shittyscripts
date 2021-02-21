#!/usr/bin/env python3
# A calculator simply tells me if I am currently underpaying
# All stupid online calculators ask me to predict future

import argparse
import sys


# (upto, tax rate)
FEDERAL = [
    (9950, 0.1),
    (40525, 0.12),
    (86375, 0.22),
    (164925, 0.24),
    (209425, 0.32),
    (523600, 0.35),
    (sys.maxsize, 0.37),
]

CA = [
    (8932, 0.01),
    (21175, 0.02),
    (33421, 0.04),
    (46394, 0.06),
    (58634, 0.08),
    (299508, 0.093),
    (359407, 0.103),
    (599012, 0.113),
    (1000000, 0.123),
    (sys.maxsize, 0.133),
]


def calc_income_tax(income, brackets):
    tax = 0
    prev = 0
    for bracket, rate in brackets:
        if income > bracket:
            tax += (bracket - prev) * rate
        else:
            tax += (income - prev) * rate
            break
        prev = bracket
        income -= bracket - prev
    return tax


def calc_long_term_tax(income, gain):
    brackets = [
        (40000, 0),
        (441450, 0.15),
        (sys.maxsize, 0.2),
    ]

    if gain < 0:
        return 0
    for bracket, rate in brackets:
        if income <= bracket:
            return gain * rate

def calc_niit(income, gain):
    if gain < 0:
        return 0
    cutoff = 200000
    if income + gain > cutoff:
        return min(gain, income + gain - cutoff) * 0.038
    return 0


def annihilate(a, b):
    if a * b >= 0:
        return a, b
    if a > 0:
        return max(0, a + b), min(0, a + b)
    else:
        return min(0, a + b), max(0, a + b)


def parse_args():
    parser = argparse.ArgumentParser(description="Simple Tax Calculator")
    parser.add_argument(
        "-i", "--income", type=float, required=True, help="YTD Gross Pay"
    )
    parser.add_argument(
        "-d", "--deduction", type=float, required=True, help="YTD Pre-tax Deduction"
    )
    parser.add_argument(
        "-sg", "--st-gain", type=float, default=0, help="YTD short-term gain"
    )
    parser.add_argument(
        "-lg", "--lt-gain", type=float, default=0, help="YTD long-term gain"
    )
    parser.add_argument(
        "-sc", "--st-carryover", type=float, default=0, help="Short-term Loss Carryover"
    )
    parser.add_argument(
        "-lc", "--lt-carryover", type=float, default=0, help="Long-term Loss Carryover"
    )

    parser.add_argument(
        "-w", "--withhold", type=float, required=True, help="YTD Withhold"
    )
    parser.add_argument(
        "-p", "--payments", type=float, default=0, help="YTD Quarterly Payments"
    )

    parser.add_argument(
        "--state", action="store_true", help="Calculate CA tax instead of federal"
    )
    return parser.parse_args()


def federal(args):
    income = args.income - args.deduction
    st_gain = args.st_gain + args.st_carryover
    lt_gain = args.lt_gain + args.lt_carryover
    st_gain, lt_gain = annihilate(st_gain, lt_gain)
    gain = st_gain + lt_gain
    if gain < 0:
        income += max(-3000, gain)
    else:
        income += st_gain
    print(f"Gross income: {income:.2f}")
    print(f"Long-term gain: {lt_gain:.2f}")
    print(f"Short-term gain: {st_gain:.2f}")
    print()

    withhold = args.withhold + args.payments
    income_tax = calc_income_tax(income, FEDERAL)
    lt_tax = calc_long_term_tax(income, lt_gain)
    niit = calc_niit(income, gain)
    total = income_tax + lt_tax + niit
    print(f"Income tax: {income_tax:.2f}")
    print(f"Long-term gain tax: {lt_tax:.2f}")
    print(f"NIIT: {niit:.2f}")
    print(f"Paid: {withhold:.2f} ({withhold / total * 100:.2f}%)")
    print(f"Required: {total:.2f}")
    print(f"Owe: {total - withhold:.2f}")


def ca(args):
    income = args.income - args.deduction
    gain = args.st_gain + args.st_carryover + args.lt_gain + args.lt_carryover
    if gain < 0:
        income += max(-3000, gain)
    else:
        income += gain
    print(f"Gross income: {income:.2f}")

    withhold = args.withhold + args.payments
    tax = calc_income_tax(income, CA)
    print(f"Income tax: {tax:.2f}")
    print(f"Paid: {withhold:.2f}  ({withhold / tax * 100:.2f}%)")
    print(f"Owe: {tax - withhold:.2f}")


def main():
    args = parse_args()
    if args.st_carryover > 0 or args.lt_carryover > 0:
        print("Carryover must be negative")
        return -1

    if args.state:
        ca(args)
    else:
        federal(args)


sys.exit(main())
