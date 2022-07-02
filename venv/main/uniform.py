# -*- coding: utf-8 -*-
"""
@Created at 2022/4/30 18:59
@Author: Kurt
@file:uniform.py
@Desc:
"""
import numpy as np
from tools_uniform import *
import logging

logging.basicConfig()
logger = logging.getLogger("uniform")
logger.setLevel(logging.ERROR)


class uniform:
    def __init__(self, c, cr, s, h, step=0.01):
        self.optimal_profit = 0
        self.optimal_p = 0
        self.alpha_o = 0
        self.alpha_s = 0

        self.solve_equilibrium(c, cr, s, h, step)

    def solve_equilibrium(self, c, cr, s, h, step=0.01):
        for p in np.arange(0, 1, step):
            current_scenario = scenario_check(p=p, c=c, s=s, h=h)
            alpha_o, alpha_s = calculate_demand(p=p, c=c, s=s, h=h, scenario=current_scenario)

            current_profit = calculate_profit(cr=cr, p=p, alpha_o=alpha_o, alpha_s=alpha_s)
            logger.info("current p: {:.3f}, scenario: {}, alpha_s: {:.3f}, alpha_o: {:.3f}, profit: {:.5f}".format(
                p, current_scenario, alpha_s, alpha_o, current_profit))

            if myround(self.optimal_profit - current_profit) < 0:
                self.optimal_profit = current_profit
                self.optimal_p = p
                self.alpha_o = alpha_o
                self.alpha_s = alpha_s
        logger.info("optimal price: {:.5f}, profit: {:.5f}".format(self.optimal_p, self.optimal_profit))
        logger.info("online demand: {:.3f}, offline demand: {:.5f}".format(self.alpha_o, self.alpha_s))


if __name__ == "__main__":
    uniform(c=0.1, cr=0.32, s=0.49, h=0.51, step=0.005)
    # cr = 0.3
    # con = 0.05
    # for c in np.arange(0.05, 0.2, 0.01):
    #     logger.info("------------current c: {:.3f}---------------".format(c))
    #     solve_equilibrium(c=c, cr=cr, con=con)
