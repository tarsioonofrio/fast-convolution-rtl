# Fast Convolution
## Generator

Manual factorization of s(x) = (g0 + g1x + g2x2)(d0 + d1x + d2x2)
with 6 multiplications and 10 additions

## Bind

Nesting is a method that bind two fast convolution matrices by multipling the input data
twice: one time in normal form, and other time by transposed form.

## Operations
Total multiplications: 36
Sums:
A: 18
C: 24
Total: 42
