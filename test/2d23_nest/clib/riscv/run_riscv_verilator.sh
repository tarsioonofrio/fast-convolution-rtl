#!/bin/bash

RISCV_DIR=$PWD
# Diretório de origem
SRC_DIR=$(realpath ../src)
SIM_DIR=$1


function run_riscv_verilator(){
    # Linha específica para edição
    LINE_NUM=47
    for FILE in "$SRC_DIR"/*.c; do
        cd ${1}
        # Extrai o nome do arquivo sem o caminho e sem a extensão
        FILE_NAME=$(basename "$FILE" .c)
        if [ -n "$2" ] && [ "$FILE_NAME" == "simple-conv" ]; then
            continue  # Pula para o próximo arquivo
        fi
        
        echo "FILE: ${FILE_NAME}"

        module purge
        module load riscv64-elf/14.1.0
        make clean

        if [ -z "${3}" ]; then
            make all TARGET=${FILE_NAME}
            REPORT=report_${FILE_NAME}
        else
            make all TARGET=${FILE_NAME} OPT=opt
            REPORT=report_opt_${FILE_NAME}
        fi

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
        cp debug/Report.txt ${1}/${REPORT}.txt
    done
}

run_riscv_verilator ${RISCV_DIR} 0
run_riscv_verilator ${RISCV_DIR} 1 1

