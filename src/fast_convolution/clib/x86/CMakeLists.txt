cmake_minimum_required(VERSION 3.0)
project(fast_conv C)

set(CMAKE_C_STANDARD 90)

add_executable(simple-conv ../src/simple-conv.c ../src/lib/convolution.c ../src/lib/util.c)
target_include_directories(simple-conv PRIVATE ../src/lib/include)
target_include_directories(simple-conv PRIVATE ../src/data)

if(EXISTS "../src/int/filter1d.c")
    add_executable(filter1d ../src/filter1d.c ../src/lib/convolution.c ../src/lib/util.c)
    target_include_directories(filter1d PRIVATE ../src/lib/include)
    target_include_directories(filter1d PRIVATE ../src/data)

    add_executable(filter1d-optim ../src/filter1d.c ../src/lib/optim.c ../src/lib/convolution.c ../src/lib/util.c)
    target_include_directories(filter1d-optim PRIVATE ../src/lib/include)
    target_include_directories(filter1d-optim PRIVATE ../src/data)
    target_compile_definitions(filter1d-optim PRIVATE OPTIM)
endif()

if(EXISTS "../src/int/filter2d-iter.c")
    add_executable(filter2d-iter ../src/filter2d-iter.c ../src/lib/convolution.c ../src/lib/util.c)
    target_include_directories(filter2d-iter PRIVATE ../src/lib/include)
    target_include_directories(filter2d-iter PRIVATE ../src/data)

    add_executable(filter2d-iter-optim ../src/filter2d-iter.c ../src/lib/optim.c ../src/lib/convolution.c ../src/lib/util.c)
    target_include_directories(filter2d-iter-optim PRIVATE ../src/lib/include)
    target_include_directories(filter2d-iter-optim PRIVATE ../src/data)
    target_compile_definitions(filter2d-iter-optim PRIVATE OPTIM)
endif()

if(EXISTS "../src/int/filter2d-nest.c")
    add_executable(filter2d-nest ../src/filter2d-nest.c ../src/lib/convolution.c ../src/lib/util.c)
    target_include_directories(filter2d-nest PRIVATE ../src/lib/include)
    target_include_directories(filter2d-nest PRIVATE ../src/data)

    add_executable(filter2d-nest-optim ../src/filter2d-nest.c ../src/lib/optim.c ../src/lib/convolution.c ../src/lib/util.c)
    target_include_directories(filter2d-nest-optim PRIVATE ../src/lib/include)
    target_include_directories(filter2d-nest-optim PRIVATE ../src/data)
    target_compile_definitions(filter2d-nest-optim PRIVATE OPTIM)
endif()
