# -*- coding: utf-8 -*-
"""
@Created at 2022/4/29 10:21
@Author: Kurt
@file:tools_dual.py
@Desc:
"""
import numpy as np

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


def scenario_check(pon, poffs, s, h, c):
    if myround(poffs - 1 / 2 * pon - 2 * c) > 0:
        if myround(pon - 4 * c) <= 0:
            if myround(h - poffs + pon) >= 0:
                return 1
            else:
                return 2
        else:
            return 3
    else:
        return 4


def calculate_prior_demand(pon, poffs, c, s, h, scenario):
    if scenario == 1:
        alpha_ss_prior = 1 / (h - s) * (1 - min(1, poffs + 2 * c)) * (h - max(s, poffs - pon))
        if myround(s - 2 * c + 1 / 2 * pon) <= 0:
            alpha_o = 1 / (2 * (h - s)) * (min(2 * c - 1 / 2 * pon, 1 / 2 * (1 - 3 / 2 * pon)) - s) * (
                        2 - min(1, 1 / 2 * pon + 4 * c) - min(1, 2 * s + 3 / 2 * pon))
            alpha_so_prior = 1 / (2 * (h - s)) * (poffs - pon - min(poffs - pon, max(s, 2 * c - 1 / 2 * pon))) * (
                    2 - min(1, poffs - 2 * c) - min(1, 1 / 2 * pon + 4 * c))
        elif myround(s - poffs + pon) <= 0:
            alpha_o = 0
            alpha_so_prior = 1 / (2 * (h - s)) * (min(poffs - pon, 1 - pon - 2 * c) - s) * (
                        2 - min(1, poffs + 2 * c) - min(1, pon + s + 2 * c))
        else:
            alpha_o = 0
            alpha_so_prior = 0
    elif scenario == 2:
        alpha_ss_prior = 0
        if myround(h - 2 * c + 1 / 2 * pon) > 0:
            #  if s<2*c-1/2*pon
            if myround(s - 2 * c + 1 / 2 * pon) <= 0:
                alpha_o = 1 / (2 * (h - s)) * (min(2 * c - 1 / 2 * pon, 1 / 2 * (1 - 3 / 2 * pon)) - s) * (
                            2 - min(1, 1 / 2 * pon + 4 * c) - min(1, 2 * s + 3 / 2 * pon))
                alpha_so_prior = 1 / (2 * (h - s)) * (min(h, 1 - pon - 2 * c) - (2 * c - 1 / 2 * pon)) * (
                            2 - min(1, pon + h + 2 * c) - min(1, 1 / 2 * pon + 4 * c))
            else:
                alpha_o = 0
                alpha_so_prior = 1 / (2 * (h - s)) * (min(h, 1 - pon - 2 * c) - s) * (
                            2 - min(1, pon + h + 2 * c) - min(1, pon + s + 2 * c))
        else:
            alpha_o = 1 / (2 * (h - s)) * (min(h, 1 / 2 * (1 - 3 / 2 * pon)) - s) * (
                        2 - min(1, 2 * h + 3 / 2 * pon) - min(1, 2 * s + 3 / 2 * pon))
            alpha_so_prior = 0
    elif scenario == 3:
        alpha_o = 0
        if myround(poffs - pon) >= 0:
            alpha_so_prior = 1 / (2 * (h - s)) * (
                        min(h, poffs - pon, 1 - pon - 2 * c) - min(s, poffs - pon, 1 - pon - 2 * c)) * (
                                     2 - min(1, poffs + 2 * c, pon + h + 2 * c) - min(1, poffs + 2 * c,
                                                                                      pon + s + 2 * c))
            alpha_ss_prior = 1 / (h - s) * (max(poffs - pon, h) - max(poffs - pon, s)) * (1 - min(1, poffs + 2 * c))
        else:
            alpha_so_prior = 0
            alpha_ss_prior = 1 / (h - s) * (h - s) * (1 - min(1, poffs + 2 * c))
    elif scenario == 4:
        alpha_so_prior = 0
        if myround(1 / 2 * poffs - 3 / 4 * pon + c) >= 0:
            alpha_o = 1 / (2 * (h - s)) * (min(h, 1 / 2 * poffs - 3 / 4 * pon + c, 1 / 2 * (1 - 3 / 2 * pon)) -
                                           min(s, 1 / 2 * poffs - 3 / 4 * pon + c, 1 / 2 * (1 - 3 / 2 * pon))) * (
                              2 - min(1, poffs + 2 * c, 2 * h + 3 / 2 * pon) - min(1, 2 * s + 3 / 2 * pon))
            alpha_ss_prior = 1 / (h - s) * (
                        max(h, 1 / 2 * poffs - 3 / 4 * pon + c) - max(s, 1 / 2 * poffs - 3 / 4 * pon + c)) * (
                                     1 - min(1, poffs + 2 * c))
        else:
            alpha_o = 0
            alpha_ss_prior = 1 / (h - s) * (h - s) * (1 - min(1, poffs + 2 * c))
    else:
        raise Exception("Prior demand cal fail!")

    alpha_o = myround(alpha_o)
    alpha_so_prior = myround(alpha_so_prior)
    alpha_ss_prior = myround(alpha_ss_prior)
    if 0 <= alpha_so_prior <= 1 and 0 <= alpha_ss_prior <= 1 and 0 <= alpha_o <= 1:
        alpha_s = alpha_so_prior + alpha_ss_prior
    else:
        print("c: {}, s:{}, h:{}, pon: {:.3f}, poffs: {:.3f}, scenario: {}".format(
            c, s, h, pon, poffs, scenario))
        print("alpha_o:{:.5f}, alpha_so:{:.5f}, alpha_ss: {:.5f}".format(alpha_o, alpha_so_prior, alpha_ss_prior))
        raise Exception("error prior demand!")

    alpha_l = 1 - alpha_o - alpha_s
    alpha_s = myround(alpha_s)
    alpha_l = myround(alpha_l)

    return alpha_o, alpha_s, alpha_l


