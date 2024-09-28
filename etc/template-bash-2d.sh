FOLDER=$(basename $0 .sh)
mkdir ${FOLDER}
cd ${FOLDER}

# init fast-conv repository with 2d convolution and output of size (3,3)
fast-conv init 2d -o 3
# build a fast conv 2d using toom cook method
fast-conv build 2d toom-cook
# bind 2d fast convolution with nested method
fast-conv build 2d bind nest

# bin 2d fast convolution with iterated method
# fast-conv build 2d bind iter

# quantizate with 4 shifs
fast-conv quant shift -b 4
fast-conv example seq
# generate example with random data
fast-conv example rand
# simulate with file
fast-conv sim file
# simulate with rand data
fast-conv sim rand

# show config data
# fast-conv show