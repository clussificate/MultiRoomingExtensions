# -*- coding: utf-8 -*-
"""
@Created at 2022/7/3 13:07
@Author: Kurt
@file:dual.py
"""
from collections import Counter
import numpy as np
import logging
import ray
import matplotlib.pyplot as plt
from scipy.stats import truncnorm

logging.basicConfig()
logger = logging.getLogger("dual")
logger.setLevel(logging.ERROR)

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


def tie_found(c, con, rho, pon, poff, return_cost):
    """
    the tie break rule is independent of theta, due to the homogeneous online costs.
    """
    u_o = 1 / 2 * (1 + rho) * (- pon) - 1 / 2 * (1 - rho) * return_cost - con
    u_s = 1 / 2 * (1 + rho) * (- poff) - c
    if myround(u_o - u_s) == 0:
        return True
    else:
        return False


def get_return_probability(model_para, pon, kernel):
    assert kernel in ['constant', 'sqrt', 'linear', "normal"]

    if kernel == "sqrt":
        m = model_para['m']
        return min(m * pon ** (1 / 2), 1)
    elif kernel == "linear":
        a = model_para['a']
        b = model_para['b']
        return max((min(b, pon) - a) / (b - a), 0)
    elif kernel == 'normal':
        # the Truncated Normal Distribution is used.
        mu = model_para['mu']
        std = model_para['std']
        return truncnorm.cdf(pon, a=(0 - mu) / std, b=(1 - mu) / std, loc=mu, scale=std)


def get_expected_return_cost(pon, model_para, kernel):
    """
    TODO: the expected return cost of other kernel is needed.
    """
    assert kernel in ['linear']
    a = model_para['a']
    b = model_para['b']
    if kernel == 'linear':
        if pon <= a:
            return pon
        elif pon >= b:
            return (a + b) / 2
        else:
            return (2 * b * pon - a * a - pon * pon) / (2 * (b - a))


def utility_tie_online(theta, c, con, rho, pon, poff, return_cost):
    """
    In this function, the tie is broken by assuming consumers buy online directly
    :param theta: value of theta
    :param return_cost: consumer expected return cost.
    :param rho: correlation between bH and aH
    """
    u_o = 1 / 2 * (1 + rho) * (theta - pon) - 1 / 2 * (1 - rho) * return_cost - con
    u_s = 1 / 2 * (1 + rho) * (theta - poff) - c
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


def utility_tie_offline(theta, c, con, rho, pon, poff, return_cost):
    """
    In this function, the tie is broken by assuming consumers visit the store
    :param theta: value of theta
    """
    u_o = 1 / 2 * (1 + rho) * (theta - pon) - 1 / 2 * (1 - rho) * return_cost - con
    u_s = 1 / 2 * (1 + rho) * (theta - poff) - c
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


def simulate_behavior(consumers, c, con, rho, pon, poff, return_cost):
    # if consumers are indifferent between buying online directly and visiting the store,
    # we break the tie by maximizing the retailer's profit
    if tie_found(c=c, con=con, rho=rho, pon=pon, poff=pon, return_cost=return_cost):
        behaviors_tie_online = [
            utility_tie_online(theta=consumer, c=c, con=con, rho=rho, pon=pon, poff=poff, return_cost=return_cost)
            for consumer in consumers]
        behaviors_tie_offline = [
            utility_tie_offline(theta=consumer, c=c, con=con, rho=rho, pon=pon, poff=poff, return_cost=return_cost)
            for consumer in consumers]

        return behaviors_tie_online, behaviors_tie_offline
    else:
        # if there is no tie, utility_tie_online and utility_tie_offline are equivalent.
        behaviors = [utility_tie_online(theta=consumer, c=c, con=con, rho=rho, pon=pon, poff=poff,
                                        return_cost=return_cost) for consumer in consumers]
        return behaviors


