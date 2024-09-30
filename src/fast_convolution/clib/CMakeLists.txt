cmake_minimum_required(VERSION 3.21)
project(fast_conv C)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
# generate file to clangd LSP

set(CMAKE_C_STANDARD 90)

set(PRJ1D 1d3)
set(PRJ2D_NEST 2d3_nest)
set(PRJ2D_ITER 2d3_iter)

set(TEST_PATH ../../../test)

# set include paths
set(INC_FLOAT src/float/lib/include)
set(INC_INT src/int/lib/include)
set(TEST_DATA1 ${TEST_PATH}/${PRJ1D}/clib/src/data)
set(TEST_DATA2 ${TEST_PATH}/${PRJ2D_NEST}/clib/src/data)
set(TEST_DATA1_FLOAT ${TEST_PATH}/${PRJ1D}/clib/src/data_float)
set(TEST_DATA2_FLOAT ${TEST_PATH}/${PRJ2D_NEST}/clib/src/data_float)
set(TEST_INC_OPT1 ${TEST_PATH}/${PRJ1D}/clib/src/lib/include)
set(TEST_INC_OPT2_NEST ${TEST_PATH}/${PRJ2D_NEST}/clib/src/lib/include)
set(TEST_INC_OPT2_ITER ${TEST_PATH}/${PRJ2D_ITER}/clib/src/lib/include)

# set libs paths
set(LIB_FLOAT src/float/lib/convolution_float.c src/float/lib/util_float.c)
set(LIB_INT src/int/lib/convolution.c src/int/lib/util.c)

#set(LIB_INT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/filter1dim.c)
#set(LIB_INT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/filter2dim_nest.c)
#set(LIB_INT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/filter2dim_nest.c)
#set(LIB_INT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/opt_fast_conv.c src/int/lib/filter1dim.c)
#set(LIB_INT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/opt_fast_conv.c src/int/lib/filter2dim_nest.c)
#set(LIB_INT src/int/lib/convolution.c src/int/lib/util.c src/int/lib/opt_fast_conv_iter.c src/int/lib/filter2dim_iter.c)
set(TEST_LIB_OPT1 ${TEST_PATH}/${PRJ1D}/clib/src/lib/optim.c)
set(TEST_LIB_OPT2_NEST ${TEST_PATH}/${PRJ2D_NEST}/clib/src/lib/optim.c)
set(TEST_LIB_OPT2_ITER ${TEST_PATH}/${PRJ2D_ITER}/clib/src/lib/optim.c)



# targets
# float
add_executable(float-fast-conv1d src/float/fast-conv1d-float.c ${LIB_FLOAT})
add_executable(float-fast-conv2d-nest src/float/fast-conv2d-nest-float.c ${LIB_FLOAT})
add_executable(float-fast-conv2d-iter src/float/fast-conv2d-iter-float.c ${LIB_FLOAT})

add_executable(float-filter1d src/float/filter1d-float.c ${LIB_FLOAT})
add_executable(float-filter2d-nest src/float/filter2d-nest-float.c ${LIB_FLOAT})
add_executable(float-filter2d-iter src/float/filter2d-iter-float.c ${LIB_FLOAT})

# int
add_executable(standard src/int/standard.c ${LIB_INT})
add_executable(matrix-mult src/int/matrix-mult.c ${LIB_INT})

add_executable(filter1d src/int/filter1d.c ${LIB_INT})
add_executable(filter2d-nest src/int/filter2d-nest.c ${LIB_INT})
add_executable(filter2d-iter src/int/filter2d-iter.c ${LIB_INT})

# opt
add_executable(filter1d-opt src/int/filter1d.c ${LIB_INT} ${TEST_LIB_OPT1})
add_executable(filter2d-nest-opt src/int/filter2d-nest.c ${LIB_INT} ${TEST_LIB_OPT2_NEST})
add_executable(filter2d-iter-opt src/int/filter2d-iter.c ${LIB_INT} ${TEST_LIB_OPT2_ITER})



# include header
# float
target_include_directories(float-fast-conv1d PRIVATE ${INC_FLOAT})
target_include_directories(float-fast-conv2d-nest PRIVATE ${INC_FLOAT})
target_include_directories(float-fast-conv2d-iter PRIVATE ${INC_FLOAT})

target_include_directories(float-filter1d PRIVATE ${INC_FLOAT})
target_include_directories(float-filter2d-nest PRIVATE ${INC_FLOAT})
target_include_directories(float-filter2d-iter PRIVATE ${INC_FLOAT})

# int
target_include_directories(matrix-mult PRIVATE ${INC_INT})
target_include_directories(standard PRIVATE ${INC_INT})

target_include_directories(filter1d PRIVATE ${INC_INT})
target_include_directories(filter2d-nest PRIVATE ${INC_INT})
target_include_directories(filter2d-iter PRIVATE ${INC_INT})

# opt
target_include_directories(filter1d-opt PRIVATE ${INC_INT} ${TEST_INC_OPT1})
target_include_directories(filter2d-nest-opt PRIVATE ${INC_INT} ${TEST_INC_OPT2_NEST})
target_include_directories(filter2d-iter-opt PRIVATE ${INC_INT} ${TEST_INC_OPT2_ITER})

# include data
# float
target_include_directories(float-fast-conv1d PRIVATE  ${TEST_DATA1} ${TEST_DATA1_FLOAT})
target_include_directories(float-fast-conv2d-nest PRIVATE ${TEST_DATA2} ${TEST_DATA2_FLOAT})
target_include_directories(float-fast-conv2d-iter PRIVATE ${TEST_DATA2} ${TEST_DATA2_FLOAT})

target_include_directories(float-filter1d PRIVATE ${TEST_DATA1} ${TEST_DATA1_FLOAT})
target_include_directories(float-filter2d-nest PRIVATE ${TEST_DATA2} ${TEST_DATA2_FLOAT})
target_include_directories(float-filter2d-iter PRIVATE ${TEST_DATA2} ${TEST_DATA2_FLOAT})

# int
target_include_directories(matrix-mult PRIVATE ${TEST_DATA1})
target_include_directories(standard PRIVATE ${TEST_DATA1})

target_include_directories(filter1d PRIVATE ${TEST_DATA1})
target_include_directories(filter2d-nest PRIVATE ${TEST_DATA2})
target_include_directories(filter2d-iter PRIVATE ${TEST_DATA2})

# opt
target_include_directories(filter1d-opt PRIVATE ${TEST_DATA1})
target_include_directories(filter2d-nest-opt PRIVATE ${TEST_DATA2})
target_include_directories(filter2d-iter-opt PRIVATE ${TEST_DATA2})

# directives
target_compile_definitions(filter1d-opt PUBLIC OPTIM=1)
target_compile_definitions(filter2d-nest-opt PUBLIC OPTIM=2)
target_compile_definitions(filter2d-iter-opt PUBLIC OPTIM=3)

# link libs
target_link_libraries(float-fast-conv1d m)
target_link_libraries(float-fast-conv2d-nest m)
target_link_libraries(float-fast-conv2d-iter m)
target_link_libraries(float-filter1d m)
target_link_libraries(float-filter2d-nest m)
target_link_libraries(float-filter2d-iter m)
