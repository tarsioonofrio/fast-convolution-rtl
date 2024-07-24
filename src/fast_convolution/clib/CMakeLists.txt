cmake_minimum_required(VERSION 3.21)
project(c C)

set(CMAKE_C_STANDARD 90)

add_executable(simple-conv simple-conv.c libs/convolution.c libs/convolution.h test1d/sim.h libs/util.c libs/util.h test1d/init.h)
add_executable(matrix-mult matrix-mult.c libs/convolution.c libs/convolution.h test1d/sim.h libs/util.c libs/util.h test1d/init.h)
add_executable(fast-conv fast-conv.c libs/convolution.c libs/convolution.h libs/util.c libs/util.h test1d/init.h test1d/build.h test1d/example.h test1d/sim.h )
add_executable(filter1d filter1d.c libs/convolution.c libs/convolution.h libs/util.c libs/util.h test1d/init.h test1d/init.h test1d/build.h test1d/example.h test1d/sim.h )
add_executable(filter2d filter2d.c libs/convolution.c libs/convolution.h libs/util.c libs/util.h test1d/init.h test1d/sim.h )