def cal_profit(pon, poff, cr, rho, behaviors, gamma):
    """
    :param gamma: return probability of an online-direct consumer.
    :return:
    """
    alpha_o, alpha_s = get_demand(behaviors)
    logger.debug("current demand: alpha_o {:.3f}, alpha_s {:.3f}, return probability:{:.3f}".format(
        alpha_o, alpha_s, gamma))
    online_profit = alpha_o * (1 / 2 * (1 + rho) * pon + 1 / 2 * (1 - rho) * (
            (1 - gamma) * pon - gamma * cr))  # w.p. 1/2, b=b_H.
    store_profit = alpha_s * 1 / 2 * (1 + rho) * poff  # w.p. 1/2, b=b_H
    logger.debug("current demand: online_profit {:.5f}, store_profit {:.5f}".format(online_profit, store_profit))
    profit = 1 / 2 * store_profit + 1 / 2 * online_profit  # w.p. 1/2, a=a_H
    return profit


class dual:
    def __init__(self, c, con, cr, rho, model_para, kernel="constant", step=0.001, density=0.001):
        self.pon = 0
        self.poff = 0
        self.profit = 0
        self.solve(c=c, con=con, cr=cr, rho=rho, model_para=model_para, kernel=kernel, step=step, density=density)

    def solve(self, c, con, cr, rho, model_para, kernel, step, density):
        consumers = np.arange(0, 1, density)
        optimal_profit = 0
        optimal_pon = 0
        for pon in np.arange(0.001, 1, step):
            poff = pon + con
            if kernel == 'constant':
                gamma = 1 / 2
                return_cost = 1/2 * pon
            else:
                gamma = get_return_probability(model_para=model_para, pon=pon, kernel=kernel)
                return_cost = get_expected_return_cost(pon=pon, model_para=model_para, kernel=kernel)
            #             logger.debug("current m: {:.3f}, pon: {:.3f}".format(m, pon))
            if tie_found(c=c, con=con, rho=rho, pon=pon, poff=pon, return_cost=return_cost):
                behaviors_tie_online, behaviors_tie_offline = simulate_behavior(consumers=consumers, c=c, con=con,
                                                                                rho=rho, pon=pon, poff=poff,
                                                                                return_cost=return_cost)
                profit_tie_online = cal_profit(pon=pon, poff=poff, cr=cr, rho=rho,
                                               behaviors=behaviors_tie_online, gamma=gamma)
                profit_tie_offline = cal_profit(pon=pon, poff=poff, cr=cr, rho=rho,
                                                behaviors=behaviors_tie_offline, gamma=gamma)
                profit = max(profit_tie_online, profit_tie_offline)
            else:
                behaviors = simulate_behavior(consumers=consumers, c=c, con=con, pon=pon, poff=poff,
                                              rho=rho, return_cost=return_cost)
                profit = cal_profit(pon=pon, poff=poff, cr=cr, rho=rho, behaviors=behaviors, gamma=gamma)

            logger.debug("current loop: pon={:.3f}, poff={:.3f}, profit={:.5f}".format(pon, poff, profit))
            logger.debug("-------" * 10)
            if profit - optimal_profit > 0:
                optimal_profit = profit
                optimal_pon = pon
        self.pon = optimal_pon
        self.poff = optimal_pon + con
        self.profit = optimal_profit


@ray.remote
def get_dual_result(c, con, cr, rho, model_para, kernel, step, density):
    dual_ins = dual(c=c, con=con, rho=rho, model_para=model_para, cr=cr, kernel=kernel, step=step, density=density)
    return dual_ins.pon, dual_ins.poff, dual_ins.profit


if __name__ == "__main__":
    sel_c = np.arange(0.1, 0.18, 0.005)
    cr = 0.32
    con = 0.05
    rho = 0

    # if kernel == "constant", we set return rate as 1/2.
    model_para = {"a": 0.0, "b": 1}
    kernel = 'linear'
    # model_para = {"mu": 0.0, "std": 0.9}
    # kernel = 'normal'
    # dual_ins = dual(con=con, return_prop=return_prop, cr=cr, c=0.1, step=0.001, density=0.0001)

    result_ids = []
    for c in sel_c:
        result_ids.append(get_dual_result.remote(c=c, con=con, cr=cr, rho=rho, model_para=model_para, kernel=kernel,
                                                 step=0.0025, density=0.0001))
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
