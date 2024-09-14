cmake_minimum_required(VERSION 3.21)
project(fast_conv C)

set(CMAKE_C_STANDARD 90)

# generate file to clangd LSP
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(TEST_PATH ../../../test)

set(OPT_NEST src/int/lib_optim/fast_conv_nest.c)
set(OPT_ITER src/int/lib_optim/fast_conv_iter.c)

set(TEST_DATA1 ${TEST_PATH}/1d/clib/src/data)
set(TEST_DATA2 ${TEST_PATH}/2d/clib/src/data)
set(TEST_OPT1 ${TEST_PATH}/1d/clib/src/lib_optim/optim.c)
set(TEST_OPT2 ${TEST_PATH}/2d/clib/src/lib_optim/optim.c)
set(TEST_OPT1_INC ${TEST_PATH}/1d/clib/src/lib_optim/include)
set(TEST_OPT2_INC ${TEST_PATH}/2d/clib/src/lib_optim/include)

set(LIB_INT src/int/lib/convolution.c src/int/lib/fast_conv.c src/int/lib/util.c)
set(LIB_FLOAT src/float/lib/convolution_float.c src/float/lib/util_float.c)
set(LIB_OPT src/int/lib/convolution.c src/int/lib/util.c)


# targets
add_executable(simple-conv src/int/simple-conv.c ${LIB_INT})
add_executable(matrix-mult src/int/matrix-mult.c ${LIB_INT})

add_executable(fast-conv1d-float src/float/fast-conv1d-float.c ${LIB_FLOAT})
add_executable(fast-conv2d-nest-float src/float/fast-conv2d-nest-float.c ${LIB_FLOAT})
add_executable(fast-conv2d-iter-float src/float/fast-conv2d-iter-float.c ${LIB_FLOAT})

add_executable(filter1d-float src/float/filter1d-float.c ${LIB_FLOAT})
add_executable(filter2d-nest-float src/float/filter2d-nest-float.c ${LIB_FLOAT})
add_executable(filter2d-iter-float src/float/filter2d-iter-float.c ${LIB_FLOAT})

add_executable(filter1d src/int/filter1d.c ${LIB_INT})
add_executable(filter2d-iter src/int/filter2d-iter.c ${LIB_INT})
add_executable(filter2d-nest src/int/filter2d-nest.c ${LIB_INT})

add_executable(filter1d-opt src/int/filter1d.c ${LIB_OPT})
add_executable(filter2d-nest-opt src/int/filter2d-iter.c ${LIB_OPT} ${OPT_NEST} ${TEST_OPT2})
add_executable(filter2d-iter-opt src/int/filter2d-nest.c ${LIB_OPT} ${OPT_ITER} ${TEST_OPT2})

# include lib
target_include_directories(fast-conv1d-float PRIVATE src/float/lib/include)
target_include_directories(fast-conv2d-nest-float PRIVATE src/float/lib/include)
target_include_directories(fast-conv2d-iter-float PRIVATE src/float/lib/include)

target_include_directories(filter1d-float PRIVATE src/float/lib/include)
target_include_directories(filter2d-nest-float PRIVATE src/float/lib/include)
target_include_directories(filter2d-iter-float PRIVATE src/float/lib/include)

target_include_directories(filter1d PRIVATE src/int/lib/include)
target_include_directories(filter2d-nest PRIVATE src/int/lib/include)
target_include_directories(filter2d-iter PRIVATE src/int/lib/include)

target_include_directories(filter1d-opt PRIVATE src/int/lib/include ${TEST_OPT1_INC})
target_include_directories(filter2d-nest-opt PRIVATE src/int/lib/include ${TEST_OPT2_INC})
target_include_directories(filter2d-iter-opt PRIVATE src/int/lib/include ${TEST_OPT2_INC})

target_include_directories(simple-conv PRIVATE src/int/lib/include)
target_include_directories(simple-conv PRIVATE ${TEST_DATA1})
target_include_directories(matrix-mult PRIVATE src/int/lib/include)


# include data
target_include_directories(fast-conv1d-float PRIVATE ${TEST_DATA1})
target_include_directories(fast-conv2d-nest-float PRIVATE ${TEST_DATA2})
target_include_directories(fast-conv2d-iter-float PRIVATE ${TEST_DATA2})

target_include_directories(filter1d-float PRIVATE ${TEST_DATA1})
target_include_directories(filter2d-nest-float PRIVATE ${TEST_DATA2})
target_include_directories(filter2d-iter-float PRIVATE ${TEST_DATA2})

target_include_directories(filter1d PRIVATE ${TEST_DATA1})
target_include_directories(filter2d-nest PRIVATE ${TEST_DATA2})
target_include_directories(filter2d-iter PRIVATE ${TEST_DATA2})

target_include_directories(filter1d-opt PRIVATE ${TEST_DATA1})
target_include_directories(filter2d-nest-opt PRIVATE ${TEST_DATA2})
target_include_directories(filter2d-iter-opt PRIVATE ${TEST_DATA2})

# link libs
target_link_libraries(fast-conv1d-float m)
target_link_libraries(fast-conv2d-nest-float m)
target_link_libraries(fast-conv2d-iter-float m)
target_link_libraries(filter1d-float m)
target_link_libraries(filter2d-nest-float m)
target_link_libraries(filter2d-iter-float m)
