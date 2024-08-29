================
Fast Convolution
================

Package that implement some fast convolution algoritms


Install
-------

`pip install -e .`


Features
--------

* TODO


RS5
---

* Geração do hex para RS5 (riscv64-elf)

cd RS5/app/(applcation)

    module load riscv64-elf/14.1.0
    make clean
    make all


Simulação (verilator)

cd ../../sim/

Importante :  o  testbench.sv   lê o binário na linha 43

    localparam string        BIN_FILE        = "../app/conv/test.bin";



    module purge
    module load verilator/5.024-CXX20
    source /opt/rh/gcc-toolset-13/enable
    make
    more debug/Report.txt


Credits
-------


This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
