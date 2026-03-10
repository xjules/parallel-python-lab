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
- Multiple Python threads can execute **bytecode simultaneously**
- Enables **true CPU parallelism** with threads
- Still experimental (not default yet)
- ⚠️ Many libraries are **not yet thread-safe**
- CPU-bound tasks

------------------------------------------------------------------------

# Installing Free-Threaded Python (uv + venv)
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

- Threads are **truly in parallel**
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

# Asyncio + Free-Threaded

- `asyncio` runs an **event loop** that is typically **single-threaded**
- Free-threaded Python does **not** make coroutines parallel
- `await` still means: _"pause me, run something else"_
- `asyncio` offloads work to **threads**, which can execute in parallel
- **one loop** = one thread that drives coroutine execution

---

# Async execution of CPU work (now worth it)

Before (GIL): thread offload helps mostly for I/O or C-extensions releasing GIL  
After (no-GIL): thread offload can speed up **pure Python CPU loops**

```python
import asyncio

def cpu_work(n: int) -> int:
    s = 0
    for i in range(n):
        s += i
    return s

async def main():
    # 4 CPU jobs in parallel threads (no-GIL makes this real parallelism)
    results = await asyncio.gather(
        asyncio.to_thread(cpu_work, 50_000_000),
        asyncio.to_thread(cpu_work, 50_000_000),
        asyncio.to_thread(cpu_work, 50_000_000),
        asyncio.to_thread(cpu_work, 50_000_000),
    )
    print(sum(results))

asyncio.run(main())
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
    tasks = [worker(sem, 30_000_000) for _ in range(100)]
    results = await asyncio.gather(*tasks)

asyncio.run(main())
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
# Messaging

```python
def worker(loop: asyncio.AbstractEventLoop, q: asyncio.Queue):
    # quick sync job / signal to the loop
    loop.call_soon_threadsafe(q.put_nowait, "hello from thread")

async def main():
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()

    await asyncio.to_thread(worker, loop, q)

    item = await q.get()
    print(item)

asyncio.run(main())
```
---
# Across thread and across loops
```python
async def consume(x):
    await asyncio.sleep(0)
    print(f"consumed: {x}")

def worker(loop):
    # start async work and get the results
    fut = asyncio.run_coroutine_threadsafe(consume("from thread"), loop)
    fut.result()

async def main():
    loop = asyncio.get_running_loop()
    await asyncio.to_thread(worker, loop)

asyncio.run(main())
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

# Synchronization: you need it *more*, not less

No-GIL means **real data races** are now possible in Python code.

Rules of thumb:

- Coroutines share memory inside the loop (safe-ish by sequencing)
- Threads run truly parallel → shared state needs locks

Use the right primitive:

- Inside async code: `asyncio.Lock`, `asyncio.Queue`
- Across threads: `threading.Lock`, `queue.Queue`
- Between async + threads: prefer message passing; avoid shared mutable state

---

# Thread ↔ Loop interaction: call it safely

If a background thread must signal the event loop:

- use `loop.call_soon_threadsafe(...)`

```python
import asyncio, threading

async def main():
    loop = asyncio.get_running_loop()
    fut = loop.create_future()

    def in_thread():
        # safe cross-thread handoff
        loop.call_soon_threadsafe(fut.set_result, "done")

    threading.Thread(target=in_thread).start()
    print(await fut)

asyncio.run(main())
```

---

# The honest takeaway

Free-threaded Python is **not** “async but faster”.

It gives you a sharper tool:

- `asyncio` = orchestration + I/O concurrency
- threads (no-GIL) = real CPU parallelism **when you offload**
- synchronization = your responsibility (locks / queues / ownership)

If you keep the architecture clean (message passing, bounded concurrency),
you get speed **without** turning your code into a race-condition museum.