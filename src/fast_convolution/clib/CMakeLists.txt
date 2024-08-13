cmake_minimum_required(VERSION 3.21)
project(fast_conv C)

set(CMAKE_C_STANDARD 90)

# targets
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


# include lib
target_include_directories(fast-conv1d-float PRIVATE src/float/lib/include)
target_include_directories(fast-conv2d-nest-float PRIVATE src/float/lib/include)
target_include_directories(fast-conv2d-iter-float PRIVATE src/float/lib/include)

target_include_directories(filter1d-float PRIVATE src/float/lib/include)
target_include_directories(filter2d-nested-float PRIVATE src/float/lib/include)
target_include_directories(filter2d-iter-float PRIVATE src/float/lib/include)

target_include_directories(filter1d PRIVATE src/int/lib/include)
target_include_directories(filter2d-nested PRIVATE src/int/lib/include)
target_include_directories(filter2d-iter PRIVATE src/int/lib/include)

target_include_directories(simple-conv PRIVATE src/int/lib/include)
target_include_directories(simple-conv PRIVATE test/test1d)
target_include_directories(matrix-mult PRIVATE src/int/lib/include)


# include data
target_include_directories(fast-conv1d-float PRIVATE test/test1d)
target_include_directories(fast-conv2d-nest-float PRIVATE test/test2d)
target_include_directories(fast-conv2d-iter-float PRIVATE test/test2d)

target_include_directories(filter1d-float PRIVATE test/test1d)
target_include_directories(filter2d-nested-float PRIVATE test/test2d)
target_include_directories(filter2d-iter-float PRIVATE test/test2d)

target_include_directories(filter1d PRIVATE test/test1d)
target_include_directories(filter2d-nested PRIVATE test/test2d)
target_include_directories(filter2d-iter PRIVATE test/test2d)


# link libs
target_link_libraries(fast-conv1d-float m)
target_link_libraries(fast-conv2d-nest-float m)
target_link_libraries(fast-conv2d-iter-float m)
target_link_libraries(filter1d-float m)
target_link_libraries(filter2d-nested-float m)
target_link_libraries(filter2d-iter-float m)
