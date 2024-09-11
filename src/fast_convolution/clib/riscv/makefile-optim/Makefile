#!/bin/bash

RISCV_DIR=$PWD
# Diretório de origem
SRC_DIR=$(realpath ../src)
SIM_DIR=$(realpath ${RISCV_DIR}/../../../sim/)


function run_riscv_verilator(){
    # Linha específica para edição
    LINE_NUM=47

    for FILE in "$SRC_DIR"/*.c; do
        cd ${1}
        # Extrai o nome do arquivo sem o caminho e sem a extensão
        FILE_NAME=$(basename "$FILE" .c)
        echo "Nome do arquivo sem extensão: ${FILE_NAME}"

        module purge
        module load riscv64-elf/14.1.0
        make clean
        make all TARGET=${FILE_NAME}


        cd ${SIM_DIR}
        # Novo texto para substituição
        BIN_FILE="\"${1}/${FILE_NAME}.bin\""
        # Substituir o conteúdo entre aspas na linha 45
        sed -i "${LINE_NUM}s|\".*\"|${BIN_FILE}|" testbench.sv

        module purge
        module load verilator/5.024-CXX20
        source /opt/rh/gcc-toolset-13/enable
        make clean
        make
        cp debug/Report.txt ${1}/report_${FILE_NAME}.txt
    done
}

# run_riscv_verilator ${RISCV_DIR}/makefile-normal

run_riscv_verilator ${RISCV_DIR}/makefile-optim

# Loop sobre todos os arquivos .c no diretório ../src
