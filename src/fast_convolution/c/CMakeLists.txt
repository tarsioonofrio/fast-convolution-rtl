cmake_minimum_required(VERSION 3.21)
project(c C)

set(CMAKE_C_STANDARD 90)

add_executable(simple-conv simple-conv.c convolution.c convolution.h example.h)
add_executable(fast-conv fast-conv.c convolution.c convolution.h example.h)
