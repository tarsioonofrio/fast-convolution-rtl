cmake_minimum_required(VERSION 3.0)

project(MyProject)

# Defina as opções de compilação
include_directories(${CMAKE_SOURCE_DIR}/../src/lib/include ${CMAKE_SOURCE_DIR}/../src/data ${CMAKE_SOURCE_DIR}/common/include)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=rv32im_zicsr -mabi=ilp32 -Os -Wall -std=c23")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --specs=nano.specs -T ../common/link.ld -march=rv32im_zicsr -mabi=ilp32 -nostartfiles")

set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "")
set(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "")


set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR riscv64)

# Definir o caminho do Toolchain RISCV
set(CMAKE_C_COMPILER riscv64-elf-gcc)
set(CMAKE_OBJCOPY riscv64-elf-objcopy)
set(CMAKE_OBJDUMP riscv64-elf-objdump)

# Defina os arquivos fonte
# set(SRC_FILES
#     ../src/simple-conv.c
#     ${CMAKE_SOURCE_DIR}/../src/lib/*.c
#     ${CMAKE_SOURCE_DIR}/common/*.c
# )

# set(ASM_FILES
#     ${CMAKE_SOURCE_DIR}/common/*.S
# )

# Adicione os targets
add_executable(simple-conv ${CMAKE_SOURCE_DIR}/../src/simple-conv.c ${CMAKE_SOURCE_DIR}/../src/lib/convolution.c ${CMAKE_SOURCE_DIR}/../src/lib/util.c ${CMAKE_SOURCE_DIR}/common/crt0.S ${CMAKE_SOURCE_DIR}/common/newlib.c)
# add_executable(simple-conv ${SRC_FILES} ${ASM_FILES})
# target_link_libraries(simple-conv -specs=nano.specs -T common/link.ld)

# Adicione mais targets conforme necessário
# add_executable(outro-target ${OUTRO_SRC_FILES})

# Adicione comandos pós-compilação (binário e lst)
add_custom_command(TARGET simple-conv POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} simple-conv simple-conv.bin -O binary
    COMMAND ${CMAKE_OBJDUMP} -S simple-conv > simple-conv.lst
)