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
import matplotlib.pyplot as plt
import pandas as pd

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
    p_list = []
    u_demand = []
    piu_list = []
    pon_list = []
    poff_list = []
    d_demand = []
    pid_list = []

    cr = 0.32
    con = 0.1
    res_cnt = 0
    step = 0.01
    sel_c = np.arange(0.0, 0.2, 0.005)

    for c in sel_c:
        logger.debug("----------current c: {:.3f}---------".format(c))
        uniform_ins = uniform(c=c, cr=cr, con=con, step=step)
        dual_ins = dual(c=c, cr=cr, con=con, step=step)

        p_list.append(uniform_ins.optimal_p)
        u_demand.append([uniform_ins.alpha_o, uniform_ins.alpha_s])
        piu_list.append(uniform_ins.optimal_profit)

        pon_list.append(dual_ins.optimal_pon)
        poff_list.append(dual_ins.optimal_poff)
        pid_list.append(dual_ins.optimal_profit)
        d_demand.append([dual_ins.alpha_o, dual_ins.alpha_so, dual_ins.alpha_ss])

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

    cols = ["c", "p_u", "on_demand_u", "off_demand_u", "pi_u",
            "pon", "poff", "on_demand_d", "show_demand_d", "off_demand_d", "pi_d"]
    data = np.array([sel_c, p_list, [x[0] for x in u_demand], [x[1] for x in u_demand], piu_list,
                     pon_list, poff_list, [x[0] for x in d_demand], [x[1] for x in d_demand],
                     [x[2] for x in d_demand], pid_list]).T

    data_frame = pd.DataFrame(data=data, columns=cols)
    data_frame.to_excel("output.xlsx", index=False)

    fig = plt.figure(figsize=(5, 8))
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(sel_c, piu_list, c='red', ls='--', ms=6, marker='*', label="Uniform")
    ax1.plot(sel_c, pid_list, c='blue', ls='--', ms=6, marker='o', label="Dual")

    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(sel_c, p_list, c='red', ls='--', ms=6, marker='*', label="Uniform")
    ax2.plot(sel_c, pon_list, c='blue', ls='--', ms=6, marker='o', label="Online of Dual")
    ax2.plot(sel_c, poff_list, c='green', ls='--', ms=6, marker='D',
             label="Offline of Dual")

    ax1.legend(prop=dict(size=9), frameon=False)
    ax1.set_ylabel("Profits", fontsize=16)
    ax1.set_xlabel("c", fontsize=16)

    ax2.legend(prop=dict(size=9), frameon=False)
    ax2.set_ylabel("Prices", fontsize=16)
    ax2.set_xlabel("c", fontsize=16)
    plt.tight_layout()
    plt.show()
