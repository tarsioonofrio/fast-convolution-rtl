cmake_minimum_required(VERSION 3.0)
project(fast_conv C)

set(CMAKE_C_STANDARD 90)

# targets
add_executable(executable ../src/main.c ../src/lib/convolution.c ../src/lib/util.c)

# include lib
target_include_directories(executable PRIVATE ../src/lib/include)

# include data
target_include_directories(executable PRIVATE ../src/data)
