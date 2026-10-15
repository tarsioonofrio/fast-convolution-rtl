=====
Usage
=====

The package installs the ``fast-conv`` command line interface. Run
``fast-conv --help`` to list the top-level subcommands, or ask for the help of
a specific one::

    fast-conv --help
    fast-conv build 1d toom-cook --help

A typical workflow runs on a repository, which is the current directory by
default (``-p/--path`` selects another one):

1. ``init`` the problem sizes in one or two dimensions::

       fast-conv init 1d -i 32 -o 30 -w 3
       fast-conv init 2d -i 32 -o 30 -w 3

2. ``build`` the fast algorithm. The 1-D and 2-D builders are ``toom-cook``,
   ``manual`` and ``tolimlin4x3``; 2-D transforms can also be bound with
   ``bind nest`` or ``bind kron``::

       fast-conv build 1d toom-cook
       fast-conv build 2d toom-cook
       fast-conv build 2d bind kron

3. ``quant`` the coefficients, without quantization or with a bit shift::

       fast-conv quant none
       fast-conv quant shift --bits 4

4. ``sim`` to generate the SystemVerilog packages, C headers and golden
   datasets. Features and weights can come from files, integers or a normal
   distribution::

       fast-conv sim file --feature images/karatsuba032.jpg --weight images/laplace.json
       fast-conv sim int -i 1 -o 1
       fast-conv sim normal -i 1 -o 1
