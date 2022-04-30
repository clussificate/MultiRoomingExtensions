# -*- coding: utf-8 -*-
"""
@Created at 2022/4/30 19:33
@Author: Kurt
@file:tools_uniform.py
@Desc:
"""


def scenario_check(p, c, con):
    if p >= 4 * c:
        return 1
    elif p >= 4 * (c - con):
        return 2
    else:
        return 3


def calculate_demand(p, c, con, scenario):
    if scenario == 1:
        if p >= 1 - 2 * c:
            alpha_o = 0
            alpha_s = 0
        else:
            alpha_o = 0
            alpha_s = 1 / con * con * (1 - p - 2 * c)
    elif scenario == 2:
        if p >= 2 / 3:
            alpha_o = 0
            alpha_s = 0
        elif p > 1 - 2 * c:
            alpha_o = 1 / (2 * con) * (1 - 3 / 2 * p)*(1 / 2 - 3 / 4 * p)
            alpha_s = 0
        else:
            alpha_o = 1 / (2 * con) * (2 - 5 / 2 * p - 2 * c)*(c - 1 / 4 * p)
            alpha_s = 1 / con * (con - c + 1 / 4 * p) * (1 - p - 4 * c)
    else:
        alpha_s = 0
        if p >= 2 / 3:
            alpha_o = 0
        elif p >= 2 / 3 * (1 - 2 * con):
            alpha_o = 1 / (2 * con) * (1 - 3 / 2 * p) * (1 / 2 - 3 / 4 * p)
        else:
            alpha_o = 1 / (2 * con)*con*(2 - 3*p - 2*con)
    return alpha_o, alpha_s


def calculate_profit(cr, p, alpha_o, alpha_s):
    online_profit = alpha_o * (1/2 * p + 1/2 * (1/2*p - 1/2*cr))  # w.p. 1/2, b=b_H. Then w.p. 1/2 consumer returns it.
    store_profit = alpha_s * 1/2 * p                   # w.p. 1/2, b=b_H
    profit = 1/2 * store_profit + 1/2 * online_profit  # w.p. 1/2, a=a_H
    return profit
