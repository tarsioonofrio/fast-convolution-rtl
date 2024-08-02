cmake_minimum_required(VERSION 3.21)
project(fast_conv C)

set(CMAKE_C_STANDARD 90)

add_executable(simple-conv src/int/simple-conv.c src/int/lib/convolution.c src/int/lib/util.c)
add_executable(matrix-mult src/int/matrix-mult.c src/int/lib/convolution.c src/int/lib/util.c)

add_executable(fast-conv1d-float src/float/fast-conv1d-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)
add_executable(fast-conv2d-nest-float src/float/fast-conv2d-nest-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)
add_executable(fast-conv2d-iter-float src/float/fast-conv2d-iter-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)

add_executable(filter1d-float src/float/filter1d-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)
add_executable(filter2d-nested-float src/float/filter2d-nested-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)
add_executable(filter2d-iter-float src/float/filter2d-iter-float.c src/float/lib/convolution_float.c src/float/lib/util_float.c)

add_executable(filter1d src/int/filter1d.c src/int/lib/convolution.c src/int/lib/util.c)
add_executable(filter2d-iter src/int/filter2d-iter.c src/int/lib/convolution.c src/int/lib/util.c)
add_executable(filter2d-nested src/int/filter2d-nested.c src/int/lib/convolution.c src/int/lib/util.c)


target_link_libraries(fast-conv1d-float m)
target_link_libraries(fast-conv2d-nest-float m)
target_link_libraries(fast-conv2d-iter-float m)
target_link_libraries(filter1d-float m)
target_link_libraries(filter2d-nested-float m)
target_link_libraries(filter2d-iter-float m)
