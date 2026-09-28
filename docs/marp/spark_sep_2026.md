---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---

<style>
section pre {
    font-size: 0.72em;
    line-height: 1.15;
}
</style>

# From Concurrency to Full Parallelism in Modern Python

## Choosing the right execution model


Julius Parulek

---

# Models

> Why did the async function break up with the synchronous function? Because it was tired of being blocked.

execution models:

- synchronous execution
- asynchronous concurrency
- async orchestration plus threads
- free-threaded CPU parallelism

---

# Blocking Behavior

In synchronous programs:

```python
load_data()   # waits
compute()     # waits
save_data()   # waits
```

Every step **owns the thread** until it returns.

This model is simple, but inefficient for many workloads.

---

# Concurrency or parallelism?

Which statement is correct?

- A. Concurrency and parallelism mean the same thing
- B. Concurrency is overlapping progress; parallelism is simultaneous execution
- C. Parallelism works on only one CPU core

---

# Understanding the Bottlenecks

Which workload should benefit most from `concurrency`?

- A: 10,000 HTTP requests
- B: 10,000 image processing

---

# I/O-Bound vs CPU-bound Workloads

In I/O Bound program spends most time **waiting** for external systems:
- These workloads benefit from **concurrency**
- **asyncio**, threading - **GIL**

In CPU-Bound program spends most time **computing**:
- These workloads benefit from **parallelism**
- multiprocessing or **free-threaded Python**

---

# GIL in standard CPython

In the standard CPython build, the Global Interpreter Lock allows only one
thread at a time to execute Python bytecode in an interpreter.

    Will two Python threads make this faster?
    ```python
    def work():
        total = 0
        for _ in range(10**8):
            total += 1
    ```
    - A: yes
    - B: no
    - C: only if the function is declared `async`



---

# GIL in standard CPython - why?

GIL exists primarily because of how **CPython manages memory**

**Reference counting** tracks how many references an object has; when the count
reaches zero, the object can be deallocated. The GIL historically made this
bookkeeping simpler by preventing simultaneous bytecode execution in an
interpreter.

---

# GIL in standard CPython - when?

For CPU-bound Python code, the GIL remains locked
- This makes standard multithreading ineffective for speeding up CPU-bound tasks

The GIL is also released around many blocking **I/O operations**.

- **Asyncio** to handle many I/O-bound tasks concurrently

---

# Asyncio: built-in library to write concurrent code

```python
async def greet():
    print("hello")

greet()
print("finished")
```

What is printed?
- A: `hello`, then `finished`
- B: `finished`, and possibly a warning
- C: nothing

---

# Coroutines

`async def` creates a coroutine - It runs only when it is awaited or scheduled as a task.

```python
await greet()
# or
task = asyncio.create_task(greet())
```

`await` - pause the current coroutine until the awaited operation finishes

**Yielding Control** - when we `await`, we tell the Event Loop: 
    - _"I am still waiting; go ahead and run something else in the meantime"_

---

# The sleep job

```python
async def sleep_job(seconds):
    await asyncio.sleep(seconds)

task_a = asyncio.create_task(sleep_job(2))
task_b = asyncio.create_task(sleep_job(3))

await task_a
await task_b
```

How long?

- A: 2 seconds
- B: 3 seconds
- C: 5 seconds

---

# Tasks overlap while waiting

Both tasks are scheduled before the first result is awaited.

```text
time: 0 ---- 2 -------- 3
task A:     [==========]
task B:     [===============]
```

**Answer: approximately 3 seconds.**

---

# Mixed awaits - I.

```python
sleep2 = asyncio.create_task(sleep_job(2))
sleep3 = asyncio.create_task(sleep_job(3))

await sleep_job(2)
await sleep2
await sleep3
```

What is the total duration?

- A: about 2 seconds
- B: about 3 seconds
- C: about 5 seconds

---

# Mixed awaits - II.

```python
sleep2 = asyncio.create_task(sleep_job(2))
sleep3 = asyncio.create_task(sleep_job(3))

await sleep2
await sleep3
await sleep_job(2)
```

What is the total duration?

- A: about 2 seconds
- B: about 3 seconds
- C: about 5 seconds

