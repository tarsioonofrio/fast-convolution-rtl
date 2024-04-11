#!/usr/bin/env python
# coding: utf-8

import sympy as sy
import numpy as np

from matplotlib import pyplot as plt

from notebooks.fast_convolution import toom_cook, g2bg, log2_lst, log2_matrix

# from sympy import init_printing
# init_printing(use_latex='png', forecolor='White', backcolor='Black')

d_num = 4
g_num = 3

d_values = list(range(1, d_num+1))
g_values = list(range(1, g_num+1))
print(d_values, g_values)

c_mtx, cq, b_mtx, a_mtx = toom_cook(d_num, g_num, [0, -1, 1, -2, 2, np.inf])
# c_mtx, cq, b_mtx, a_mtx

fig = plt.figure(figsize=(3, 3), linewidth=1, edgecolor='black')
fig.text(.2, .7, "plain text: alpha > beta")
fig.text(.2, .5, "Mathtext: $\\alpha > \\beta$")
fig.text(.2, .3, r"raw string Mathtext: $\alpha > \beta$")
plt.show()

c_log = log2_matrix(log2_lst(c_mtx))
a_log = log2_matrix(log2_lst(a_mtx))

bg_mtx = g2bg(cq, b_mtx, g_values)

s = sy.MatMul(c_mtx, bg_mtx, a_mtx, sy.Matrix(d_values))
s


cm = plt.figure(linewidth=1, edgecolor='black')
cm.text(.2, .7, f"r{c_mtx._repr_latex_()}")
# fig.text(.2, .5, "Mathtext: $\\alpha > \\beta$")
# fig.text(.2, .3, r"raw string Mathtext: $\alpha > \beta$")
plt.show()

