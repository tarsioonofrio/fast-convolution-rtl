=================================================================================
fast-convolution-rtl: fast-convolution algorithms, golden models and RTL helpers
=================================================================================

This package builds fast 1-D and 2-D convolution algorithms (Toom-Cook, the Winograd polynomial / Tolimieri
linear construction and manual factorizations), quantizes them, simulates them in integer arithmetic and
exports what an RTL implementation needs: SystemVerilog packages and helper modules, C headers and golden
datasets.

It generates the datasets and golden outputs of the FastConv accelerators
(`FastConv_SystemVerilog <https://github.com/tarsioonofrio/FastConv_SystemVerilog>`_), including those of

    "Trading Multiplications for Simpler Transforms: Area and Energy Efficiency of Polynomial Winograd
    Convolution," submitted to the *IEEE International Symposium on Circuits and Systems (ISCAS)*, 2027.

The integer simulation models the RTL arithmetic bit for bit (truncated or rounded transformed weights,
fractional bits, word-width wrap-around), so an RTL run is accepted only when every output word equals the
golden. It also writes WinoCNN-compatible inputs, used to run the WinoCNN baseline on the same data.

Layout
------

==========================  ======================================================================================
Folder                      Content
==========================  ======================================================================================
``src/fast_convolution/``   the package: ``cli.py`` (``fast-conv``), builders (``build.py``, ``bind.py``, ``fast.py``,
                            ``naive.py``, ``cyclic.py``, ``fft.py``), quantization (``quant.py``), integer simulation
                            and dataset export (``simulation.py``, ``winocnn.py``), SystemVerilog/C/LaTeX writers,
                            ``template/`` (SystemVerilog and Makefile templates), ``clib/`` (C library)
``test/``                   ``pytest`` suite and one reference repository per algorithm (``1d-tc3``, ``2d-tcn16``, ...)
``docs/``                   Sphinx documentation (``usage.rst``, ``installation.rst``)
``images/``                 example inputs for ``sim file`` (images, a Laplace kernel)
``etc/``                    shell templates and debugging helpers
==========================  ======================================================================================

Algorithms
----------

An algorithm lives in a *repository*: a folder whose ``config/`` holds the problem size (``init.json``), the
matrices (``build.json``: interpolation points ``p``, input transform ``c``, scaling ``q``, weight transform
``b``, inverse ``a``), the generator name (``gen.json``), the bind method (``bind.json``) and the quantization
(``quant.json``). The builders write these files; any other bilinear algorithm can be added by writing
``build.json`` by hand.

==================  ==========================================  ========================================
Builder             Algorithm                                   Example repository in ``test/``
==================  ==========================================  ========================================
``toom-cook``       Toom-Cook interpolation, any output size;   ``1d-tc2``, ``1d-tc3``, ``2d-tcn4``,
                    points given with ``--p1``/``--p2``         ``2d-tcn9``, ``2d-tcn16``
``tolimlin4x3``     Tolimieri linear F(4,3), the Winograd       ``1d-tolimlin``, ``2d-tolimlin``
                    polynomial algorithm of the ISCAS 2027 WP
``manual``          the six-multiplication and 6×6              ``1d-if3``, ``2d-ifn9``, ``2d-ifk9``
                    manual factorizations (Inspection
                    Factorization)
``bind nest|kron``  2-D algorithm from two 1-D ones (nested     every ``2d-*``
                    or Kronecker)
==================  ==========================================  ========================================

Quick start
-----------

Install in a Python 3.9 virtual environment (NumPy 1.24 has no wheels for newer Pythons) and run the tests
(about 30 s)::

    uv venv --python 3.9 .venv && uv pip install --python .venv/bin/python -e .   # or python3.9 -m venv + pip
    .venv/bin/python -m pytest -q              # 144 passed
    git restore -- test                        # the tests rewrite test/*/sim/sim/sim.txt

Build the 2-D Toom-Cook F(2,3) from scratch and generate the dataset of the ISCAS 2027 point ``TCtw``
(3 input channels, 12 output channels, 32×32 input, seed 0, 16-bit words, truncated transformed weights)::

    mkdir tc23 && cd tc23
    fast-conv init 2d -o 2 -w 3
    fast-conv build 2d toom-cook
    fast-conv build 2d bind nest
    fast-conv quant shift -b 8
    fast-conv sim normal --image-side 32 -i 3 -o 12 -d 0 --no-c --truncated-weight-transform --nbits 16 -n tctw

``s.txt``, ``g.txt`` and ``d.txt`` in ``sim/sim-tctw/`` are byte-identical to the committed dataset
``FastConv_SystemVerilog/rtl/conv2x2/data/tcn4/sim/sim-032-3-12-normal-trunc-nbits16/``. Without a LaTeX
compiler the builders print a warning and skip the PDF of the derivation.

Requirements
------------

==================  ===============  ==================================================================
Item                Version used     Notes
==================  ===============  ==================================================================
Python              3.9              dependencies in ``requirements.txt`` (SymPy 1.12, NumPy 1.24,
                                     SciPy 1.10, ...)