---

# `gather` result order

- It automatically turns coroutines into tasks

```python
results = await asyncio.gather(
    asyncio.sleep(3, result="A"),
    asyncio.sleep(1, result="B"),
)
print(results)
```

What is printed?

- A: `['A', 'B']`
- B: `['B', 'A']`
- C: whichever task finishes first, with no guarantee

---

# Completion order is not result order

`asyncio.gather` returns results in the same order as its inputs.

```text
completion: B, then A
results:    A, then B
```

This is useful when the input position identifies the job.
It can be surprising when the application needs streaming results instead.

---

# The event loop in one picture

```text
                 ready tasks
                     |
                     v
     I/O events -> event loop -> resumed coroutines
                     ^
                     |
                 await points
```

The loop runs one task at a time until that task:

- finishes
- reaches an `await`
- raises an exception

---

# CPU work inside asyncio - version I

```python
async def cpu_job(n): # takes ca. 2 secs for 10**8
    total = 0
    for i in range(n):
        total += i
    return total

task_a = asyncio.create_task(cpu_job(10**8))
task_b = asyncio.create_task(cpu_job(10**8))
task_sleep = asyncio.create_task(asyncio.sleep(2))
```

Does the sleep run while the CPU jobs execute? Duration?

- A: 2 seconds
- B: 4 seconds
- C: 6 seconds

---

# CPU work inside asyncio - version II

```python
async def cpu_job(n):
    total = 0
    for i in range(n):
        total += i
    return total

task_sleep = asyncio.create_task(asyncio.sleep(2))
task_a = asyncio.create_task(cpu_job(10**8))
task_b = asyncio.create_task(cpu_job(10**8))
```

Does the sleep run while the CPU jobs execute? Duration?

- A: 2 seconds
- B: 4 seconds
- C: 6 seconds

---

# Cooperative means cooperative

`asyncio` cannot interrupt a coroutine that never yields.

```text
CPU job A: [====================]
CPU job B:                       [====================]
sleep:                           waits in the queue
```

Asyncio is excellent at **latency hiding for I/O**.
It is not a CPU parallelism mechanism.

Run: [`io_cpu_bound.py`](../../examples/async_demo/io_cpu_bound.py)

---

# Is this file access async?

```python
async def read_file(path):
    with open(path, "rb") as file:
        return file.read()

await asyncio.gather(
    read_file("file1"),
    read_file("file2"),
)
```

Does `asyncio.gather` make the reads non-blocking?

- A: yes, because the function is `async`
- B: no, `read()` still blocks the event-loop thread
- C: only if there are two files

---

# Syntax does not change the underlying operation

This is still synchronous file I/O running on the event-loop thread.

Move the blocking function away from the loop:

```python
content = await asyncio.to_thread(read_file, path)
```

Now the event loop can schedule other coroutines while the worker thread waits.

---

# What does `to_thread` solve?

```python
await asyncio.gather(
    asyncio.to_thread(read_file, "file1"),
    asyncio.to_thread(read_file, "file2"),
)
```

Which statement is best?

- A: It makes every Python calculation run in parallel
- B: It keeps blocking work from freezing the event loop
- C: It removes the need for synchronization

---

# The hybrid architecture

```text
asyncio event loop
       |
       | schedules and coordinates
       v
threads / processes
       |
       v
blocking or CPU-heavy work
```

The event loop is the coordinator.
The workers perform work that should not occupy the loop.

---

# One hundred workers

```python
tasks = [
    asyncio.to_thread(cpu_work, 50_000_000)
    for _ in range(100)
]
await asyncio.gather(*tasks)
```

Is this automatically a good design?

- A: yes, more tasks always means more speed
- B: no, bound concurrency to protect CPU and memory
- C: no, because `gather` cannot run threads

---

# Bounded concurrency

```python
sem = asyncio.Semaphore(8)

async def worker():
    async with sem:
        return await asyncio.to_thread(cpu_work, 50_000_000)
```

The number of tasks and the number of active workers are different decisions.

Use a queue, worker pool, or semaphore when resources are limited.

---

# Free-threaded Python: what changed?

Python 3.13 introduced the optional free-threaded build.

