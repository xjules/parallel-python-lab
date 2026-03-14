---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---


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

- Async excels at **I/O-bound** workloads
    - web scraping
    - API calls
    - file processing
    - streaming pipelines
    - messaging
- Typical pattern: `wait → process → wait → process`
    - while waiting, the event loop runs other tasks

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

- limit concurrency; ex. 1000 downloads but only 10 workers
    - bounded concurrency
    - stable memory usage
    - predictable load

``` python
async def worker(queue):
    while True:
        job = await queue.get()
        await process(job)
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
- Ex., Download → Parse → Store
- Each stage 
    - reads from async Queue
    - writes to async Queue
    - Queue → Workers → Queue → Workers

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
# CPU bound code blocks the event loop
once started, each task will keep event loop busy

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
# Event loop - central scheduler
- The core of every `asyncio` application that manages and distributes execution
- Execution Model runs in a **single thread** and performs three primary jobs
    - **Monitor** OS I/O events (network sockets, pipes, etc.).
    - **Run** ready callbacks and scheduled tasks
    - **Resume** coroutines whose awaited operations (like I/O) have completed
---

# Event loop - managing concurrency
- The Loop Cycle - maintains a queue of tasks and runs them one at a time until a task hits `await`
- Yielding control - when a coroutine hits `await`, it pauses and tells the loop: 
    - _I am waiting for I/O; run something else in the meantime_

---
# Event loop - efficiency

- OS Notification
    - The loop uses efficient system-level APIs (**epoll**, **kqueue**, or **IOCP**) to track these pauses without wasting CPU cycles
    - Thousands of "ultra-light" tasks can overlap on a single CPU core, creating massive concurrency for I/O-bound workloads


---
# Event loop - creation `asyncio.run()`
- The recommended way to launch an async application
- Automated Lifecycle that performs three critical steps:
    1. Creates a brand-new **Event Loop**
    2. Runs the main coroutine until completion
    3. Handles cleanup and closes the loop automatically

``` python
async def main_task():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

    sleep2 = asyncio.create_task(my_job(2))
asyncio.run(main_task(), debug=True)
```
---
# Event loop - direct access
``` python
async def main_task():
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

    loop = asyncio.get_running_loop()
    loop.call_soon(my_job)
asyncio.run(main_task())
```
---
# Event loop - signal handlers
``` python
async def main_task():
    def cancel_tasks():
        tasks = asyncio.all_tasks()
        [task.cancel() for task in tasks]
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, cancel_tasks)
asyncio.run(main_task())
```
---

# Event Loop - run sync tasks concurrently

``` python

def sync_job_1():
    # heavy job
def sync_job_2():
    # heavy job
async def run():
    my_loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, sync_io_task_1),
        loop.run_in_executor(None, sync_io_task_2),
    ]
    results = await asyncio.gather(*tasks)
asyncio.run(run())
```