cmake_minimum_required(VERSION 3.21)
project(c C)

set(CMAKE_C_STANDARD 90)

add_executable(simple-conv simple-conv.c libs/convolution.c libs/util.c)
add_executable(matrix-mult matrix-mult.c libs/convolution.c libs/util.c)

add_executable(fast-conv1d-float fast-conv1d-float.c libs/convolution_float.c libs/util_float.c)
add_executable(fast-conv2d-nest-float fast-conv2d-nest-float.c libs/convolution_float.c libs/util_float.c)
add_executable(fast-conv2d-iter-float fast-conv2d-iter-float.c libs/convolution_float.c libs/util_float.c)

add_executable(filter1d-float filter1d-float.c libs/convolution_float.c libs/util_float.c)
add_executable(filter2d-float filter2d-float.c libs/convolution_float.c libs/util_float.c)

add_executable(filter1d filter1d.c libs/convolution.c libs/util.c)
add_executable(filter2d filter2d.c libs/convolution.c libs/util.c)


target_link_libraries(fast-conv1d-float m)
target_link_libraries(fast-conv2d-nest-float m)
target_link_libraries(fast-conv2d-iter-float m)
target_link_libraries(filter1d-float m)
target_link_libraries(filter2d-float m)

target_link_libraries(filter1d)
target_link_libraries(filter2d)