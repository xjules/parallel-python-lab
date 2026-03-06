---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---
# Tasks
- Represents the actual **concurrency**
- Submits a coroutine to the event loop in the background
  - Scheduled and starts immediately
  - Runs concurrently
``` python
cook = Cook()
consumer = Consumer():
task1 = asyncio.create_task(cook.run())
task2 = asyncio.create_task(consumer.run())
await task1
await task2
```

---
# Await tasks
- direct handle on a task
```python
tasks = [asyncio.create_task(Cook(i).run()) for i in range(10)]
```
   - raise exception by gather

```python
results = await asyncio.gather(*tasks, return_exceptions=False)
```
    - return exception by gather
    ```python
    results = await asyncio.gather(*tasks, return_exceptions=True)
    ```
---

# Futures - tasks

- Placeholder for a result
  - promise of a value
- Lower-level primitives
- Tasks are built on Futures
```python
tasks = [asyncio.create_task(Cook(i).run()) for i in range(10)]
```

---
# Futures - event

``` python
class Cook:
    async def do_sth_else(fut):
        # do sth else
        fut.set_result("sth else done")

    async def run(self):
        my_loop = asyncio.get_running_loop()
        fut_event = my_loop.create_future()
        asyncio.create_task(self.do_sth(fut_event))
        await fut_event
```
---

# Async context manager

- asynchronous version of the with statement 
- It uses async with to handle resources
- await to open or close 
- `__aenter__` and `__aexit__` 
- Non-blocking cleanup

### Note: implement async with foodtruck:

---

# Async context manager - alternative

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def seismic_file_access():
    print("Opening file...")
    try:
        yield "seismic file"
    finally:
        print("Closing file...")
```
---
# TaskGroup
- async context manager that provides structured concurrency
- safer alternative to `asyncio.gather()`
    - if one task fails **all other tasks** are automatically cancelled
```python
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(cook.run())
        t2 = tg.create_task(consumer.run())
    # at this point t1 and t2 are finished!
```
---

# Async Iterators

``` python
async def async_range(count):
    for i in range(count):
        await asyncio.sleep(0.5)
        yield i

async for number in async_range(5):
    print(f"N: {number}")
```
---
# Task coordination
- real systems must handle
    - thousands of jobs
    - different processing stages
    - limited resources
    - tasks depending on other tasks

`Async code quickly becomes chaos without structure.`

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

- Work split into stages
    - Ex., Download → Parse → Store
- Each stage 
    - reads from async Queue
    - writes to async Queue
    - Queue → Workers → Queue → Workers

``` python
download_q = asyncio.Queue()
parse_q = asyncio.Queue()
store_q = asyncio.Queue()
```
---
# Task Coordination

- Tasks often depend on each other
    - wait until resource is available
    - signal when work is ready
    - limit concurrency
- Asyncio provides primitives for this.

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

- signal between tasks.

``` python
event = asyncio.Event() # create
await event.wait() # wait for signal
event.set() # fire up
```
- Use cases:
    - system initialization
    - synchronization
    - notifying workers

---

# Semaphore

- limit number of concurrent operations.

``` python
sem = asyncio.Semaphore(10) # create with max 10 async workers
async with sem: # gate
    await download(url)
```
- Use cases:
    - API rate limits
    - database connections
    - network throttling

---

# Async Locks

- protect shared resources
    - Ex., when multiple tasks modify the same data
``` python
lock = asyncio.Lock()

async with lock:
    shared_counter += 1
```
---

# Structured Concurrency

- modern asyncio encourages to use `TaskGroup`

``` python
async with asyncio.TaskGroup() as tg:
    tg.create_task(worker())
    tg.create_task(worker())
```

- if one task fails:
    - all tasks cancel
    - system remains consistent

