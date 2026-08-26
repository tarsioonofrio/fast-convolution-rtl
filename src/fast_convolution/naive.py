# https://gist.github.com/better-data-science/1bed20956e4ba510c4170123a784e8b5#file-conv_from_scratch-py
import numpy as np


def naive_convolve(data: np.array, kernel: np.array) -> np.array:
    data = np.asarray(data)
    kernel = np.asarray(kernel)
    if data.ndim != 2 or kernel.ndim != 2:
        raise ValueError("naive_convolve expects two-dimensional arrays")
    kernel_rows, kernel_cols = kernel.shape
    new_shape = (
        data.shape[0] - kernel_rows + 1,
        data.shape[1] - kernel_cols + 1,
    )
    if min(new_shape) <= 0:
        raise ValueError("kernel must not be larger than data")
    output = np.zeros(shape=new_shape, dtype=np.result_type(data, kernel))

    for i in range(new_shape[0]):
        for j in range(new_shape[1]):
            tmp = data[i : i + kernel_rows, j : j + kernel_cols]
            output[i, j] = np.sum(np.multiply(tmp, kernel))
    return output
