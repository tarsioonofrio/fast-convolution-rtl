cmake_minimum_required(VERSION 3.21)
project(c C)

set(CMAKE_C_STANDARD 90)

add_executable(simple-conv simple-conv.c libs/convolution.c libs/convolution.h test1d/sim.h libs/util.c libs/util.h test1d/init.h)
add_executable(matrix-mult matrix-mult.c libs/convolution.c libs/convolution.h test1d/sim.h libs/util.c libs/util.h test1d/init.h)

add_executable(fast-conv1d-float fast-conv1d-float.c libs/convolution.c libs/convolution.h libs/util.c libs/util.h test1d/init.h test1d/build_float.h test1d/example_float.h)
add_executable(fast-conv2d-nest-float fast-conv2d-nest-float.c libs/convolution.c libs/convolution.h libs/util.c libs/util.h test2d/init.h test2d/build_float.h test2d/bind_nest.h)
add_executable(fast-conv2d-iter-float fast-conv2d-iter-float.c libs/convolution.c libs/convolution.h libs/util.c libs/util.h test2d/init.h test2d/build_float.h test2d/example.h)

add_executable(filter1d filter1d-float.c libs/convolution.c libs/convolution.h libs/util.c libs/util.h test1d/init.h test1d/init.h test1d/build.h test1d/example.h test1d/sim.h )
add_executable(filter2d filter2d-float.c libs/convolution.c libs/convolution.h libs/util.c libs/util.h test2d/init.h test2d/build.h test2d/bind_nest.h test2d/example.h test2d/sim.h)
