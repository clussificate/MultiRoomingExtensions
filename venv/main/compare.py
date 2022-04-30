# -*- coding: utf-8 -*-
"""
@Created at 2022/4/30 20:46
@Author: Kurt
@file:compare.py
@Desc:
"""
import numpy as np
import dual
import uniform
import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

for c in np.arange(0.25, 0.3, 0.01):
    print("----------current c: {:.3f}---------".format(c))
    p, uniform_profit = uniform.solve_equilibrium(c=c, cr=0.1, con=0.2)
    pon, poffs, poff, dual_profit = dual.solve_equilibrium(c=c, cr=0.1, con=0.2)
    print("Uniform price: {:.3f}, uniform profit: {:.3f}".format(p, uniform_profit))
    print("online price: {:.3f}, store price: {:.3f}, uniform profit: {:.3f}".format(pon, poff, dual_profit))
