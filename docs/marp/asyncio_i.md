---
marp: true
theme: dracula
class: invert
paginate: true
size: 16:9
---
# Asyncio

standard python library to write concurrent code

- Single-threaded
- Cooperative multitasking
- Tasks explicitly yield control

---
# Coroutines

``` python
async def run():
    await something()
    ...
    await something_else()
```

- `async def` creates a coroutine
- `await` yields control to the event loop if awaited object is not ready
    - requires **an event loop!**
- Normal functions block
- Coroutines can cooperate
- Calling a coroutine function **does not run the code**.

---
# The `await`
The Suspension Point - used to pause the current coroutine until the awaited operation finishes

- **Yielding Control** - when you `await`, you tell the Event Loop: 
    - _"I am still waiting; go ahead and run something else in the meantime"_
- `await` can **only** be used inside a coroutine, `async def`

---
# Tasks
Represents the actual **concurrency**

- Submits a coroutine to the event loop in the [background](../../src/examples/sleep_job/my_job.py)
  - Scheduled and starts immediately
  - Runs concurrently
``` python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep2 = asyncio.create_task(my_job(2))
sleep3 = asyncio.create_task(my_job(3))
await sleep2
await sleep3
```
---
# Tasks - results
- awaiting tasks delivers results!
``` python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

sleep2 = asyncio.create_task(my_job(2))
sleep3 = asyncio.create_task(my_job(3))
result2 = await sleep2
result3 = await sleep3
```
---
# Tasks - mix
- how long this takes?
``` python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep2 = asyncio.create_task(my_job(2))
sleep3 = asyncio.create_task(my_job(3))
await my_job(2)
await sleep2
await sleep3
```
[Execution](./execution_ex.md)

---
# Tasks - cancellation

**straightforward!**

```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep_job = asyncio.create_task(my_job(100))
await asyncio.sleep(1)
sleep_job.cancel()
#...
await sleep_job

```
---
# Tasks - cancellation

cancellation injects `CancelledError` at the next await point

```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)  # <--- the point of cancellation

sleep_job = asyncio.create_task(my_job(100))
await asyncio.sleep(1)
sleep_job.cancel()
#...
await sleep_job

```
---
# Tasks - cancellation
propagated and not handled
```python
sleep_job.cancel()
#...
await sleep_job

```
```
asyncio/tasks.py", line 718, in sleep_job
    return await future
           ^^^^^^^^^^^^
asyncio.exceptions.CancelledError
```
---
# Tasks - cancellation
handling - I.
```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep_job = asyncio.create_task(my_job(100))
await asyncio.sleep(1)
sleep_job.cancel()
#...
try:
    await sleep_job
except asyncio.CancellationError
  ...
```
---
# Tasks - cancellation
handling - II.
```python
async def my_job(sleep_time):
    try:
        await asyncio.sleep(sleep_time)
    except asyncio.CancellationError
        pass

sleep_job = asyncio.create_task(my_job(100))
await asyncio.sleep(1)
sleep_job.cancel()
await sleep_job
```

---
# Task - timeout cancellation
```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep_task = asyncio.create_task(my_job(100))
try:
    await asyncio.wait_for(sleep_task, timeout=1)
except asyncio.exceptions.TimeoutError:
    print(f"Task {sleep_task.cancelled()=}")
```
---
# Task - shield
```python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)

sleep_task = asyncio.create_task(my_job(10))
try:
    await asyncio.wait_for(asyncio.shield(sleep_task), timeout=1)
except asyncio.exceptions.TimeoutError:
    print(f"Task {sleep_task.cancelled()=}")
await sleep_task
```
---
# Awaitables

```
          Awaitable  (anything you can "await")
           ┌──────────────┴──────────────┐
       Coroutine                      Future
    (async def fn)            (placeholder for a result;
     yields control            set_result / set_exception)
                                     │
                                   Task
                            (Future + scheduled Coroutine;
                             created via create_task())
```
- **Future** — low-level: _pending → result/exception_
- **Task** — a `Future` that wraps & drives a coroutine on the event loop
---
# Future
Placeholder for a result
- promise of a value
- lower-level primitive
```python
async def my_job(sleep_time, future):
    await asyncio.sleep(sleep_time)
    future.set_result(sleep_time)
    await asyncio.sleep(1.0)

future = asyncio.Future()
sleep_task = asyncio.create_task(my_job(10, future))
value = await future # assert value==10
await sleep_task
```
---
# Future - note!
Cannot be set twice or more!

```python
future = asyncio.Future()

async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    
    future.set_result(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

sleep2 = asyncio.create_task(my_job(2))
results = await asyncio.gather(my_job(3), sleep2, future)
```
---
# `asyncio.gather`
runs and await multiple awaitables
- Results are in the same same order as the inputs
- It automatically turns coroutines into tasks
``` python
async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

future = asyncio.Future()
sleep2 = asyncio.create_task(my_job(2))
results = await asyncio.gather(my_job(3), sleep2, future)
print(results)
```
---
# Gather - note!
```python
future = asyncio.Future()

async def my_job(sleep_time):
    await asyncio.sleep(sleep_time)
    
    future.set_result(sleep_time)
    return f"Sleeping for {sleep_time} seconds"

sleep2 = asyncio.create_task(my_job(2))
# let's not raise!
results = await asyncio.gather(my_job(3), sleep2, future, return_exceptions=True)
```
---
# Async - Queue

Async producer / consumer queue

- coroutine safe
- work distribution
- job distribution
- streaming systems

```python
queue = asyncio.Queue()

await queue.put(order)
order = await queue.get()
```
---
# TaskGroup
async context manager that provides structured concurrency

- safer alternative to `asyncio.gather()`
    - if one task fails **all other tasks** are automatically cancelled
```python
    async def my_job(sleep_time):
        await asyncio.sleep(sleep_time)
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(my_job(2))
        t2 = tg.create_task(my_job(5))
    # at this point t1 and t2 are finished!
```
---

# Async context manager
asynchronous version of the with statement

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
# Async Iterators

```python
async def async_range(count):
    for i in range(count):
        await asyncio.sleep(0.5)
        yield i

async for number in async_range(5):
    print(f"N: {number}")
```

---
# Tasks - async foodtruck

- Implement **async** version of the foodtruck 
    - We don't want to wait for the stage to finish
    - All stages should be async. 
    - Try to use asyncio.gather(...). 
    - Each task should exit gracefully. We don't want Ctrl+C
- Implement **exception** handling
- Introduce random exception to the cook stage (random chance order gets burned) and handle it