def store_utility_compare(loc, pon, poff):
    # a consumer located at [con, theta]. The offline shopping cost c is sunk
    u_ss = 1 / 2 * (loc[1] - poff)
    u_so = 1 / 2 * (loc[1] - pon - loc[0])
    u_l = 0

    if myround(u_ss - max(u_so, u_l)) >= 0:
        return "ss"
    elif myround(u_so - u_l) >= 0:
        return "so"
    else:
        return "l"


def cal_profit(pon, cr, alpha_o, store_profit):
    online_direct_profit = alpha_o * (
            1 / 2 * pon + 1 / 4 * (pon - cr))  # w.p 1/2, we have a=a_H, if a=a_L, w.p. 1/2, product return
    profit = 1 / 2 * online_direct_profit + store_profit  # w.p 1/2, we have b=b_H
    return profit


def cal_store_profit(pon, poff, alpha_ss, alpha_so):
    """
    This method optimizes the retailer's profit from in-store consumers
    """
    store_profit = 1 / 2 * alpha_ss * poff + 1 / 2 * alpha_so * pon  # w.p 1/2, we have a=a_H,
    return 1 / 2 * store_profit  # w.p 1/2, we have b=b_H


def FindRationalExpectations(c, s, h, pon, poffs, scenario, step=0.01):
    max_store_profit = 0
    max_store_price = 0
    max_store_demand_online = 0
    max_store_demand_offline = 0
    for poff in np.arange(0, 1, step):
        store_scenario = store_scenario_check(c=c, s=s, h=h, pon=pon, poffs=poffs, poff=poff, scenario=scenario)
        alpha_ss, alpha_so = calculate_store_demand(c=c, s=s, h=h, pon=pon, poffs=poffs, poff=poff,
                                                    store_scenario=store_scenario)
        current_profit_store = cal_store_profit(pon=pon, poff=poff, alpha_ss=alpha_ss, alpha_so=alpha_so)
        # print("current poff: {:.3}, current store profit: {:.5}".format(poff, current_profit_store))
        if max_store_profit < current_profit_store:
            max_store_demand_online = alpha_so
            max_store_demand_offline = alpha_ss
            max_store_profit = current_profit_store
            max_store_price = poff

    # print("poffs:{:.3}, Max store pirce：{:.3}".format(poffs, max_store_price))

    if abs(poffs - max_store_price) >= EPSILON:
        return False, None, None, None, None  # no RE in current poffs
    else:
        return True, max_store_profit, max_store_price, max_store_demand_online, max_store_demand_offline


