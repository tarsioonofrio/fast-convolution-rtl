#!/bin/bash

ROOT=$1
OUTPUT=$2
FILES=$(find ROOT -type f -name "report*.txt")

FIRST_FILE=$(echo "$FILES" | head -n 1)
HEAD_FILE=$(dirname ${FIRST_FILE})/header.txt
cut -c 1-25 ${FIRST_FILE} > ${HEAD_FILE}
sed -i "1i\\\\" ${HEAD_FILE}

for F in ${FILES}; do
    NAME=$(basename ${F})
    CUT_NAME=$(dirname ${F})/cut-${NAME}
    cut -c 26- ${F} > ${CUT_NAME}
    sed -i "1i${F}" ${CUT_NAME}
done

FILES_CUT=$(find ${ROOT} -type f -name "cut-report*.txt")

paste -d ";"  ${HEAD_FILE} ${FILES_CUT} > ${OUTPUT}
