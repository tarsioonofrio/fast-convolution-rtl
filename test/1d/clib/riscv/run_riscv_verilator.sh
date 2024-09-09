#!/bin/bash

# Caminho do arquivo
file="../../sim/testbench.sv"

# Linha específica para edição
line_number=45

# Novo texto para substituição
new_text='"../novo/caminho/nome_do_arquivo.bin"'

# Substituir o conteúdo entre aspas na linha 45
sed -i "${line_number}s|\".*\"|${new_text}|" "$file"

# Ou para substituir tudo depois do caractere '=' na linha 45
# sed -i "${line_number}s|=.*|= ${new_text}|" "$file"

# Ou para substituir tudo após o caractere 47 na linha 45
# sed -i "${line_number}s|.\{47\}.*|${new_text}|" "$file"
