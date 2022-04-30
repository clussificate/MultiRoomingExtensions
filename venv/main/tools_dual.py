# -*- coding: utf-8 -*-
"""
@Created at 2022/4/29 10:21
@Author: Kurt
@file:tools_dual.py
@Desc:
"""
import numpy as np
import logging

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


def scenario_check(pon, poffs, c, con):
    if 1 / 2 * pon + 2 * c < poffs < 1 - 2 * c and pon <= 4 * c and poffs < pon + con:
        return 1
    elif 1 / 2 * pon + 2 * c < poffs < 1 - 2 * c and pon <= 4 * c and poffs >= pon + con:
        return 2
    elif 1 / 2 * pon + 2 * c < poffs < 1 - 2 * c and pon > 4 * c and poffs < pon + con:
        return 3
    elif 1 / 2 * pon + 2 * c < poffs < 1 - 2 * c and pon > 4 * c and poffs >= pon + con:
        return 4
    elif 1 / 2 * pon + 2 * c < poffs and poffs >= 1 - 2 * c and pon <= 4 * c and poffs < pon + con:
        return 5
    elif 1 / 2 * pon + 2 * c < poffs and poffs >= 1 - 2 * c and pon <= 4 * c and poffs >= pon + con:
        return 6
    elif 1 / 2 * pon + 2 * c < poffs and poffs >= 1 - 2 * c and pon > 4 * c and poffs < pon + con:
        return 7
    elif 1 / 2 * pon + 2 * c < poffs and poffs >= 1 - 2 * c and pon > 4 * c and poffs >= pon + con:
        return 8
    elif 1 / 2 * pon + 2 * c >= poffs and poffs < 1 - 2 * c and 0 < 1 / 2 * poffs - 3 / 4 * pon + c < con:
        return 9
    elif 1 / 2 * pon + 2 * c >= poffs and poffs < 1 - 2 * c and con <= 1 / 2 * poffs - 3 / 4 * pon + c:
        return 10
    elif 1 / 2 * pon + 2 * c >= poffs and poffs < 1 - 2 * c and 1 / 2 * poffs - 3 / 4 * pon + c <= 0:
        return 11
    elif 1 / 2 * pon + 2 * c >= poffs >= 1 - 2 * c and 0 < 1 / 2 * poffs - 3 / 4 * pon + c < con:
        return 12
    elif 1 / 2 * pon + 2 * c >= poffs >= 1 - 2 * c and 1 / 2 * poffs - 3 / 4 * pon + c >= con:
        return 13
    elif 1 / 2 * pon + 2 * c >= poffs >= 1 - 2 * c and 1 / 2 * poffs - 3 / 4 * pon + c <= 0:
        return 14
    else:
        logging.error("pon: {}, poffs: {}, c: {}, con: {}".format(pon, poffs, c, con))
        raise Exception("Unidentified scenario")


