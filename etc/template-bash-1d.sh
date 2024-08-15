# init fast-conv repository with 1d convolution and output of size 3
fast-conv init 1d -o 3
# build a fast conv 1d using toom cook method
fast-conv build 1d toom-cook
# quantizate with 4 shifs
fast-conv quant shift -b 4
# generate example with sequential data
fast-conv example seq
# generate example with random data
fast-conv example rand
# simulate with file
fast-conv sim file
# simulate with rand data
fast-conv sim rand

# show config data
# fast-conv show