def calculate_store_demand_shape1(c, s, h, pon, poffs, poff):
    if myround(h - (poffs - pon + 2 * c)) <= 0:
        # no instore consumer leaves with empty hand.
        alpha_so = 1 / (h - s) * (min(poff - pon, h) - min(poff - pon, s)) * (1 - poffs - 2 * c)
        alpha_ss = 1 / (h - s) * (max(poff - pon, h) - max(poff - pon, s)) * (1 - poffs - 2 * c)
    elif myround(s - (poffs - pon + 2 * c)) <= 0:
        alpha_so = 1 / (2 * (h - s)) * (min(poff - pon, h) - max(poffs - pon + 2 * c, poff - pon)) * (
                    2 - poff - min(pon + h, poffs + 2 * c))
        +1 / (h - s) * (min(poffs - pon + 2 * c, poff - pon) - min(poff - pon, s)) * (1 - poffs - 2 * c)
        alpha_ss = 1 / (h - s) * (max(h, poff - pon) - max(s, poff - pon)) * (1 - max(poff, poffs + 2 * c))
    else:
        alpha_so = 1 / (2 * (h - s)) * (min(poff - pon, h) - min(poff - pon, s)) * (
                2 - min(poff, pon + h) - (pon + s))
        alpha_ss = 1 / (h - s) * (max(poff - pon, h) - max(poff - pon, s)) * (1 - max(poff, poffs + 2 * c))
    return alpha_so, alpha_ss


def calculate_store_demand_shape2(c, s, h, pon, poffs, poff):
    if myround(1 - poffs - 2 * c) >= 0:
        # if there are "ss_prior" consumers before visiting the store.
        if myround(h - (poffs - pon + 2 * c)) > 0:
            # some consumers will leave
            alpha_so = 1 / (2 * (h - s)) * (min(poffs - pon, poff - pon) - min(poff - pon, s)) * (
                        2 - min(poff + 2 * c, poffs + 2 * c) - (pon + s + 2 * c))
            +1 / (h - s) * (min(poffs - pon + 2 * c, poff - pon) - min(poffs - pon, poff - pon)) * (1 - poffs - 2 * c)
            +1 / (2 * (h - s)) * (min(h, poff - pon, poffs - pon + 2 * c) - (poffs - pon + 2 * c)) * (
                        2 - min(pon + h, poff) - (poffs + 2 * c))
            alpha_ss = 1 / (h - s) * (max(h, poff - pon) - max(poff - pon, poffs - pon)) * (
                        1 - max(poffs + 2 * c, poff))
            +1 / (2 * (h - s)) * (max(min(poffs - pon - max(poff - pon, s)), 0)) * (
                        2 - (poffs + 2 * c) - max(pon + s + 2 * c, poff + 2 * c))
        else:
            # all consumers will buy
            alpha_so = 1 / (2 * (h - s)) * (min(poff - pon, poffs - pon) - min(poff - pon, s)) * (
                        2 - min(poffs + 2 * c, poff + 2 * c) - (pon + s + 2 * c))
            +1 / (h - s) * (min(poff - pon, h) - min(poff - pon, poffs - pon)) * (1 - poffs - 2 * c)
            alpha_ss = 1 / (h - s) * (max(h, poff - pon) - max(s, poff - pon)) * (1 - (poffs - 2 * c))
            +1 / (2 * (h - s)) * (max(poff - pon, poffs - pon) - max(poff - pon, s)) * (
                        2 - (poffs + 2 * c) - max(pon + s + 2 * c, poff + 2 * c))
    else:
        alpha_so = 1 / (2 * (h - s)) * (min(poff - pon, 1 - pon - 2 * c) - min(poff - pon, s)) * (
                    2 - min(1, poff + 2 * c) - (pon + s + 2 * c))
        alpha_ss = 1 / (2 * (h - s)) * (max(poffs - pon, poff - pon) - max(poff - pon, s)) * (
                    1 - max(poff + 2 * c, pon + s + 2 * c))
    return alpha_so, alpha_ss


