cmake_minimum_required(VERSION 3.21)
project(fast_conv C)

set(CMAKE_C_STANDARD 90)

# generate file to clangd LSP
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# targets
add_executable(simple-conv src/int/simple-conv.c src/int/lib/convolution.c src/int/lib/util.c)
add_executable(matrix-mult src/int/matrix-mult.c src/int/lib/convolution.c src/int/lib/util.c)

add_executable(fast-conv1d-float src/float/fast-conv1d-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)
add_executable(fast-conv2d-nest-float src/float/fast-conv2d-nest-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)
add_executable(fast-conv2d-iter-float src/float/fast-conv2d-iter-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)

add_executable(filter1d-float src/float/filter1d-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)
add_executable(filter2d-nest-float src/float/filter2d-nest-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)
add_executable(filter2d-iter-float src/float/filter2d-iter-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)

add_executable(filter1d src/int/filter1d.c src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/include/fast_conv.h)
add_executable(filter2d-iter src/int/filter2d-iter.c src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/include/fast_conv.h)
add_executable(filter2d-nest src/int/filter2d-nest.c src/int/lib/convolution.c src/int/lib/util.c src/int/lib/fast_conv.c src/int/lib/include/fast_conv.h)


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

target_include_directories(simple-conv PRIVATE src/int/lib/include)
target_include_directories(simple-conv PRIVATE ../../../test/1d/clib/src/data)
target_include_directories(matrix-mult PRIVATE src/int/lib/include)


# include data
target_include_directories(fast-conv1d-float PRIVATE ../../../test/1d/clib/src/data)
target_include_directories(fast-conv2d-nest-float PRIVATE ../../../test/2d/clib/src/data)
target_include_directories(fast-conv2d-iter-float PRIVATE ../../../test/2d/clib/src/data)

target_include_directories(filter1d-float PRIVATE ../../../test/1d/clib/src/data)
target_include_directories(filter2d-nest-float PRIVATE ../../../test/2d/clib/src/data)
target_include_directories(filter2d-iter-float PRIVATE ../../../test/2d/clib/src/data)

target_include_directories(filter1d PRIVATE ../../../test/1d/clib/src/data)
target_include_directories(filter2d-nest PRIVATE ../../../test/2d/clib/src/data)
target_include_directories(filter2d-iter PRIVATE ../../../test/2d/clib/src/data)


# link libs
target_link_libraries(fast-conv1d-float m)
target_link_libraries(fast-conv2d-nest-float m)
target_link_libraries(fast-conv2d-iter-float m)
target_link_libraries(filter1d-float m)
target_link_libraries(filter2d-nest-float m)
target_link_libraries(filter2d-iter-float m)
