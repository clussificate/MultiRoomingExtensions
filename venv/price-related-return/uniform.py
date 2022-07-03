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
import ray
import matplotlib.pyplot as plt

logging.basicConfig()
logger = logging.getLogger("uniform")
logger.setLevel(logging.ERROR)

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

    def __init__(self, c, con, cr, return_prop, step=0.001, density=0.001):
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
        self.solve(c=c, con=con, cr=cr, return_prop=return_prop, step=step, density=density)

    def solve(self, c, con, cr, return_prop, step, density):
        consumers = np.arange(0, 1, density)

        optimal_profit = 0
        optimal_price = 0
        for p in np.arange(0.001, 1, step):
            if isinstance(return_prop, str):
                m = 1 / (2 * p)
            else:
                m = return_prop
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


@ray.remote
def get_uniform_result(c, con, cr, return_prop, step, density):
    uniform_ins = uniform(c=c, con=con, return_prop=return_prop, cr=cr, step=step, density=density)
    return uniform_ins.p, uniform_ins.profit


if __name__ == "__main__":
    sel_c = np.arange(0.1, 0.155, 0.005)
    cr = 0.32
    con = 0.05
    return_prop = 1  # if this is a string, it means that we set m=1/(2*p), which degrades to the baseline model.

    result_ids = []
    for c in sel_c:
        result_ids.append(get_uniform_result.remote(c=c, con=con, cr=cr, return_prop=return_prop,
                                                    step=0.001, density=0.0001))

    results = ray.get(result_ids)
    p_list = []
    pid_list = []
    for result in results:
        p_list.append(result[0])
        pid_list.append(result[1])
    fig = plt.figure(figsize=(5, 8))
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(sel_c, pid_list, c='red', ls='--', ms=6, marker='*', label="profit")

    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(sel_c, p_list, c='blue', ls='--', ms=6, marker='o', label="uniform price")

    # ax1.axis(ymin=0.026, ymax=0.042)
    # ax2.axis(ymin=0.26, ymax=0.46)

    ax1.legend(prop=dict(size=9), frameon=False)
    ax1.set_ylabel("Profits", fontsize=16)
    ax1.set_xlabel("c", fontsize=16)
    ax2.legend(prop=dict(size=9), frameon=False)
    ax2.set_ylabel("Prices", fontsize=16)
    ax2.set_xlabel("c", fontsize=16)
    plt.tight_layout()
    plt.show()
