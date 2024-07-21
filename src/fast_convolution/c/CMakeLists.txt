cmake_minimum_required(VERSION 3.21)
project(c C)

set(CMAKE_C_STANDARD 90)

add_executable(simple-conv simple-conv.c convolution.c convolution.h example.h util.c util.h config.h)
add_executable(fast-conv fast-conv.c convolution.c convolution.h example.h util.c util.h config.h)
add_executable(filter1d filter1d.c convolution.c convolution.h example.h util.c util.h config.h)
add_executable(filter2d filter2d.c convolution.c convolution.h example.h util.c util.h config.h)
