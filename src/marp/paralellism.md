1. The Classic: multiprocessing
This is the standard way to bypass the GIL by spawning entirely separate instances of the Python interpreter. It is best for independent, heavy tasks like resizing thousands of images or running separate simulations.
python
from multiprocessing import Pool

def heavy_math(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    numbers = [10**7, 10**7 + 1, 10**7 + 2, 10**7 + 3]
    # Creates a pool that defaults to your total number of CPU cores
    with Pool() as p:
        results = p.map(heavy_math, numbers)
    print(results)
Use code with caution.

Best for: CPU-bound tasks where tasks don't need to "talk" to each other much.
Documentation: Python Multiprocessing
2. The Easy Button: joblib
Highly popular in the data science community, Joblib provides a cleaner syntax for parallel loops and handles the underlying multiprocessing logic for you efficiently.
python
from joblib import Parallel, delayed

def process_data(x):
    return x ** 2

# n_jobs=-1 uses all available CPU cores
results = Parallel(n_jobs=-1)(delayed(process_data)(i) for i in range(10))
Use code with caution.

Best for: "Embarrassingly parallel" loops (like for loops where each iteration is independent).
3. The Performance Powerhouse: Numba
If your code is mostly numerical (NumPy arrays), Numba is often faster than OpenCL for development. It uses Just-In-Time (JIT) compilation to turn your Python code into machine code that runs across all cores using the parallel=True flag.
python
from numba import njit, prange
import numpy as np

@njit(parallel=True)
def parallel_sum(arr):
    s = 0
    # 'prange' tells Numba to execute this loop in parallel across cores
    for i in prange(arr.shape[0]):
        s += arr[i]
    return s

data = np.arange(1000000)
print(parallel_sum(data))
Use code with caution.

Best for: High-performance math on arrays without writing C code.
4. Big Data Scaling: Dask
If your dataset is too big for your RAM, Dask breaks your data into chunks and processes them in parallel across all CPU cores automatically.
python
import dask.array as da

# Create a massive array split into smaller chunks
x = da.random.random((10000, 10000), chunks=(1000, 1000))
# Operations are automatically parallelized across CPU cores
result = x.mean().compute()
Use code with caution.

Best for: Dataframes or arrays that exceed your computer's memory.
Which one should you choose?
Use Multiprocessing for general-purpose scripts.
Use Numba for pure mathematical/scientific computing.
Use Dask if you are struggling with massive CSVs or large NumPy arrays.
Do you have a specific script or a loop that is currently running too slow?