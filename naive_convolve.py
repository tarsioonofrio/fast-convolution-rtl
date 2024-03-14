# https://gist.github.com/better-data-science/1bed20956e4ba510c4170123a784e8b5#file-conv_from_scratch-py
import numpy as np


def naive_convolve(data: np.array, kernel: np.array) -> np.array:
    # To simplify things
    k = kernel.shape[0]
    new_shape = (data.shape[0] - 2, data.shape[1] - 2)
    # 2D array of zeros
    output = np.zeros(shape=new_shape, dtype=int)

    # Iterate over the rows
    for i in range(data.shape[0] - k + 1):
        # Iterate over the columns
        for j in range(data.shape[1] - k + 1):
            # img[i, j] = individual pixel value
            # Get the current matrix
            tmp = data[i:i + k, j:j + k]
            # Apply the convolution - element-wise multiplication and summation of the result
            # Store the result to i-th row and j-th column of our convolved_img array
            # 9 multiplications, 8 aditions per output
            output[i, j] = np.sum(np.multiply(tmp, kernel))
    return output
