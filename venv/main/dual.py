# -*- coding: utf-8 -*-
"""
@Created at 2022/4/29 10:19
@Author: Kurt
@file:dual.py
@Desc:
TODO: we may need to rewrite the file if we use simulation method.

"""
from tools_dual import *
import logging
import ray

logging.basicConfig()
logger = logging.getLogger('dual')
logger.setLevel(logging.INFO)
EPSILON = 0.000001


class dual:
    def __init__(self, c, cr, s, h, step):
        self.optimal_profit = 0
        self.optimal_pon = 0
        self.optimal_poff = 0
        self.optimal_poffs = 0
        self.prior_demand_online = 0
        self.prior_demand_offline = 0
        self.alpha_o = 0  # true direct online demand
        self.alpha_so = 0  # true showrooming demand
        self.alpha_ss = 0  # true offline demand
        self.consumers = None
        # start to solve the problem
        self.solve_equilibrium(c, cr, s, h, step)

    def solve_equilibrium(self, c, cr, s, h, step):
        for pon in np.arange(0, 1, step):
            logger.debug("-------------------------")
            # given pon, find the RE that maximizes total profit given pon from all potential REs.
            RE_profit_givenpon = 0  # the RE that maximizes total profit given pon.
            poffs_givenpon = 0  # the RE that maximizes total profit given pon.
            poffstar_givenpon = 0  # the RE that maximizes total profit given pon.
            prior_demand_online_givenpon = 0
            prior_demand_offline_givenpon = 0
            alpha_o_givenpon = 0
            alpha_so_givenpon = 0
            alpha_ss_givenpon = 0

            # star to find REs
            for poffs in np.arange(0, 1, step):
                current_scenario = scenario_check(pon=pon, poffs=poffs, c=c, s=s, h=h)
                alpha_o, alpha_s, alpha_l = calculate_prior_demand(pon=pon, poffs=poffs, c=c,
                                                                   s=s, h=h, scenario=current_scenario)

                # if alpha_o > 1 or alpha_o < 0 or alpha_s > 1 or alpha_s < 0: logger.error("c: {}, s:{}, h:{},
                # pon: {:.3f}, poffs: {:.3f}, scenario: {}".format( c, s, h, pon, poffs, current_scenario))
                # logger.error("ex-ante alpha_o:{:.3f}, ex-ante alpha_s: {:.3f}".format(alpha_o, alpha_s)) raise
                # Exception("error prior demand!")

                if not alpha_s:
                    # zero prior store demand, RE exists
                    RE_profit_givenpon_zero_store_demand = cal_profit(pon=pon, cr=cr, alpha_o=alpha_o, store_profit=0)
                    logger.debug("Current poffs causes zero store demand, and online profit: {:.5f}".format(
                        RE_profit_givenpon_zero_store_demand))
                    if myround(RE_profit_givenpon - RE_profit_givenpon_zero_store_demand) < 0:
                        RE_profit_givenpon = RE_profit_givenpon_zero_store_demand
                        poffs_givenpon = poffs
                        poffstar_givenpon = poffs
                        alpha_o_givenpon = alpha_o
                        alpha_so_givenpon = 0
                        alpha_ss_givenpon = 0
                        prior_demand_online_givenpon = alpha_o
                        prior_demand_offline_givenpon = alpha_s

                        logger.info("Given pon={:.3f}, no store demand, a RE is found: poffs: {:.3f}, poff: {:.3f}, "
                                    "prior_online:{:.3f}, total profit: {:.6f}, scenario: {}.".format(
                            pon, poffs_givenpon, poffstar_givenpon, alpha_o, RE_profit_givenpon, current_scenario))
                    continue  # look for the next poffs

                # if prior store demand > 0, start to find a RE
                RE_found, store_profit, store_price, store_demand_online, store_demand_offline = \
                    FindRationalExpectations(c=c, s=s, h=h, pon=pon, poffs=poffs, scenario=current_scenario, step=step)
                # print("store_price:{}".format(store_price))

                if RE_found:
                    potential_RE_profit_givenpon = cal_profit(pon=pon, cr=cr, alpha_o=alpha_o,
                                                              store_profit=store_profit)
                    logger.info(
                        "Given pon={:.3f}, a RE is found."
                        " poffs: {:.3f}, poff: {:.3f}, store profit:{:.5f}, prior_online:{:.3f}, prior_store:{:.3f}, "
                        "total profit: {:.5f}, scenario: {}".format(
                            pon, poffs, store_price, store_profit, alpha_o, alpha_s, potential_RE_profit_givenpon,
                            current_scenario))
                    # Given pon, if we find a RE in the current poffs, compare it with optimal RE collected in other
                    if myround(RE_profit_givenpon - potential_RE_profit_givenpon) < 0:
                        RE_profit_givenpon = potential_RE_profit_givenpon
                        poffs_givenpon = store_price
                        poffstar_givenpon = store_price
                        alpha_o_givenpon = alpha_o
                        alpha_so_givenpon = store_demand_online
                        alpha_ss_givenpon = store_demand_offline
                        prior_demand_online_givenpon = alpha_o
                        prior_demand_offline_givenpon = alpha_s
                else:
                    continue

            if myround(self.optimal_profit - RE_profit_givenpon) < 0:
                self.optimal_profit = RE_profit_givenpon
                self.optimal_poff = poffstar_givenpon
                self.optimal_poffs = poffs_givenpon
                self.optimal_pon = pon
                self.alpha_o = alpha_o_givenpon
                self.alpha_so = alpha_so_givenpon
                self.alpha_ss = alpha_ss_givenpon
                self.prior_demand_offline = prior_demand_offline_givenpon
                self.prior_demand_online = prior_demand_online_givenpon

        if self.optimal_pon:
            logger.info("ponstar: {:.3f}, poffs:{:.3f}, poffstar:{:.3f}, profit:{:.5f}".format(
                self.optimal_pon, self.optimal_poffs, self.optimal_poff, self.optimal_profit))
            logger.info(
                "Prior demands: online: {:.3f}, offline: {:.3f}; True demands: o: {:.3f} so:{:.3f}, ss:{:.3f}".format(
                    self.prior_demand_online, self.prior_demand_offline, self.alpha_o, self.alpha_so, self.alpha_ss))
        else:
            logger.info("No RE is found.")


if __name__ == "__main__":
    dual(c=0.1, cr=0.32, s=0.049, h=0.051, step=0.01)
