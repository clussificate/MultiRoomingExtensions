# -*- coding: utf-8 -*-
"""
@Created at 2022/4/29 10:19
@Author: Kurt
@file:dual.py
@Desc:
"""
from tools_dual import *
import logging

logging.basicConfig()
logger = logging.getLogger('dual')
logger.setLevel(logging.INFO)
EPSILON = 0.000001


def solve_equilibrium(c, cr, con):
    optimal_total_profit = 0  # the RE that maximizes total profit for any pon.
    optimal_poffs = 0
    optimal_poff = 0
    optimal_pon = 0
    for pon in np.arange(0, 1, 0.01):
        logger.info("----------------------------")
        # given pon, find the RE that maximizes total profit given pon from all potential REs.
        RE_profit_givenpon = 0  # the RE that maximizes total profit given pon.
        poffs_givenpon = 0  # the RE that maximizes total profit given pon.
        poffstar_givenpon = 0  # the RE that maximizes total profit given pon.

        # star to find REs
        for poffs in np.arange(0, 1, 0.01):
            current_scenario = scenario_check(pon=pon, poffs=poffs, c=c, con=con)
            if current_scenario:  # print("current poffs: {}".format(poffs))
                alpha_o, alpha_s, alpha_l = calculate_prior_demand(pon=pon, poffs=poffs, c=c,
                                                                   con=con, scenario=current_scenario)
                if alpha_o > 1 or alpha_o < 0 or alpha_s > 1 or alpha_s < 0:
                    logger.error("c: {}, con:{}, pon: {:.3f}, poffs: {:.3f}, scenario: {}".format(
                        c, con, pon, poffs, current_scenario))
                    logger.error("alpha_o:{:.3f}, alpha_s: {:.3f}".format(alpha_o, alpha_s))
                    raise Exception("error prior demand!")
            else:
                continue

            if not alpha_s:
                # zero prior store demand, RE exists
                RE_profit_givenpon_zero_store_demand = cal_profit(pon=pon, cr=cr, alpha_o=alpha_o, store_profit=0)
                logger.info("Current poffs causes zero store demand, and online profit: {:.3f}".format(
                    RE_profit_givenpon_zero_store_demand))
                if RE_profit_givenpon < RE_profit_givenpon_zero_store_demand:
                    RE_profit_givenpon = RE_profit_givenpon_zero_store_demand
                continue  # look for the next poffs

            # if prior store demand > 0, start to find a RE
            RE_found, store_profit, store_price = FindRationalExpectations(pon=pon, poffs=poffs, c=c, con=con,
                                                                           alpha_s=alpha_s)
            # print("store_price:{}".format(store_price))

            if RE_found:
                logger.info(
                    "Given pon={:.5f}, a RE is found. poffs: {:.5f}, poff: {:.5f}.".format(pon, poffs, store_price))
                # Given pon, if we find a RE in the current poffs, compare it with optimal RE collected in other poffs.
                potential_RE_profit_givenpon = cal_profit(pon=pon, cr=cr, alpha_o=alpha_o,
                                                          store_profit=store_profit)

                logger.info("store profit:{:.5f}, alpha_o:{:.5f}, total: {:.5f}".format(
                    store_profit, alpha_o, potential_RE_profit_givenpon))
                if RE_profit_givenpon < potential_RE_profit_givenpon:
                    RE_profit_givenpon = potential_RE_profit_givenpon
                    poffs_givenpon = store_price
                    poffstar_givenpon = store_price
            else:
                continue

        if optimal_total_profit < RE_profit_givenpon:
            optimal_total_profit = RE_profit_givenpon
            optimal_poff = poffstar_givenpon
            optimal_poffs = poffs_givenpon
            optimal_pon = pon

    if optimal_pon:
        logger.info("ponstar: {}, poffs:{}, poffstar:{}, profit:{}".format(
            optimal_pon, optimal_poffs, optimal_poff, optimal_total_profit))
    else:
        logger.info("No RE is found.")

    return optimal_pon, optimal_poffs, optimal_poff, optimal_total_profit


if __name__ == "__main__":
    print("now")
    solve_equilibrium(c=0.25, cr=0.1, con=0.2)
