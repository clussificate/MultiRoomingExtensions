# -*- coding: utf-8 -*-
"""
@Created at 2022/4/30 20:46
@Author: Kurt
@file:compare.py
@Desc:
"""
import numpy as np
from dual import dual
from uniform import uniform
import logging

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


if __name__ == "__main__":
    logging.getLogger('dual').setLevel(logging.ERROR)
    logging.getLogger('uniform').setLevel(logging.ERROR)

    logging.basicConfig()
    logger = logging.getLogger("compare")
    logger.setLevel(logging.DEBUG)
    cr = 0.32
    con = 0.1
    res_cnt = 0
    step = 0.01
    for c in np.arange(0.10, 0.22, 0.005):
        logger.debug("----------current c: {:.3f}---------".format(c))
        uniform_ins = uniform(c=c, cr=cr, con=con, step=step)
        dual_ins = dual(c=c, cr=cr, con=con, step=step)
        logger.debug("Uniform price: {:.3f}, uniform profit: {:.5f}".format(
            uniform_ins.optimal_p, uniform_ins.optimal_profit))
        logger.debug("online price: {:.3f}, store price: {:.3f}, dual profit: {:.5f}".format(
            dual_ins.optimal_pon, dual_ins.optimal_poff, dual_ins.optimal_profit))
        if myround(uniform_ins.optimal_p - dual_ins.optimal_pon) < 0 and \
                myround(uniform_ins.optimal_profit - dual_ins.optimal_profit) > 0:
            res_cnt = res_cnt + 1
            logger.info("HPLP RESULT IS FOUND....")
    if res_cnt == 0:
        logger.info("No HPLP RESULT....")
