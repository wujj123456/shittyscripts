#!/usr/bin/env python3
# A calculator simply tells me if I am currently underpaying
# All stupid online calculators ask me to predict future

import sys


def calc_income_tax(income):
    brackets = [
        (9700, 0.1),
        (39475, 0.12),
        (84200, 0.22),
        (160725, 0.24),
        (204100, 0.32),
        (510300, 0.35),
        (sys.maxsize, 0.37),
    ]

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
        (39375, 0),
        (434550, 0.15),
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


def prompt(text):
    result = input(f"{text}: ")
    if result.strip():
        return int(result)
    else:
        return 0


def main():
    income = prompt("YTD Gross Pay")
    income -= prompt("Pre-tax deduction")
    short_gain = prompt("YTD short-term gain")
    long_gain = prompt("YTD long-term gain")
    loss_carryover = prompt("Loss carryover")
    income = income + short_gain - loss_carryover

    short_gain_amend = max(0, short_gain - loss_carryover)
    long_gain_amend = max(0, long_gain - max(0, loss_carryover - short_gain))

    withhold = prompt("YTD withhold")
    withhold += prompt("YTD payments")

    it = calc_income_tax(income)
    ltt = calc_long_term_tax(income, long_gain)
    niit = calc_niit(income, long_gain_amend + short_gain_amend)
    total = it + ltt + niit

    print(f"income tax: {it} long-term: {ltt} NIIT: {niit}")
    print(f"paid: {withhold} required: {total} owe: {total - withhold}")


main()