LaTeX               optional         ``latexmk`` or ``pdflatex`` for the PDFs of each derivation
C compiler, CMake   optional         to build the generated C library in ``clib/``
==================  ===============  ==================================================================

Where each dataset of the papers comes from
-------------------------------------------

Every dataset in ``FastConv_SystemVerilog/rtl/conv*/data/<algorithm>/sim/`` was written by ``fast-conv sim``
on the algorithm repository next to it (``data/<algorithm>/config/``). Its ``generation.json`` records the
command options (seed, channels, image side, word width, rounding, fractional bits), the revision of this
package and the SHA-256 of ``pack_data.sv``; ``README.md`` in the dataset folder repeats the exact command.
The six datasets of the ISCAS 2027 paper are listed in ``FastConv_SystemVerilog/report/iscas2027/``.

============================  ===============================================================================
Dataset option                Meaning
============================  ===============================================================================
``sim normal -d <seed>``      inputs and weights drawn from N(0, 1) with that seed, quantized to Q8
``--truncated-weight-``       transformed weights shifted to the RTL word before the MACs (the RTL computes or
``transform``                 stores them this way)
``--rounding nearest``        round instead of floor the transformed weights and the products
``--weight-frac-bits F``      F extra fractional bits kept in the transformed weights
``--extra-frac-bits G``       G fractional bits kept in the partial sums and removed by one final shift
``--nbits N``                 signed N-bit words with wrap-around, as the RTL registers
``--exact-scaled``            transformed weights exported as integer numerators, scaled once at the output
============================  ===============================================================================

Flow, step by step
------------------

1. **init** (``fast-conv init 1d|2d -i <in> -o <out> -w <kernel>``) writes ``config/init.json``.
2. **build** (``fast-conv build 1d|2d <builder>``) derives the matrices into ``config/build.json`` and a LaTeX
   derivation into ``build/``. For 2-D, ``build 2d bind nest`` (or ``kron``) combines the two dimensions and
   writes the carry-save adder trees of the input transform (``build/bind-nest/``).
3. **quant** (``fast-conv quant none|shift -b <bits>``) fixes the fixed-point format (Q8 with ``-b 8``).
4. **sim** (``fast-conv sim file|int|normal``) runs the naive and the fast convolution in floating point and in
   integer arithmetic, then writes:

   * ``sv/``: ``pack_param.sv``, ``mult_matrices.sv``/``mult_matrices_csa.sv`` (input transform) and the
     time-multiplexed ``mux_mult_XX.sv``;
   * ``clib/``: ``build.h``, ``build_shift.h``, ``init.h``, ``sim.h``, ``sim_float.h`` (unless ``--no-c``);
   * ``sim/sim-<name>/``: ``pack_data.sv`` (inputs, weights and golden output for the testbench), the
     reference arrays ``d`` (naive), ``g`` (fast, floating point), ``s`` (fast, integer), ``sim.txt``,
     ``generation.json``, and ``winocnn/`` (``feature.bin``, ``weight.bin``, ``params.json``).

``fast-conv example rand|seq|list`` prints a small worked example. ``docs/usage.rst`` describes every option.

Notes
-----

- **Bias** is zero unless ``--enable-bias`` is given to a ``sim`` subcommand (``--bias`` sets the mean).
- **Exact Winograd weights** (``--exact-scaled``): the 2-D weight transform is exported as integer numerators
  without rounding each coefficient; products and accumulation stay at the common scale (4 for TC 2×2) and the
  output is reduced once. ``pack_data.sv`` then sets ``EXACT_SCALED_WEIGHTS = 1`` and ``WEIGHT_TRANSFORM_SCALE``
  and appends the quantized spatial weights, so a row-by-row RTL can read the nine raw weights. The option is
  refused together with ``--enable-bias``, which the matching RTL does not support.
- **Algorithms without a builder** (for instance the 7-product bit-shift F(4,3) or the direct convolution used
  by FastConv) are added by writing ``config/build.json``; ``bind`` needs a generator name it knows in
  ``config/gen.json`` (use ``tolimlin_4x3`` during the bind and restore the descriptive name afterwards).
- **Verilator line limit.** Long arrays in ``pack_data.sv`` can exceed the about 40 000 tokens per line that
  Verilator 5.052 accepts; FastConv wraps them at 16 values per line, values unchanged.
- Earlier versions of this README described building an RS5 (RISC-V) application; that code is not part of
  this repository.

Limitations
-----------

- Only 2-D algorithms support ``--truncated-weight-transform`` and the rounding and fractional-bit options.
- Inputs are synthetic (normal distribution, files or integers); real network layers are fed through
  ``sim file`` or by building the payload in Python (``fast_convolution.simulation.SimulationPayload``).
- The quantization model is fixed point with power-of-two scales.

License
-------

``pyproject.toml`` declares the package "Not open source"; no license file has been added, so the author keeps
all rights. The package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
