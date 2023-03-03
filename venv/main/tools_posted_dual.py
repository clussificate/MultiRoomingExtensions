# -*- coding: utf-8 -*-
"""
@Created at 2023/3/2 19:14
@Author: Kurt
@file:tools_posted_dual.py
@Desc:
"""

import numpy as np

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


def scenario_check(c, pon, poff):
    if myround(poff - 1 / 2 * pon - 2 * c) >= 0:
        store_scenario = 1
    else:
        store_scenario = 2
    return store_scenario


def calculate_profit(cr, pon, poff, alpha_o, alpha_ss, alpha_so):
    online_profit = alpha_o * (
            1 / 2 * pon + 1 / 2 * (1 / 2 * pon - 1 / 2 * cr))  # w.p. 1/2, b=b_H. Then w.p. 1/2 consumer returns it.
    store_profit = alpha_ss * 1 / 2 * poff  # w.p. 1/2, b=b_H
    showroom_profit = alpha_so * 1 / 2 * pon
    profit = 1 / 2 * store_profit + 1 / 2 * online_profit + 1 / 2 * showroom_profit  # w.p. 1/2, a=a_H
    return profit


def calculate_shape1(c, s, h, pon, poff):
    alpha_o = 1 / (2 * (h - s)) * (min(2 * c - 1 / 2 * pon, h) - min(2 * c - 1 / 2 * pon, s)) * (
            1 - min(1, 1 / 2 * pon + 4 * c, 2 * h + 3 / 2 * pon)
            + 1 - min(1, 2 * s + 3 / 2 * pon))

    alpha_so = 1 / (2 * (h - s)) * (max(min(h, poff - pon, 1 - pon - 2 * c), 2 * c - 1 / 2 * pon) -
                                    min(max(s, 2 * c - 1 / 2 * pon), poff - pon)) * (
                       1 - min(1, poff + 2 * c, pon + h + 2 * c) + 1 - min(1,
                                                                           max(1 / 2 * pon + 4 * c, pon + s + 2 * c)))

    alpha_ss = 1 / (h - s) * (max(poff - pon, h) - max(poff - pon, s)) * (1 - min(1, poff + 2 * c))
    return alpha_o, alpha_so, alpha_ss


def calculate_shape2(c, s, h, pon, poff):
    alpha_o = 1 / (2 * (h - s)) * (min(h, 1 / 2 * poff - 3 / 4 * pon + c) - min(s, 1 / 2 * poff - 3 / 4 * pon + c)) * (
            1 - min(1, poff + 2 * c, 2 * h + 3 / 2 * pon) + 1 - min(1, 2 * s + 3 / 2 * pon))
    alpha_so = 0
    alpha_ss = 1 / (h - s) * (max(1 / 2 * poff - 3 / 4 * pon + c, h) - max(1 / 2 * poff - 3 / 4 * pon + c, s)) * (
            1 - min(1, poff + 2 * c))
    return alpha_o, alpha_so, alpha_ss


def calculate_demand(c, s, h, pon, poff, scenario):
    # lower bound of con of in-store consumers.

    if scenario == 1:
        alpha_o, alpha_so, alpha_ss = calculate_shape1(c, s, h, pon, poff)
    elif scenario == 2:
        alpha_o, alpha_so, alpha_ss = calculate_shape2(c, s, h, pon, poff)
    else:
        print("c: {}, h:{}, pon: {:.3f}, store scenario: {}".format(
            c, h, pon, scenario))
        raise Exception("error store scenario!")

    alpha_o = myround(alpha_o)
    alpha_so = myround(alpha_so)
    alpha_ss = myround(alpha_ss)
    if 0 <= alpha_o <= 1 and 0 <= alpha_so <= 1 and 0 <= alpha_ss <= 1:
        return alpha_o, alpha_so, alpha_ss
    else:
        print("c: {}, s:{}, h:{}, pon:{} poff: {:.3f}, scenario: {}, o:  {:.3f}, ss: {:.3f},so: {:.3f}".format(
            c, s, h, pon, poff, scenario, alpha_o, alpha_ss, alpha_so))
        raise Exception("error in store demand!")
