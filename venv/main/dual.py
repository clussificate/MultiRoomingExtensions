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


def solve_equilibrium(c, cr, con, step=0.01):
    optimal_total_profit = 0  # the RE that maximizes total profit for any pon.
    optimal_poffs = 0
    optimal_poff = 0
    optimal_pon = 0
    for pon in np.arange(0, 1, step):
        logger.debug("-------------------------")
        # given pon, find the RE that maximizes total profit given pon from all potential REs.
        RE_profit_givenpon = 0  # the RE that maximizes total profit given pon.
        poffs_givenpon = 0  # the RE that maximizes total profit given pon.
        poffstar_givenpon = 0  # the RE that maximizes total profit given pon.

        # star to find REs
        for poffs in np.arange(0, 1, step):
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
                logger.debug("Current poffs causes zero store demand, and online profit: {:.5f}".format(
                    RE_profit_givenpon_zero_store_demand))
                if myround(RE_profit_givenpon - RE_profit_givenpon_zero_store_demand) < 0:
                    # if pon == 0.37:
                    #     logger.info("current zero-store-demand profit: {:.8f}, "
                    #                  "optimal zero-store-demand profit: {:.8f}".format(
                    #         RE_profit_givenpon_zero_store_`demand, RE_profit_givenpon))
                    RE_profit_givenpon = RE_profit_givenpon_zero_store_demand
                    poffs_givenpon = poffs
                    poffstar_givenpon = poffs
                    logger.info("Given pon={:.3f}, no store demand, a RE is found: poffs: {:.3f}, poff: {:.3f}, "
                                "alpha_o:{:.3f}, total profit: {:.6f}, scenario: {}.".format(
                        pon, poffs_givenpon, poffstar_givenpon, alpha_o, RE_profit_givenpon, current_scenario))
                continue  # look for the next poffs

            # if prior store demand > 0, start to find a RE
            RE_found, store_profit, store_price = FindRationalExpectations(pon=pon, poffs=poffs, c=c, con=con,
                                                                           alpha_s=alpha_s, step=step)
            # print("store_price:{}".format(store_price))

            if RE_found:
                potential_RE_profit_givenpon = cal_profit(pon=pon, cr=cr, alpha_o=alpha_o,
                                                          store_profit=store_profit)
                logger.info(
                    "Given pon={:.3f}, a RE is found."
                    " poffs: {:.3f}, poff: {:.3f}, store profit:{:.5f}, alpha_o:{:.3f}, alpha_s:{:.3f}, "
                    "total profit: {:.6f}, scenario: {}".format(
                        pon, poffs, store_price, store_profit, alpha_o, alpha_s, potential_RE_profit_givenpon,
                        current_scenario))
                # Given pon, if we find a RE in the current poffs, compare it with optimal RE collected in other poffs.
                # logger.info("store profit:{:.5f}, "
                #             "alpha_o:{:.3f}, alpha_s:{:.3f}, total profit: {:.6f}, scenario: {}".format(
                #     store_profit, alpha_o, alpha_s, potential_RE_profit_givenpon, current_scenario))
                if myround(RE_profit_givenpon - potential_RE_profit_givenpon) < 0:
                    RE_profit_givenpon = potential_RE_profit_givenpon
                    poffs_givenpon = store_price
                    poffstar_givenpon = store_price
            else:
                continue

        if myround(optimal_total_profit - RE_profit_givenpon) < 0:
            optimal_total_profit = RE_profit_givenpon
            optimal_poff = poffstar_givenpon
            optimal_poffs = poffs_givenpon
            optimal_pon = pon

    if optimal_pon:
        logger.info("ponstar: {:.3f}, poffs:{:.3f}, poffstar:{:.3f}, profit:{:.5f}".format(
            optimal_pon, optimal_poffs, optimal_poff, optimal_total_profit))
    else:
        logger.info("No RE is found.")

    return optimal_pon, optimal_poffs, optimal_poff, optimal_total_profit


if __name__ == "__main__":
    solve_equilibrium(c=0.15, cr=0.3, con=0.1, step=0.005)
