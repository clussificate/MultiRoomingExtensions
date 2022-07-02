# -*- coding: utf-8 -*-
"""
@Created at 2022/7/2 15:38
@Author: Kurt
@file:uniform.py
@Desc:
"""
import ray
from collections import Counter
import numpy as np

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


@ray.remote
def utility_tie_online(loc, c, con, m, p):
    """
    In this function, the tie is broken by assuming consumers buy online directly
    :param loc: value of theta
    """
    u_o = 1 / 2 * loc + 1 / 2 * m * p * p - p - con
    u_s = 1 / 2 * (loc - p) - c
    if myround(u_o - u_s) >= 0:
        if myround(u_o) >= 0:
            return "o"
        else:
            return "l"
    else:
        if myround(u_s) >= 0:
            return "s"
        else:
            return "l"


@ray.remote
def utility_tie_offline(loc, c, con, m, p):
    """
    In this function, the tie is broken by assuming consumers visit the store
    :param loc: value of theta
    """
    u_o = 1 / 2 * loc + 1 / 2 * m * p * p - p - con
    u_s = 1 / 2 * (loc - p) - c
    if myround(u_o - u_s) > 0:
        if myround(u_o) >= 0:
            return "o"
        else:
            return "l"
    else:
        if myround(u_s) >= 0:
            return "s"
        else:
            return "l"


# @ray.remote
# def get_consumer_behavior(consumers, c, con, m, p):
#     tie_online = [utility_tie1(c=c, con=con, m=m, p=p, loc=consumer) for consumer in consumers]
#     tie_offline = [utility_tie2(c=c, con=con, m=m, p=p, loc=consumer) for consumer in consumers]
#     return tie_online, tie_offline

def get_demand(behaviors):
    total = len(behaviors)
    count = Counter(behaviors)
    alpha_o = count['o'] / total
    alpha_s = count['s'] / total
    alpha_l = count['l'] / total
    assert myround(alpha_o + alpha_s + alpha_l - 1) == 0

    return alpha_o, alpha_s


def simulate_behavior(consumers, c, con, m, p):
    # if consumers are indifferent between buying online directly and visiting the store,
    # we break the tie by maximizing the retailer's profit
    if myround(1 / 2 * m * p * p - 1 / 2 * p + c - con) == 0:
        result_id_online = []
        result_id_offline = []
        for consumer in consumers:
            result_id_online.append(utility_tie_online.remote(loc=consumer, c=c, con=con, m=m, p=p))
            result_id_offline.append(utility_tie_offline.remote(loc=consumer, c=c, con=con, m=m, p=p))
        behaviors_tie_online = ray.get(result_id_online)
        behaviors_tie_offline = ray.get(result_id_offline)

        return behaviors_tie_online, behaviors_tie_offline
    else:
        # if there is no tie, utility_tie_online and utility_tie_offline are equivalent.
        result_id = []
        for consumer in consumers:
            result_id.append(utility_tie_online.remote(loc=consumer, c=c, con=con, m=m, p=p))
        behaviors = ray.get(result_id)

        return behaviors


def cal_profit(m, p, cr, behaviors):
    alpha_o, alpha_s = get_demand(behaviors)
    online_profit = alpha_o * (1 / 2 * p + 1 / 2 * ((1 - m * p) * p - m * p * cr))  # w.p. 1/2, b=b_H.
    store_profit = alpha_s * 1 / 2 * p  # w.p. 1/2, b=b_H
    profit = 1 / 2 * store_profit + 1 / 2 * online_profit  # w.p. 1/2, a=a_H
    return profit


class uniform:

    def __init__(self, c, con, cr, m, step=0.001, density=0.001):
        """
        :param c: offline shopping cost
        :param con: online shopping cost
        :param cr: retailer return cost
        :param m: return probability of direct online purchase
        :param step: step size of price
        :param density=0.001: density of consumers
        """
        self.solve(c=c, con=con, cr=cr, m=m, step=step, density=density)

    def solve(self, c, con, cr, m, step, density):
        consumers = np.arange(0, 1, density)

        for p in range(0, 1, step):
            if myround(1 / 2 * m * p * p - 1 / 2 * p + c - con) == 0:
                behaviors_tie_online, behaviors_tie_offline = simulate_behavior(consumers=consumers,
                                                                                c=c, con=con, m=m, p=p)
                profit_tie_online = cal_profit(m=m, p=p, cr=cr, behaviors=behaviors_tie_online)
                profit_tie_offline = cal_profit(m=m, p=p, cr=cr, behaviors=behaviors_tie_offline)
                profit = max(profit_tie_online, profit_tie_offline)
            else:
                behaviors = simulate_behavior(consumers=consumers, c=c, con=con, m=m, p=p)
                profit = cal_profit(m=m, p=p, cr=cr, behaviors=behaviors)




        pass
