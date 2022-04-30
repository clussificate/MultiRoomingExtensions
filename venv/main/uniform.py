# -*- coding: utf-8 -*-
"""
@Created at 2022/4/30 18:59
@Author: Kurt
@file:uniform.py
@Desc:
"""
import numpy as np
from tools_uniform import *


def solve_equilibrium(c, cr, con):
    optimal_total_profit = 0
    optimal_p = 0
    for p in np.arange(0, 1, 0.01):
        current_scenario = scenario_check(c, con, p)
        alpha_o, alpha_s = calculate_demand(p=p, c=c, con=con, scenario=current_scenario)

        current_profit = calculate_profit(cr=cr, p=p, alpha_o=alpha_o, alpha_s=alpha_s)

        if optimal_total_profit < current_profit:
            optimal_total_profit = current_profit
            optimal_p = p
    print("optimal price: {:.5f}, profit: {:.5f}".format(optimal_p, optimal_total_profit))
    return optimal_p, optimal_total_profit


solve_equilibrium(c=0.05, cr=0.1, con=0.2)
