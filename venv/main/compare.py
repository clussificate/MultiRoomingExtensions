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

if __name__ == "__main__":
    logging.getLogger('dual').setLevel(logging.ERROR)
    logging.getLogger('uniform').setLevel(logging.ERROR)

    logging.basicConfig()
    logger = logging.getLogger("compare")
    logger.setLevel(logging.DEBUG)
    cr = 0.35
    con = 0.05
    for c in np.arange(0.05, 0.2, 0.01):

        logger.debug("----------current c: {:.3f}---------".format(c))
        p, uniform_profit = uniform.solve_equilibrium(c=c, cr=cr, con=con)
        pon, poffs, poff, dual_profit = dual.solve_equilibrium(c=c, cr=cr, con=con)
        logger.debug("Uniform price: {:.3f}, uniform profit: {:.5f}".format(p, uniform_profit))
        logger.debug("online price: {:.3f}, store price: {:.3f}, dual profit: {:.5f}".format(
            pon, poff, dual_profit))
        if p <= pon and uniform_profit > dual_profit:
            logger.info("find HPLP result....")
