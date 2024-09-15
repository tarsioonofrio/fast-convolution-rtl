cmake_minimum_required(VERSION 3.21)
project(fast_conv C)

set(CMAKE_C_STANDARD 90)

# generate file to clangd LSP
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(TEST_PATH ../../../test)

# set include paths
set(INC_INT src/int/lib/include)
#set(INC_INT_ITER src/int/include/base src/int/include/fast_iter)
set(TEST_DATA1 ${TEST_PATH}/1d/clib/src/data)
set(TEST_DATA2 ${TEST_PATH}/2d_nest/clib/src/data)
set(TEST_INC_OPT1 ${TEST_PATH}/1d/clib/src/lib/optim/include)
set(TEST_INC_OPT2_NEST ${TEST_PATH}/2d_nest/clib/src/lib_optim/include)
set(TEST_INC_OPT2_ITER ${TEST_PATH}/2d_iter/clib/src/lib_optim/include)

# set libs paths
set(LIB_FLOAT src/float/lib/convolution_float.c src/float/lib/util_float.c)

set(LIB1D src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/filter1dim.c)
set(LIB2D_NEST src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/filter2dim_nest.c)
set(LIB2D_ITER src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/filter2dim_nest.c)
set(LIB1D_OPT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/opt_fast_conv.c src/int/lib/filter1dim.c)
set(LIB2D_NEST_OPT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/opt_fast_conv.c src/int/lib/filter2dim_nest.c)
set(LIB2D_ITER_OPT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/opt_fast_conv_iter.c src/int/lib/filter2dim_iter.c)
set(TEST_LIB_OPT1 ${TEST_PATH}/1d/clib/src/lib_optim/optim.c)
set(TEST_LIB_OPT2_NEST ${TEST_PATH}/2d_nest/clib/src/lib_optim/optim.c)
set(TEST_LIB_OPT2_ITER ${TEST_PATH}/2d_iter/clib/src/lib_optim/optim.c)



# targets
# float
add_executable(fast-conv1d-float src/float/fast-conv1d-float.c ${LIB_FLOAT})
add_executable(fast-conv2d-nest-float src/float/fast-conv2d-nest-float.c ${LIB_FLOAT})
add_executable(fast-conv2d-iter-float src/float/fast-conv2d-iter-float.c ${LIB_FLOAT})

add_executable(filter1d-float src/float/filter1d-float.c ${LIB_FLOAT})
add_executable(filter2d-nest-float src/float/filter2d-nest-float.c ${LIB_FLOAT})
add_executable(filter2d-iter-float src/float/filter2d-iter-float.c ${LIB_FLOAT})

# int
add_executable(simple-conv src/int/simple-conv.c ${LIB1D})
add_executable(matrix-mult src/int/matrix-mult.c ${LIB1D})

add_executable(filter1d src/int/filter1d.c ${LIB1D})
add_executable(filter2d-nest src/int/filter2d-nest.c ${LIB2D_NEST})
add_executable(filter2d-iter src/int/filter2d-iter.c ${LIB2D_ITER})

# opt
add_executable(filter1d-opt src/int/filter1d.c ${LIB1D_OPT} ${TEST_LIB_OPT1})
add_executable(filter2d-nest-opt src/int/filter2d-nest.c ${LIB2D_NEST_OPT} ${TEST_LIB_OPT2_NEST})
add_executable(filter2d-iter-opt src/int/filter2d-iter.c ${LIB2D_ITER_OPT} ${TEST_LIB_OPT2_ITER})



# include header
# float
target_include_directories(fast-conv1d-float PRIVATE src/float/lib/include)
target_include_directories(fast-conv2d-nest-float PRIVATE src/float/lib/include)
target_include_directories(fast-conv2d-iter-float PRIVATE src/float/lib/include)

target_include_directories(filter1d-float PRIVATE src/float/lib/include)
target_include_directories(filter2d-nest-float PRIVATE src/float/lib/include)
target_include_directories(filter2d-iter-float PRIVATE src/float/lib/include)

# int
target_include_directories(matrix-mult PRIVATE ${INC_INT})
target_include_directories(simple-conv PRIVATE ${INC_INT})

target_include_directories(filter1d PRIVATE ${INC_INT})
target_include_directories(filter2d-nest PRIVATE ${INC_INT})
target_include_directories(filter2d-iter PRIVATE ${INC_INT})

# opt
target_include_directories(filter1d-opt PRIVATE ${INC_INT} ${TEST_INC_OPT1})
target_include_directories(filter2d-nest-opt PRIVATE ${INC_INT} ${TEST_INC_OPT2_NEST})
target_include_directories(filter2d-iter-opt PRIVATE ${INC_INT} ${TEST_INC_OPT2_ITER})



# include data
# float
target_include_directories(fast-conv1d-float PRIVATE ${TEST_DATA1})
target_include_directories(fast-conv2d-nest-float PRIVATE ${TEST_DATA2})
target_include_directories(fast-conv2d-iter-float PRIVATE ${TEST_DATA2})

target_include_directories(filter1d-float PRIVATE ${TEST_DATA1})
target_include_directories(filter2d-nest-float PRIVATE ${TEST_DATA2})
target_include_directories(filter2d-iter-float PRIVATE ${TEST_DATA2})

# int
target_include_directories(matrix-mult PRIVATE ${TEST_DATA1})
target_include_directories(simple-conv PRIVATE ${TEST_DATA1})

target_include_directories(filter1d PRIVATE ${TEST_DATA1})
target_include_directories(filter2d-nest PRIVATE ${TEST_DATA2})
target_include_directories(filter2d-iter PRIVATE ${TEST_DATA2})

# opt
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
