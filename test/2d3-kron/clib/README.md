# Fast Convolution
## Generator

Toom Cook is a method for linear convolution that garanties the minimal number
of multiplications by the Winograd theorem but rapdly increase the number of sums.

## Bind

Kronecker is a method that bind two fast convolution matrices by multipling the input data
by a kronecker product of the two transform matrices.

## Operations
Total multiplications: 25
Sums:
A: 121
C: 287
Total: 408
