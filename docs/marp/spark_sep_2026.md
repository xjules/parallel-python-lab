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
load_data()  # waits
compute()  # waits
save_data()  # waits
```

Every step **owns the thread** until it returns.

This model is simple, but inefficient for many workloads.

---

# Concurrency or parallelism?

Which statement is correct?

- A. Concurrency and parallelism mean the same thing
- B. Concurrency is overlapping progress; parallelism is simultaneous execution
- C. Concurrency requires at least two CPU cores

---

# Understanding the Bottlenecks

Which workload should benefit most from `concurrency`?

- A: 10,000 HTTP requests
- B: 10,000 image processing operations

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

The Global Interpreter Lock allows only one
thread at a time to execute Python bytecode in an interpreter

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

- **Reference counting** tracks how many references an object has
-  when the count reaches zero, the object can be deallocated 
- The GIL historically made this bookkeeping simpler by preventing simultaneous bytecode execution

---

# GIL in standard CPython - when?

For CPU-bound Python code, the GIL remains locked
- This makes standard multithreading ineffective for speeding up CPU-bound tasks

The GIL is released blocking **I/O operations**.

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

`asyncio.gather` returns results in the same order as its inputs

```text
completion: B, then A
results:    A, then B
```

- useful when the input position identifies the job


---

# CPU work inside asyncio - version I

```python
async def cpu_job(n):  # takes ca. 2 secs for 10**8
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

Asyncio is excellent at **latency hiding for I/O**, but not for a CPU parallelism mechanism.

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

# Injecting async does not solve it!

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

# A worker thread doesn't guarantee CPU parallelism

- `asyncio.to_thread()` moves blocking work off the event-loop thread
  - the loop can keep running while the worker waits

- GIL allows only one thread at a time to execute Python bytecode
  - helps with blocking I/O, but usually does not speed up pure-Python CPU work.

**What if the GIL is disabled?** 

---

# Free-threaded Python

Python 3.13 introduced the optional free-threaded build.

In Python 3.14, it became **officially supported**
- but remains optional, not the default build

---

# Is the GIL actually disabled?

Check the **runtime state** -- after importing your dependencies:

```python
import sys

print("GIL enabled:", sys._is_gil_enabled())
```
- `False` means Python threads can execute Python code in parallel in this run.

Free-threaded Python is not automatically faster for every workload; expect
some single-thread overhead and benchmark the real workload.

---

# Parallelism still needs limits

With the GIL disabled, CPU-bound threads can run in parallel
- CPU cores and memory are still limited

```python
tasks = [asyncio.to_thread(cpu_work, 50_000_000) for _ in range(100)]
await asyncio.gather(*tasks)
```

What should we control?

- A: only the total number of tasks
- B: the number of jobs active at once, to protect CPU and memory
- C: nothing; the GIL is disabled

---

# Bound active work

```python
sem = asyncio.Semaphore(8)


async def worker():
    async with sem:
        return await asyncio.to_thread(cpu_work, 50_000_000)
```

- Use a queue, worker pool, or semaphore when resources are limited.

---

# Layered approach


- asyncio:    coordinate and communicate
- threads:    execute synchronous work
- no-GIL:     allow Python threads to execute in parallel

Parallel work still needs two things: protect shared resources, and use
thread-safe signalling to coordinate between workers and the event loop.



---
# Asyncio + Free-Threaded

`asyncio` runs an **event loop** that is typically **single-threaded**
- Free-threaded Python does **not** make coroutines parallel
- `await` still means: _"pause me, run something else"_
- `asyncio` offloads work to **threads**, which can execute in parallel
- **one loop** = one thread that drives coroutine execution

---

# Async with CPU bound work

```python
def cpu_work(n):
    s = 0
    for i in range(n):
        s += i
    return s
async def main():
    results = await asyncio.gather(
        asyncio.to_thread(cpu_work, 50_000_000),
        asyncio.to_thread(cpu_work, 50_000_000),
        asyncio.to_thread(cpu_work, 50_000_000),
        asyncio.to_thread(cpu_work, 50_000_000),
    )
    print(sum(results))
```

---

# Other options for CPU parallelism

- **Free-threaded threads:** shared memory; Python threads can run CPU code in
    parallel when the GIL is disabled.
- **InterpreterPoolExecutor (Python 3.14+):** each worker has an isolated
    interpreter and its own GIL; inputs and results are serialized.
- **ProcessPoolExecutor:** separate processes; broad compatibility, with
    process startup and serialization costs.

Choose based on compatibility, data-sharing needs, and measured performance.
For mixed workloads, let `asyncio` coordinate I/O and send CPU work to a bounded
worker pool.

---

# Match the tool to the workload

| Workload | Start with |
|---|---|
| Many I/O waits | `asyncio` |
| Blocking library call | `asyncio.to_thread` |
| Pure-Python CPU work | free-threaded threads, interpreters, or processes |
| I/O followed by CPU work | `asyncio` plus bounded workers |