def calculate_store_demand_shape3(c, s, h, pon, poffs, poff):
    if myround(pon + h + 2 * c - 1) <= 0:
        alpha_so = 1 / (2 * (h - s)) * (min(poff - pon, h) - min(poff - pon, s)) * (
                    2 - min(poff + 2 * c, pon + h + 2 * c) - (pon + s + 2 * c))
        alpha_ss = 1 / (2 * (h - s)) * (max(poff - pon, h) - max(poff - pon, s)) * (
                    2 - max(poff + 2 * c, pon + s + 2 * c) - (pon + h + 2 * c))
    else:
        alpha_so = 1 / (2 * (h - s)) * (min(poff - pon, 1 - pon - 2 * c) - min(poff - pon, s)) * (
                    2 - min(poff + 2 * c, 1) - (pon + s + 2 * c))
        alpha_ss = 1 / (2 * (h - s)) * (max(poff - pon, 1 - pon - 2 * c) - max(poff - pon, s)) * (
                    1 - max(poff + 2 * c, pon + s + 2 * c))
    return alpha_so, alpha_ss


def calculate_store_demand(c, s, h, pon, poffs, poff, store_scenario):
    # lower bound of con of in-store consumers.
    k = max(s, min(1 / 2 * poffs - 3 / 4 * pon + c, 2 * c - 1 / 2 * pon))

    if store_scenario == 1:
        alpha_so, alpha_ss = calculate_store_demand_shape1(c=c, s=k, h=h, pon=pon, poffs=poffs, poff=poff)
    elif store_scenario == 2:
        alpha_so, alpha_ss = calculate_store_demand_shape2(c=c, s=k, h=h, pon=pon, poffs=poffs, poff=poff)
    elif store_scenario == 3:
        alpha_so, alpha_ss = calculate_store_demand_shape3(c=c, s=k, h=h, pon=pon, poffs=poffs, poff=poff)
    else:
        print("c: {}, k:{}, h:{}, pon: {:.3f}, poffs: {:.3f}, store scenario: {}".format(
            c, k, h, pon, poffs, store_scenario))
        raise Exception("error store scenario!")

    alpha_so = myround(alpha_so)
    alpha_ss = myround(alpha_ss)
    if alpha_ss > 1 or alpha_ss < 0.0 or alpha_so > 1 or alpha_so < 0.0:
        print("c: {}, s:{}, k:{}, h:{},poffs: {:.3f}, poff: {:.3f},ss: {:.3f},so: {:.3f}".format(
            c, s, k, h, poffs, poff, alpha_ss, alpha_so))
        raise Exception("error in store demand!")
    return alpha_so, alpha_ss


def store_scenario_check(c, s, h, pon, poffs, poff, scenario):
    store_scenario = 0
    if scenario == 1:
        if myround(s - poffs + pon) >= 0:
            store_scenario = 1
        else:
            store_scenario = 2
    elif scenario == 2:
        store_scenario = 3
    elif scenario == 3:
        if myround(s - poffs + pon) < 0:
            store_scenario = 2
        else:
            store_scenario = 1
    else:
        store_scenario = 1

    return store_scenario