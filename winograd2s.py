#%%

import itertools

import sympy as sy
import numpy as np

from scipy.linalg import block_diag

#%% md

Tamanho dos vetores

#%%

nd = 3
ng = 2

#%% md

Vetor de exemplo

#%%

vd = list(range(1, nd+1))
vg = list(range(1, ng+1))

#%% md

Grau do polinômio

#%%

pd = nd - 1
pg = ng - 1

#%%

x = sy.symbols("x")
x

#%%

di = sy.symbols(" ".join(f"d{i}^2"for i in range(ng)))
di

#%%

gi = sy.symbols(" ".join(f"g{i}^2"for i in range(ng)))
gi

#%% md

# S2 livro

#%%

s2a = sy.Matrix([di[0] + di[1], di[0], di[1]])
s2a

#%%

s2b = sy.diag(gi[0], gi[1] - gi[0], gi[0] + gi[1])
s2b

#%%

s2c = sy.Matrix([
    [1, 0, -1],
    [1, 1, 0],
])

s2c

#%%

sy.MatMul(s2c, s2b, s2a)

#%%

sy.expand(s2c * s2b * s2a)

#%%

la = [[d.coeff(c, 1) for c in di] for d in list(s2a)]
la

#%%

sy.Matrix(la)

#%%

lb = [[sum(d).coeff(c, 1) for c in gi] for d in s2b.tolist()]
lb
sy.Matrix(lb)

#%% md

# S2 Társio


#%%

di2 = sy.symbols(" ".join(f"d{i}"for i in range(nd)))
di2

#%%

gi2 = sy.symbols(" ".join(f"g{i}"for i in range(ng)))
gi2

#%%

s2a2 = sy.Matrix([di2[0] + di2[1] - di2[2], di2[0] - di2[2], di2[1]])
s2a2

#%%

s2b2 = sy.diag(gi2[0], gi[1] - gi2[0], gi2[0] + gi2[1])
s2b2

#%%

sy.MatMul(s2c, s2b2, s2a2)
