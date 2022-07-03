# -*- coding: utf-8 -*-
"""
@Created at 2022/7/3 13:07
@Author: Kurt
@file:dual.py
@Desc:
"""
from collections import Counter
import numpy as np
import logging
import ray
import matplotlib.pyplot as plt

logging.basicConfig()
logger = logging.getLogger("uniform")
logger.setLevel(logging.DEBUG)

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


def utility_tie_online(loc, c, con, m, pon, poff):
    """
    In this function, the tie is broken by assuming consumers buy online directly
    :param loc: value of theta
    """
    u_o = 1 / 2 * loc + 1 / 2 * m * pon * pon - pon - con
    u_s = 1 / 2 * (loc - poff) - c
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


def utility_tie_offline(loc, c, con, m, pon, poff):
    """
    In this function, the tie is broken by assuming consumers visit the store
    :param loc: value of theta
    """
    u_o = 1 / 2 * loc + 1 / 2 * m * pon * pon - pon - con
    u_s = 1 / 2 * (loc - poff) - c
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


def simulate_behavior(consumers, c, con, m, pon, poff):
    # if consumers are indifferent between buying online directly and visiting the store,
    # we break the tie by maximizing the retailer's profit
    if myround(1 / 2 * m * pon * pon - pon + 1 / 2 * poff + c - con) == 0:
        behaviors_tie_online = [utility_tie_online(loc=consumer, c=c, con=con,
                                                   m=m, pon=pon, poff=poff) for consumer in consumers]
        behaviors_tie_offline = [utility_tie_offline(loc=consumer, c=c, con=con,
                                                     m=m, pon=pon, poff=poff) for consumer in consumers]

        return behaviors_tie_online, behaviors_tie_offline
    else:
        # if there is no tie, utility_tie_online and utility_tie_offline are equivalent.
        behaviors = [utility_tie_online(loc=consumer, c=c, con=con, m=m, pon=pon, poff=poff) for consumer in consumers]

        return behaviors


def cal_profit(m, pon, poff, cr, behaviors):
    alpha_o, alpha_s = get_demand(behaviors)
    online_profit = alpha_o * (1 / 2 * pon + 1 / 2 * ((1 - m * pon) * pon - m * pon * cr))  # w.p. 1/2, b=b_H.
    store_profit = alpha_s * 1 / 2 * poff  # w.p. 1/2, b=b_H
    profit = 1 / 2 * store_profit + 1 / 2 * online_profit  # w.p. 1/2, a=a_H
    return profit


class dual:
    def __init__(self, c, con, cr, m, step=0.001, density=0.001):
        self.pon = 0
        self.poff = 0
        self.profit = 0
        self.solve(c=c, con=con, cr=cr, m=m, step=step, density=density)

    def solve(self, c, con, cr, m, step, density):
        consumers = np.arange(0, 1, density)
        optimal_profit = 0
        optimal_pon = 0
        for pon in np.arange(0.001, 1, step):
            poff = pon + con
            if isinstance(m, str):
                m = 1 / (2 * pon)
            logger.debug("current loop: pon={:.3f}".format(pon))
            if myround(1 / 2 * m * pon * pon - pon + 1 / 2 * poff + c - con) == 0:
                behaviors_tie_online, behaviors_tie_offline = simulate_behavior(consumers=consumers,
                                                                                c=c, con=con, m=m, pon=pon, poff=poff)
                profit_tie_online = cal_profit(m=m, pon=pon, poff=poff, cr=cr, behaviors=behaviors_tie_online)
                profit_tie_offline = cal_profit(m=m, pon=pon, poff=poff, cr=cr, behaviors=behaviors_tie_offline)
                profit = max(profit_tie_online, profit_tie_offline)
            else:
                behaviors = simulate_behavior(consumers=consumers, c=c, con=con, m=m, pon=pon, poff=poff)
                profit = cal_profit(m=m, pon=pon, poff=poff, cr=cr, behaviors=behaviors)

            if profit - optimal_profit > 0:
                optimal_profit = profit
                optimal_pon = pon
        self.pon = optimal_pon
        self.pon = optimal_pon + con
        self.profit = optimal_pon


@ray.remote
def get_dual_result(c, con, cr, m, step, density):
    dual_ins = dual(c=c, con=con, m=m, cr=cr, step=step, density=density)
    return dual_ins.pon, dual_ins.poff, dual_ins.profit


if __name__ == "__main__":
    sel_c = np.arange(0.1, 0.155, 0.005)
    cr = 0.32
    con = 0.05
    m = "k"  # if m is a string, this means that we set m=1/(2*p), which degrades to the baseline model.

    result_ids = []
    for c in sel_c:
        result_ids.append(get_dual_result.remote(c=c, con=con, cr=cr, m=m,
                                                 step=0.001, density=0.0001))
    results = ray.get(result_ids)

    pon_list = []
    poff_list = []
    pid_list = []
    for result in results:
        pon_list.append(result[0])
        poff_list.append(result[1])
        pid_list.append(result[2])
    fig = plt.figure(figsize=(5, 8))
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(sel_c, pid_list, c='red', ls='--', ms=6, marker='*', label="Dual")

    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(sel_c, pon_list, c='blue', ls='--', ms=6, marker='o', label="Online of Dual")
    ax2.plot(sel_c, poff_list, c='green', ls='--', ms=6, marker='D',
             label="Offline of Dual")

    ax1.axis(ymin=0.026, ymax=0.042)
    ax2.axis(ymin=0.26, ymax=0.46)

    ax1.legend(prop=dict(size=9), frameon=False)
    ax1.set_ylabel("Profits", fontsize=16)
    ax1.set_xlabel("c", fontsize=16)
    ax2.legend(prop=dict(size=9), frameon=False)
    ax2.set_ylabel("Prices", fontsize=16)
    ax2.set_xlabel("c", fontsize=16)
    plt.tight_layout()
    plt.show()
