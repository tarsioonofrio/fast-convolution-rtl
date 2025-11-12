from __future__ import annotations

from .bitmath import log2_lst, log2_matrix, matrix_to_log2, recursive_log2
from .codegen_c import (
    c_hadamart_product_nollop,
    c_header,
    c_matmul_shift_noloop,
    c_matmul_shift_noloop_nest,
    c_shift,
    matmul,
)
from .convolution import (
    conv_circ_fft,
    default_convolve,
    symmetrical_cyclic_convolution,
    winograd_cyclic_conv2x2,
)
from .csa import (
    count_sums,
    csa_config,
    csa_config_nest,
    csa_lst,
    csa_parcels,
    csa_parcels_nest,
    max_power,
    write_csa_config,
    write_csa_parcels,
)
from .plotting import plot_pdf, plot_pdf2col
from .polynomials import symmetrical_polynomial_factorization
from .sv_codegen import (
    is_two_power,
    matmul_sv,
    matmul_sv2,
    sv_bitshift,
    sv_mux_mult,
    sv_nest,
    sv_pkg,
)

__all__ = [
    "plot_pdf",
    "plot_pdf2col",
    "symmetrical_polynomial_factorization",
    "symmetrical_cyclic_convolution",
    "winograd_cyclic_conv2x2",
    "conv_circ_fft",
    "default_convolve",
    "c_header",
    "c_shift",
    "c_matmul_shift_noloop",
    "c_matmul_shift_noloop_nest",
    "c_hadamart_product_nollop",
    "matmul",
    "recursive_log2",
    "log2_lst",
    "log2_matrix",
    "matrix_to_log2",
    "count_sums",
    "csa_lst",
    "max_power",
    "csa_config",
    "csa_config_nest",
    "write_csa_config",
    "csa_parcels",
    "csa_parcels_nest",
    "write_csa_parcels",
    "is_two_power",
    "matmul_sv",
    "matmul_sv2",
    "sv_bitshift",
    "sv_nest",
    "sv_mux_mult",
    "sv_pkg",
]
