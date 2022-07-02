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
import ray

EPSILON = 0.000001


def myround(num):
    num = num if abs(num) > EPSILON else 0
    return num


@ray.remote
def get_uniform_result(c, cr, s, h, step=0.01):
    uniform_ins = uniform(c=c, cr=cr, s=s, h=h, step=step)
    return uniform_ins.optimal_p, uniform_ins.alpha_o, uniform_ins.alpha_s, uniform_ins.optimal_profit


@ray.remote
def get_dual_result(c, cr, s, h, step=0.01):
    dual_ins = dual(c=c, cr=cr, s=s, h=h, step=step)
    return dual_ins.optimal_pon, dual_ins.optimal_poff, dual_ins.alpha_o, dual_ins.alpha_so, dual_ins.alpha_ss, dual_ins.optimal_profit


def main(xs, filenames, step=0.0025, plot=False):
    for x, filename in zip(xs, filenames):
        p_list = []
        u_demand = []

        piu_list = []
        pon_list = []
        poff_list = []
        d_demand = []
        pid_list = []

        cr = 0.32
        s = 0.05 - x
        h = 0.05 + x
        sel_c = np.arange(0.1, 0.181, 0.0025)

        results_uniform_id = []
        results_dual_id = []

        for c in sel_c:
            results_uniform_id.append(get_uniform_result.remote(c=c, cr=cr, s=s, h=h, step=step))
            results_dual_id.append(get_dual_result.remote(c=c, cr=cr, s=s, h=h, step=step))

        results_uniform = ray.get(results_uniform_id)
        results_dual = ray.get(results_dual_id)

        for result_uniform, result_dual in zip(results_uniform, results_dual):
            p_list.append(result_uniform[0])
            u_demand.append([result_uniform[1], result_uniform[2]])
            piu_list.append(result_uniform[3])

            pon_list.append(result_dual[0])
            poff_list.append(result_dual[1])
            d_demand.append([result_dual[2], result_dual[3], result_dual[4]])
            pid_list.append(result_dual[5])

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

        cols = ["c", "p_u", "on_demand_u", "off_demand_u", "pi_u",
                "pon", "poff", "on_demand_d", "show_demand_d", "off_demand_d", "pi_d"]
        data = np.array([sel_c, p_list, [k[0] for k in u_demand], [k[1] for k in u_demand], piu_list,
                         pon_list, poff_list, [k[0] for k in d_demand], [k[1] for k in d_demand],
                         [k[2] for k in d_demand], pid_list]).T

        data_frame = pd.DataFrame(data=data, columns=cols)
        data_frame.to_excel(filename, index=False)


if __name__ == "__main__":
    logging.getLogger('dual').setLevel(logging.ERROR)
    logging.getLogger('uniform').setLevel(logging.ERROR)

    logging.basicConfig()
    logger = logging.getLogger("compare")
    logger.setLevel(logging.INFO)

    # filenames = ["output_x_1e-3.xlsx", "output_x_1e-2.xlsx", "output_x_2e-2.xlsx"]
    # xs = [0.001, 0.01, 0.02]
    # filenames = ["output_x_1e-3.xlsx"]
    # xs = [0.001]
    # main(xs, filenames)
    try:
        main([0.05], ["output_x_5e-2.xlsx"], step=0.005, plot=True)
    except:
        print("the last work has not been successfully completed.")
