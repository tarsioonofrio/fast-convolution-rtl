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

CLI
---

Bias is only enabled when passing ``--enable-bias`` to ``fast-conv sim`` subcommands.

Example::

    python -m fast_convolution.cli sim int --enable-bias --bias 4


Pesos Winograd exatos
---------------------

Para os algoritmos 2-D, ``sim`` pode exportar a transformada dos pesos como
numeradores inteiros, sem arredondar cada um dos coeficientes transformados.
Use ``--exact-scaled`` nos subcomandos ``sim file``, ``sim int`` ou
``sim normal``. Para TC2x2 a escala comum atual é quatro; os produtos e a
acumulação permanecem nessa escala e a redução é feita uma única vez na saída.

O pacote ``pack_data.sv`` gerado nesse modo marca o contrato com
``EXACT_SCALED_WEIGHTS = 1`` e informa a escala em
``WEIGHT_TRANSFORM_SCALE``. A variante RTL correspondente deve manter a
acumulação alargada e consumir os 16 numeradores transformados diretamente.
Essa variante permanece no contrato sem bias do ``Conv`` atual; o gerador
recusa ``--exact-scaled`` combinado com ``--enable-bias`` para não produzir um
golden output que o RTL não possa reproduzir.

O mesmo pacote também inclui, ao final da região dos pesos transformados, os
pesos espaciais quantizados originais. Isso permite a variante RTL
``stream12-rowconst4-exact``: ela lê os nove valores, calcula somente a linha
necessária da transformada por ciclo e mantém o numerador sem a rede de
arredondamento por linha.


RS5
---

* Geração do hex para RS5 (riscv64-elf)

cd RS5/app/(application)

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
    make; more debug/Report.txt


Credits
-------


This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
