import argparse
from pathlib import Path

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

parser.add_argument('-f', '--file', type=Path)
parser.add_argument(
    '-p', '--points', nargs='+', default=[0, -1, 1, -2, 'inf'],
    help=("Number of points to interpolate. If no vector size is provided, "
          "is assumed that the format is M=P-3+1")
)
parser.add_argument(
    '-s', '--vector-size', nargs=2, type=int,
    help=("Size of two vectors to be convoluted. The two sizes must be in "
          "format P=M+N-1 where P is number of points to be interpolated, "
          "M and N are respectively the first and second values of the "
          "argument. M as the size o features and N size of weights."))

parser.add_argument('-r', '--random', type=int, default=0)
parser.add_argument('-i', '--image-side', type=int)


args = parser.parse_args()


image = Image.open(args.file).convert('L')
points = [np.inf if p == 'inf' else p for p in args.points]

if args.vector_size is None:
    n_size = 3
    m_size = len(points) - 3 + 1
else:
    m_size = args.vector_size[0]
    n_size = args.vector_size[1]


feature = np.array(image)
weight = np.array([
    [0, 1, 0],
    [1, -4, 1],
    [0, 1, 0],
])

output = signal.convolve2d(feature, weight[::-1, ::-1], mode='valid')
output_naive = naive_convolve(feature, weight)

print(f"Output default and naive are equals: {np.all(output == output_naive)}")

fast_conv = [
    toom_cook_conv_1d(m_size, n_size, points, weight[i])
    for i in range(weight.shape[0])
]

output_fast = np.sum(axis=0, a=[
    filter1d_slide2d(
        fast_conv[i], feature, output.shape, i, len(points), m_size
    )
    for i in range(0, weight.shape[0])
])

print(f"Output default and fast are equals: {np.all(output == output_fast)}")

size = output.size

print("Naive totals:")
print(f"Iterations: {size}")
print(f"Multiplications: {size * 9}")
print(f"Additions: {size * 8}")


print("Fast totals:")

fast_count = filter1d_slide2d_count(output.shape, m_size)
mult = fast_count * len(points) * len(fast_conv)
print(f"Iterations: {fast_count}")
print(f"Multiplications: {mult}")

add0 = fast_count * 20 * len(fast_conv)
add1 = fast_count * 2 * len(fast_conv)
print(f"Additions: {add0 + add1}")

print(f"* Additions for each batch processed: {add0}")
print(f"* Additions to join batches: {add1}")
print(
    f"Extra operations - bit shifts and etc: {fast_count * 9 * len(fast_conv)}"
)
