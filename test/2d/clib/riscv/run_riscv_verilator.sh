#!/bin/bash

module load riscv64-elf/14.1.0

make clean
make all

riscv_path=$PWD
# Diretório de origem
src_dir=$(realpath ../src)

# Caminho do arquivo
# test_bench_file="../../../sim/testbench.sv"

# Linha específica para edição
line_number=47

module purge
module load verilator/5.024-CXX20
source /opt/rh/gcc-toolset-13/enable

cd ../../../sim/

# Loop sobre todos os arquivos .c no diretório ../src
for file in "$src_dir"/*.c; do
    # Extrai o nome do arquivo sem o caminho e sem a extensão
    filename=$(basename "$file" .c)

    # Faz algo com o nome do arquivo
    echo "Nome do arquivo sem extensão: $filename"

    # Novo texto para substituição
    bin_file="\"${riscv_path}/${filename}.bin\""
    # Substituir o conteúdo entre aspas na linha 45
    sed -i "${line_number}s|\".*\"|${bin_file}|" testbench.sv

    make clean
    make
    cp debug/Report.txt ${riscv_path}/report_${filename}.txt
done




# Ou para substituir tudo depois do caractere '=' na linha 45
# sed -i "${line_number}s|=.*|= ${new_text}|" "$file"

# Ou para substituir tudo após o caractere 47 na linha 45
# sed -i "${line_number}s|.\{47\}.*|${new_text}|" "$file"