In Python 3.14, it became **officially supported**—but remains optional, not the
default build.

Which statement is accurate?

- A: every Python 3.14 installation runs without the GIL
- B: free-threading is supported, but you must install/use that build
- C: it is still experimental in Python 3.14

---

# Is the GIL actually off?

A free-threaded-capable build does not guarantee the GIL stays disabled.
Importing an extension that is not marked as free-threading-compatible can
automatically enable it.

Check the **runtime state**, especially after importing your dependencies:

```python
import sys

print("GIL enabled:", sys._is_gil_enabled())
```

`False` means Python threads can execute Python code in parallel in this run.

Free-threaded Python is not automatically faster for every workload: Python
3.14's single-thread overhead is roughly 5–10% versus the standard build,
depending on platform and compiler. Benchmark the real workload and its memory use.

---

# Two layers, two jobs

```text
asyncio:    coordinate and communicate
threads:    execute synchronous work
no-GIL:     allow Python threads to execute in parallel
```

Free-threaded Python changes the CPU-bound case. Built-in containers protect
many individual operations internally, but compound operations on shared state
are not automatically atomic. Locks, queues, and ownership still matter.

Python 3.14 also supports multiple event loops running in separate threads on
free-threaded builds; each loop still schedules its own coroutines cooperatively.

Run: [`ft_job.py`](../../examples/async_demo/ft_job.py)

---

# Another CPU-parallel option: interpreters

Python 3.14 added `concurrent.futures.InterpreterPoolExecutor`.

Each worker runs in a separate interpreter with its **own GIL**, so CPU-bound
Python work can run on multiple cores—even with a standard GIL-enabled build.

How does it avoid threads sharing mutable Python objects?

- A: shared objects are protected by one global lock
- B: each interpreter is isolated; inputs and results are serialized
- C: it runs each job in a separate process

---

# Interpreter workers: isolation is the tradeoff

```python
from concurrent.futures import InterpreterPoolExecutor

def cpu_work(n):
    return sum(i * i for i in range(n))

with InterpreterPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(cpu_work, [2_000_000] * 4))
```

- **Threads:** shared memory; need a free-threaded build for Python CPU parallelism
- **Interpreters:** separate interpreter state; communicate through serialized inputs/results
- **Processes:** separate processes; also communicate through serialized data

Use importable, picklable callables and arguments. Interpreter startup,
serialization, and extension compatibility still affect whether this is a win.

---

# How does a thread report back?

```python
def worker(loop, queue):
    result = cpu_work()
    loop.call_soon_threadsafe(queue.put_nowait, result)
```

Why not call `queue.put_nowait` directly?

- A: the worker may be running outside the event-loop thread
- B: queues can only contain strings
- C: `call_soon_threadsafe` makes CPU work faster

---

# Communicate across the boundary

Use thread-safe scheduling to send a message back to the loop:

```python
loop.call_soon_threadsafe(queue.put_nowait, message)
```

The preferred shape is often:

```text
worker owns computation
queue carries messages
event loop owns async coordination
```

---

# Choose the model

For each workload, choose one:

1. `asyncio`
2. threads or processes
3. async plus workers

**A.** 10,000 slow HTTP requests

**B.** A pure-Python numerical calculation on a free-threaded build

**C.** A service that downloads data and then performs heavy calculations

---

# The decision table

| Workload | First tool to consider |
|---|---|
| Many I/O waits | `asyncio` |
| Blocking library | `asyncio.to_thread` or a worker pool |
| Pure-Python CPU work | processes, or free-threaded threads |
| Mixed I/O and CPU | async orchestration plus workers |
| Shared state | queues, ownership, and explicit synchronization |

The right choice is not simply “use async.”

It is “where does this program spend its time?”

---

# Rules to take home

1. **`async` does not mean parallel.**
2. **`await` creates a chance for other work to run.**
3. **CPU work needs a parallel execution mechanism.**

> When this job is waiting, who should use the time?

---

# Closing perspective

The execution model should follow the workload:

- overlap waiting with `asyncio`
- move blocking work to workers
- use parallel execution for CPU-bound work
- combine these models when an application has mixed workloads
