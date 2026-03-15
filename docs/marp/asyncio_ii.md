---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---

# Event loop - central scheduler
The core of every `asyncio` application that manages and distributes execution
- Execution Model runs in a **single thread** and performs three primary jobs
    - **Monitor** OS I/O events (network sockets, pipes, etc.).
    - **Run** ready callbacks and scheduled tasks
    - **Resume** coroutines whose awaited operations (like I/O) have completed
---
# Event loop - managing concurrency
Loop cycle maintains a queue of tasks and runs them one at a time until
- a task hits `await`, which yields control
    - `I am waiting for I/O; run something else in the meantime`

The loop uses efficient system-level APIs (**epoll**, **kqueue**, or **IOCP**) to track these pauses without wasting CPU cycles
- Thousands of "ultra-light" tasks can overlap on a single CPU core!

---
# Event loop - creation `asyncio.run()`

Performs three critical steps
- Creates a brand-new **Event Loop**
- Runs the main coroutine until completion
- Handles cleanup and closes the loop automatically

``` python
async def main_task():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

    sleep = asyncio.create_task(my_job(2))
    await sleep
asyncio.run(main_task(), debug=True)
```
---
# Task coordination

real systems must handle
- thousands of jobs
- different processing stages
- limited resources
- tasks depending on other tasks

`Async code quickly becomes chaos without structure`

---
# Async Workload Types

Async excels at **I/O-bound** workloads
- web scraping
- API calls
- file processing
- streaming pipelines
- messaging

Typical pattern: `wait → process → wait → process`. While waiting, the event loop runs other tasks

---
# Common Async Patterns

Patterns decides how tasks interact

- Fan-out / Fan-in
- Worker pool
- Producer--Consumer
- Pipelines

---
# Fan-Out / Fan-In

- Split work → run concurrently → collect results.
    - Fan-out: many tasks start
    - Fan-in: results gathered

``` python
async def download(url):
    ...

results = await asyncio.gather(
    *(download(u) for u in urls)
)
```

---
# Worker Pool Pattern

Limit concurrency using fixed number of workers  eg., 1000 downloads but only 10 workers

Benefits include bounded concurrency, stable memory usage, predictable load, ..

``` python
async def worker(queue):
    while True:
        job = await queue.get()
        await process(job)
        queue.task_done()
    ...
    # shutdown gracefully: await queue.join()
```
---
# Producer--Consumer Pattern

- Producer → Queue → Consumer
    - Tasks generate work for other tasks.
- Examples:
    - job distribution
    - pipelines
    - streaming systems
``` python
await queue.put(job)
job = await queue.get()
```
---
# Async Pipelines
Work split into stages
- eg., Download → Parse → Store
- Each stage reads from one async Queue and writes to another

Queue → Workers → Queue → Workers

```python
download_q = asyncio.Queue()
parse_q = asyncio.Queue()
store_q = asyncio.Queue()
```
---
# Task Coordination
Tasks often depend on each other
- wait until resource is available
- signal when work is ready
- limit concurrency
- Asyncio provides primitives for this

---

# Coordination Primitives

- To control **when task run** and **who can run it**
    - `Queue`
    - `Event`
    - `Lock`
    - `Semaphore`
    - `Condition`

---

# Event

signal between tasks.

``` python
event = asyncio.Event() # create
await event.wait() # wait for signal
event.set() # fire up
```
Use cases:
- system initialization
- synchronization
- notifying workers

---

# Semaphore

limit number of concurrent operations.

``` python
sem = asyncio.Semaphore(10) # create with max 10 async workers
async with sem: # gate
    await download(url)
```
Use cases:
- API rate limits
- database connections
- network throttling

---
# Async Locks

``` python
lock = asyncio.Lock()

async with lock:
    shared_counter += 1
```
Use cases:
- protect shared resources
- multiple tasks modify the same data

---
# CPU bound code 
once started, each [task](../../src/examples/lecture/io_cpu_bound.py) will keep event loop busy

```python
async def cpu_bound_job(n):
    count = 0
    for i in range(n):
        count += i
    return count

    task_sum_1 = asyncio.create_task(cpu_bound_job(10**8)) #2secs
    task_sum_2 = asyncio.create_task(cpu_bound_job(10**8)) #2secs
    result1 = await task_sum_1
    result2 = await task_sum_2
    print(f"Results: {result1=} {result2=}")
```
---
# CPU bound code never yields
```python
async def cpu_bound_job(n):
    count = 0
    for i in range(n):
        count += i
    return count

    task_sum_1 = asyncio.create_task(cpu_bound_job(10**8)) #2secs
    task_sum_2 = asyncio.create_task(cpu_bound_job(10**8)) #2secs
    task_sleep = asyncio.create_task(asyncio.sleep(2)) #2secs
    result1 = await task_sum_1
    result2 = await task_sum_2
    await task_sleep
    print(f"Results: {result1=} {result2=}")
```
---
# I/O bound code - disk access
```python
async def read_file(path):
    with open(path, "r") as f:
        return f.read()

async def main():
    t1 = asyncio.create_task(read_file("file1.txt"))
    t2 = asyncio.create_task(read_file("file2.txt"))

    content1 = await t1
    content2 = await t2
    print(len(content1), len(content2))
```

`async def` won't make the code non-blocking

---
# I/O bound code - disk access
move blocking work off the event loop

```python
def read_file(path):
    with open(path, "rb") as f:
        return f.read()

async def read_task(name, path):
    content = await asyncio.to_thread(read_file, path)

t1 = asyncio.create_task(read_task("file1.txt"))
t2 = asyncio.create_task(read_task("file2.txt"))

await asyncio.gather(t1, t2)
```
---

# I/O bound code - disk access -equivalent
move blocking work off the event loop

```python
def read_file(path):
    with open(path, "rb") as f:
        return f.read()

async def read_task(name, path):
    loop = asyncio.get_running_loop()
    content = await loop.run_in_executor(None, read_file, path)

t1 = asyncio.create_task(read_task("file1.txt"))
t2 = asyncio.create_task(read_task("file2.txt"))

await asyncio.gather(t1, t2)
```
---
# I/O bound code - aiofiles

```python
async def read_file(path):
    async with aiofiles.open(path, "rb") as f:
        return await f.read()

t1 = asyncio.create_task(read_file("file1.txt"))
t2 = asyncio.create_task(read_file("file2.txt"))

await asyncio.gather(t1, t2)
```

the event loop can schedule other tasks while disk I/O is pending
- `asyncio.to_thread` moves blocking code to a thread

---
# It works ....

- Disk, network, and database calls spend most time **waiting**
- While one task waits, the event loop runs another task
- Asyncio improves latency hiding

Rule of thumb:

CPU-bound  
→ processes / native code / GPU

I/O-bound  
→ asyncio / async frameworks

---
# Task: foodtruck – Pipeline System

Refactor the async foodtruck into a **pipeline architecture**

- Orde Queue with **limited size**
- Use **asyncio.Queue** for order flow
- Implement a **worker pool** for cooks (multiple cooks allowed)
- Use **asyncio.Semaphore** to limit cooking stations
- Introduce random cooking failures (burned orders)
- Handle exceptions without crashing the system
- Graceful shutdown