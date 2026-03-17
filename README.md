### Welcome to the workshop:
# From Concurrent Design to Full Parallelism in Modern Python

:boom: Workshop Agenda :boom:
---

- :books: Foundations (08.00-9.15):
    - synchronous execution
    - asynchronous vs. parallel execution
    - the Global Interpreter Lock (GIL)
- :books: asyncio - part I. (9:30-11:30)
    - fundamentals
    - coroutines, awaitables
    - scheduling
- :pizza: lunch (11:30-12:00)
- :books: asyncio - part II. (12:00-13:15)
    - async patterns
    - async in IO bound problems
- :books: parallel python - part I. (13:30-14:50)
    - free threaded python (no GIL)
    - across cores, loops and threads
- :books: parallel python - part II. (15:00-16:30)
    - architecture
    - opencl
    - Python :left_right_arrow: GPU interaction

----------------------------------
:warning: Prerequisites
Participants must have the following installed before the workshop:

uv environment manager with support for Python 3.13t (free-threaded Python)
Ability to create a Python environment using:
```
uv venv .venv-async --python 3.13t
source .venv-async/bin/activate
uv pip install aiofiles
```

:starwars-baby-yoda-sip: For the opencl session:
OpenCL drivers installed for either CPU or GPU
Verify OpenCL availability with:
```
uv venv .venv-opencl --python 3.13
source .venv-opencl/bin/activate
uv pip install numpy matplotlib pyopencl
python -c "import pyopencl as cl; print(cl.get_platforms())"
```
An example of the output:
```
[<pyopencl.Platform 'NVIDIA CUDA' at 0x1ce70f50>, <pyopencl.Platform 'Intel(R) OpenCL Graphics' at 0x1cf48ed0>]
```

The CPU OpenCL is the easiest:
- Intel OpenCL CPU runtime
- POCL (Portable OpenCL) — most common on Linux
- Apple OpenCL (macOS)
- OpenCL with WSL should work too
