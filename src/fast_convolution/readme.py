conv_toom_cook = """
Toom Cook its a method for linear convolution that garanties the minimal number
of multiplications by the Winograd theorem but rapdly increase the number of sums.
"""

conv_manual_fact = """
Manual factorization of s(x) = (g0 + g1x + g2x2)(d0 + d1x + d2x2)
with 6 multiplications and 10 additions
"""

bind_nested = """
Bind two fast convolution matrices with multipling the input data
twice by the tranform matrices, one time in normal form,
and other time by transposed form.
"""

bind_kron = """
Bind two fast convolution matrices with multipling the input data
by a kronecker product of the two transform matrices.
"""
