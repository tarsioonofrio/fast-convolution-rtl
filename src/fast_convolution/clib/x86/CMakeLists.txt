cmake_minimum_required(VERSION 3.0)
project(fast_conv C)

set(CMAKE_C_STANDARD 90)

# targets
add_executable(simple-conv ../src/simple-conv.c ../src/lib/convolution.c ../src/lib/util.c)
add_executable(fast-conv ../src/fast-conv.c ../src/lib/convolution.c ../src/lib/util.c)
add_executable(fast-conv-optim ../src/fast-conv.c ../src/lib/optim.c ../src/lib/convolution.c ../src/lib/util.c)

# include lib
target_include_directories(simple-conv PRIVATE ../src/lib/include)
target_include_directories(fast-conv PRIVATE ../src/lib/include)
target_include_directories(fast-conv-optim PRIVATE ../src/lib/include)

# include data
target_include_directories(simple-conv PRIVATE ../src/data)
target_include_directories(fast-conv PRIVATE ../src/data)
target_include_directories(fast-conv-optim PRIVATE ../src/data)

# add OPTIM macro to fast-conv-optim
target_compile_definitions(fast-conv-optim PRIVATE OPTIM)
