# -*- coding: utf-8 -*-
"""
@Created at 2022/7/2 15:38
@Author: Kurt
@file:uniform.py
@Desc:
"""
from collections import Counter
import numpy as np
import logging

logging.basicConfig()
logger = logging.getLogger("uniform")
logger.setLevel(logging.DEBUG)

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


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
        behaviors_tie_online = [utility_tie_online(loc=consumer, c=c, con=con, m=m, p=p) for consumer in consumers]
        behaviors_tie_offline = [utility_tie_offline(loc=consumer, c=c, con=con, m=m, p=p) for consumer in consumers]

        return behaviors_tie_online, behaviors_tie_offline
    else:
        # if there is no tie, utility_tie_online and utility_tie_offline are equivalent.
        behaviors = [utility_tie_online(loc=consumer, c=c, con=con, m=m, p=p) for consumer in consumers]

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
        self.p = 0
        self.profit = 0
        self.solve(c=c, con=con, cr=cr, m=m, step=step, density=density)

    def solve(self, c, con, cr, m, step, density):
        consumers = np.arange(0, 1, density)

        optimal_profit = 0
        optimal_price = 0
        for p in np.arange(0, 1, step):
            logger.debug("current loop: p={:.3f}".format(p))
            if myround(1 / 2 * m * p * p - 1 / 2 * p + c - con) == 0:
                behaviors_tie_online, behaviors_tie_offline = simulate_behavior(consumers=consumers,
                                                                                c=c, con=con, m=m, p=p)
                profit_tie_online = cal_profit(m=m, p=p, cr=cr, behaviors=behaviors_tie_online)
                profit_tie_offline = cal_profit(m=m, p=p, cr=cr, behaviors=behaviors_tie_offline)
                profit = max(profit_tie_online, profit_tie_offline)
            else:
                behaviors = simulate_behavior(consumers=consumers, c=c, con=con, m=m, p=p)
                profit = cal_profit(m=m, p=p, cr=cr, behaviors=behaviors)

            if profit - optimal_profit > 0:
                optimal_profit = profit
                optimal_price = p
        self.p = optimal_price
        self.profit = optimal_profit


if __name__ == "__main__":
    c = 0.1
    cr = 0.32
    con = 0.05
    m = 1 / 4
    uniform_ins = uniform(c=c, con=con, cr=cr, m=m, step=0.001, density=0.001)
    print(uniform_ins.p, uniform_ins.profit)