def calculate_prior_demand(pon, poffs, c, con, scenario):
    if scenario == 1:
        alpha_o = 1 / (2 * con) * (2 - 2 * pon - 4 * c) * (2 * c - 1 / 2 * pon)
        alpha_so_prior = 1 / (2 * con) * (2 - 6 * c - poffs - 1 / 2 * pon) * (poffs - 1 / 2 * pon - 2 * c)
        alpha_ss_prior = 1 / con * (con - poffs + pon) * (1 - poffs - 2 * c)
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 2:
        if con > 2 * c - 1 / 2:
            alpha_o = 1 / (2 * con) * (2 - 2 * pon - 4 * c) * (2 * c - 1 / 2 * pon)
            alpha_so_prior = 1 / (2 * con) * (2 - con - 3 / 2 * pon - 6 * c) * (con + 1 / 2 * pon - 2 * c)
        else:
            alpha_o = 1 / (2 * con) * con * (2 - 2 * con - 3 * pon)
            alpha_so_prior = 0
        alpha_ss_prior = 0
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 3:
        alpha_o = 0
        if poffs >= pon:
            alpha_so_prior = 1 / (2 * con) * (2 - poffs - pon - 4 * c) * (poffs - pon)
            alpha_ss_prior = 1 / con * (con - poffs + pon) * (1 - 2 * c - poffs)
        else:
            alpha_so_prior = 0
            alpha_ss_prior = 1 / con * con * (1 - 2 * c - poffs)
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 4:
        alpha_o = 0
        alpha_so_prior = 1 / (2 * con) * con * (2 - con - 2 * pon - 4 * c)
        alpha_ss_prior = 0
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 5:
        alpha_o = 1 / (2 * con) * (2 - min(1, 1 / 2 * pon + 4 * c, 3 / 2 * pon) - min(1, 1 / 2 * pon + 4 * c)) * (
            min(2 * c - 1 / 2 * pon, 1 / 2 * (1 - 3 / 2 * pon)))
        alpha_so_prior = 1 / (2 * con) * (1 - min(1 / 2 * pon + 4 * c, 1)) * (1 - 1 / 2 * pon - 4 * c)
        alpha_ss_prior = 0
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 6:
        alpha_ss_prior = 0
        if con >= 1 - pon - 2 * c:
            alpha_o = 1 / (2 * con) * (2 - min(1, 1 / 2 * pon + 4 * c, 3 / 2 * pon) - min(1, 1 / 2 * pon + 4 * c)) * (
                min(2 * c - 1 / 2 * pon, 1 / 2 * (1 - 3 / 2 * pon)))
            alpha_so_prior = 1 / (2 * con) * (1 - min(1 / 2 * pon + 4 * c, 1)) * (1 - 1 / 2 * pon - 4 * c)
        elif 1 - pon * 2 * c > con >= 2 * c - 1 / 2 * pon:
            alpha_o = 1 / (2 * con) * (2 - 2 * pon - 4 * c) * (2 * c - 1 / 2 * pon)
            alpha_so_prior = 1 / (2 * con) * (2 - 3 / 2 * pon - con - 6 * c) * (con - 2 * c + 1 / 2 * pon)
        else:
            alpha_o = 1 / (2 * con) * con * (2 - min(1, 2 * con + 3 / 2 * pon) - min(1, 3 / 2 * pon))
            alpha_so_prior = 0
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 7:
        if pon >= 1 - 2 * c or poffs <= pon:
            alpha_o = 0
            alpha_s = 0
        else:
            alpha_o = 0
            alpha_so_prior = 1 / (2 * con) * (1 - pon - 2 * c) * (1 - pon - 2 * c)
            alpha_ss_prior = 0
            alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 8:
        if pon >= 1 - 2 * c:
            alpha_o = 0
            alpha_s = 0
        else:
            alpha_o = 0
            alpha_ss_prior = 0
            alpha_so_prior = 1 / (2 * con) * min(con, 1 - pon - 2 * c) * (2 - pon - 2 * c - min(1, pon + con + 2 * c))
            alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 9:
        alpha_o = 1 / (2 * con) * (2 - poffs - 2 * c - 3 / 2 * pon) * (1 / 2 * poffs - 3 / 4 * pon + c)
        alpha_so_prior = 0
        alpha_ss_prior = 1 / con * (con - 1 / 2 * poffs + 3 / 4 * pon - c) * (1 - poffs - 2 * c)
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 10:
        alpha_o = 1 / (2 * con) * con * (2 - 2 * con - 3 * pon)
        alpha_so_prior = 0
        alpha_ss_prior = 0
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 11:
        alpha_o = 0
        alpha_so_prior = 0
        alpha_ss_prior = 1 / con * con * (1 - poffs - 2 * c)
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 12:
        alpha_o = 1 / (2 * con) * (1 - min(3 / 2 * pon, 1)) * (1 / 2 - 3 / 4 * pon)
        alpha_so_prior = 0
        alpha_ss_prior = 0
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 13:
        if pon >= 2 / 3:
            alpha_o = 0
        else:
            alpha_o = 1 / (2 * con) * min(con, 1 / 2 * (1 - 3 / 2 * pon)) * (
                    2 - 3 / 2 * pon - min(2 * con + 3 / 2 * pon, 1))
        alpha_so_prior = 0
        alpha_ss_prior = 0
        alpha_s = alpha_so_prior + alpha_ss_prior
        alpha_l = 1 - alpha_o - alpha_s
    elif scenario == 14:
        alpha_o = 0
        alpha_s = 0
        alpha_l = 1 - alpha_o - alpha_s
    else:
        raise Exception("Demand cal fail.")

    alpha_o = myround(alpha_o)
    alpha_s = myround(alpha_s)
    alpha_l = myround(alpha_l)

    return alpha_o, alpha_s, alpha_l


def calculate_store_demand(pon, poff, c, con, alpha_s):
    if pon <= poff <= pon + con:
        prop_ss = 1 / con * (con - poff + pon) * (1 - poff)
        prop_so = 1 / (2 * con) * (2 - poff - pon) * (poff - pon)
    elif poff > pon + con:
        prop_ss = 0
        prop_so = 1 / (2 * con) * (2 - 2 * pon - con) * con
    else:
        prop_ss = 1 / con * (1 - poff) * con
        prop_so = 0

    prop_ss = prop_ss
    prop_so = prop_so

    alpha_ss = myround(alpha_s * prop_ss)
    alpha_so = myround(alpha_s * prop_so)

    return alpha_ss, alpha_so


# def cal_profit(pon, poff, cr, alpha_o, alpha_ss, alpha_so):
#     store_profit = 1 / 2 * alpha_ss * poff + 1 / 2 * alpha_so * pon  # w.p 1/2, we have a=a_H,
#     online_direct_profit = alpha_o * (
#                 1 / 2 * pon + 1 / 4 * (pon - cr))  # w.p 1/2, we have a=a_H, if a=a_L, w.p. 1/2, product return
#     profit = 1 / 2 * (online_direct_profit + store_profit)  # w.p 1/2, we have b=b_H
#     return profit

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
    return 1 / 2 * store_profit


def FindRationalExpectations(pon, poffs, c, con, alpha_s):
    max_store_profit = 0
    max_store_price = 0
    for poff in np.arange(0, 1, 0.01):
        alpha_ss, alpha_so = calculate_store_demand(pon=pon, poff=poff,
                                                    c=c, con=con, alpha_s=alpha_s)
        if alpha_ss > 1 or alpha_ss < 0.0 or alpha_so > 1 or alpha_so < 0.0:
            print("error instore demand")
            print("poffs: {:.3f}, poff: {:.3f},ss: {:.3f},so: {:.3f}".format(
                poffs, poff, alpha_ss, alpha_so))
        current_profit_store = cal_store_profit(pon=pon, poff=poff, alpha_ss=alpha_ss, alpha_so=alpha_so)
        # print("current poff: {:.3}, current store profit: {:.5}".format(poff, current_profit_store))
        if max_store_profit < current_profit_store:
            max_store_profit = current_profit_store
            max_store_price = poff

    # print("poffs:{:.3}, Max store pirce：{:.3}".format(poffs, max_store_price))

    if abs(poffs - max_store_price) >= EPSILON:
        return False, None, None  # no RE in current poffs
    else:
        return True, max_store_profit, max_store_price
