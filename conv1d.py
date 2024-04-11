import argparse

import numpy as np
# import sympy as sy
from PIL import Image
from scipy import signal
# from matplotlib import pyplot as plt

from notebooks.naive_convolve import naive_convolve
from notebooks.fast_convolution import (
    toom_cook_conv_1d, filter1d_slide2d, filter1d_slide2d_count
)


parser = argparse.ArgumentParser(
    description='1D Toom-Cook convolution in image with one channel',
    # epilog='Text at the bottom of help'
)

parser.add_argument('-p', '--path', required=True)
args = parser.parse_args()

image = Image.open(args.path).convert('L')

feature = np.array(image)
weight = np.array([
    [0, 1, 0],
    [1, -4, 1],
    [0, 1, 0],
])

wr = weight[::-1, ::-1]
output = signal.convolve2d(feature, wr, mode='valid')
output_naive = naive_convolve(feature, weight)

print(f"Output default and naive are equals: {np.all(output == output_naive)}")


points = [0, -1, 1, -2, np.inf]
fast_conv = [toom_cook_conv_1d(3, 3, points, weight[i]) for i in range(3)]
output_fast = np.sum(axis=0, a=[
    filter1d_slide2d(fast_conv[i], feature, output.shape, i)
    for i in range(0, 3)
])

print(f"Output default and fast are equals: {np.all(output == output_fast)}")

size = output.size

print("Naive totals:")
print(f"Multiplications: {size * 9}")
print(f"Additions: {size * 8}")


print("Fast totals:")

fast_count = filter1d_slide2d_count(output.shape, weight.shape[0])
mult = fast_count * len(points) * len(fast_conv)
print(f"Multiplications: {mult}")

add0 = fast_count * 20 * len(fast_conv)
add1 = fast_count * 2 * len(fast_conv)
print(f"Additions: {add0 + add1}")

print(f"* Additions for each batch processed: {add0}")
print(f"* Additions to join batches: {add1}")
print(f"Extra operations - bit shifts and etc: {fast_count * 9 * len(fast_conv)}")