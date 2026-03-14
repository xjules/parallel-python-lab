---
class: invert
marp: true
paginate: true
size: "16:9"
theme: dracula
---

# Free-Threaded Python (No-GIL)

Python 3.13 introduces an **experimental free-threaded build**

- Removes the **Global Interpreter Lock**
- Multiple Python threads can execute Python bytecode **at the same time**
- Enables **true CPU parallelism** with threads
- Still experimental (not default yet)
    - ⚠️ Many libraries are **not yet thread-safe**
- CPU-bound tasks

------------------------------------------------------------------------

# Installing Free-Threaded Python
3.13t or 3.14t = free-threaded build
``` bash
uv venv env313t --python 3.13t
```
Verify that the **GIL is disabled**:

``` python
import sys
print(sys._is_gil_enabled())
```

---
# Example

Threads are **truly in parallel**
``` python
def work():
    total = 0
    for i in range(10**8):
        total += i
    print(total)

threads = [threading.Thread(target=work) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```
---
# Are threads enough?

threads scale poorly for IO concurrency
async scales poorly for CPU parallelism

eg., 10000 HTTP requests
- threads: 10000 threads - memory explosion
- async - 10000 tasks - cheap

---
# Async + Parallel Architecture

```
async event loop
        │
        │ orchestrates
        ▼
thread pool / process pool
        │
        ▼
CPU parallel work
```
---


---

# Asyncio + Free-Threaded

`asyncio` runs an **event loop** that is typically **single-threaded**
- Free-threaded Python does **not** make coroutines parallel
- `await` still means: _"pause me, run something else"_
- `asyncio` offloads work to **threads**, which can execute in parallel
- **one loop** = one thread that drives coroutine execution

---
# Async with CPU bound work

GIL 
- thread offload helps mostly for I/O or C-extensions releasing GIL  

No-GIL
- thread offload can speed up **pure Python CPU loops**

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

# Bounded concurrency

Use Semaphore!
- avoid `gather(*[to_thread(...) for _ in range(10_000)])`

```python
async def worker(sem: asyncio.Semaphore):
    async with sem:
        # CPU bound sync code in parallel_work
        return await asyncio.to_thread(parallel_work)

async def main():
    sem = asyncio.Semaphore(8)
    tasks = [worker(sem) for _ in range(100)]
    results = await asyncio.gather(*tasks)
```
---
# Better control
```python
async def main():
    async with asyncio.TaskGroup() as tg:
        for _ in range(20):
            tg.create_task(asyncio.to_thread(heavy_calculation, 10**7))
asyncio.run(main())

```

---
# Message to the main loop

```python
def worker(loop: asyncio.AbstractEventLoop, q: asyncio.Queue):
    # quick sync job / signal to the loop
    loop.call_soon_threadsafe(q.put_nowait, "worker started ...")
    cpu_bound_func(...)
    loop.call_soon_threadsafe(q.put_nowait, "worker finished.")

async def main():
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()
    await asyncio.to_thread(worker, loop, q)
    while True:
        item = await q.get()
        print(item)
```
---
# Collaboration

```python
def worker(job_id: int, loop: asyncio.AbstractEventLoop, q: asyncio.Queue):
    loop.call_soon_threadsafe(q.put_nowait, f"worker {job_id} started ...")
    cpu_bound_func(...)
    loop.call_soon_threadsafe(q.put_nowait, f"worker {job_id} finished.")

async def main():
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()
    async with asyncio.TaskGroup() as tg:
        for i in range(100):
            tg.create_task(asyncio.to_thread(worker, i, loop, q))
        while True:
            item = await q.get()
            print(item)
```
---
# Collaboration - cont.

```python
async def send_status(msg):
    # send async message
def worker(job_id: int, loop: asyncio.AbstractEventLoop, q: asyncio.Queue):
    loop.call_soon_threadsafe(q.put_nowait, f"worker {job_id} started ...")
    cpu_bound_func(...)
    loop.run_coroutine_threadsafe(send_status(f"worker {job_id} finished."))
async def main():
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()
    async with asyncio.TaskGroup() as tg:
        for i in range(100):
            tg.create_task(asyncio.to_thread(worker, i, loop, q))
        while True:
            item = await q.get()
            print(item)
```
---
# Call soon vs run coroutine

- `loop.call_soon_threadsafe`
    - when a thread wants to signal the loop
    - Examples: push to asyncio.Queue, cancel a task, wake a coroutine
- `run_coroutine_threadsafe`
    - when a thread wants to run async code and get the result

- [diagram](loop_thread_fig.md)
---

# Synchronization is inevitable!

No-GIL means **real data races** are now possible in Python code
- Coroutines share memory inside the loop
- Threads run truly parallel → shared state needs locks

The right primitive:
- Inside async code: `asyncio.Lock`, `asyncio.Queue`
- Across threads: `threading.Lock`, `queue.Queue`
- Between async + threads: prefer message passing

---

# Summary

Free-threaded Python is **not** “async but faster”.

It gives you a sharper tool:

- `asyncio` = orchestration + I/O concurrency
- threads (no-GIL) = real CPU parallelism **when you offload**
- synchronization = your responsibility (locks / queues / ownership)

If you keep the architecture clean (message passing, bounded concurrency),
you get speed **without** turning your code into a race-condition museum.