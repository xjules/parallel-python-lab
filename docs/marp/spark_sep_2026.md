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

# Concurrency

Allowing more than one task to be handled at the same time
- broader term than parallelism, ie. multiple tasks have the ability to run in an **overlapping manner**
- we **switch** between tasks
    - baker starts a second cake while the first is in owen

Concurrency is about **managing** many things at once, but **not necessarily doing** them at the exact same instant.

---

# Parallelism

Executing multiple operations at the **exact same time**
- Concurrency can happen on a single-core CPU via "time slicing," 
- Parallelism **requires a CPU / GPU with multiple cores or multiple machines**.
    - Two distinct bakers working on two different cakes simultaneously

Parallelism implies concurrency, but concurrency does not always imply parallelism

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
- This makes standard multithreading ineffective for speeding up CPU-bound tasks

GIL exists primarily because of memory management
- For CPU-bound Python code, the GIL remains locked
- GIL is released during **I/O operations**
- **Asyncio** to handle many I/O-bound tasks concurrently

---

# Asyncio: to write concurrent code

Coroutines

```python
async def greet():
    print("hello")

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

What is the total duration?

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

# Mixed awaits

```python
sleep2 = asyncio.create_task(sleep_job(2))
sleep3 = asyncio.create_task(sleep_job(3))

await sleep_job(2)
await sleep2
await sleep3
```

```python
sleep2 = asyncio.create_task(sleep_job(2))
sleep3 = asyncio.create_task(sleep_job(3))

await sleep2
await sleep3
await sleep_job(2)
```

What is the total duration?

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
`asyncio.gather` returns results in the same order as its inputs

```text
completion: B, then A
results:    A, then B
```

- useful when the input position identifies the job


---

# CPU work inside asyncio

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

```python

task_sleep = asyncio.create_task(asyncio.sleep(2))
task_a = asyncio.create_task(cpu_job(10**8))
task_b = asyncio.create_task(cpu_job(10**8))
```

Duration? 6secs (top) and 6secs (bottom)

---

# Scheduling

`asyncio` cannot interrupt a coroutine that never yields.

```text
Top: CPU tasks scheduled first (~6 seconds total)
CPU A: [0----2]
CPU B:       [2----4]
sleep:                  [4----6]

Bottom: sleep task scheduled first (~4 seconds total)
timer:  [0----2] expires
CPU A:  [0----2]
CPU B:        [2----4]
resume:               sleep resumes at ~4
```

Asyncio is excellent at **latency hiding for I/O**, but not for a CPU parallelism mechanism.

---

# Is file access async?

```python
async def read_file(path):
    with open(path, "rb") as file:
        return file.read()

await asyncio.gather(
    read_file("file1"),
    read_file("file2"),
)
```

 - This is still synchronous file I/O running on the event-loop thread.

Move the blocking function away from the loop!

```python
content = await asyncio.to_thread(read_file, path)
```

---

# What does `to_thread` solve?

```python
await asyncio.gather(
    asyncio.to_thread(read_file, "file1"),
    asyncio.to_thread(read_file, "file2"),
)
```
- `asyncio.to_thread()` moves blocking work off the event-loop thread
  - the loop can keep running while the worker waits

- GIL allows only one thread at a time to execute Python bytecode
  - helps with blocking I/O, but doesn't speed up CPU work.

**What if the GIL is disabled?** 

---

# Free-threaded Python

Python 3.13 introduced the optional free-threaded build.

In Python 3.14, it became **officially supported**
- but remains optional, not the default build

```python
import sys

print("GIL enabled:", sys._is_gil_enabled())
```
Free-threaded Python is not automatically faster for every workload

---

# Parallelism still needs limits

With the GIL disabled, CPU-bound threads can run in parallel
- CPU cores and memory are still limited

```python
tasks = [asyncio.to_thread(cpu_work, 50_000_000) for _ in range(100)]
await asyncio.gather(*tasks)
```

Bound active work!

```python
sem = asyncio.Semaphore(8)
async def worker():
    async with sem:
        return await asyncio.to_thread(cpu_work, 50_000_000)
```
- Use queue, worker pool, or semaphore

---

# Layered approach


- asyncio:    coordinate and communicate
- threads:    execute synchronous work
- no-GIL:     allow Python threads to execute in parallel

Parallel work still needs 
- protect shared resources
- use thread-safe signalling to coordinate between workers and the event loop



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

---

# Match the tool to the workload

| Workload | Start with |
|---|---|
| Many I/O waits | `asyncio` |
| Blocking library call | `asyncio.to_thread` |
| Pure-Python CPU work | free-threaded threads, interpreters, or processes |
| I/O followed by CPU work | `asyncio` plus bounded workers |
