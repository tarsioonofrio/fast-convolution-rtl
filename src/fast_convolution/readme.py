toom_cook = """
Toom Cook is a method for linear convolution that garanties the minimal number
of multiplications by the Winograd theorem but rapdly increase the number of sums.
"""

manual_factorization = """
Manual factorization of s(x) = (g0 + g1x + g2x2)(d0 + d1x + d2x2)
with 6 multiplications and 10 additions
"""

tolimlin_4x3 = """
Tolimieri linear convolution for output length 4 and kernel length 3.
"""

bind_nested = """
Nesting is a method that bind two fast convolution matrices by multipling the input data
twice: one time in normal form, and other time by transposed form.
"""

bind_kron = """
Kronecker is a method that bind two fast convolution matrices by multipling the input data
by a kronecker product of the two transform matrices.
"""
