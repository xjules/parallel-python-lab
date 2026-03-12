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
uv python install 3.13t
uv venv <path_to_env> --python 3.13t
```

:starwars-baby-yoda-sip: Nice to have (for the opencl session):
OpenCL drivers installed for either CPU or GPU
Verify OpenCL availability with:
```
uv venv --python 3.13
source .venv/bin/activate
uv pip install pyopencl
python -c "import pyopencl as cl; print(cl.get_platforms())"
```
The CPU OpenCL is the easiest:
- Intel OpenCL CPU runtime
- POCL (Portable OpenCL) — most common on Linux
- Apple OpenCL (macOS)
- OpenCL with WSL should work too


:phone: Please reach out if you are experiencing problems with any of the above :top: (edited)