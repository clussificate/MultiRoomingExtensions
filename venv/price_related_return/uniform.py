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
from scipy.stats import truncnorm

logging.basicConfig()
logger = logging.getLogger("uniform")
logger.setLevel(logging.ERROR)

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


def tie_found(c, con, rho, p, return_cost):
    """
    the tie break rule is independent of theta, due to the homogeneous online costs.
    """
    u_o = 1 / 2 * (1 + rho) * (- p) - 1 / 2 * (1 - rho) * return_cost - con
    u_s = 1 / 2 * (1 + rho) * (- p) - c
    if myround(u_o - u_s) == 0:
        return True
    else:
        return False


def get_expected_return_cost(p, model_para, kernel):
    """
    TODO: the expected return cost of other kernel is needed.
    """
    assert kernel in ['linear']
    a = model_para['a']
    b = model_para['b']
    if kernel == 'linear':
        if p <= a:
            return p
        elif p >= b:
            return (a + b) / 2
        else:
            return (2 * b * p - a * a - p * p) / (2 * (b - a))


def get_return_probability(model_para, p, kernel):
    assert kernel in ['sqrt', 'linear', "normal"]

    if kernel == "sqrt":
        m = model_para['m']
        return min(m * p ** (1 / 2), 1)
    elif kernel == "linear":
        a = model_para['a']
        b = model_para['b']
        return max((min(b, p) - a) / (b - a), 0)
    elif kernel == 'normal':
        # the Truncated Normal Distribution is used.
        mu = model_para['mu']
        std = model_para['std']
        return truncnorm.cdf(p, a=(0 - mu) / std, b=(1 - mu) / std, loc=mu, scale=std)


def utility_tie_online(theta, c, con, p, rho, return_cost):
    """
    In this function, the tie is broken by assuming consumers buy online directly
    :param theta: value of theta
    :param return_cost : consumer expected return rate
    """
    u_o = 1 / 2 * (1 + rho) * (theta - p) - 1 / 2 * (1 - rho) * return_cost - con
    u_s = 1 / 2 * (1 + rho) * (theta - p) - c
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


def utility_tie_offline(theta, c, con, p, rho, return_cost):
    """
    In this function, the tie is broken by assuming consumers visit the store
    :param theta: value of theta
    :param return_cost : consumer expected return rate
    """
    u_o = 1 / 2 * (1 + rho) * (theta - p) - 1 / 2 * (1 - rho) * return_cost - con
    u_s = 1 / 2 * (1 + rho) * (theta - p) - c
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


def simulate_behavior(consumers, c, con, rho, p, return_cost):
    """
    :param return_cost: consumer expected return rate
    """
    # if consumers are indifferent between buying online directly and visiting the store,
    # we break the tie by maximizing the retailer's profit
    if tie_found(c=c, con=con, rho=rho, p=p, return_cost=return_cost):
        behaviors_tie_online = [utility_tie_online(theta=consumer, c=c, con=con, p=p, return_cost=return_cost, rho=rho)
                                for consumer in consumers]
        behaviors_tie_offline = [
            utility_tie_offline(theta=consumer, c=c, con=con, p=p, return_cost=return_cost, rho=rho)
            for consumer in consumers]

        return behaviors_tie_online, behaviors_tie_offline
    else:
        # if there is no tie, utility_tie_online and utility_tie_offline are equivalent.
        behaviors = [utility_tie_online(theta=consumer, c=c, con=con, p=p, return_cost=return_cost, rho=rho)
                     for consumer in consumers]

        return behaviors


def cal_profit(p, cr, gamma, rho, behaviors):
    """
    :param gamma : return rate
    """
    alpha_o, alpha_s = get_demand(behaviors)
    online_profit = alpha_o * (
            1 / 2 * (1 + rho) * p + 1 / 2 * (1 - rho) * ((1 - gamma) * p - gamma * cr))  # w.p. 1/2, b=b_H.
    store_profit = alpha_s * 1 / 2 * (1 + rho) * p  # w.p. 1/2, b=b_H
    profit = 1 / 2 * store_profit + 1 / 2 * online_profit  # w.p. 1/2, a=a_H
    return profit


class uniform:

    def __init__(self, c, con, cr, rho, model_para, kernel='linear', step=0.001, density=0.001):
        """
        :param c: offline shopping cost
        :param con: online shopping cost
        :param cr: retailer return cost
        :param step: step size of price
        :param density=0.001: density of consumers
        """
        self.p = 0
        self.profit = 0
        self.solve(c=c, con=con, cr=cr, rho=rho, model_para=model_para, kernel=kernel, step=step, density=density)

    def solve(self, c, con, cr, rho, model_para, kernel, step, density):
        consumers = np.arange(0, 1, density)

        optimal_profit = 0
        optimal_price = 0
        for p in np.arange(0.001, 1, step):
            if kernel == 'constant':
                gamma = 1 / 2
                return_cost = 1 / 2 * p
            else:
                gamma = get_return_probability(model_para=model_para, p=p, kernel=kernel)
                return_cost = get_return_probability(model_para=model_para, p=p, kernel=kernel)
            logger.debug("current loop: p={:.3f}".format(p))
            #             if myround(1 / 2 * m * p * p - 1 / 2 * p + c - con) == 0:
            if tie_found(c=c, con=con, rho=rho, p=p, return_cost=return_cost):
                behaviors_tie_online, behaviors_tie_offline = simulate_behavior(consumers=consumers, c=c, con=con, p=p,
                                                                                return_cost=return_cost, rho=rho)
                profit_tie_online = cal_profit(p=p, cr=cr, behaviors=behaviors_tie_online, gamma=gamma, rho=rho)
                profit_tie_offline = cal_profit(p=p, cr=cr, behaviors=behaviors_tie_offline, gamma=gamma, rho=rho)
                profit = max(profit_tie_online, profit_tie_offline)
            else:
                behaviors = simulate_behavior(consumers=consumers, c=c, con=con, p=p, return_cost=return_cost, rho=rho)
                profit = cal_profit(p=p, cr=cr, behaviors=behaviors, gamma=gamma, rho=rho)

            if profit - optimal_profit > 0:
                optimal_profit = profit
                optimal_price = p
        self.p = optimal_price
        self.profit = optimal_profit


@ray.remote
def get_uniform_result(c, con, cr, rho, model_para, kernel, step, density):
    uniform_ins = uniform(c=c, con=con, rho=rho, model_para=model_para,
                          cr=cr, kernel=kernel, step=step, density=density)
    return uniform_ins.p, uniform_ins.profit


if __name__ == "__main__":

    logger.setLevel(logging.DEBUG)
    sel_c = np.arange(0.1, 0.155, 0.005)
    cr = 0.32
    con = 0.05
    rho = 0

    model_para = {"a": 0.0, "b": 1.0}
    kernel = 'linear'
    # model_para = {"mu": 0.0, "std": 0.6}
    # kernel = "normal"  # if kernel == "constant", we set return rate as 1/2.

    result_ids = []
    for c in sel_c:
        result_ids.append(get_uniform_result.remote(c=c, con=con, cr=cr, rho=rho, model_para=model_para,
                                                    kernel=kernel, step=0.0025, density=0.0001))

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
