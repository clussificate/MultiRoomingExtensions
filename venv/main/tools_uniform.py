# -*- coding: utf-8 -*-
"""
@Created at 2022/4/30 19:33
@Author: Kurt
@file:tools_uniform.py
@Desc:
"""
EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


def scenario_check(p, c, s, h):
    if myround(p - 4 * (c - s)) >= 0:
        return 2
    elif myround(p - 4 * (c - h)) <= 0:
        return 3
    else:
        return 1


def calculate_demand(p, c, s, h, scenario):
    if scenario == 1:
        alpha_o = 1 / (2 * (h - s)) * (2 - min(1, p + 2 * c) - min(1, 3 / 2 * p + 2 * s)) * (
                min(c - 1 / 4 * p, 1 / 2 - 3 / 4 * p) - min(s, 1 / 2 - 3 / 4 * p))
        alpha_s = 1 / (h - s) * (1 - min(1, p + 2 * c)) * (h - min(c - 1 / 4 * p, 1 / 2 - 3 / 4 * p))
    elif scenario == 2:
        alpha_o = 0
        alpha_s = 1 / (h - s) * (1 - min(1, p + 2 * c)) * (h - s)
    else:
        alpha_s = 0
        alpha_o = 1 / (2 * (h - s)) * (2 - min(1, 3 / 2 * p + 2 * h) - min(1, 3 / 2 * p + 2 * s)) * (
                    min(h, 1 / 2 - 3 / 4 * p) - min(s, 1 / 2 - 3 / 4 * p))
    alpha_o = myround(alpha_o)
    alpha_s = myround(alpha_s)
    if 0 <= alpha_o <= 1 and 0 <= alpha_s <= 1:
        return alpha_o, alpha_s
    else:
        print("c: {}, s:{}, h:{}, p: {:.3f}, scenario: {}".format(
            c, s, h, p, scenario))
        print("alpha_o:{:.5f}, alpha_s: {:.5f}".format(alpha_o, alpha_s))
        raise Exception("error prior demand!")


def calculate_profit(cr, p, alpha_o, alpha_s):
    online_profit = alpha_o * (
            1 / 2 * p + 1 / 2 * (1 / 2 * p - 1 / 2 * cr))  # w.p. 1/2, a=a_H. Then w.p. 1/2 consumer returns it.
    store_profit = alpha_s * 1 / 2 * p  # w.p. 1/2, b=b_H
    profit = 1 / 2 * store_profit + 1 / 2 * online_profit  # w.p. 1/2, b=b_H
    return profit
