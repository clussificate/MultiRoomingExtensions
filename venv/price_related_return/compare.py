# -*- coding: utf-8 -*-
"""
@Created at 2022/7/3 16:58
@Author: Kurt
@file:compare.py
@Desc:
"""
from dual import dual
from uniform import uniform
import ray
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

logging.basicConfig()
logger = logging.getLogger("compare")
logger.setLevel(logging.INFO)
logging.getLogger('dual').setLevel(logging.ERROR)
logging.getLogger('uniform').setLevel(logging.ERROR)


@ray.remote
def get_uniform_result(c, con, cr, return_prop, step, density):
    uniform_ins = uniform(c=c, con=con, return_prop=return_prop, cr=cr, step=step, density=density)
    return uniform_ins.p, uniform_ins.profit


@ray.remote
def get_dual_result(c, con, cr, return_prop, step, density):
    dual_ins = dual(c=c, con=con, return_prop=return_prop, cr=cr, step=step, density=density)
    return dual_ins.pon, dual_ins.poff, dual_ins.profit


def main(ms, filenames, plot=False, save=False):
    for m, filename in zip(ms, filenames):
        p_list = []
        piu_list = []

        pon_list = []
        poff_list = []
        pid_list = []

        cr = 0.32
        con = 0.05
        step = 0.001
        density = 0.005
        sel_c = np.arange(0.05, 0.18, 0.005)

        results_uniform_id = []
        results_dual_id = []

        for c in sel_c:
            results_uniform_id.append(
                get_uniform_result.remote(c=c, con=con, cr=cr, return_prop=m, step=step, density=density))
            results_dual_id.append(
                get_dual_result.remote(c=c, con=con, cr=cr, return_prop=m, step=step, density=density))

        results_uniform = ray.get(results_uniform_id)
        results_dual = ray.get(results_dual_id)

        for result_uniform, result_dual in zip(results_uniform, results_dual):
            p_list.append(result_uniform[0])
            piu_list.append(result_uniform[1])

            pon_list.append(result_dual[0])
            poff_list.append(result_dual[1])
            pid_list.append(result_dual[2])

        if plot:
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
        if save:
            cols = ["c", "p_u", "pi_u", "pon", "poff", "pi_d"]
            data = np.array([sel_c, p_list, piu_list, pon_list, poff_list, pid_list]).T

            data_frame = pd.DataFrame(data=data, columns=cols)
            data_frame.to_excel(filename, index=False)

        logger.info("a work is finished...")


if __name__ == "__main__":

    # ms = [2]
    # filenames=["None"]
    # main(ms, filenames, save=False, plot=True)

    start_time = datetime.datetime.now()
    filenames = ["output_m_5e-1.xlsx", "output_m_1.xlsx", "output_m_1p5.xlsx", "output_m_3.xlsx"]
    ms = [0.5, 1, 1.5, 2]  # sensitivity of return probability
    main(ms, filenames, save=True)
    end_time = datetime.datetime.now()
    logger.info("Total time: {} seconds".format((end_time - start_time).seconds))
