# -*- coding: utf-8 -*-
"""
@Created at 2023/3/2 18:53
@Author: Kurt
@file:posted_dual.py
@Desc:
"""
import numpy as np
from tools_posted_dual import *
import logging


logging.basicConfig()
logger = logging.getLogger("posted dual")
logger.setLevel(logging.ERROR)


class posted_dual:
    def __init__(self, c, cr, s, h, step=0.01):
        self.optimal_profit = 0
        self.optimal_pon = 0
        self.optimal_poff = 0
        self.alpha_o = 0
        self.alpha_so = 0
        self.alpha_ss = 0

        self.solve_equilibrium(c, cr, s, h, step)

    def solve_equilibrium(self, c, cr, s, h, step=0.01):
        for poff in np.arange(0, 1, step):
            for pon in np.arange(0, 1, step):
                current_scenario = scenario_check(pon=pon, poff=poff, c=c)
                alpha_o, alpha_so, alpha_ss = calculate_demand(pon=pon, poff=poff, c=c, s=s, h=h, scenario=current_scenario)

                current_profit = calculate_profit(cr=cr, pon=pon, poff=poff, alpha_o=alpha_o,
                                                  alpha_ss=alpha_ss, alpha_so=alpha_so)
                logger.info("current pon: {:.3f}, poff: {:.3f}, scenario: {}, alpha_o: {:.3f}, alpha_so: {:.3f}, "
                            "alpha_ss: {:.3f}, profit: {:.5f}".format(
                    pon, poff, current_scenario, alpha_o, alpha_so, alpha_ss, current_profit))

                if myround(self.optimal_profit - current_profit) < 0:
                    self.optimal_profit = current_profit
                    self.optimal_pon = pon
                    self.optimal_poff = poff
                    self.alpha_o = alpha_o
                    self.alpha_so = alpha_so
                    self.alpha_ss = alpha_ss
        logger.info("optimal online price: {:.5f}, optimal offline price: {:.5f}, profit: {:.5f}".format(
            self.optimal_pon, self.optimal_poff, self.optimal_profit))
        logger.info("online demand: {:.3f}, showroom demand: {:.5f}, store demand: {:.5f}".format(
            self.alpha_o, self.alpha_so, self.alpha_ss))


if __name__ == "__main__":
    posted_dual(c=0.13, cr=0.32, s=0.03, h=0.07, step=0.005)
    # cr = 0.3
    # con = 0.05
    # for c in np.arange(0.05, 0.2, 0.01):
    #     logger.info("------------current c: {:.3f}---------------".format(c))
    #     solve_equilibrium(c=c, cr=cr, con=con)
