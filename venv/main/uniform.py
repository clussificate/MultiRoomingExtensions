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
logger.setLevel(logging.INFO)


def solve_equilibrium(c, cr, con):
    optimal_total_profit = 0
    optimal_p = 0
    for p in np.arange(0, 0.5, 0.01):
        current_scenario = scenario_check(c=c, con=con, p=p)
        alpha_o, alpha_s = calculate_demand(p=p, c=c, con=con, scenario=current_scenario)

        current_profit = calculate_profit(cr=cr, p=p, alpha_o=alpha_o, alpha_s=alpha_s)
        logger.info("current p: {:.3f}, scenario: {}, alpha_s:{:.5f}, alpha_o:{:.5f}, profit: {:.5f}".format(
            p, current_scenario, alpha_s, alpha_o, current_profit))
        if optimal_total_profit < current_profit:
            optimal_total_profit = current_profit
            optimal_p = p
    logger.info("optimal price: {:.5f}, profit: {:.5f}".format(optimal_p, optimal_total_profit))
    return optimal_p, optimal_total_profit


if __name__ == "__main__":
    cr = 0.3
    con = 0.05
    for c in np.arange(0.05, 0.2, 0.01):
        logger.info("------------current c: {:.3f}---------------".format(c))
        solve_equilibrium(c=c, cr=cr, con=con)
